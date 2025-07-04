#!/usr/bin/env python3
import requests
import json

# Backend URL
BASE_URL = "http://localhost:8001"

def test_login_and_users():
    # Test login
    login_data = {
        "username": "admin@lms.com",
        "password": "admin123"
    }
    
    print("Testing login...")
    login_response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Login status: {login_response.status_code}")
    if login_response.status_code == 200:
        login_result = login_response.json()
        print(f"Login successful! Token: {login_result.get('access_token', 'No token')[:50]}...")
        
        # Test users endpoint with token
        token = login_result.get('access_token')
        if token:
            print("\nTesting users endpoint with token...")
            users_response = requests.get(
                f"{BASE_URL}/api/v1/users/?skip=0&limit=100",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
            )
            
            print(f"Users endpoint status: {users_response.status_code}")
            if users_response.status_code == 200:
                users_data = users_response.json()
                print(f"Users found: {len(users_data)}")
                for user in users_data[:3]:  # Show first 3 users
                    print(f"  - {user.get('username')} ({user.get('email')}) - Role: {user.get('role')}")
            else:
                print(f"Users endpoint error: {users_response.text}")
        else:
            print("No token received from login")
    else:
        print(f"Login failed: {login_response.text}")
    
    # Test users endpoint without token
    print("\nTesting users endpoint without token...")
    users_response_no_token = requests.get(
        f"{BASE_URL}/api/v1/users/?skip=0&limit=100"
    )
    print(f"Users endpoint (no token) status: {users_response_no_token.status_code}")
    if users_response_no_token.status_code != 200:
        print(f"Expected 403/401 error: {users_response_no_token.text}")

if __name__ == "__main__":
    test_login_and_users()