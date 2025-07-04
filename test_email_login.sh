#!/bin/bash

echo "Testing login with correct admin email..."
curl -X POST "http://127.0.0.1:8001/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@lms.com&password=admin123" \
  -s | jq .

echo -e "\n\nTesting login with admin username..."
curl -X POST "http://127.0.0.1:8001/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" \
  -s | jq .