import re
import logging
from difflib import SequenceMatcher
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- CONFIGURATION ---
ELEMENT_WAIT_TIMEOUT = 5
CONTACT_PAGE_TIMEOUT = 8
PAGE_LOAD_TIMEOUT = 10

class FuzzyMatcher:
    @staticmethod
    def get_similarity(a, b):
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    @staticmethod
    def match_score(text, keywords_list):
        if not text: 
            return 0
        text = text.lower().strip()
        best_score = 0
        for keyword in keywords_list:
            if keyword in text:
                if text.startswith(keyword) or f" {keyword}" in text:
                    return 100
                best_score = max(best_score, 85)
            sim = FuzzyMatcher.get_similarity(text, keyword)
            best_score = max(best_score, sim * 100)
        return best_score

class KeywordDatabase:
    high_probability_page_with_these_pages = ["career", "careers", "job", "jobs", "hiring", "vacancy", "opening", "recruit"]
    mid_probability_page_with_these_pages = ["contact", "about", "team", "people", "work", "join", "talent"]
    HIGH_VALUE_PREFIXES_OF_EMAIL = ["career", "job", "hiring", "recruit", "hr", "talent", "cv"]
    BLACKLIST_PREFIXES = ["sales", "support", "help", "billing", "invoice", "orders", "marketing"]

class LinkRanker:
    def __init__(self):
        self.fuzzy = FuzzyMatcher()
        
    def rank_links(self, link_data_list, current_url):
        """
        Expects a list of dicts: [{'href': '...', 'text': '...'}]
        Optimized: Calculate scores once per link
        """
        ranked_links = []
        seen_urls = set()
        
        print(f"\n[Link Analysis] Evaluating {len(link_data_list)} unique internal links...")
        
        for link in link_data_list:
            href = link['href'].strip()
            text = (link['text'][:60].strip() or "NO TEXT").replace('\n', ' ')
            
            # Skip duplicates and current page
            if href in seen_urls or href == current_url:
                continue
                
            seen_urls.add(href)
            
            # Calculate scores once
            high_prob_score = self.fuzzy.match_score(text, KeywordDatabase.high_probability_page_with_these_pages)
            mid_prob_score = self.fuzzy.match_score(text, KeywordDatabase.mid_probability_page_with_these_pages)
            
            # Determine tier and use best score
            if high_prob_score > 70:
                tier = 1
                score = high_prob_score
            elif mid_prob_score > 70:
                tier = 2
                score = mid_prob_score
            else:
                continue  # Skip links that don't match
            
            ranked_links.append({
                'href': href,
                'text': text,
                'score': score,
                'tier': tier
            })
            
            print(f"  [{tier}] {text:<45} | Score: {score:.1f}")
        
        # Sort by tier first, then by score
        sorted_links = sorted(ranked_links, key=lambda x: (x['tier'], -x['score']))
        
        # Verbose Table Output
        print("\n" + "-" * 100)
        print(f"{'SCORE':<8} | {'TIER':<5} | {'LINK TEXT':<50} | {'URL'}")
        print("-" * 100)
        for l in sorted_links[:10]:
            print(f"{l['score']:<8.1f} | {l['tier']:<5} | {l['text']:<50} | {l['href']}")
        print("-" * 100)
        
        return sorted_links

class EmailExtractor:
    def __init__(self, driver):
        self.driver = driver
        self.ranker = LinkRanker()
        self.fuzzy = FuzzyMatcher()
        self.visited_pages = set()
        self.wait = WebDriverWait(driver, ELEMENT_WAIT_TIMEOUT)

    def get_internal_links_js(self):
        """Uses raw JS to find internal links only (same origin)."""
        js_script = """
        const origin = window.location.origin;
        return Array.from(document.querySelectorAll('a'))
            .filter(a => a.href && a.href.startsWith(origin) && !a.href.includes('#'))
            .map(a => ({
                href: a.href,
                text: (a.innerText || a.getAttribute('aria-label') || "").trim()
            }))
            .filter(a => a.text.length > 0);
        """
        try:
            return self.driver.execute_script(js_script)
        except Exception as e:
            print(f"[!] JS execution error: {e}")
            return []

    def _safe_page_load(self, url, timeout=PAGE_LOAD_TIMEOUT):
        """Load page with timeout handling and wait for body element."""
        try:
            self.driver.set_page_load_timeout(timeout)
            self.driver.get(url)
            
            # Wait for body to be present
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            return True
        except TimeoutException:
            print(f"    [⏱] Page load timeout - proceeding with partial content")
            return True
        except Exception as e:
            print(f"    [✗] Failed to load page: {str(e)[:80]}")
            return False

    def get_emails_from_website(self, website_url):
        all_emails = {}
        self.visited_pages.clear()
        
        print(f"\n{'='*60}\nSTARTING SCRAPE: {website_url}\n{'='*60}")
        
        try:
            # 1. Homepage Extraction
            print(f"[*] Accessing Homepage: {website_url}")
            if not self._safe_page_load(website_url):
                print("[!] Could not load homepage, aborting")
                return []
            
            self.visited_pages.add(website_url)
            home_emails = self._extract_and_score_emails("Homepage")
            self._merge_emails(all_emails, home_emails)
            
            # Early Exit if "Jackpot" found
            if any(d['score'] >= 90 for d in all_emails.values()):
                print("[!] Jackpot found on homepage! Finishing.")
                return self._format_results(all_emails)

            # 2. JS Link Extraction
            print("[*] Extracting internal links...")
            raw_internal_links = self.get_internal_links_js()
            print(f"[*] Found {len(raw_internal_links)} links on homepage")
            
            if not raw_internal_links:
                print("[!] No internal links found")
                return self._format_results(all_emails)
            
            ranked_links = self.ranker.rank_links(raw_internal_links, website_url)
            # 3. Visit top candidates
            target_links = [l for l in ranked_links if l['tier'] <= 2]
            max_pages = min(4, len(target_links))
            
            for i, link in enumerate(target_links[:max_pages]):
                url = link['href']
                if url in self.visited_pages:
                    continue
                
                print(f"\n[Step {i+1}/{max_pages}] Navigating to: {link['text']}")
                
                if not self._safe_page_load(url, timeout=CONTACT_PAGE_TIMEOUT):
                    continue
                
                self.visited_pages.add(url)
                
                try:
                    subpage_emails = self._extract_and_score_emails(f"Page: {link['text']}")
                    self._merge_emails(all_emails, subpage_emails)
                    
                    if any(d['score'] >= 90 for d in subpage_emails.values()):
                        print(f"    [✓] High-value email found. Stopping depth search.")
                        break
                except Exception as e:
                    print(f"    [!] Error extracting emails: {str(e)[:60]}")

        except Exception as e:
            print(f"[CRITICAL ERROR] {str(e)[:100]}")
            
        print(f"\n{'='*60}\nSCRAPE COMPLETE: Found {len(all_emails)} unique emails.\n{'='*60}")
        return self._format_results(all_emails)

    def _extract_and_score_emails(self, source_name):
        found = {}
        try:
            # Extract emails from page text
            body = self.driver.find_element(By.TAG_NAME, "body").text
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', body)
            
            # Also check mailto links
            try:
                mailtos = self.driver.find_elements(By.XPATH, "//a[starts-with(@href, 'mailto:')]")
                for m in mailtos:
                    href = m.get_attribute('href')
                    if href:
                        email = href.replace('mailto:', '').split('?')[0]
                        emails.append(email)
            except NoSuchElementException:
                pass

            unique_emails = list(set(emails))
            if unique_emails:
                print(f"    [+] Analyzing {len(unique_emails)} emails on {source_name}:")
                
            for email in unique_emails:
                prefix = email.split('@')[0].lower()
                
                # Scoring
                is_bad = self.fuzzy.match_score(prefix, KeywordDatabase.BLACKLIST_PREFIXES) > 85
                is_gold = self.fuzzy.match_score(prefix, KeywordDatabase.HIGH_VALUE_PREFIXES_OF_EMAIL) > 85
                
                if is_bad:
                    score, tag = 5, "REJECT (Blacklist)"
                elif is_gold:
                    score, tag = 95, "GOLD (Hiring/HR)"
                else:
                    score, tag = 45, "NEUTRAL (Info/Contact)"
                    
                print(f"        - {email:<35} | Score: {score:<3} | {tag}")
                found[email] = {'score': score, 'source': source_name}
                
        except Exception as e:
            print(f"    [!] Error extracting emails: {str(e)[:60]}")
            
        return found

    def _merge_emails(self, main_dict, new_emails):
        for email, data in new_emails.items():
            if email not in main_dict or data['score'] > main_dict[email]['score']:
                main_dict[email] = data

    def _format_results(self, emails_dict):
        # Filter out the junk and sort by relevance
        sorted_results = sorted(
            [e for e, d in emails_dict.items() if d['score'] > 10],
            key=lambda e: emails_dict[e]['score'],
            reverse=True
        )
        return sorted_results