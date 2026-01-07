# Gmail App Password Setup for Z-Cloud OTP

## Problem
Email OTP sending is failing because the app password is invalid or expired.

## Solution: Generate a New Gmail App Password

### Step 1: Go to Google Account Security
1. Visit: https://myaccount.google.com/apppasswords
2. Sign in with your Gmail account (akwifonguhjoy@gmail.com)

### Step 2: Select App and Device
1. **Select app:** Choose "Mail"
2. **Select device:** Choose "Windows Computer" (or your OS)

### Step 3: Generate Password
1. Google will generate a 16-character app password
2. **Copy this password** (it looks like: `abcd efgh ijkl mnop`)

### Step 4: Set Environment Variable

#### Option A: PowerShell (Recommended for Windows)
```powershell
$env:EMAIL_PASSWORD='your_16_char_password'
```

#### Option B: Command Prompt (CMD)
```cmd
set EMAIL_PASSWORD=your_16_char_password
```

#### Option C: Permanent (Add to System Environment)
1. Open System Properties (Win+Pause or right-click This PC → Properties)
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Click "New" under User variables
5. Variable name: `EMAIL_PASSWORD`
6. Variable value: `your_16_char_password`
7. Click OK and restart your terminal

### Step 5: Test Email Sending
```powershell
# In PowerShell, first set the variable
$env:EMAIL_PASSWORD='your_app_password'

# Then test
python test_email_send.py
```

## Expected Output
```
✓ Connected to smtp.gmail.com:587
✓ STARTTLS enabled
✓ Successfully authenticated
✓ Email sent successfully!
✓ All tests passed! Email system is working.
```

## Fallback: Console OTP (for testing without email)
If you don't set EMAIL_PASSWORD, the system will still work:
- OTP codes will print to the **console** instead of being sent via email
- Users can see the code in the terminal where the app is running
- Useful for local development/testing

## Running Z-Cloud with Email
```powershell
# Step 1: Set the environment variable
$env:EMAIL_PASSWORD='your_app_password'

# Step 2: Start the system
python start_web_api.py
```

## Troubleshooting

### "Username and Password not accepted"
- The app password is wrong or expired
- Generate a new one at https://myaccount.google.com/apppasswords

### "2-Step Verification is not enabled"
- Enable it at https://myaccount.google.com/security
- Then generate an app password

### "Less secure apps" error
- App passwords only work with 2-Step Verification
- They bypass the "Less secure apps" setting

## Note
- The app password is **16 characters with spaces**
- When setting as environment variable, **remove the spaces**
- Keep the password secure - don't commit it to git!
