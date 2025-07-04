#!/bin/bash

echo "Testing enrollment creation..."

# Step 1: Login as admin
echo "1. Admin login..."
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d @test_admin_login.json \
  http://localhost:8001/api/v1/auth/login > admin_token_response.json

ADMIN_TOKEN=$(cat admin_token_response.json | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Admin token: $ADMIN_TOKEN"

# Step 2: Get all users to find user@lms.com ID
echo "2. Getting users..."
curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8001/api/v1/users/ > users_response.json

echo "Users response:"
cat users_response.json

# Step 3: Try to create enrollment manually
echo "3. Creating enrollment..."
echo '{
  "user_id": "USER_ID_HERE",
  "course_id": "c4ab4817-5bee-4143-a35a-27730b380019"
}' > enrollment_request.json

echo "Enrollment request template created. Please check users_response.json for actual user ID."

# Step 4: Test user login
echo "4. Testing user login..."
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d @test_user_login.json \
  http://localhost:8001/api/v1/auth/login > user_token_response.json

USER_TOKEN=$(cat user_token_response.json | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "User token: $USER_TOKEN"

# Step 5: Check current enrolled courses
echo "5. Current enrolled courses:"
curl -s -H "Authorization: Bearer $USER_TOKEN" \
  http://localhost:8001/api/v1/courses/enrolled

echo "\nDone. Check the JSON files for details."