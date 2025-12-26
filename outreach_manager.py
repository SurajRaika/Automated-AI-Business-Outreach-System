"""Handles generating and sending emails using City and Company Name only."""
import random

import logging
import os
import subprocess
import re

# Import the new standalone function
from gemini_generator import generate_personalized_html 


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$")

# Config
# TEMPLATE_FILE is now defined in gemini_generator.py

class OutreachManager:
    """Handles generating and sending emails using City and Company Name only."""

    def __init__(self,something=None):
        logging.info("Initialized OutreachManager (Lightweight Mode).")

    # The _generate_personalized_html method has been removed from this class.

    def _create_html_email_file(self, city, company_name, target_email):
        """
        Generates a personalized HTML email by calling the generation helper, 
        and then saves the content to a file.
        """
        
        # --- 1. Get HTML Content by calling the external function ---
        html_content = generate_personalized_html(city, company_name)
        
        if html_content is None:
            return None # Generation failed, message already printed

        # --- 2. Save File ---
        try:
            output_dir = "generated_email"
            os.makedirs(output_dir, exist_ok=True)

            # Sanitize filename
            safe_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '_')).rstrip()
            file_name = f"outreach_{safe_name}_{target_email.split('@')[0]}.html"
            file_path = os.path.join(output_dir, file_name)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            logging.info(f"Generated email HTML: {file_path}")
            print(f"    ✓ HTML generated: {file_path}")
            return file_path

        except Exception as e:
            logging.error(f"File write error: {e}")
            print("    ❌ Could not save HTML file")
            return None

    def _send_email_cli(self, target_email, html_file):
        """Sends the email via send_email.py CLI."""
        if not html_file or not os.path.isfile(html_file):
            print("    ✗ Email not sent (HTML file missing).")
            return False

        try:
            # subject = [
            #     "Full-Stack Developer",
            #     "Developer",
            #     "Developer — Application",
            #     "Developer Position",
            #     "Developer Opportunity",
            #     "Software Developer",
            #     "Job Inquiry",
            #     "Application",
            #     "Developer — Available",
            #     "Open to Developer Role",
            # ]
            subject = [
                "Quick intro...",
                "Just introducing myself...",
                "Sharing a quick intro...",
                "A quick note...",
                "Just a short intro...",
                "Quick hello...",
                "Reaching out...",
                "Intro...",
                "A quick message...",
                "Just saying hi...",
            ]

            # Run local CLI sender
            result = subprocess.run(
                ["python3", "send_email.py", target_email, random.choice(subject), html_file],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print(f"    ✓ Email sent to {target_email}")
                logging.info(f"Email sent to {target_email}")
                return True
            else:
                print(f"    ✗ Email failed for {target_email}")
                logging.error(f"CLI Stderr: {result.stderr}")
                return False

        except Exception as e:
            logging.error(f"Error calling send_email.py: {e}")
            return False

    def process_outreach(self, company_name, target_email, city):
        """Orchestrates the outreach."""
        print(f"  → Email Sending: {company_name} in {city} , {target_email}...")

        # 1. Create HTML (Now calls the imported function)
        html_file = self._create_html_email_file(city, company_name, target_email)

        # 2. Send Email (CLI)
        if html_file:
            sent = self._send_email_cli(target_email, html_file)

            # 3. Log if successful
            if sent:
                print(f"    ✅ Email sent and logged: {target_email}")
                return True

        print(f"    ❌ Email NOT sent: {target_email}")
        return False


if __name__ == "__main__":
    # === TEST RUNNER ===
    # Ensure you have run: export GEMINI_API_KEY="your_key_here"
    
    print("\n=== OutreachManager Lightweight Test ===\n")

    outreach = OutreachManager()

    # Test Data
    test_company_name = "Ventive Software"
    test_city = "Boise Idaho"
    test_email = "suajraika5sr@gmail.com" 

    success = outreach.process_outreach(
        company_name=test_company_name,
        city=test_city,
        target_email=test_email,
    )
    print(f"\nResult of process_outreach: {'SUCCESS' if success else 'FAILURE'}")