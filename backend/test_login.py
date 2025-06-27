#!/usr/bin/env python3
"""
Script to test login with created accounts
"""

import requests
import json

def test_login(email, password, role):
    """Test login for a specific account"""
    url = "http://localhost:8001/api/v1/auth/login"
    data = {
        "username": email,
        "password": password
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"\n🔐 Testing {role} login:")
        print(f"   Email: {email}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Login successful!")
            print(f"   Token type: {result.get('token_type')}")
            print(f"   Access token: {result.get('access_token')[:50]}...")
            return result.get('access_token')
        else:
            print(f"   ❌ Login failed: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Cannot connect to server at {url}")
        return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def test_protected_endpoint(token, role):
    """Test accessing protected endpoint with token"""
    url = "http://localhost:8001/api/v1/auth/me"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"\n👤 Testing {role} profile access:")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Profile access successful!")
            print(f"   User ID: {result.get('id')}")
            print(f"   Email: {result.get('email')}")
            print(f"   Role: {result.get('role')}")
            print(f"   Full name: {result.get('full_name')}")
        else:
            print(f"   ❌ Profile access failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("Testing LMS Authentication System")
    print("=" * 50)
    print("DEBUG: Script started")
    
    # Test accounts
    accounts = [
        ("admin@lms.com", "admin123", "Admin"),
        ("user@lms.com", "user123", "User"),
        ("instructor@lms.com", "instructor123", "Instructor")
    ]
    
    tokens = {}
    
    # Test login for each account
    for email, password, role in accounts:
        token = test_login(email, password, role)
        if token:
            tokens[role] = token
    
    print("\n" + "=" * 50)
    print("Testing Protected Endpoints")
    print("=" * 50)
    
    # Test protected endpoints
    for role, token in tokens.items():
        test_protected_endpoint(token, role)
    
    print("\n✅ Authentication testing completed!")