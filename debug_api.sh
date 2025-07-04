#!/bin/bash

# Lấy token
echo "Getting admin token..."
RESPONSE=$(curl -s -X POST "http://127.0.0.1:8001/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@lms.com&password=admin123")

echo "Login response:"
echo "$RESPONSE"
echo

TOKEN=$(echo "$RESPONSE" | jq -r '.access_token // empty')
echo "Token: $TOKEN"
echo

if [ ! -z "$TOKEN" ]; then
  echo "Testing courses endpoint..."
  curl -v -H "Authorization: Bearer $TOKEN" \
    "http://127.0.0.1:8001/api/v1/courses" 2>&1
  echo
  echo
  
  echo "Testing users endpoint..."
  curl -v -H "Authorization: Bearer $TOKEN" \
    "http://127.0.0.1:8001/api/v1/users" 2>&1
  echo
  echo
  
  echo "Testing blogs endpoint..."
  curl -v -H "Authorization: Bearer $TOKEN" \
    "http://127.0.0.1:8001/api/v1/blogs" 2>&1
else
  echo "No token received!"
fi