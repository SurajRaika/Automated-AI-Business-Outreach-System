# config.py
"""Configuration settings for the scraper"""

# WebDriver Configuration
EDGE_DRIVER_PATH = "/home/suraj/.local/bin/msedgedriver"
EDGE_BINARY_PATH = "/usr/bin/microsoft-edge-stable"
GEMINI_API_KEY=""
# Logging Configuration
LOG_FILE = 'scraping.log'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# Timeouts (in seconds)
PAGE_LOAD_TIMEOUT = 15
ELEMENT_WAIT_TIMEOUT = 10
CONTACT_PAGE_TIMEOUT = 8
REQUEST_TIMEOUT = 5

# Excel Configuration
EXCEL_DIRECTORY = 'excel_files'
EXCEL_HEADERS = [
    "Company Name", "Website", "Email", "Phone", 
    "Rating Ratio", "Number of Ratings", "Social Media", "City",
    "Sent Status", "Sent Date" # <--- NEW COLUMNS
]
TABLE_STYLE = 'TableStyleMedium9'

# Scraping Configuration
MAX_CONTACT_LINKS_TO_CHECK = 3
MIN_EMAIL_COUNT_FOR_EARLY_EXIT = 2
MAX_EMAIL_LENGTH = 100

# Invalid email patterns
INVALID_EMAIL_DOMAINS = [
    'example.com', 'test.com', 'domain.com', 'email.com',
    'yourdomain.com', 'yourcompany.com', 'company.com',
    'sample.com', 'demo.com', 'placeholder.com', 'your-email.com',
    'tempmail.com', 'mailinator.com', 'sentry.io', 'wixpress.com'
]

INVALID_EMAIL_PREFIXES = [
    'noreply', 'no-reply', 'donotreply', 'do-not-reply',
    'mailer-daemon', 'postmaster', 'webmaster@example'
]

INVALID_EMAIL_EXTENSIONS = ['.png', '.jpg', '.gif', '.css', '.js']

# Social media domains
SOCIAL_MEDIA_DOMAINS = [
    "facebook.com", "twitter.com", "instagram.com", "linkedin.com",
    "snapchat.com", "tiktok.com", "x.com", "youtube.com", "pinterest.com"
]

# XPath patterns for contact pages
CONTACT_PAGE_PATTERNS = [
    "//a[contains(translate(text(), 'CONTACT', 'contact'), 'contact')]",
    "//a[contains(translate(@href, 'CONTACT', 'contact'), 'contact')]",
    "//a[contains(translate(text(), 'ABOUT', 'about'), 'about')]",
    "//a[contains(translate(@href, 'ABOUT', 'about'), 'about')]",
    "//a[contains(translate(@href, 'CONTACT', 'contact'), 'contact-us')]",
    "//a[contains(translate(@href, 'TEAM', 'team'), 'team')]"
]

# Google search configuration
GOOGLE_SEARCH_BASE_URL = "https://www.google.com/search?sca_esv=6704a90ecd962571&sca_upv=1&tbs=lf:1,lf_ui:2&tbm=lcl&q="

# City delimiter for multi-city input
CITY_DELIMITER = ","