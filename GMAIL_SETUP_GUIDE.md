# Z-Cloud Gmail Setup - Complete Guide

## ❌ Current Issue

The App Password we're using returned authentication error from Gmail.
This means either:

- The App Password is incorrect
- It hasn't been properly generated
- It's been revoked

## ✅ How to Get a Valid Gmail App Password

### Step 1: Enable 2-Factor Authentication (if not already enabled)

1. Go to: https://myaccount.google.com/security
2. Look for "2-Step Verification" section
3. If not enabled, click "Enable" and follow the steps
4. Verify with your phone

### Step 2: Generate App Password

1. Go to: https://myaccount.google.com/apppasswords
2. You should see a dropdown menu with:
   - "Select the app" → Choose **"Mail"**
   - "Select the device" → Choose **"Windows Computer"**
3. Click "Generate"
4. Google will show you a 16-character password like: `xxxx xxxx xxxx xxxx`
5. **Copy this password** (note the spaces)

### Step 3: Remove Spaces and Use It

The password might look like: `xyza bcde fghi jklm`

**Remove all spaces:** `xyzabcdefghijklm`

### Step 4: Update Z-Cloud Configuration

Option A: Set as environment variable in PowerShell:

```powershell
$env:EMAIL_PASSWORD = "xyzabcdefghijklm"
```

Option B: Hardcode in email_config.py (not recommended):

```python
SENDER_PASSWORD = 'xyzabcdefghijklm'
```

## 🔍 Verification Checklist

Before testing again, verify:

- [ ] Gmail account has 2FA enabled
- [ ] App Password was generated from Gmail settings
- [ ] App Password is 16 characters (spaces removed)
- [ ] No typos in the password
- [ ] EMAIL_PASSWORD environment variable is set
- [ ] Web API has been restarted

## 📱 Common Issues

**Issue: "Username and Password not accepted"**

- Solution: Double-check the App Password from Gmail

**Issue: "Less secure apps not allowed"**

- Solution: Make sure you're using an App Password, not your regular Gmail password

**Issue: "Email still not received"**

- Solution: Check Gmail spam folder
- Wait 1-2 minutes for email to arrive
- Check if Gmail is blocking the sender

## 🔄 After Getting New App Password

1. Copy the new 16-character password
2. Remove spaces: `xxxx xxxx xxxx xxxx` → `xxxxxxxxxxxxxxxx`
3. Set environment variable:
   ```powershell
   $env:EMAIL_PASSWORD = "xxxxxxxxxxxxxxxx"
   ```
4. Restart web API:
   ```powershell
   cd c:\Users\PFI\Desktop\cloud\CloudSim\Z-Cloud
   python web_api.py
   ```
5. Test with: `python test_otp_email.py`

## 📧 Test Steps

1. Run test script
2. Wait for "SUCCESS" message
3. Check Gmail inbox (not spam folder)
4. If received → System is working!
5. If not received after 2 minutes → Check spam folder

---

**Need Help?**
Visit Gmail Security Settings: https://myaccount.google.com/security
