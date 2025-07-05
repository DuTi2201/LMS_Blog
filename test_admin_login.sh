#!/bin/bash

# Test admin login
echo "Testing admin login..."

response=$(curl -s -X POST "http://127.0.0.1:8001/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Origin: http://localhost:3000" \
  -d "username=admin@lms.com&password=admin123")

echo "Response: $response"

# Extract token if login successful
if echo "$response" | grep -q "access_token"; then
  token=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
  echo "Login successful! Token: $token"
  
  # Test authenticated endpoint
  echo "Testing authenticated endpoint..."
  curl -s -X GET "http://127.0.0.1:8001/api/v1/auth/me" \
    -H "Authorization: Bearer $token" \
    -H "Origin: http://localhost:3000"
else
  echo "Login failed!"
fi