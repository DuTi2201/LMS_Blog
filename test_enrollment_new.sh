#!/bin/bash

# Get admin token
echo "Getting admin token..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@lms.com","password":"admin123"}')

echo "Login response: $LOGIN_RESPONSE"

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

echo "Token: $TOKEN"

if [ -z "$TOKEN" ]; then
  echo "Failed to get token"
  exit 1
fi

# Test enrollment API with different course
echo "Testing enrollment API with different course..."
RESPONSE=$(curl -s -X POST "http://localhost:8001/api/v1/enrollments/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "user_id": "218feaa0-109c-4015-82ba-32f49c9b1044",
    "course_id": "c4ab4817-5bee-4143-a35a-27730b380019"
  }' \
  -v 2>&1)

echo "Response: $RESPONSE"