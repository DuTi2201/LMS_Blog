#!/bin/bash

echo "Testing admin login..."
response=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin" \
  -d "password=admin123")

echo "Login response:"
echo $response | jq .

# Extract token
token=$(echo $response | jq -r '.access_token')
echo "Token: $token"

# Test courses API with token
echo "\nTesting courses API..."
curl -s -X GET http://localhost:8001/api/v1/courses/ \
  -H "Authorization: Bearer $token" \
  -H "Accept: application/json" | jq .