# Z-Cloud OTP Email System - Quick Start

## What's New
✅ OTP codes are now sent to user emails during registration and login
✅ Email sender: `tenguh.rejoice@ictuniversity.edu.cm`
✅ Professional HTML emails with security information
✅ OTP codes expire after 5 minutes
✅ Max 5 failed attempts per OTP

## How It Works

### Registration Flow:
1. User fills registration form
2. Account is created
3. OTP code is generated and **emailed** to their email address
4. User enters OTP to verify email
5. Account is activated

### Login Flow:
1. User enters email + password
2. OTP code is generated and **emailed** to their email address
3. User enters OTP to complete login
4. User accesses dashboard

## Setup Instructions

### To Enable Email Sending:

**Step 1: Generate Gmail App Password**
1. Open: https://myaccount.google.com/apppasswords
2. Select: "Mail" and "Windows Computer"
3. Google generates a 16-character password
4. Copy this password

**Step 2: Set Environment Variable (Windows PowerShell)**
```powershell
$env:EMAIL_PASSWORD = "paste_your_app_password_here"
```

**Step 3: Restart Web API**
```powershell
python start_web_api.py
```

### Or Use the Setup Script:
```powershell
.\setup_email.ps1
```

## Current System Features

| Feature | Status |
|---------|--------|
| OTP Generation | ✅ Active |
| Email Sending | ⏳ Needs EMAIL_PASSWORD |
| Console Fallback | ✅ Always available |
| Email Account | ✅ tenguh.rejoice@ictuniversity.edu.cm |
| OTP Expiry | ✅ 5 minutes |
| Max Attempts | ✅ 5 attempts |

## Without Environment Variable Set

If EMAIL_PASSWORD is not set:
- ✅ OTP codes appear in terminal/console
- ✅ Users can use these codes to verify
- ✅ No actual emails are sent
- ℹ️ This is for development/testing

## With Environment Variable Set

If EMAIL_PASSWORD is set:
- ✅ OTP codes are emailed to users
- ✅ Emails are formatted professionally
- ✅ Security warnings are included
- ✅ Same codes appear in terminal as backup

## Testing

1. **Test Registration:**
   - Go to http://localhost:8081/register
   - Create new account
   - Check email or console for OTP
   - Enter OTP to verify

2. **Test Login:**
   - Go to http://localhost:8081/login
   - Use registered email + password
   - Check email or console for OTP
   - Enter OTP to login

## Files Modified

- `web_api.py` - Added OTP routes and email sending
- `login.html` - Added OTP verification screen
- `register.html` - Added OTP verification screen
- `user_manager.py` - Modified to skip old email sending

## Files Created

- `email_config.py` - Email configuration template
- `EMAIL_SETUP.md` - Detailed setup instructions
- `setup_email.ps1` - Automated setup script (Windows)
- `OTP_EMAIL_SYSTEM.md` - This file

## Support

For detailed instructions, see: `EMAIL_SETUP.md`
For Gmail App Password help: https://support.google.com/accounts/answer/185833

---

**System Email:** tenguh.rejoice@ictuniversity.edu.cm
**OTP Validity:** 5 minutes
**Max Retries:** 5 attempts
