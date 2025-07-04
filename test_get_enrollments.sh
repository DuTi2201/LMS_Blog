#!/bin/bash

# Get admin token
echo "Getting admin token..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@lms.com","password":"admin123"}')

echo "Login response: $LOGIN_RESPONSE"

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')

echo "Token: $TOKEN"

if [ -z "$TOKEN" ] || [ "$TOKEN" == "null" ]; then
  echo "Failed to get token"
  exit 1
fi

# Get user info from /me endpoint
echo "Getting user info..."
ME_RESPONSE=$(curl -s -X GET http://localhost:8001/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN")

echo "Me response: $ME_RESPONSE"

USER_ID=$(echo $ME_RESPONSE | jq -r '.id')

echo "User ID: $USER_ID"

if [ -z "$USER_ID" ] || [ "$USER_ID" == "null" ]; then
    echo "Failed to get User ID"
    exit 1
fi

# Test GET enrollments API
echo "Testing GET enrollments API..."
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X GET "http://localhost:8001/api/v1/enrollments/user/$USER_ID" \
  -H "Authorization: Bearer $TOKEN")

echo "Response: $RESPONSE"

HTTP_CODE=$(echo "$RESPONSE" | tail -n1 | cut -d: -f2)

if [ "$HTTP_CODE" -ne 200 ]; then
    echo "Error: API call failed with status code $HTTP_CODE"
    exit 1
fi

echo "Successfully retrieved enrollments."