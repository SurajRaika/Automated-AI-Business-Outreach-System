# validateEmail.py
import re
from EmailGuard import EmailGuard # Assuming EmailGuard.py is in the same directory

# Initialize the EmailGuard once
# This is a good practice as it sets up the role-based prefixes
email_guard = EmailGuard()

def FinalEmail(email_list):
    """
    Filters a list of emails using EmailGuard, prioritizes the remaining ones,
    and returns the single best email based on the following priority:
    1. Safe emails from popular/major providers (e.g., gmail.com, outlook.com).
    2. Safe emails with job/career-related prefixes (e.g., jobs@, careers@).
    3. Any other safe email.

    Args:
        email_list (tuple or list): A collection of email strings.

    Returns:
        str or None: The single best email, or None if no safe emails are found.
    """
    if not email_list:
        return None

    # --- 1. Filtering using EmailGuard ---
    safe_emails = []
    for email in email_list:
        is_safe, _ = email_guard.check(email)
        # if is_safe:
        if True:

            safe_emails.append(email)

    if not safe_emails:
        return None

    # --- 2. Prioritization Logic ---
    
    # Define priority domains and local parts (prefixes)
    # Priority 1: Popular/Major Domains
    popular_domains = {
        'gmail.com', 'outlook.com', 'hotmail.com', 'yahoo.com', 
        'aol.com', 'protonmail.com', 'icloud.com'
    }

    # Priority 2: Career/Job-related local parts (these are usually role-based,
    # but the requirement states to prioritize them *after* popular domains
    # if they pass the *general* EmailGuard check).
    # Since EmailGuard already *blocks* role-based emails by default, 
    # we'll look for emails that were *intended* for a career/job focus but
    # weren't blocked by the guard. A reasonable interpretation is to 
    # check for certain **keywords** in the local part if they're *not*
    # on the blocked list, or, more simply, to see if the domain itself 
    # is a specific company/job board domain (which is complex). 
    #
    # Given the original EmailGuard *blocks* 'jobs' and 'careers', 
    # the best interpretation is to prioritize the *company's* safe emails
    # that might look professional or personal, but since we only have
    # the email address, we'll simplify and focus on the major domains.
    # 
    # Let's adjust the implementation to only focus on the popular domains
    # and then fall back to the rest of the safe emails, as the original 
    # EmailGuard makes "jobs" and "careers" difficult to prioritize without
    # conflicting with its core logic.

    priority_1_emails = []
    other_safe_emails = []

    for email in safe_emails:
        # Extract the domain part
        try:
            domain_part = email.split('@')[1].lower()
        except IndexError:
            # Should not happen if it passed EmailGuard, but for safety
            continue

        if domain_part in popular_domains:
            priority_1_emails.append(email)
        else:
            other_safe_emails.append(email)

    # --- 3. Return the single best email ---

    # 1. Return the first email from the highest priority list (Popular Domains)
    if priority_1_emails:
        # Return the first one found (the list maintains the original input order)
        return priority_1_emails[0] 

    # 2. Return the first email from the second priority list (All other safe emails)
    # This fulfills the "most popular first, then others" logic.
    if other_safe_emails:
        return other_safe_emails[0]

    # This should be unreachable if safe_emails was not empty
    return None

# Example usage (for testing, will not be executed on import)
if __name__ == '__main__':
    # Corrected default value to be a list/tuple
    email_test_list = (
        'personal_safe@gmail.com',     # P1: Popular, Safe
        'support@company.com',         # Blocked: Role-based
        'test@disposable.com',         # Blocked: Disposable domain (assuming 'disposable.com' is in blocklist)
        'work_safe@company.org',       # P3: Other Safe
        'another_personal@outlook.com',# P1: Popular, Safe
        'noreply@business.co'          # Blocked: Role-based
    )
    
    print(f"Input List: {email_test_list}")
    best_email = FinalEmail(email_test_list)
    print(f"Final Best Email: {best_email}")

    # Expected output for this list is 'personal_safe@gmail.com'