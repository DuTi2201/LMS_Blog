#!/bin/bash

# Test CRUD operations for LMS Backend
BASE_URL="http://localhost:8000/api/v1"
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTEwMzkyMTAsInN1YiI6IjEifQ.6QJwVQJadBz-c2ul4kRbO1HBZt5oXhqJ3qEucotiP80"

echo "=== Testing Blog Management CRUD ==="

# 1. Get all blog posts
echo "\n1. Getting all blog posts:"
curl -X GET "${BASE_URL}/blogs/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json"

echo "\n\n2. Getting blog categories:"
curl -X GET "${BASE_URL}/blog-categories/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json"

echo "\n\n3. Creating a new blog category:"
curl -X POST "${BASE_URL}/blog-categories/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Category", "description": "A test category for CRUD testing"}'

echo "\n\n4. Getting blog tags:"
curl -X GET "${BASE_URL}/blog-tags/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json"

echo "\n\n5. Creating a new blog tag:"
curl -X POST "${BASE_URL}/blog-tags/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name": "test-tag", "color": "#FF5733"}'

echo "\n\n=== Testing Learning Path CRUD ==="

echo "\n\n6. Getting all courses:"
curl -X GET "${BASE_URL}/courses/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json"

echo "\n\n7. Creating a new course:"
curl -X POST "${BASE_URL}/courses/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Course", "description": "A test course for CRUD testing", "level": "beginner", "duration_hours": 2, "is_published": true}'

echo "\n\n=== CRUD Testing Complete ==="