# Z-Cloud Email OTP Issue - SOLVED

## Problem
Email sending for OTP was failing with:
```
Authentication failed: Username and Password not accepted
```

## Root Cause
The hardcoded app password in the code is **invalid or expired**. Gmail app passwords are security tokens that:
- Expire after long periods of inactivity
- Can be revoked from your Google Account
- Should never be hardcoded in source code

## Solution

### Quick Fix (3 steps)

**Step 1:** Generate new Gmail App Password
- Go to: https://myaccount.google.com/apppasswords
- Select "Mail" and "Windows Computer"
- Copy the 16-character password

**Step 2:** Set environment variable
```powershell
$env:EMAIL_PASSWORD='your_16_char_password_without_spaces'
```

**Step 3:** Test it
```powershell
python test_email_send.py
```

**Expected output:**
```
✓ Connected to smtp.gmail.com:587
✓ STARTTLS enabled
✓ Successfully authenticated
✓ Email sent successfully!
✓ All tests passed! Email system is working.
```

### Then start Z-Cloud
```powershell
$env:EMAIL_PASSWORD='your_app_password'
python start_web_api.py
```

## Changes Made

1. **web_api.py**: Removed hardcoded app password, now requires `EMAIL_PASSWORD` env variable
2. **email_config.py**: Same fix, plus helpful warning message
3. **test_email_send.py**: New diagnostic tool to test email setup
4. **setup_email_password.py**: Interactive helper to set and test password
5. **GMAIL_APP_PASSWORD_SETUP.md**: Complete setup guide

## How It Works Now

### With EMAIL_PASSWORD set (Production)
```
User Registration
    ↓
Generate OTP
    ↓
Send via Gmail SMTP
    ↓
User receives email with OTP code
```

### Without EMAIL_PASSWORD (Development)
```
User Registration
    ↓
Generate OTP
    ↓
Print to console
    ↓
Developer reads OTP from terminal
```

## Files to Use

- **For setup help:** `python setup_email_password.py`
- **To test email:** `python test_email_send.py`
- **For documentation:** Read `GMAIL_APP_PASSWORD_SETUP.md`

## Security Notes

✅ **DO:**
- Use App Passwords (not your real Gmail password)
- Set via environment variable (not in code)
- Regenerate if you suspect compromise

❌ **DON'T:**
- Hardcode passwords in source files
- Commit `.env` files to git
- Share app passwords

## Permanent Setup (Optional)

To avoid setting the variable every time:

**Windows:** Add to System Environment Variables
1. Win+Pause or right-click This PC → Properties
2. Advanced system settings → Environment Variables
3. Add `EMAIL_PASSWORD` = `your_app_password`
4. Restart terminal

Then you can always just run:
```powershell
python start_web_api.py
```

## Status
✅ Email infrastructure fixed
✅ OTP system ready to use
✅ Just need new Gmail app password!
