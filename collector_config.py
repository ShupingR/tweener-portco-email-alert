"""
Configuration for Daily Email Collector
======================================

This file contains configuration settings for the daily email collection system.
Modify these settings as needed for your environment.
"""

# Email Collection Settings
DEFAULT_DAYS_BACK = 7  # Default number of days to look back for emails
MAX_DAYS_BACK = 365    # Maximum allowed days back

# Forwarders to monitor (these are the people who forward portfolio company emails)
EMAIL_FORWARDERS = [
    "scot@tweenerfund.com",
    "scot@refibuy.ai", 
    "nikita@tweenerfund.com",
    "shuping@tweenerfund.com",
    "shuping.ruan@gmail.com"
]

# Claude Analysis Settings
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_MAX_TOKENS = 1000
CLAUDE_CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence to save an email update

# Database Settings
DATABASE_URL = "sqlite:///tracker.db"  # Can be overridden by environment variable

# File Storage Settings
ATTACHMENTS_DIR = "attachments"
MAX_ATTACHMENT_SIZE_MB = 50  # Maximum size for individual attachments

# Email Content Limits
MAX_EMAIL_BODY_LENGTH = 10000  # Characters to store in database
MAX_SUBJECT_LENGTH = 500       # Characters for email subject

# Logging and Output Settings
SHOW_RECENT_UPDATES_COUNT = 5  # Number of recent updates to show after collection
DRY_RUN_PREVIEW_COUNT = 5      # Number of emails to preview in dry-run mode

# Performance Settings
EMAIL_PROCESSING_BATCH_SIZE = 50  # Process emails in batches
CONNECTION_TIMEOUT_SECONDS = 30   # IMAP/SMTP connection timeout

# Company Classification
# These settings control how companies are classified as portfolio vs non-portfolio
AUTO_CREATE_NON_PORTFOLIO = True  # Automatically create records for non-portfolio companies
PORTFOLIO_COMPANY_DEFAULT = True   # Default value for is_tweener_portfolio when creating companies

# File Organization
USE_COMPANY_SPECIFIC_DIRS = True   # Create separate directories for each company's attachments
USE_TIMESTAMPED_FILENAMES = True   # Add timestamps to attachment filenames to prevent conflicts

# Error Handling
CONTINUE_ON_EMAIL_ERROR = True     # Continue processing other emails if one fails
MAX_RETRIES = 3                    # Maximum retries for failed operations
RETRY_DELAY_SECONDS = 5            # Delay between retries

# Debug and Development
DEBUG_MODE = False                 # Enable debug logging
SAVE_RAW_EMAIL_CONTENT = False     # Save raw email content for debugging (not recommended for production)

# Notification Settings (for future use)
NOTIFY_ON_NEW_COMPANIES = True     # Whether to log when new companies are discovered
NOTIFY_ON_ERRORS = True            # Whether to log errors prominently

# Data Retention (for future use)
KEEP_EMAIL_HISTORY_DAYS = 0        # 0 = keep forever, >0 = delete after N days
KEEP_ATTACHMENT_HISTORY_DAYS = 0   # 0 = keep forever, >0 = delete after N days 