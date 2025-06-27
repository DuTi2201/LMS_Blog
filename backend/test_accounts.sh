#!/bin/bash

echo "Testing LMS Authentication System"
echo "===================================="

# Test Admin Login
echo "\n🔐 Testing Admin Login:"
echo "Email: admin@lms.com"
echo "Password: admin123"
echo "Response:"
curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@lms.com","password":"admin123"}' | python3 -m json.tool

echo "\n\n🔐 Testing User Login:"
echo "Email: user@lms.com"
echo "Password: user123"
echo "Response:"
curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user@lms.com","password":"user123"}' | python3 -m json.tool

echo "\n\n🔐 Testing Instructor Login:"
echo "Email: instructor@lms.com"
echo "Password: instructor123"
echo "Response:"
curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"instructor@lms.com","password":"instructor123"}' | python3 -m json.tool

echo "\n\n✅ Authentication testing completed!"