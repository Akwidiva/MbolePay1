#!/usr/bin/env python3
"""
test_email_send.py - Test the email OTP sending functionality

Usage:
    python test_email_send.py                    # Send to default email
    python test_email_send.py recipient@example.com  # Send to specific email
"""

import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
EMAIL_CONFIG = {
    'sender_email': 'akwifonguhjoy@gmail.com',
    'sender_password': os.getenv('EMAIL_PASSWORD', 'saqcepdqrshkfkqo'),
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587
}

def test_email_send(recipient_email=None):
    """Test if email sending works"""
    
    print("=" * 60)
    print("Z-Cloud Email OTP Test")
    print("=" * 60)
    
    # Get recipient email
    if not recipient_email:
        recipient_email = input(f"\nEnter recipient email (default: {EMAIL_CONFIG['sender_email']}): ").strip()
        if not recipient_email:
            recipient_email = EMAIL_CONFIG['sender_email']
    
    # Validate email
    if '@' not in recipient_email:
        print(f"❌ Invalid email address: {recipient_email}")
        return False
    
    # Check if password is set
    password = EMAIL_CONFIG['sender_password']
    print(f"\n1. Checking email credentials...")
    print(f"   From: {EMAIL_CONFIG['sender_email']}")
    print(f"   To: {recipient_email}")
    print(f"   Password Set: {bool(password)}")
    print(f"   SMTP Server: {EMAIL_CONFIG['smtp_server']}")
    print(f"   SMTP Port: {EMAIL_CONFIG['smtp_port']}")
    
    if not password:
        print("\n❌ EMAIL_PASSWORD environment variable is NOT set!")
        print("   Set it with: $env:EMAIL_PASSWORD='your_app_password'")
        print("   Or use: set EMAIL_PASSWORD=your_app_password")
        return False
    
    # Test SMTP connection
    print(f"\n2. Testing SMTP connection...")
    try:
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        print(f"   ✓ Connected to {EMAIL_CONFIG['smtp_server']}:{EMAIL_CONFIG['smtp_port']}")
        
        # Test STARTTLS
        server.starttls()
        print(f"   ✓ STARTTLS enabled")
        
        # Test login
        print(f"3. Testing SMTP authentication...")
        server.login(EMAIL_CONFIG['sender_email'], password)
        print(f"   ✓ Successfully authenticated")
        
        # Create test email
        print(f"\n4. Creating test email...")
        
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = recipient_email
        msg['Subject'] = "Z-Cloud OTP Test - 123456"
        
        body = """
        <html>
        <body>
            <h2>Z-Cloud OTP Test</h2>
            <p>If you received this email, the OTP system is working!</p>
            <p><strong>Test Code: 123456</strong></p>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        print(f"5. Sending test email to {recipient_email}...")
        server.send_message(msg)
        print(f"   ✓ Email sent successfully!")
        
        server.quit()
        print(f"\n✓ All tests passed! Email system is working.")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"   ❌ Authentication failed: {e}")
        print(f"   Check your EMAIL_PASSWORD environment variable")
        return False
    except smtplib.SMTPException as e:
        print(f"   ❌ SMTP error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False

if __name__ == '__main__':
    # Get recipient email from command line argument if provided
    recipient = sys.argv[1] if len(sys.argv) > 1 else None
    success = test_email_send(recipient)
    exit(0 if success else 1)
