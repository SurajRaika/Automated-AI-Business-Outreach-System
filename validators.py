# validators.py
"""Validation utilities for URLs and emails"""

import re
from config import (
    INVALID_EMAIL_DOMAINS, 
    INVALID_EMAIL_PREFIXES, 
    INVALID_EMAIL_EXTENSIONS,
    MAX_EMAIL_LENGTH
)


def is_valid_url(url):
    """Validate if URL is proper and not blank/data URL"""
    if not url or not isinstance(url, str):
        return False

    url = url.strip()

    # Check for invalid URLs
    invalid_patterns = ['data:', 'javascript:', 'about:blank', 'mailto:']
    if any(url.startswith(pattern) for pattern in invalid_patterns):
        return False

    # Check if URL has proper format
    if not url.startswith(('http://', 'https://')):
        return False

    # Check minimum length and domain existence
    if len(url) < 10 or '.' not in url:
        return False

    return True


def is_valid_email(email):
    """Validate if email address is legitimate"""
    if not email or '@' not in email or '.' not in email:
        return False
    
    email = email.lower().strip()
    
    # Basic email pattern
    email_pattern = r'^[A-Za-z0-9][\w\.-]*@[A-Za-z0-9][\w\.-]*\.[A-Za-z]{2,}$'
    if not re.match(email_pattern, email):
        return False
    
    # Filter invalid domains
    if any(invalid in email for invalid in INVALID_EMAIL_DOMAINS):
        return False
    
    # Filter invalid prefixes
    if any(email.startswith(prefix) for prefix in INVALID_EMAIL_PREFIXES):
        return False
    
    # Filter file extensions
    if any(ext in email for ext in INVALID_EMAIL_EXTENSIONS):
        return False
    
    # Filter suspiciously long emails
    if len(email) > MAX_EMAIL_LENGTH:
        return False
    
    # Filter emails with suspicious patterns
    if email.count('@') > 1 or email.count('..') > 0:
        return False
    
    return True


def filter_valid_emails(emails):
    """Filter a collection of emails and return only valid ones"""
    return [email for email in emails if is_valid_email(email)]


def extract_emails_from_text(text):
    """Extract email addresses from text using regex"""
    if not text:
        return []
    
    email_pattern = r'\b[A-Za-z0-9][\w\.-]*@[A-Za-z0-9][\w\.-]*\.[A-Za-z]{2,}\b'
    matches = re.findall(email_pattern, text, re.IGNORECASE)
    return [e.lower().strip() for e in matches]


def extract_obfuscated_emails(text):
    """Extract obfuscated emails like 'info [at] company [dot] com'"""
    if not text:
        return []
    
    obfuscated_pattern = r'\b[\w\.-]+\s*\[at\]\s*[\w\.-]+\s*\[dot\]\s*[a-z]{2,}\b'
    matches = re.findall(obfuscated_pattern, text, re.IGNORECASE)
    
    cleaned_emails = []
    for match in matches:
        cleaned = match.replace('[at]', '@').replace('[dot]', '.').replace(' ', '')
        cleaned_emails.append(cleaned.lower().strip())
    
    return cleaned_emails