#!/usr/bin/env python3
import requests
import json

# Test login first
login_url = "http://localhost:8001/api/v1/auth/login"
login_data = {
    "username": "admin@lms.com",
    "password": "admin123"
}

print("Testing login...")
try:
    login_response = requests.post(login_url, json=login_data)
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        access_token = login_result.get('access_token')
        print(f"Access token obtained: {access_token[:20]}..." if access_token else "No token")
        
        # Test users API with token
        users_url = "http://localhost:8001/api/v1/users/"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        print("\nTesting users API with token...")
        users_response = requests.get(users_url, headers=headers)
        print(f"Users API status: {users_response.status_code}")
        
        if users_response.status_code == 200:
            users_data = users_response.json()
            print(f"Users count: {len(users_data)}")
        else:
            print(f"Users API error: {users_response.text}")
    else:
        print(f"Login failed: {login_response.text}")
        
except Exception as e:
    print(f"Error: {e}")