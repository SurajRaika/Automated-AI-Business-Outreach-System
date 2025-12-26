import os
import time
import json
import re
import base64
import sys
from pathlib import Path
from openpyxl import Workbook
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Configuration & Paths ---
EDGE_DRIVER_PATH = "/home/suraj/.local/bin/msedgedriver"
EDGE_BINARY_PATH = "/usr/bin/microsoft-edge-stable"
INPUT_FILE = "companies.txt"
EXCEL_DIR = "excel_files"

os.makedirs(EXCEL_DIR, exist_ok=True)

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return re.sub(r'^-|-$', '', text)

def create_filename(business_name, cities):
    """Matches your specific metadata naming convention"""
    slug = slugify(business_name)
    meta = {"business": business_name, "cities": cities}
    meta_json = json.dumps(meta)
    meta_b64 = base64.urlsafe_b64encode(meta_json.encode()).decode()
    filename = f"{slug}__meta={meta_b64}.xlsx"
    return os.path.join(EXCEL_DIR, filename)

def setup_driver():
    options = Options()
    options.binary_location = EDGE_BINARY_PATH
    # Removed headless to see the browser
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0")
    service = Service(executable_path=EDGE_DRIVER_PATH)
    return webdriver.Edge(service=service, options=options)

def check_captcha_page(driver):
    """Check if current page is Google's sorry/captcha page"""
    current_url = driver.current_url
    return "google.com/sorry" in current_url

def handle_captcha_pause(driver, company_name):
    """Pause and wait for user to solve captcha"""
    print(f"\n⚠️  CAPTCHA DETECTED on Google!")
    print(f"Current URL: {driver.current_url}")
    print(f"\n📋 Please solve the CAPTCHA manually in the browser window...")
    input("✅ Press ENTER once you've solved the CAPTCHA and want to continue: ")
    print(f"Resuming scraping for: {company_name}\n")

def get_official_website_js(driver, company_name):
    """Uses JavaScript to find website link - most reliable method"""
    try:
        search_url = f"https://www.google.com/search?q={company_name}"
        driver.get(search_url)
        time.sleep(2)  # Wait for page to fully load
        
        # Execute the JavaScript to find website
        website_url = driver.execute_script("""
            const websiteUrl = [...document.querySelectorAll('a')]
                .find(a => a.innerText.trim() === 'Website' && a.href.includes('http'))
                ?.href;
            return websiteUrl || null;
        """)
        
        # If website not found, check for captcha
        if not website_url:
            if check_captcha_page(driver):
                handle_captcha_pause(driver, company_name)
                # Try again after captcha is solved
                driver.get(search_url)
                time.sleep(2)
                website_url = driver.execute_script("""
                    const websiteUrl = [...document.querySelectorAll('a')]
                        .find(a => a.innerText.trim() === 'Website' && a.href.includes('http'))
                        ?.href;
                    return websiteUrl || null;
                """)
        
        return website_url if website_url else "Not Found"
    except Exception as e:
        print(f" [Error: {str(e)}]", end="")
        return "Error"

def get_official_website_python(driver, company_name):
    """Python equivalent as fallback"""
    try:
        search_url = f"https://www.google.com/search?q={company_name}"
        driver.get(search_url)
        wait = WebDriverWait(driver, 7)
        
        # Wait for all links to load
        wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
        
        # Find all anchor tags
        links = driver.find_elements(By.TAG_NAME, "a")
        
        for link in links:
            try:
                text = link.get_attribute("innerText")
                href = link.get_attribute("href")
                if text and href and "http" in href:
                    if text.strip() == "Website":
                        return href
            except:
                continue
        
        return "Not Found"
    except Exception as e:
        print(f" [Error: {str(e)}]", end="")
        return "Error"

def save_to_excel(data, business_name, cities):
    """Saves data using openpyxl directly"""
    filepath = create_filename(business_name, cities)
    wb = Workbook()
    ws = wb.active
    ws.title = "Company Results"
    
    # Header
    ws.append(["Company Name", "Official Website"])
    
    # Rows
    for company, link in data:
        ws.append([company, link])
    
    wb.save(filepath)
    return filepath

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py 'Search Category'")
        return
    
    user_input = sys.argv[1]
    business_label = f"job_Search_{user_input}"
    city_label = ["remote"]
    
    # Read companies from file
    if not os.path.exists(INPUT_FILE):
        print(f"File {INPUT_FILE} not found.")
        return
    
    with open(INPUT_FILE, "r") as f:
        companies = [line.strip() for line in f if line.strip()]
    
    driver = setup_driver()
    results = []
    
    try:
        print(f"Scraping {len(companies)} companies...\n")
        for name in companies:
            print(f"-> {name}", end=" ", flush=True)
            # Use JavaScript method (most reliable)
            link = get_official_website_js(driver, name)
            results.append((name, link))
            print(f"[{link}]")
            time.sleep(1.5)  # Anti-ban delay
        
        # Save to Excel
        output_path = save_to_excel(results, business_label, city_label)
        print(f"\nSuccessfully saved to: {output_path}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()