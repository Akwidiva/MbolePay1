#!/usr/bin/env python3
"""
user_manager.py - User enrollment and authentication for Z-Cloud

This module handles user registration, email verification, and user management
for the Z-Cloud distributed storage system.
"""

import os
import json
import smtplib
import hashlib
import secrets
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
from datetime import datetime, timedelta

class UserManager:
    """Manages user enrollment, verification, and authentication"""

    def __init__(self, users_file='users.json', smtp_config=None):
        self.users_file = users_file
        self.users = self._load_users()

        # Default SMTP configuration (Gmail)
        self.smtp_config = smtp_config or {
            'server': 'smtp.gmail.com',
            'port': 587,
            'username': 'akwifonguhjoy@gmail.com',  # User's email as specified
            'password': os.getenv('EMAIL_PASSWORD', ''),  # Should be set as environment variable
            'from_email': 'akwifonguhjoy@gmail.com',
            'from_name': 'Z-Cloud System'
        }

        # Verification code expiry (24 hours)
        self.verification_expiry = 24 * 60 * 60

    def _load_users(self) -> Dict:
        """Load users from JSON file"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not load {self.users_file}, starting with empty user database")
                return {}
        return {}

    def _save_users(self):
        """Save users to JSON file"""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2, default=str)

    def _generate_verification_code(self) -> str:
        """Generate a 6-digit verification code"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(6)])

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.smtp_config['from_name']} <{self.smtp_config['from_email']}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            # Add body
            msg.attach(MIMEText(body, 'html'))

            # Create SMTP connection
            server = smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port'])
            server.starttls()

            # Login (only if password is provided)
            if self.smtp_config.get('password'):
                server.login(self.smtp_config['username'], self.smtp_config['password'])

            # Send email
            server.send_message(msg)
            server.quit()

            return True

        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    def register_user(self, email: str, password: str) -> Dict:
        """Register a new user - OTP will be sent by web_api"""
        # Check if user already exists - reject if email is already registered
        if email in self.users:
            return {'success': False, 'message': 'This email is already registered. Please login or use a different email.'}
        
        # Create new user
        self.users[email] = {
            'email': email,
            'password_hash': self._hash_password(password),
            'verified': False,
            'verification_code': self._generate_verification_code(),
            'verification_sent_at': time.time(),
            'registered_at': time.time(),
            'verified_at': None,
            'last_login': None
        }

        # Save user to database
        self._save_users()
        
        # Return success - OTP will be sent by web_api's OTP system
        return {
            'success': True,
            'message': 'Registration successful. OTP will be sent to your email.',
            'email': email
        }

    def _send_verification_email(self, email: str, code: str) -> bool:
        """Send verification email with code"""
        subject = "Z-Cloud Email Verification"

        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0; font-size: 24px;">Welcome to Z-Cloud!</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Your Distributed Cloud Storage Network</p>
            </div>

            <div style="background: white; border: 1px solid #e1e8ed; border-radius: 0 0 10px 10px; padding: 30px;">
                <h2 style="color: #2c3e50; margin-top: 0;">Verify Your Email Address</h2>

                <p>Thank you for registering with Z-Cloud! To complete your registration and start using our distributed cloud storage, please verify your email address.</p>

                <div style="background: #f8f9fa; border: 2px solid #3498db; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0;">
                    <h3 style="margin: 0; color: #2c3e50; font-size: 18px;">Your Verification Code</h3>
                    <div style="font-size: 32px; font-weight: bold; color: #3498db; letter-spacing: 5px; margin: 10px 0;">{code}</div>
                    <p style="margin: 10px 0 0 0; color: #7f8c8d; font-size: 14px;">This code will expire in 24 hours</p>
                </div>

                <p><strong>What you can do with Z-Cloud:</strong></p>
                <ul>
                    <li>Upload and store files securely across multiple nodes</li>
                    <li>Access your files from anywhere with automatic replication</li>
                    <li>Monitor storage usage and node performance</li>
                    <li>Experience fault-tolerant distributed storage</li>
                </ul>

                <p style="color: #e74c3c; font-weight: bold;">Important: Do not share this verification code with anyone.</p>

                <hr style="border: none; border-top: 1px solid #e1e8ed; margin: 30px 0;">

                <p style="color: #7f8c8d; font-size: 12px;">
                    If you didn't request this verification, please ignore this email.<br>
                    This email was sent by Z-Cloud System.
                </p>
            </div>
        </body>
        </html>
        """

        return self._send_email(email, subject, body)

    def verify_email(self, email: str, code: str) -> Dict:
        """Verify user's email with verification code"""
        if email not in self.users:
            return {'success': False, 'message': 'User not found'}

        user = self.users[email]

        # Check if already verified
        if user.get('verified', False):
            return {'success': False, 'message': 'Email already verified'}

        # Check verification code
        if user.get('verification_code') != code:
            return {'success': False, 'message': 'Invalid verification code'}

        # Check expiry
        sent_at = user.get('verification_sent_at', 0)
        if time.time() - sent_at > self.verification_expiry:
            return {'success': False, 'message': 'Verification code has expired. Please register again.'}

        # Mark as verified
        user['verified'] = True
        user['verified_at'] = time.time()
        user['verification_code'] = None  # Clear the code
        user['verification_sent_at'] = None

        self._save_users()

        return {
            'success': True,
            'message': 'Email verified successfully! You can now log in to Z-Cloud.',
            'email': email
        }

    def authenticate_user(self, email: str, password: str) -> Dict:
        """Authenticate user login - only check email and password (OTP handles verification)"""
        if email not in self.users:
            return {'success': False, 'message': 'Invalid email or password'}

        user = self.users[email]

        # Check password
        if user['password_hash'] != self._hash_password(password):
            return {'success': False, 'message': 'Invalid email or password'}

        # Password is correct - OTP verification will happen next
        return {
            'success': True,
            'message': 'Password verified. OTP will be sent to your email.',
            'email': email,
            'user_data': {
                'email': email,
                'registered_at': user.get('registered_at')
            }
        }

    def get_user_info(self, email: str) -> Optional[Dict]:
        """Get user information"""
        return self.users.get(email)

    def resend_verification(self, email: str) -> Dict:
        """Resend verification code"""
        if email not in self.users:
            return {'success': False, 'message': 'User not found'}

        user = self.users[email]

        if user.get('verified', False):
            return {'success': False, 'message': 'Email already verified'}

        # Generate new code
        user['verification_code'] = self._generate_verification_code()
        user['verification_sent_at'] = time.time()

        # Send email
        success = self._send_verification_email(email, user['verification_code'])

        if success:
            self._save_users()
            return {'success': True, 'message': 'Verification code sent successfully'}
        else:
            return {'success': False, 'message': 'Failed to send verification email'}

    def get_storage_info(self) -> Dict:
        """Get overall storage information"""
        # Calculate total storage across all nodes
        total_storage = 0
        used_storage = 0
        active_nodes = 0

        # This would need to be integrated with the actual node storage tracking
        # For now, return placeholder data
        return {
            'total_storage_gb': 2562,  # Sum of all node storages
            'used_storage_gb': 15.2,   # Current usage
            'available_storage_gb': 2546.8,
            'active_nodes': 5,         # Number of online nodes
            'total_nodes': 8,          # Total registered nodes
            'storage_utilization_percent': 0.6
        }