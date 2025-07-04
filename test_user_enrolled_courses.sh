#!/bin/bash

# Test user login and enrolled courses
echo "Testing user login and enrolled courses..."

# Login as user
echo "1. Login as user@lms.com..."
USER_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"user@lms.com","password":"user123"}' \
  http://localhost:8001/api/v1/auth/login)

echo "Login response: $USER_RESPONSE"

# Extract access token
USER_TOKEN=$(echo $USER_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "User token: $USER_TOKEN"

if [ -n "$USER_TOKEN" ]; then
  echo "\n2. Getting enrolled courses for user..."
  curl -s -H "Authorization: Bearer $USER_TOKEN" \
    http://localhost:8001/api/v1/courses/enrolled
else
  echo "Failed to get user token"
fi

echo "\n\n3. Testing admin login for comparison..."
# Login as admin
ADMIN_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@lms.com","password":"admin123"}' \
  http://localhost:8001/api/v1/auth/login)

# Extract admin token
ADMIN_TOKEN=$(echo $ADMIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$ADMIN_TOKEN" ]; then
  echo "\n4. Getting all courses for admin..."
  curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
    http://localhost:8001/api/v1/courses/
else
  echo "Failed to get admin token"
fi

echo "\n\nTest completed."