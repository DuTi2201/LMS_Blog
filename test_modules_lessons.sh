#!/bin/bash

# Get admin token
echo "Getting admin token..."
response=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin" \
  -d "password=admin123")

token=$(echo $response | jq -r '.access_token')
echo "Token obtained: ${token:0:20}..."

# Get existing course ID
echo "\n=== Getting existing course ==="
courses_response=$(curl -s -X GET http://localhost:8001/api/v1/courses/ \
  -H "Authorization: Bearer $token")
course_id=$(echo $courses_response | jq -r '.[0].id')
echo "Using course ID: $course_id"

# Test CREATE Module
echo "\n=== Testing CREATE Module ==="
module_response=$(curl -s -X POST http://localhost:8001/api/v1/modules/ \
  -H "Authorization: Bearer $token" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Test Module CRUD\",
    \"description\": \"Module for testing CRUD operations\",
    \"course_id\": \"$course_id\",
    \"order_index\": 1
  }")

echo "Module create response:"
echo $module_response | jq .
module_id=$(echo $module_response | jq -r '.id')
echo "Created module ID: $module_id"

# Test CREATE Lesson
echo "\n=== Testing CREATE Lesson ==="
lesson_response=$(curl -s -X POST http://localhost:8001/api/v1/lessons/ \
  -H "Authorization: Bearer $token" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Test Lesson CRUD\",
    \"content\": \"Lesson content for testing\",
    \"module_id\": \"$module_id\",
    \"order_index\": 1,
    \"lesson_type\": \"video\",
    \"video_url\": \"https://example.com/video.mp4\",
    \"duration\": 120
  }")

echo "Lesson create response:"
echo $lesson_response | jq .
lesson_id=$(echo $lesson_response | jq -r '.id')
echo "Created lesson ID: $lesson_id"

# Test READ Module with lessons
echo "\n=== Testing READ Module with lessons ==="
curl -s -X GET http://localhost:8001/api/v1/modules/$module_id \
  -H "Authorization: Bearer $token" | jq .

# Test READ Course with modules
echo "\n=== Testing READ Course with modules ==="
curl -s -X GET http://localhost:8001/api/v1/courses/$course_id \
  -H "Authorization: Bearer $token" | jq .

echo "\n=== Modules and Lessons Test Complete ==="