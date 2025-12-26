#!/usr/bin/env python3
import sys
import argparse
import logging

# Try to import required libraries with friendly error messages
try:
    from email_validator import validate_email, EmailNotValidError
    from disposable_email_domains import blocklist
except ImportError as e:
    sys.stderr.write(f"Error: Missing dependency. Please run: pip install email-validator disposable-email-domains\n")
    sys.exit(1)

class EmailGuard:
    def __init__(self):
        # Role-based emails that are technically valid but bad for outreach/marketing
        self.role_based_prefixes = {
            "admin", "support", "info", "contact", "sales", "marketing", 
            "help", "office", "billing", "abuse", "noreply", "no-reply", 
            "webmaster", "jobs", "careers"
        }

    def check(self, email):
        """
        Validates the email and returns a tuple: (is_safe: bool, reason: str)
        """
        try:
            # 1. SYNTAX & DNS DELIVERABILITY CHECK
            # check_deliverability=True performs a DNS lookup to ensure the domain accepts email.
            valid = validate_email(email, check_deliverability=True)
            
            # Use normalized version (e.g., proper casing)
            email_normalized = valid.normalized
            domain = valid.domain
            local_part = valid.local_part
            
        except EmailNotValidError as e:
            return False, f"Invalid Syntax/DNS: {str(e)}"

        # 2. DISPOSABLE EMAIL CHECK
        if domain in blocklist:
            return False, "High Risk: Disposable/Burner Domain"

        # 3. ROLE-BASED CHECK
        if local_part.lower() in self.role_based_prefixes:
            return False, f"Low Quality: Role-based address ({local_part}@)"

        return True, "Safe: Passed all checks"

def main():
    # Setup CLI Arguments
    parser = argparse.ArgumentParser(
        description="Check if an email is safe for Gmail outreach. Returns True or False."
    )
    parser.add_argument("email", type=str, help="The email address to validate")
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Print the reason for the result (e.g., 'False: Disposable Domain')"
    )
    
    args = parser.parse_args()

    # Initialize Guard
    guard = EmailGuard()
    
    # Run Check
    is_safe, reason = guard.check(args.email)

    # Output Logic
    if args.verbose:
        # If verbose, print the boolean AND the reason
        print(f"{is_safe} | {reason}")
    else:
        # Standard mode: Just print True or False
        print(is_safe)

    # System Exit Codes for Shell Scripting compatibility
    # Exit 0 if Safe, Exit 1 if Unsafe
    sys.exit(0 if is_safe else 1)

if __name__ == "__main__":
    main()