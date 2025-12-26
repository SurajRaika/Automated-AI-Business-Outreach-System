"""Website email extraction processor"""

import logging
from validators import is_valid_url
from email_extractor import EmailExtractor
from validateEmail import FinalEmail
# NOTE: EmailExtractor is assumed to exist and work.
# NOTE: validators.is_valid_url is assumed to exist.
# NOTE: excel_manager and outreach_manager are available in context.

# NEW IMPORT:
from outreach_manager import OutreachManager
import time
import random

class WebsiteProcessor:
    """Processes websites to extract email addresses and manage outreach"""
    
    def __init__(self, driver, excel_manager):
        self.driver = driver
        self.excel_manager = excel_manager
        # Assuming EmailExtractor is available and needs the driver
        # self.email_extractor = EmailExtractor(driver) 
        # Mocking for environment independence:
        try:
             self.email_extractor = EmailExtractor(driver)
        except NameError:
             # Placeholder if EmailExtractor is not defined in the execution environment
             logging.warning("EmailExtractor not found; using a mock object.")
             class MockEmailExtractor:
                 def get_emails_from_website(self, website): return []
             self.email_extractor = MockEmailExtractor()
             
        # NEW: Initialize OutreachManager
        # NOTE: The driver argument is usually ignored by OutreachManager's current __init__
        self.outreach_manager = OutreachManager(driver) 
    
    def process_all_websites(self, city=None, delete_without_email=True):
        print(f"\n{'='*60}")
        print("Starting Website Email Extraction and Outreach")
        if city:
            print(f"Processing city: {city}")
        print(f"{'='*60}\n")

        companies = self.excel_manager.get_companies_without_emails(city)
        total_companies = len(companies)

        if total_companies == 0:
            print("✗ No companies found that need email extraction.")
            return {
                'updated': 0,
                'skipped': 0,
                'no_email': 0,
                'deleted': 0,
                'outreach_sent': 0
            }

        print(f"Found {total_companies} companies to process\n")

        stats = {
            'outreach_sent': 0,
            'updated': 0,
            'skipped': 0,
            'no_email': 0,
            'deleted': 0
        }

        for idx, company in enumerate(companies, 1):
            company_name = company['name']
            company_website = company['website']
            company_city = company['city']

            print(f"[{idx}/{total_companies}] Processing: {company_name} ({company_city})")

            # Validate website URL
            if not is_valid_url(company_website):
                print(f"  ✗ Invalid URL: '{company_website}' - Skipping")
                stats['skipped'] += 1
                continue

            # Check if already has email (should be redundant if using get_companies_without_emails, but safe check)
            if self.excel_manager.has_contact_info(company_website, company_city):
                print(f"  ⊙ Already has email - Skipping")
                stats['skipped'] += 1
                continue

            print(f"  → Visiting: {company_website}")
            email_list = self.email_extractor.get_emails_from_website(company_website)
            if email_list:
                print(f"  ✓ Found {len(email_list)} email(s): {', '.join(email_list[:3])}")
            main_email = FinalEmail(email_list)
                
            if main_email:
                print("main_email is :",main_email)

                # 1. Update Excel row with contact info (always do this if info found)
                update_result = self.excel_manager.update_row_with_details(
                    company_name,
                    company_website,
                    main_email,
                    None,   # phone placeholder
                    None,   # rating ratio
                    None,   # number of ratings
                    [],     # socials placeholder
                    company_city
                )

                if update_result:
                    stats['updated'] += 1
                    print(f"  ✓ Updated in Excel")
                
                # 2. Check if outreach is needed
                if self.excel_manager._email_already_sent(main_email):
                    print(f"  ⊙ Outreach skipped: Email {main_email} already marked as sent.")
                    stats['skipped'] += 1
                else:
                    # 3. Attempt Outreach (FIXED ARG ORDER: name, email, city)
                    if self.outreach_manager.process_outreach(company_name, main_email, company_city):
                        print(f"  ✓ Outreach sent to {main_email}")
                        stats['outreach_sent'] += 1
                        # 4. Flag as sent in Excel after successful sending
                        self.excel_manager.flag_company_as_sent(company_website, main_email, True)
                    else:
                        print(f"  ✗ Outreach FAILED for {main_email}")
                        stats['skipped'] += 1 # Count failed attempt as skipped for summary
            else:
                print(f"  ⊙ No email found")
                stats['no_email'] += 1
                
                if delete_without_email:
                    if self.excel_manager.delete_row_without_email(company_website, company_city):
                        print(f"  ✗ Deleted from Excel (no email)")
                        stats['deleted'] += 1

            delay = random.uniform(0, 10)  # random float between 0 and 180 seconds
            print(f"Delaying for {delay:.2f} seconds...")
            time.sleep(delay)

        self._print_summary(stats, total_companies)
        return stats


    def process_all_websites_for_custom_email(self, city=None):
        """Processes companies with existing emails for outreach, skipping those already sent."""
        print(f"\n{'='*60}")
        print("Starting Website Email Outreach Tool (No Scraping)")
        if city:
            print(f"Processing city: {city}")
        print(f"{'='*60}\n")

        # Get companies that already have an email stored
        companies = self.excel_manager.get_companies_with_emails(city)
        total_companies = len(companies)

        if total_companies == 0:
            print("✗ No companies found with existing emails.")
            return {'outreach_sent': 0, 'skipped': 0}

        print(f"Found {total_companies} companies for outreach\n")

        stats = {'outreach_sent': 0, 'skipped': 0}

        for idx, company in enumerate(companies, 1):
            company_name = company['name']
            company_website = company['website']
            company_city = company['city']
            email = company.get('email')

            print(f"[{idx}/{total_companies}] Processing: {company_name} ({company_city})")

            # Validate website URL
            if not is_valid_url(company_website):
                print(f"  ✗ Invalid URL: '{company_website}' - Skipping")
                stats['skipped'] += 1
                continue

            # Validate email
            if not email or email == "None":
                print("  ✗ No valid email - Skipping")
                stats['skipped'] += 1
                continue

            # NEW: Check if email has already been sent to this address (using Excel tracking)
            if self.excel_manager._email_already_sent(email):
                print(f"  ⊙ Outreach skipped: Email {email} already marked as sent.")
                stats['skipped'] += 1
                continue

            # Outreach for every valid, unsent entry
            print(f"  → Starting outreach to {company_website}")
            
            # FIXED ARG ORDER: (company_name, target_email, city)
            if self.outreach_manager.process_outreach(company_name, email, company_city):
                print(f"  ✓ Outreach sent to {email}")
                stats['outreach_sent'] += 1
                # NEW: Flag as sent in Excel after successful sending
                self.excel_manager.flag_company_as_sent(company_website, email, True)
            else:
                print(f"  ✗ Outreach FAILED for {email}")
                stats['skipped'] += 1

            print()

        # Final summary
        print(f"\n{'='*60}")
        print("Outreach Completed")
        print(f"Sent: {stats['outreach_sent']}")
        print(f"Skipped: {stats['skipped']}")
        print(f"{'='*60}")

        return stats



    def _print_summary(self, stats, total_companies):
        print(f"\n{'='*60}")
        print("Website Email Extraction Complete")
        print(f"{'='*60}")
        print(f"✓ Successfully updated: {stats['updated']}")
        print(f"✓ Outreach Sent: {stats['outreach_sent']}") # Added sent count to summary
        print(f"⊙ Skipped: {stats['skipped']}")
        print(f"✗ No email found: {stats['no_email']}")
        
        if stats['deleted'] > 0:
            print(f"🗑  Deleted (no email): {stats['deleted']}")
        
        print(f"Total processed: {total_companies}")
        print(f"{'='*60}\n")




if __name__ == "__main__":
    import sys
    # Import your actual DriverManager
    try:
        from driver_manager import DriverManager
    except ImportError:
        # Fallback if file structure is different during testing
        class DriverManager:
            def initialize_driver(self): return True
            def get_driver(self): 
                from selenium import webdriver
                return webdriver.Edge() # Simple fallback
            def close_driver(self): pass
    # --- MOCK EXCEL MANAGER ---
    # Used to provide test data without needing a physical .xlsx file
    class MockExcelManager:
        def get_companies_without_emails(self, city):
            return [
                {'name': 'Test Company A', 'website': 'https://ecybertech.com/', 'city': 'San Francisco'},
                # {'name': 'Test Company B', 'website': 'https://google.com', 'city': 'New York'}
            ]
        def has_contact_info(self, url, city): return False
        def update_row_with_details(self, *args, **kwargs): return True
        def _email_already_sent(self, email): return False
        def flag_company_as_sent(self, *args): pass
        def delete_row_without_email(self, *args): return True

    # 1. Initialize the Driver Manager
    driver_mgr = DriverManager()
    if not driver_mgr.initialize_driver():
        print("\n✗ Failed to initialize driver. Exiting.")
        sys.exit(1)
    
    driver = driver_mgr.get_driver()

    try:
        # 2. Setup the Processor
        excel_mock = MockExcelManager()
        processor = WebsiteProcessor(driver, excel_mock)

        # 3. SAFETY OVERRIDE: Disable actual email sending
        # This replaces the outreach method with a simple print statement
        def dummy_outreach(name, email, city):
            print(f"  [SIMULATION] Would have sent email to: {email}")
            return True
        
        processor.outreach_manager.process_outreach = dummy_outreach

        # 4. Run the Test
        print("\n--- Starting Test Run (Simulation Mode) ---")
        processor.process_all_websites(city="TestCity", delete_without_email=False)

    except Exception as e:
        print(f"An error occurred during execution: {e}")

    finally:
        # 5. Safe Cleanup using your DriverManager
        driver_mgr.close_driver()