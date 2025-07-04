#!/bin/bash

# Get admin token
echo "Getting admin token..."
response=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin" \
  -d "password=admin123")

token=$(echo $response | jq -r '.access_token')
echo "Token obtained: ${token:0:20}..."

# Test CREATE - Create new course
echo "\n=== Testing CREATE Course ==="
create_response=$(curl -s -X POST http://localhost:8001/api/v1/courses/ \
  -H "Authorization: Bearer $token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Course CRUD",
    "description": "Course for testing CRUD operations",
    "short_description": "Test course",
    "difficulty_level": "intermediate",
    "estimated_duration": 120,
    "price": 99.99
  }')

echo "Create response:"
echo $create_response | jq .
course_id=$(echo $create_response | jq -r '.id')
echo "Created course ID: $course_id"

# Test READ - Get specific course
echo "\n=== Testing READ Course ==="
curl -s -X GET http://localhost:8001/api/v1/courses/$course_id \
  -H "Authorization: Bearer $token" | jq .

# Test UPDATE - Update course
echo "\n=== Testing UPDATE Course ==="
update_response=$(curl -s -X PUT http://localhost:8001/api/v1/courses/$course_id \
  -H "Authorization: Bearer $token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Test Course CRUD",
    "description": "Updated description for testing",
    "short_description": "Updated test course",
    "difficulty_level": "advanced",
    "estimated_duration": 180,
    "price": 149.99
  }')

echo "Update response:"
echo $update_response | jq .

# Test READ again to verify update
echo "\n=== Verifying UPDATE ==="
curl -s -X GET http://localhost:8001/api/v1/courses/$course_id \
  -H "Authorization: Bearer $token" | jq .

# Test DELETE
echo "\n=== Testing DELETE Course ==="
delete_response=$(curl -s -X DELETE http://localhost:8001/api/v1/courses/$course_id \
  -H "Authorization: Bearer $token")

echo "Delete response:"
echo $delete_response | jq .

# Verify deletion
echo "\n=== Verifying DELETE ==="
verify_response=$(curl -s -X GET http://localhost:8001/api/v1/courses/$course_id \
  -H "Authorization: Bearer $token")
echo "Verify deletion response:"
echo $verify_response | jq .

echo "\n=== CRUD Test Complete ==="