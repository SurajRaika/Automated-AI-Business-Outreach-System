# driver_manager.py
"""WebDriver management and initialization"""

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import WebDriverException
import logging
from config import EDGE_DRIVER_PATH, EDGE_BINARY_PATH, PAGE_LOAD_TIMEOUT


class DriverManager:
    """Manages WebDriver initialization and lifecycle"""
    
    def __init__(self):
        self.driver = None
    
    def initialize_driver(self):
        """Initialize the Edge WebDriver with proper configuration"""
        try:
            service = Service(EDGE_DRIVER_PATH)
            options = Options()
            options.binary_location = EDGE_BINARY_PATH
            # options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-gpu')
            # --user-agent line removed to match GlobalScrapper.py behavior
            # options.add_argument("--start-maximized")
            # options.add_argument("--disable-blink-features=AutomationControlled")
            # options.add_argument("--disable-gpu")

            self.driver = webdriver.Edge(service=service, options=options)
            self.driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
            logging.info("WebDriver initialized successfully")
            print("✓ Web driver initialized successfully")
            return True

        except WebDriverException as e:
            logging.error(f"WebDriver initialization failed: {e}")
            print(f"✗ Error initializing the web driver: {e}")
            return False
    
    def is_browser_alive(self):
        """Check if browser is still running"""
        try:
            if self.driver:
                self.driver.title
                return True
        except WebDriverException:
            return False
        return False
    
    def close_driver(self):
        """Close the WebDriver safely"""
        if self.driver:
            try:
                self.driver.quit()
                logging.info("Browser closed successfully")
                print("✓ Browser closed successfully")
            except Exception as e:
                logging.warning(f"Error closing browser: {e}")
    
    def get_driver(self):
        """Get the WebDriver instance"""
        return self.driver