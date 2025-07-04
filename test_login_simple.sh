#!/bin/bash

# Simple login test
echo "Testing admin login..."

curl -X POST "http://127.0.0.1:8001/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" \
  -v

echo "\nLogin test complete."