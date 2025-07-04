#!/bin/bash

# Test Learning Path CRUD Operations with Admin Account
echo "=== Testing Learning Path CRUD Operations ==="

# Backend URL
BASE_URL="http://127.0.0.1:8001/api/v1"

# Admin credentials
ADMIN_USERNAME="admin"
ADMIN_PASSWORD="admin123"

# Step 1: Login as admin
echo "\n=== Step 1: Admin Login ==="
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$ADMIN_USERNAME&password=$ADMIN_PASSWORD")

echo "Login Response: $LOGIN_RESPONSE"

# Extract access token
ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$ACCESS_TOKEN" ]; then
  echo "Failed to get access token"
  exit 1
fi

echo "Access Token: $ACCESS_TOKEN"

# Step 2: Create a new course
echo "\n=== Step 2: Create Course ==="
COURSE_RESPONSE=$(curl -s -X POST "$BASE_URL/courses/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{
    \"title\": \"Test Course for CRUD\",
    \"description\": \"This is a test course for CRUD operations\",
    \"short_description\": \"Test course\",
    \"difficulty_level\": \"beginner\",
    \"price\": 99.99,
    \"is_published\": true
  }")

echo "Course Creation Response: $COURSE_RESPONSE"

# Extract course ID
COURSE_ID=$(echo $COURSE_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -z "$COURSE_ID" ]; then
  echo "Failed to create course"
  exit 1
fi

echo "Created Course ID: $COURSE_ID"

# Step 3: Create a module
echo "\n=== Step 3: Create Module ==="
MODULE_RESPONSE=$(curl -s -X POST "$BASE_URL/courses/$COURSE_ID/modules" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{
    \"title\": \"Test Module 1\",
    \"description\": \"This is the first test module\",
    \"order_index\": 1,
    \"is_active\": true
  }")

echo "Module Creation Response: $MODULE_RESPONSE"

# Extract module ID
MODULE_ID=$(echo $MODULE_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -z "$MODULE_ID" ]; then
  echo "Failed to create module"
  exit 1
fi

echo "Created Module ID: $MODULE_ID"

# Step 4: Create a lesson
echo "\n=== Step 4: Create Lesson ==="
LESSON_RESPONSE=$(curl -s -X POST "$BASE_URL/modules/$MODULE_ID/lessons" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{
    \"title\": \"Test Lesson 1\",
    \"content\": \"This is the content of the first test lesson. It contains detailed information about the topic.\",
    \"order\": 1,
    \"module_id\": \"$MODULE_ID\",
    \"lesson_type\": \"text\",
    \"duration_minutes\": 30
  }")

echo "Lesson Creation Response: $LESSON_RESPONSE"

# Extract lesson ID
LESSON_ID=$(echo $LESSON_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -z "$LESSON_ID" ]; then
  echo "Failed to create lesson"
  exit 1
fi

echo "Created Lesson ID: $LESSON_ID"

# Step 5: Update course
echo "\n=== Step 5: Update Course ==="
UPDATE_COURSE_RESPONSE=$(curl -s -X PUT "$BASE_URL/courses/$COURSE_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{
    \"title\": \"Updated Test Course for CRUD\",
    \"description\": \"This is an updated test course for CRUD operations\",
    \"short_description\": \"Updated test course\",
    \"difficulty_level\": \"intermediate\",
    \"price\": 149.99
  }")

echo "Course Update Response: $UPDATE_COURSE_RESPONSE"

# Step 6: Update module
echo "\n=== Step 6: Update Module ==="
UPDATE_MODULE_RESPONSE=$(curl -s -X PUT "$BASE_URL/modules/$MODULE_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{
    \"title\": \"Updated Test Module 1\",
    \"description\": \"This is the updated first test module\",
    \"order_index\": 1
  }")

echo "Module Update Response: $UPDATE_MODULE_RESPONSE"

# Step 7: Update lesson
echo "\n=== Step 7: Update Lesson ==="
UPDATE_LESSON_RESPONSE=$(curl -s -X PUT "$BASE_URL/lessons/$LESSON_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{
    \"title\": \"Updated Test Lesson 1\",
    \"description\": \"This is the updated first test lesson\",
    \"instructor_name\": \"Updated Admin Teacher\",
    \"duration\": 45
  }")

echo "Lesson Update Response: $UPDATE_LESSON_RESPONSE"

# Step 8: Get all courses
echo "\n=== Step 8: Get All Courses ==="
ALL_COURSES_RESPONSE=$(curl -s -X GET "$BASE_URL/courses/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "All Courses Response: $ALL_COURSES_RESPONSE"

# Step 9: Get course with modules
echo "\n=== Step 9: Get Course with Modules ==="
COURSE_WITH_MODULES_RESPONSE=$(curl -s -X GET "$BASE_URL/courses/$COURSE_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Course with Modules Response: $COURSE_WITH_MODULES_RESPONSE"

# Step 10: Get module lessons
echo "\n=== Step 10: Get Module Lessons ==="
MODULE_LESSONS_RESPONSE=$(curl -s -X GET "$BASE_URL/modules/$MODULE_ID/lessons" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Module Lessons Response: $MODULE_LESSONS_RESPONSE"

# Step 11: Delete lesson
echo "\n=== Step 11: Delete Lesson ==="
DELETE_LESSON_RESPONSE=$(curl -s -X DELETE "$BASE_URL/lessons/$LESSON_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Delete Lesson Response: $DELETE_LESSON_RESPONSE"

# Step 12: Delete module
echo "\n=== Step 12: Delete Module ==="
DELETE_MODULE_RESPONSE=$(curl -s -X DELETE "$BASE_URL/modules/$MODULE_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Delete Module Response: $DELETE_MODULE_RESPONSE"

# Step 13: Delete course
echo "\n=== Step 13: Delete Course ==="
DELETE_COURSE_RESPONSE=$(curl -s -X DELETE "$BASE_URL/courses/$COURSE_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Delete Course Response: $DELETE_COURSE_RESPONSE"

echo "\n=== Learning Path CRUD Test Complete ==="
echo "All operations completed successfully!"
echo "You can now test the frontend at: http://localhost:3000/learning-path"
echo "Login with: vuvanduong802@gmail.com / admin123"