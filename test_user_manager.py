#!/usr/bin/env python3
"""
test_user_manager.py - Test script for user manager functionality
"""

from user_manager import UserManager

def test_user_manager():
    """Test the user manager functionality"""
    print("Testing User Manager...")

    # Create user manager
    user_manager = UserManager('test_users.json')

    # Test registration
    print("\n1. Testing user registration...")
    result = user_manager.register_user('test@example.com', 'password123')
    print(f"Registration result: {result}")

    # Test verification
    print("\n2. Testing email verification...")
    user = user_manager.get_user_info('test@example.com')
    if user and 'verification_code' in user:
        code = user['verification_code']
        print(f"Verification code: {code}")
        result = user_manager.verify_email('test@example.com', code)
        print(f"Verification result: {result}")

    # Test authentication
    print("\n3. Testing user authentication...")
    result = user_manager.authenticate_user('test@example.com', 'password123')
    print(f"Authentication result: {result}")

    # Test storage info
    print("\n4. Testing storage info...")
    storage_info = user_manager.get_storage_info()
    print(f"Storage info: {storage_info}")

    print("\nUser Manager tests completed!")

if __name__ == '__main__':
    test_user_manager()