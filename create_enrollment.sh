#!/bin/bash

# Create enrollment for user@lms.com in Web Development with FastAPI course
echo "Creating enrollment for user@lms.com..."

# Step 1: Login as admin to get token
echo "1. Getting admin token..."
ADMIN_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@lms.com","password":"admin123"}' \
  http://localhost:8001/api/v1/auth/login)

ADMIN_TOKEN=$(echo $ADMIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$ADMIN_TOKEN" ]; then
  echo "❌ Failed to get admin token"
  exit 1
fi

echo "✅ Admin token obtained"

# Step 2: Get user ID for user@lms.com
echo "2. Getting user ID for user@lms.com..."
USERS_RESPONSE=$(curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8001/api/v1/users/)

# Extract user ID (this is a simplified approach)
USER_ID=$(echo $USERS_RESPONSE | grep -B5 -A5 'user@lms.com' | grep '"id"' | head -1 | cut -d'"' -f4)

if [ -z "$USER_ID" ]; then
  echo "❌ Failed to get user ID for user@lms.com"
  exit 1
fi

echo "✅ User ID: $USER_ID"

# Step 3: Create enrollment
echo "3. Creating enrollment..."
COURSE_ID="c4ab4817-5bee-4143-a35a-27730b380019"  # Web Development with FastAPI

ENROLLMENT_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d "{\"user_id\":\"$USER_ID\",\"course_id\":\"$COURSE_ID\"}" \
  http://localhost:8001/api/v1/enrollments/)

echo "Enrollment response: $ENROLLMENT_RESPONSE"

# Step 4: Verify enrollment
echo "4. Verifying enrollment..."
USER_LOGIN_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"user@lms.com","password":"user123"}' \
  http://localhost:8001/api/v1/auth/login)

USER_TOKEN=$(echo $USER_LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$USER_TOKEN" ]; then
  echo "5. Checking enrolled courses for user..."
  curl -s -H "Authorization: Bearer $USER_TOKEN" \
    http://localhost:8001/api/v1/courses/enrolled
else
  echo "❌ Failed to get user token for verification"
fi

echo "\n✅ Enrollment process completed!"