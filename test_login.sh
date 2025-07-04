#!/bin/bash

# Test login endpoint with form data
curl -X POST "http://127.0.0.1:8001/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@lms.com&password=admin123"