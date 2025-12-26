# google_scraper.py
"""Google business search scraper"""

import time
import urllib.parse
import re
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from config import GOOGLE_SEARCH_BASE_URL, ELEMENT_WAIT_TIMEOUT


class GoogleScraper:
    """Scrapes business information from Google search results"""
    
    def __init__(self, driver, excel_manager, socketio=None):
        self.driver = driver
        self.excel_manager = excel_manager
        self.socketio = socketio
    
    def scrape_businesses(self, business_name, city):
        """Scrape businesses for a specific city"""
        print(f"\n{'='*60}")
        print(f"Searching: {business_name} in {city}")
        print(f"{'='*60}\n")

        query = f"{business_name} {city}"
        full_url = GOOGLE_SEARCH_BASE_URL + urllib.parse.quote(query)

        print(f"Search query: {query}")
        print(f"URL: {full_url}\n")

        try:
            self.driver.get(full_url)
            print("✓ Loaded Google search page\n")
            time.sleep(2)
        except Exception as e:
            print(f"✗ Error loading Google search page: {e}")
            logging.error(f"Error loading Google for {city}: {e}")
            return 0

        if self.socketio:
            self.socketio.emit('onWarn', f'Starting scrape for {city}')

        page_count = 0
        total_scraped = 0

        while True:
            page_count += 1
            print(f"--- Page {page_count} ---")

            sections = self._select_businesses()

            if not sections:
                print("✗ No businesses found on this page")
                break

            print(f"Found {len(sections)} businesses on this page")

            for idx, section in enumerate(sections, 1):
                try:
                    print(f"  [{idx}/{len(sections)}] ", end="")

                    business_data = self._extract_company_info(section)
                    
                    if not business_data['name']:
                        print("✗ Could not extract company name")
                        continue

                    print(f"{business_data['name'][:40]}")
                    print(self.excel_manager.is_data_present(
                        business_data['phone'], 
                        business_data['website'],
                        city
                    ))
                    if not self.excel_manager.is_data_present(
                        business_data['phone'], 
                        business_data['website'],
                        city
                    ):
                        self.excel_manager.insert_data(
                            company_name=business_data['name'],
                            company_website=business_data['website'],
                            company_email=None,
                            company_phone=business_data['phone'],
                            rating_ratio=business_data['rating'],
                            number_of_ratings=business_data['numRatings'],
                            city=city
                        )
                        
                        total_scraped += 1
                        print(f"      ✓ Added to Excel")
                        
                        if self.socketio:
                            self.socketio.emit('scrape_update', {'data': business_data})
                    else:
                        print(f"      ⊙ Already exists in Excel")
                        if self.socketio:
                            self.socketio.emit('onWarn', 'Data already present')

                except Exception as e:
                    logging.error(f"Error processing company: {str(e)}")
                    print(f"      ✗ Error: {str(e)}")

            # Try to go to next page
            if not self._go_to_next_page():
                print("\n✓ Reached last page")
                break

            time.sleep(3)

        print(f"\n{'='*60}")
        print(f"Completed: {business_name} in {city}")
        print(f"{'='*60}")
        print(f"Businesses scraped: {total_scraped}")
        print(f"Pages processed: {page_count}")
        print(f"{'='*60}\n")

        return total_scraped

    def _select_businesses(self):
        """Select business listing elements from page"""
        try:
            container = WebDriverWait(self.driver, ELEMENT_WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, "MjjYud"))
            )
            sections = container.find_elements(By.CSS_SELECTOR, "[jscontroller='AtSb']")
            return sections
        except TimeoutException:
            if self.socketio:
                self.socketio.emit('onError', 'Selection Error on Page - Timeout')
            logging.error("Timeout waiting for business listings")
            return []
        except Exception as e:
            if self.socketio:
                self.socketio.emit('onError', f'Selection Error: {str(e)}')
            logging.error(f"Error selecting businesses: {e}")
            return []

    def _extract_company_info(self, section: WebElement) -> dict:
        """Extract company information from a section element"""
        data = {
            'name': None,
            'phone': None,
            'website': None,
            'rating': None,
            'numRatings': None
        }

        try:
            # Extract company name
            company_name_element = section.find_element(By.CSS_SELECTOR, "span.OSrXXb")
            data['name'] = company_name_element.text

            # Extract website
            try:
                website_link = section.find_element(
                    By.CSS_SELECTOR, 
                    "a.yYlJEf.Q7PwXb.L48Cpd.brKmxb"
                )
                data['website'] = website_link.get_attribute("href")
            except NoSuchElementException:
                logging.warning(f"No website found for {data['name']}")

            # Extract phone and ratings
            parent_element = company_name_element.find_element(By.XPATH, "./..")
            next_elements = parent_element.find_elements(By.XPATH, "./following-sibling::div")[:3]

            for idx, element in enumerate(next_elements, start=1):
                # Phone number extraction
                if idx == 3:
                    parts = element.text.split('·')
                    if len(parts) >= 2:
                        phone_number_part = parts[1].strip()
                        data['phone'] = self._clean_phone_number(phone_number_part)

                # Rating extraction
                if idx == 1:
                    try:
                        data['numRatings'] = element.find_element(
                            By.XPATH, 
                            "./span/span/span[3]"
                        ).text.strip('()')
                        
                        data['rating'] = element.find_element(
                            By.XPATH, 
                            "./span/span/span[1]"
                        ).text
                    except NoSuchElementException:
                        pass

        except Exception as e:
            logging.error(f"Error extracting company info: {str(e)}")

        return data

    def _clean_phone_number(self, phone_text):
        """Clean and standardize phone number"""
        digits = re.sub(r'\D', '', phone_text)
        
        # Standardize to 10 digits
        if len(digits) == 10:
            return digits
        elif len(digits) == 11:
            return digits[1:]  # Remove country code
        elif len(digits) == 12:
            return digits[2:]  # Remove country code
        
        return None

    def _go_to_next_page(self):
        """Navigate to next page of results"""
        try:
            next_button = self.driver.find_element(By.ID, "pnnext")
            next_button_url = next_button.get_attribute("href")

            if next_button_url:
                print(f"\n→ Moving to next page...")
                self.driver.get(next_button_url)
                return True
            
            return False

        except NoSuchElementException:
            logging.info("No more pages to scrape")
            return False
        except Exception as e:
            logging.error(f"Error navigating to next page: {e}")
            print(f"\n✗ Error navigating to next page: {e}")
            return False# google_scraper.py




