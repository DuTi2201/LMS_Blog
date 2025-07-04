#!/bin/bash

# Get token first
echo "Getting token..."
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@lms.com","password":"admin123"}')

echo "Token response: $TOKEN_RESPONSE"

# Extract token
TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Extracted token: ${TOKEN:0:20}..."

# Test users API
echo "\nTesting users API..."
curl -s -X GET "http://localhost:8001/api/v1/users/?skip=0&limit=100" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"

echo "\nDone."