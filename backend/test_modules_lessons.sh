uvicorn app.main:app --reload --host 127.0.0.1 --port 8001#!/bin/bash

# Test modules and lessons CRUD operations

echo "=== Testing Modules and Lessons CRUD ==="

# Get admin token
echo "Getting admin token..."
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "Failed to get token"
  exit 1
fi

echo "Token obtained successfully"

# Get existing courses
echo "\nGetting existing courses..."
COURSES_RESPONSE=$(curl -s -X GET "http://localhost:8001/api/v1/courses/" \
  -H "Authorization: Bearer $TOKEN")

echo "Courses response: $COURSES_RESPONSE"

# Extract first course ID if exists
COURSE_ID=$(echo $COURSES_RESPONSE | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)

if [ -z "$COURSE_ID" ]; then
  echo "No courses found, creating a test course first..."
  
  # Create a test course
  COURSE_CREATE_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/v1/courses/" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "title": "Test Course for Modules",
      "description": "A test course to test modules and lessons",
      "is_published": true
    }')
  
  echo "Course create response: $COURSE_CREATE_RESPONSE"
  COURSE_ID=$(echo $COURSE_CREATE_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)
fi

echo "Using course ID: $COURSE_ID"

# Test 1: Create a module
echo "\n=== Test 1: Creating a module ==="
MODULE_CREATE_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/v1/modules/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Test Module\",
    \"description\": \"A test module for testing\",
    \"course_id\": \"$COURSE_ID\",
    \"order_index\": 1,
    \"is_published\": true
  }")

echo "Module create response: $MODULE_CREATE_RESPONSE"
MODULE_ID=$(echo $MODULE_CREATE_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)
echo "Created module ID: $MODULE_ID"

# Test 2: Get modules
echo "\n=== Test 2: Getting modules ==="
MODULES_RESPONSE=$(curl -s -X GET "http://localhost:8001/api/v1/modules/?course_id=$COURSE_ID" \
  -H "Authorization: Bearer $TOKEN")

echo "Modules response: $MODULES_RESPONSE"

# Test 3: Create a lesson in the module
if [ ! -z "$MODULE_ID" ]; then
  echo "\n=== Test 3: Creating a lesson ==="
  LESSON_CREATE_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/v1/modules/$MODULE_ID/lessons" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "title": "Test Lesson",
      "description": "A test lesson for testing",
      "instructor_name": "Test Instructor",
      "duration": 60,
      "order_index": 1,
      "is_active": true
    }')
  
  echo "Lesson create response: $LESSON_CREATE_RESPONSE"
  LESSON_ID=$(echo $LESSON_CREATE_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)
  echo "Created lesson ID: $LESSON_ID"
  
  # Test 4: Get lessons in module
  echo "\n=== Test 4: Getting lessons in module ==="
  LESSONS_RESPONSE=$(curl -s -X GET "http://localhost:8001/api/v1/modules/$MODULE_ID/lessons" \
    -H "Authorization: Bearer $TOKEN")
  
  echo "Lessons response: $LESSONS_RESPONSE"
fi

echo "\n=== Module and Lesson tests completed ==="