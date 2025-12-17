#!/usr/bin/env python3
"""
email_config.py - Email configuration for Z-Cloud OTP system

Update the email credentials here to enable actual email sending.
For Gmail, you need to:
1. Enable 2-Factor Authentication on your Google Account
2. Generate an "App Password" (not your regular password)
3. Use the App Password below
"""

# Gmail account for sending OTP codes
SENDER_EMAIL = 'akwifonguhjoy@gmail.com'

# Gmail App Password (generate from: https://myaccount.google.com/apppasswords)
# Keep this secure! In production, use environment variables instead.
import os
SENDER_PASSWORD = os.getenv('EMAIL_PASSWORD', 'wxnjrjiichlqzswh')  # Get from environment variable, fallback to app password

# Fallback: If you prefer to set directly (not recommended for production):
if not SENDER_PASSWORD:
    SENDER_PASSWORD = ''  # Can be set here as backup

# SMTP Configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

# Email settings
EMAIL_ENABLED = bool(SENDER_PASSWORD)  # Only enabled if password is set
MAX_RETRIES = 3
TIMEOUT = 10  # seconds
