#!/usr/bin/env python3
"""
Test script to verify OTP email sending is working
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random

# Set the environment variable
os.environ['EMAIL_PASSWORD'] = 'uybtimztzxjehhdw'

def generate_otp():
    """Generate a random 6-digit OTP"""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def test_send_otp_email(recipient_email):
    """Test sending OTP email"""
    try:
        sender_email = 'akwifonguhjoy.com'
        password = os.getenv('EMAIL_PASSWORD', '')
        otp = generate_otp()
        
        if not password:
            print("ERROR: EMAIL_PASSWORD is not set!")
            return False
        
        print(f"\n{'='*70}")
        print(f"TESTING OTP EMAIL SEND")
        print(f"{'='*70}")
        print(f"From: {sender_email}")
        print(f"To: {recipient_email}")
        print(f"OTP Code: {otp}")
        print(f"Password length: {len(password)} characters")
        
        # Email content
        subject = "Z-Cloud - Test OTP Email"
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #1A73E8 0%, #1557B0 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0; font-size: 24px;">☁️ Z-Cloud</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Distributed Cloud Storage</p>
            </div>

            <div style="background: white; border: 1px solid #E3E3E3; border-radius: 0 0 10px 10px; padding: 30px;">
                <h2 style="color: #202124; margin-top: 0;">Your Login Verification Code</h2>

                <p style="color: #5F6368; line-height: 1.6;">Hello,</p>
                
                <p style="color: #5F6368; line-height: 1.6;">This is a test email from Z-Cloud OTP system. Here is your verification code:</p>

                <div style="background: #F8F9FA; border: 2px solid #34A853; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0;">
                    <h3 style="margin: 0; color: #202124; font-size: 16px;">Your OTP Code</h3>
                    <div style="font-size: 48px; font-weight: bold; color: #34A853; letter-spacing: 8px; margin: 15px 0;">{otp}</div>
                    <p style="margin: 10px 0 0 0; color: #9AA0A6; font-size: 14px;">Valid for 5 minutes</p>
                </div>

                <div style="background: #FFF3CD; border-left: 4px solid #FBBC04; padding: 15px; border-radius: 4px; margin: 20px 0;">
                    <p style="margin: 0; color: #856404; font-size: 14px;">
                        <strong>⚠️ This is a TEST email:</strong> If you didn't request this, please ignore it.
                    </p>
                </div>

                <p style="color: #5F6368; line-height: 1.6; margin-top: 20px;">Test completed successfully!</p>
            </div>
        </body>
        </html>
        """
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # Attach HTML body
        msg.attach(MIMEText(body, 'html'))
        
        print(f"\n[*] Connecting to SMTP server...")
        # Send email via SMTP
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            print(f"[*] Starting TLS...")
            server.starttls()
            print(f"[*] Logging in...")
            server.login(sender_email, password)
            print(f"[*] Sending message...")
            server.send_message(msg)
        
        print(f"{'='*70}")
        print(f"✅ SUCCESS! OTP email sent to: {recipient_email}")
        print(f"✅ OTP Code: {otp}")
        print(f"{'='*70}\n")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"{'='*70}")
        print(f"❌ AUTHENTICATION ERROR!")
        print(f"Error: {e}")
        print(f"Possible causes:")
        print(f"  1. EMAIL_PASSWORD is incorrect")
        print(f"  2. Gmail 2-Factor Authentication is not enabled")
        print(f"  3. App Password is incorrect or expired")
        print(f"{'='*70}\n")
        return False
    except smtplib.SMTPException as e:
        print(f"{'='*70}")
        print(f"❌ SMTP ERROR!")
        print(f"Error: {e}")
        print(f"{'='*70}\n")
        return False
    except Exception as e:
        print(f"{'='*70}")
        print(f"❌ ERROR: {e}")
        print(f"{'='*70}\n")
        return False

if __name__ == '__main__':
    # Test email - change this to your actual Gmail address
    test_email = 'akwifonguhjoy@gmail.com'
    
    print("\n🧪 Z-Cloud OTP Email Test Script\n")
    print(f"This script will test sending an OTP email to: {test_email}")
    print(f"Please check your Gmail inbox after the test.\n")
    
    success = test_send_otp_email(test_email)
    
    if success:
        print("✅ Test passed! Check your Gmail inbox.")
        print("   Note: Emails may take 1-2 minutes to arrive.\n")
    else:
        print("❌ Test failed. See error messages above.\n")
