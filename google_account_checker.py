#!/usr/bin/env python3
"""
google_account_checker.py - Diagnose Gmail/Google account issues
"""

import os
import smtplib

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║              Z-Cloud Gmail Account Diagnostic Tool                         ║
╚════════════════════════════════════════════════════════════════════════════╝
""")

EMAIL = 'akwifonguhjoy@gmail.com'
password = input("Enter your Gmail App Password (or password to test): ").strip()

if not password:
    print("❌ No password provided")
    exit(1)

print(f"\nTesting connection with:")
print(f"  Email: {EMAIL}")
print(f"  Password length: {len(password)} chars")

# Test different approaches
tests = [
    ("Standard SMTP (Gmail)", "smtp.gmail.com", 587, True),
    ("Gmail with TLS", "smtp.gmail.com", 587, True),
    ("Gmail SSL", "smtp.gmail.com", 465, False),
]

for test_name, server, port, use_starttls in tests:
    print(f"\n{'='*60}")
    print(f"Test: {test_name}")
    print(f"  Server: {server}:{port}")
    print(f"  StartTLS: {use_starttls}")
    print(f"{'='*60}")
    
    try:
        if use_starttls:
            # Standard port 587 with STARTTLS
            server_obj = smtplib.SMTP(server, port, timeout=10)
            print("  ✓ Connected")
            server_obj.starttls()
            print("  ✓ STARTTLS enabled")
        else:
            # Port 465 with immediate SSL
            server_obj = smtplib.SMTP_SSL(server, port, timeout=10)
            print("  ✓ Connected with SSL")
        
        # Try login
        print(f"  → Attempting login as {EMAIL}...")
        server_obj.login(EMAIL, password)
        print("  ✓✓✓ SUCCESS! Login worked!")
        
        server_obj.quit()
        print("\n" + "="*60)
        print("✓ Your password is valid!")
        print("="*60)
        print("\nNow set it and restart Z-Cloud:")
        print(f'  $env:EMAIL_PASSWORD="{password}"')
        print(f'  python start_web_api.py')
        exit(0)
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"  ❌ Authentication failed: {str(e)[:80]}")
    except smtplib.SMTPException as e:
        print(f"  ❌ SMTP Error: {str(e)[:80]}")
    except Exception as e:
        print(f"  ❌ Connection Error: {str(e)[:80]}")

print("\n" + "="*60)
print("❌ All tests failed!")
print("="*60)
print("\nCommon reasons:")
print("  1. Password is incorrect")
print("  2. 2-Step Verification not enabled")
print("  3. Not an App Password (should be 16 chars)")
print("  4. Account locked or needs verification")
print("\nFix:")
print("  1. Go to: https://myaccount.google.com/security")
print("  2. Enable '2-Step Verification'")
print("  3. Go to: https://myaccount.google.com/apppasswords")
print("  4. Select 'Mail' and 'Windows Computer'")
print("  5. Copy the generated 16-char password")
print("  6. Try again: python google_account_checker.py")
print("="*60)
