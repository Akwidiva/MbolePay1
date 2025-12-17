#!/usr/bin/env powershell
# Z-Cloud Email Setup Script for Windows

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Z-Cloud Email OTP Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Email Sender: tenguh.rejoice@ictuniversity.edu.cm" -ForegroundColor Green
Write-Host ""

Write-Host "To enable email OTP sending, you need to set the EMAIL_PASSWORD environment variable." -ForegroundColor Yellow
Write-Host ""

Write-Host "Steps:" -ForegroundColor Yellow
Write-Host "1. Go to: https://myaccount.google.com/apppasswords" -ForegroundColor White
Write-Host "2. Select 'Mail' and 'Windows Computer'" -ForegroundColor White
Write-Host "3. Google will generate a 16-character app password" -ForegroundColor White
Write-Host "4. Copy the app password (remove spaces)" -ForegroundColor White
Write-Host "5. Paste it below when prompted" -ForegroundColor White
Write-Host ""

$appPassword = Read-Host "Enter your 16-character Gmail App Password (or press Enter to skip)"

if ($appPassword) {
    # Remove spaces from the app password
    $appPassword = $appPassword -replace " ", ""
    
    # Set environment variable for current session
    [System.Environment]::SetEnvironmentVariable("EMAIL_PASSWORD", $appPassword, "Process")
    
    Write-Host ""
    Write-Host "✓ Environment variable set for this session!" -ForegroundColor Green
    Write-Host "  EMAIL_PASSWORD = (hidden)" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "To make this permanent (system-wide), run this command as Administrator:" -ForegroundColor Yellow
    Write-Host "[System.Environment]::SetEnvironmentVariable('EMAIL_PASSWORD', '$appPassword', 'User')" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Then restart any running Python applications." -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "Skipped. Z-Cloud will print OTP codes to console instead of sending emails." -ForegroundColor Yellow
    Write-Host "You can set EMAIL_PASSWORD anytime by running this script again." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Setup complete! You can now:" -ForegroundColor Cyan
Write-Host "- Start Z-Cloud web API (python start_web_api.py)" -ForegroundColor Green
Write-Host "- Register a new account at http://localhost:8081/register" -ForegroundColor Green
Write-Host "- OTP codes will be emailed from: tenguh.rejoice@ictuniversity.edu.cm" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
