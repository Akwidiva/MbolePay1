# Z-Cloud OTP Email Setup Guide

## Overview
Z-Cloud now sends OTP (One-Time Password) codes via email to authenticate users during registration and login.

## Email Sender
**Email:** `tenguh.rejoice@ictuniversity.edu.cm`

## How to Enable Email OTP

### Option 1: Using Environment Variable (Recommended for Production)

1. **Generate Gmail App Password:**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer" (or your device)
   - Google will generate a 16-character app password
   - Copy this password (remove spaces)

2. **Set Environment Variable (Windows PowerShell):**
   ```powershell
   $env:EMAIL_PASSWORD = "your_16_char_app_password"
   ```

3. **Set Environment Variable (Windows CMD):**
   ```cmd
   set EMAIL_PASSWORD=your_16_char_app_password
   ```

4. **Set Environment Variable (Linux/Mac):**
   ```bash
   export EMAIL_PASSWORD="your_16_char_app_password"
   ```

### Option 2: Direct Configuration (Development Only)

1. Open `email_config.py`
2. Set `SENDER_PASSWORD = "your_16_char_app_password"`
3. Save the file

**⚠️ WARNING:** Never commit the app password to version control!

## Testing Email OTP

1. Register a new account at http://localhost:8081/register
2. Enter your email address
3. If email is working:
   - ✅ You'll receive an OTP code in your email inbox
   - ✅ Use that code to verify your account
4. If email is NOT working:
   - The OTP code will be printed to the terminal/console
   - Use that code to verify your account

## Gmail App Passwords

### What is an App Password?
- A 16-character password that works only with apps (not the regular Gmail password)
- More secure than using your actual Gmail password
- Can be revoked at any time without changing your account password

### How to Generate an App Password:
1. Enable 2-Factor Authentication on your Google Account
2. Visit: https://myaccount.google.com/apppasswords
3. Select "Mail" and "Windows Computer" (or your device type)
4. Google generates a 16-character password
5. Copy the password (without spaces)
6. Use it in the EMAIL_PASSWORD environment variable

## Troubleshooting

### "Invalid login" Error
- Check that EMAIL_PASSWORD is set correctly
- Ensure 2-Factor Authentication is enabled on the Gmail account
- Verify you're using an App Password, not your regular password

### "Connection refused" Error
- Check that SMTP_PORT (587) is not blocked by your firewall
- Try disabling antivirus temporarily to test

### Email Not Being Sent
- Check the terminal output for error messages
- Verify EMAIL_PASSWORD environment variable is set
- OTP codes are always printed to console as fallback

## Current Status

**With Environment Variable Set:** ✅ Emails will be sent to user accounts
**Without Environment Variable:** ✅ OTP codes appear in terminal (development mode)

## Security Notes

- OTP codes expire after 5 minutes
- Users get 5 failed attempts before lockout
- Never share OTP codes via unsecured channels
- The email is sent FROM: `tenguh.rejoice@ictuniversity.edu.cm`
