#!/usr/bin/env python3
"""
setup_email_password.ps1 - PowerShell script to set EMAIL_PASSWORD and test

Run with: powershell -ExecutionPolicy Bypass -File setup_email_password.ps1
"""

# This is actually a Python script, but can show PowerShell commands
# Let me create the PowerShell version instead

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                   Z-Cloud Email Setup Helper                              ║
╚════════════════════════════════════════════════════════════════════════════╝

To enable OTP email sending, follow these steps:

1. GENERATE GMAIL APP PASSWORD
   ✓ Go to: https://myaccount.google.com/apppasswords
   ✓ Select App: "Mail"
   ✓ Select Device: "Windows Computer"
   ✓ Copy the 16-character password (remove spaces)
   ✓ Paste it in the prompt below

2. You'll be able to test the connection immediately

3. Then run Z-Cloud normally with:
   python start_web_api.py

════════════════════════════════════════════════════════════════════════════

Let's do this!
""")

import getpass
import os

password = getpass.getpass("Paste your Gmail App Password (without spaces): ").strip()

if not password or len(password) < 16:
    print("❌ Invalid password. Should be 16 characters without spaces.")
    exit(1)

print(f"\n✓ Password captured ({len(password)} characters)")

# Test the connection
print("\nTesting SMTP connection...")
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('akwifonguhjoy@gmail.com', password)
    print("✓ Authentication successful!")
    
    # Create test email
    msg = MIMEMultipart('alternative')
    msg['From'] = 'akwifonguhjoy@gmail.com'
    msg['To'] = 'akwifonguhjoy@gmail.com'
    msg['Subject'] = 'Z-Cloud Setup Test'
    msg.attach(MIMEText('<h2>Z-Cloud Setup Complete!</h2>', 'html'))
    
    print("Sending test email...")
    server.send_message(msg)
    print("✓ Test email sent!")
    
    server.quit()
    
    print("\n" + "="*60)
    print("SUCCESS! Email system is ready.")
    print("="*60)
    print("\nTo use this password with Z-Cloud:")
    print(f"\nPowerShell:")
    print(f'  $env:EMAIL_PASSWORD="{password}"')
    print(f'\n  Then run: python start_web_api.py')
    print("\nOr set it permanently in System Environment Variables")
    print("="*60)
    
except smtplib.SMTPAuthenticationError:
    print("❌ Authentication failed. Password may be incorrect.")
    exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
