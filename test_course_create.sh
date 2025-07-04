#!/bin/bash

# Read token from file
TOKEN=$(cat token.txt)

# Test course creation with updated schema
curl -X POST "http://localhost:8001/api/v1/courses/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Test Course Updated",
    "description": "Test course with updated schema",
    "featured_image": "https://example.com/image.jpg",
    "level": "beginner",
    "duration_hours": 10,
    "is_published": true
  }'