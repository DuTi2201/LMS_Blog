#!/bin/bash

# Test script for Learning Path CRUD operations
# Base URL
BASE_URL="http://localhost:8000"

echo "=== Testing Learning Path CRUD Operations ==="

# Step 1: Login as admin
echo "\n1. Logging in as admin..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "vuvanduong802@gmail.com",
    "password": "admin123"
  }')

echo "Login response: $LOGIN_RESPONSE"

# Extract access token
ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
  echo "Failed to get access token. Exiting."
  exit 1
fi

echo "Access token obtained: ${ACCESS_TOKEN:0:20}..."

# Step 2: Create a new course
echo "\n2. Creating a new course..."
COURSE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/courses/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "title": "Test Course for CRUD",
    "description": "This is a test course for CRUD operations",
    "category": "Programming",
    "level": "beginner",
    "estimated_duration_hours": 10,
    "is_published": true
  }')

echo "Course creation response: $COURSE_RESPONSE"

# Extract course ID
COURSE_ID=$(echo $COURSE_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)

if [ -z "$COURSE_ID" ]; then
  echo "Failed to create course. Exiting."
  exit 1
fi

echo "Course created with ID: $COURSE_ID"

# Step 3: Create a module in the course
echo "\n3. Creating a module in the course..."
MODULE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/courses/$COURSE_ID/modules" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "title": "Test Module",
    "description": "This is a test module",
    "order": 1,
    "estimated_duration_minutes": 120
  }')

echo "Module creation response: $MODULE_RESPONSE"

# Extract module ID
MODULE_ID=$(echo $MODULE_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)

if [ -z "$MODULE_ID" ]; then
  echo "Failed to create module. Exiting."
  exit 1
fi

echo "Module created with ID: $MODULE_ID"

# Step 4: Create a lesson in the module
echo "\n4. Creating a lesson in the module..."
LESSON_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/modules/$MODULE_ID/lessons" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "title": "Test Lesson",
    "content": "This is the content of the test lesson",
    "order": 1,
    "module_id": "'$MODULE_ID'",
    "lesson_type": "text",
    "duration_minutes": 30
  }')

echo "Lesson creation response: $LESSON_RESPONSE"

# Extract lesson ID
LESSON_ID=$(echo $LESSON_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)

if [ -z "$LESSON_ID" ]; then
  echo "Failed to create lesson. Exiting."
  exit 1
fi

echo "Lesson created with ID: $LESSON_ID"

# Step 5: Get course details
echo "\n5. Getting course details..."
GET_COURSE_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/courses/$COURSE_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Course details: $GET_COURSE_RESPONSE"

# Step 6: Get modules in course
echo "\n6. Getting modules in course..."
GET_MODULES_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/courses/$COURSE_ID/modules" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Modules in course: $GET_MODULES_RESPONSE"

# Step 7: Get lessons in module
echo "\n7. Getting lessons in module..."
GET_LESSONS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/modules/$MODULE_ID/lessons" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Lessons in module: $GET_LESSONS_RESPONSE"

# Step 8: Update the lesson
echo "\n8. Updating the lesson..."
UPDATE_LESSON_RESPONSE=$(curl -s -X PUT "$BASE_URL/api/v1/lessons/$LESSON_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "title": "Updated Test Lesson",
    "content": "This is the updated content of the test lesson",
    "order": 1,
    "module_id": "'$MODULE_ID'",
    "lesson_type": "text",
    "duration_minutes": 45
  }')

echo "Lesson update response: $UPDATE_LESSON_RESPONSE"

# Step 9: Update the module
echo "\n9. Updating the module..."
UPDATE_MODULE_RESPONSE=$(curl -s -X PUT "$BASE_URL/api/v1/modules/$MODULE_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "title": "Updated Test Module",
    "description": "This is the updated test module",
    "order": 1,
    "estimated_duration_minutes": 150
  }')

echo "Module update response: $UPDATE_MODULE_RESPONSE"

# Step 10: Update the course
echo "\n10. Updating the course..."
UPDATE_COURSE_RESPONSE=$(curl -s -X PUT "$BASE_URL/api/v1/courses/$COURSE_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "title": "Updated Test Course for CRUD",
    "description": "This is the updated test course for CRUD operations",
    "category": "Programming",
    "level": "intermediate",
    "estimated_duration_hours": 15,
    "is_published": true
  }')

echo "Course update response: $UPDATE_COURSE_RESPONSE"

# Step 11: Delete the lesson
echo "\n11. Deleting the lesson..."
DELETE_LESSON_RESPONSE=$(curl -s -X DELETE "$BASE_URL/api/v1/lessons/$LESSON_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Lesson deletion response: $DELETE_LESSON_RESPONSE"

# Step 12: Delete the module
echo "\n12. Deleting the module..."
DELETE_MODULE_RESPONSE=$(curl -s -X DELETE "$BASE_URL/api/v1/modules/$MODULE_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Module deletion response: $DELETE_MODULE_RESPONSE"

# Step 13: Delete the course
echo "\n13. Deleting the course..."
DELETE_COURSE_RESPONSE=$(curl -s -X DELETE "$BASE_URL/api/v1/courses/$COURSE_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Course deletion response: $DELETE_COURSE_RESPONSE"

echo "\n=== Learning Path CRUD Test Completed ==="