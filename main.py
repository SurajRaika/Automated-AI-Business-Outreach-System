"""Main entry point for the business scraper application"""

import sys
import logging
import os # Added for path manipulation and directory creation
from config import LOG_FILE, LOG_FORMAT
from driver_manager import DriverManager
from excel_manager import ExcelManager
from google_scraper import GoogleScraper
from website_processor import WebsiteProcessor
from session_manager import SessionManager
import os




def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format=LOG_FORMAT
    )


def print_banner():
    """Print application banner"""
    print("\n" + "="*60)
    print("Google Business Scraper - Multi-City Email Extractor")
    print("="*60 + "\n")


def get_user_input():
    """Get business name and cities from user"""
    # SessionManager is assumed to exist
    try:
        session_mgr = SessionManager()
    except NameError:
        # Simple mock if SessionManager is not defined
        class MockSessionManager:
            def select_session(self): return None
            def confirm_resume(self, session): return False
            def parse_cities_input(self, cities_input): return [c.strip() for c in cities_input.split(',')]
            def create_filename(self, business_name, cities): return f"excel_files/scraped_data/{business_name.replace(' ', '_')}.xlsx"
            def save_session(self, b, c, f): pass
        session_mgr = MockSessionManager()


    # Check for existing sessions
    existing_session = session_mgr.select_session()
    
    if existing_session:
        if session_mgr.confirm_resume(existing_session):
            return {
                'business_name': existing_session['business_name'],
                'cities': existing_session['cities'],
                'filename': existing_session['filename'],  # Use filename, not filepath
                'is_resume': True
            }
    
    # Get new input
    print("="*60)
    print("New Scraping Session")
    print("="*60 + "\n")
    
    business_name = input("Enter Business type (e.g., 'dental clinic'): ").strip()
    if not business_name:
        print("\n✗ Error: Business type is required!")
        sys.exit(1)
    
    cities_input = input("Enter cities separated by comma (e.g., 'new york, los angeles, chicago'): ").strip()
    if not cities_input:
        print("\n✗ Error: At least one city is required!")
        sys.exit(1)
    
    cities = session_mgr.parse_cities_input(cities_input)
    
    if not cities:
        print("\n✗ Error: No valid cities provided!")
        sys.exit(1)
    
    print(f"\n✓ Will scrape '{business_name}' in {len(cities)} cities:")
    for city in cities:
        print(f"  • {city}")
    
    filename = session_mgr.create_filename(business_name, cities)
    
    return {
        'business_name': business_name,
        'cities': cities,
        'filename': filename,
        'is_resume': False
    }


def get_process_option():
    """Get user's choice for processing option"""
    print("\n" + "="*60)
    print("Processing Options:")
    print("="*60)
    print("  1 - Google search only")
    print("  2 - Email extraction only (from existing websites)")
    print("  3 - Full process (Google search + Email extraction)")
    print("  4 - Targeted Outreach (Send emails to companies with existing contacts that haven't been emailed yet)")
    print("="*60)
    
    while True:
        choice = input("\nSelect option (1-4): ").strip()
        if choice in ['1', '2', '3', '4']:
            return choice
        print("✗ Invalid option. Please enter 1, 2, 3, or 4.")


def run_google_search(driver_mgr, user_input):
    """Run Google search for all cities"""
    # ExcelManager and GoogleScraper are assumed to exist
    excel_mgr = ExcelManager(user_input['filename'])
    google_scraper = GoogleScraper(driver_mgr.get_driver(), excel_mgr)
    
    total_scraped = 0
    
    for city in user_input['cities']:
        print(f"\n{'*'*60}")
        print(f"Processing city: {city}")
        print(f"{'*'*60}")
        
        scraped = google_scraper.scrape_businesses(
            user_input['business_name'],
            city
        )
        total_scraped += scraped
    
    print(f"\n{'='*60}")
    print("Google Search Complete - All Cities")
    print(f"{'='*60}")
    print(f"Total businesses scraped: {total_scraped}")
    print(f"Cities processed: {len(user_input['cities'])}")
    print(f"{'='*60}\n")
    
    excel_mgr.close()
    return total_scraped


def run_email_extraction(driver_mgr, user_input, delete_without_email=True):
    """Run email extraction and outreach for all cities"""
    excel_mgr = ExcelManager(user_input['filename'])
    website_processor = WebsiteProcessor(driver_mgr.get_driver(), excel_mgr)
    
    # Initialize all expected keys from website_processor.process_all_websites
    total_stats = {
        'updated': 0,
        'skipped': 0,
        'no_email': 0,
        'deleted': 0,
        'outreach_sent': 0 
    }
    
    for city in user_input['cities']:
        print(f"\n{'*'*60}")
        print(f"Processing city: {city}")
        print(f"{'*'*60}")
        
        # stats should contain all keys initialized above
        stats = website_processor.process_all_websites(city, delete_without_email)
        
        # Accumulate stats
        for key in total_stats:
            total_stats[key] += stats.get(key, 0)
    
    print(f"\n{'='*60}")
    print("Email Extraction and Outreach Complete - All Cities") 
    print(f"{'='*60}")
    print(f"✓ Total updated (Emails found): {total_stats['updated']}") 
    print(f"✓ Total Outreach Sent: {total_stats['outreach_sent']}")
    print(f"⊙ Total skipped: {total_stats['skipped']}")
    print(f"✗ Total no email: {total_stats['no_email']}")
    
    if total_stats['deleted'] > 0:
        print(f"🗑  Total deleted: {total_stats['deleted']}")
    
    print(f"Cities processed: {len(user_input['cities'])}")
    print(f"{'='*60}\n")
    
    excel_mgr.close()
    return total_stats


def run_targeted_outreach(driver_mgr, user_input):
    """Runs outreach email generation and sending for companies with existing emails that have not yet been sent."""
    excel_mgr = ExcelManager(user_input['filename'])
    website_processor = WebsiteProcessor(driver_mgr.get_driver(), excel_mgr)
    
    # Initialize stats specific to the targeted outreach function
    total_stats = {
        'outreach_sent': 0,
        'skipped': 0,
    }
    
    for city in user_input['cities']:
        print(f"\n{'*'*60}")
        print(f"Processing city: {city}")
        print(f"{'*'*60}")
        
        # This returns {'outreach_sent': X, 'skipped': Y}
        stats = website_processor.process_all_websites_for_custom_email(city)
        
        # Accumulate stats
        total_stats['outreach_sent'] += stats.get('outreach_sent', 0)
        total_stats['skipped'] += stats.get('skipped', 0)
    
    print(f"\n{'='*60}")
    print("Targeted Outreach Complete - All Cities")
    print(f"{'='*60}")
    print(f"✓ Total Emails Sent: {total_stats['outreach_sent']}")
    print(f"⊙ Total Skipped (Already Sent/Invalid): {total_stats['skipped']}")
    print(f"Cities processed: {len(user_input['cities'])}")
    print(f"{'='*60}\n")
    
    excel_mgr.close()
    return total_stats

def main():
    """Main application entry point"""
    setup_logging()
    print_banner()
    
    # Get user input
    user_input = get_user_input()
    
    # --- FIX: Ensure Output Directory Exists ---
    # The error indicates the directory path must be created before file access.
    try:
        full_filepath = user_input['filename']
        # Extract the directory path from the full filename
        output_dir = os.path.dirname(full_filepath)
        
        if output_dir: # Only proceed if the path includes a directory structure
            os.makedirs(output_dir, exist_ok=True)
            print(f"✓ Ensured output directory exists: {output_dir}")
    except Exception as e:
        print(f"\n✗ Failed to create directory structure for output file: {e}")
        # Log the error and exit gracefully
        logging.error(f"Directory creation error: {e}", exc_info=True)
        sys.exit(1)
    # --------------------------------------------
    
    # Get processing option
    process_option = get_process_option()
    
    # Initialize driver
    # DriverManager is assumed to exist
    try:
        driver_mgr = DriverManager()
    except NameError:
        class MockDriverManager:
            def initialize_driver(self): return True
            def get_driver(self): return None
            def close_driver(self): pass
        driver_mgr = MockDriverManager()
        
    
    if not driver_mgr.initialize_driver():
        print("\n✗ Failed to initialize driver. Exiting.")
        sys.exit(1)
    
    try:
        # Save session
        # SessionManager is assumed to exist
        try:
            session_mgr = SessionManager()
        except NameError:
             class MockSessionManager:
                def save_session(self, b, c, f): pass
             session_mgr = MockSessionManager()
             
        session_mgr.save_session(
            user_input['business_name'],
            user_input['cities'],
            user_input['filename']
        )
        
        # Execute based on option
        if process_option == '1':
            print("\n→ Starting Google search for all cities...\n")
            run_google_search(driver_mgr, user_input)
        
        elif process_option == '2':
            print("\n→ Starting email extraction for all cities...\n")
            
            delete_choice = input("Delete companies without emails? (y/n): ").strip().lower()
            delete_without_email = (delete_choice == 'y')
            
            run_email_extraction(driver_mgr, user_input, delete_without_email)
        
        elif process_option == '3':
            print("\n→ Starting full process for all cities...\n")
            
            # Step 1: Google search
            run_google_search(driver_mgr, user_input)
            
            # Step 2: Email extraction
            print("\n→ Now extracting emails and running initial outreach...\n")
            
            # delete_choice = input("Delete companies without emails? (y/n): ").strip().lower()
            # delete_without_email = (delete_choice == 'y')
            delete_without_email = True

            
            run_email_extraction(driver_mgr, user_input, delete_without_email)
        
        # UPDATED OPTION 4 CALL
        elif process_option == '4':
            print("\n→ Starting Targeted Outreach...\n")
            run_targeted_outreach(driver_mgr, user_input)
        
        print("\n✓ All tasks completed successfully!")
        print(f"✓ Data saved to: {user_input['filename']}\n")
    
    except KeyboardInterrupt:
        print("\n\n✗ Interrupted by user. Cleaning up...")
    
    except Exception as e:
        print(f"\n✗ An error occurred: {e}")
        logging.error(f"Application error: {e}", exc_info=True)
    else:
        # ✅ This runs ONLY if no exception happened
        print("✔ Completed successfully. Shutting down system...")
        os.system("sudo shutdown now")
    finally:
        driver_mgr.close_driver()


if __name__ == "__main__":
    main()