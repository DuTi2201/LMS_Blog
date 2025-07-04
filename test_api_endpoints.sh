#!/bin/bash

# Lấy token admin
echo "Đăng nhập admin..."
ADMIN_RESPONSE=$(curl -s -X POST "http://127.0.0.1:8001/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@lms.com&password=admin123")

ADMIN_TOKEN=$(echo "$ADMIN_RESPONSE" | jq -r '.access_token // empty')

if [ -z "$ADMIN_TOKEN" ]; then
  echo "❌ Không thể lấy token admin"
  echo "Response: $ADMIN_RESPONSE"
  exit 1
fi

echo "✅ Đăng nhập thành công!"
echo "Token: ${ADMIN_TOKEN:0:50}..."
echo

# Test API endpoints
echo "=== KIỂM TRA CÁC API ENDPOINTS ==="
echo

# 1. Courses API
echo "1. Courses API (Learning Path):"
curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://127.0.0.1:8001/api/v1/courses" | jq '.[:2] // .'
echo

# 2. Users API
echo "2. Users API (Quản lý người dùng):"
curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://127.0.0.1:8001/api/v1/users" | jq '.[:2] // .'
echo

# 3. Blogs API
echo "3. Blogs API (Quản lý blog):"
curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://127.0.0.1:8001/api/v1/blogs" | jq '.[:2] // .'
echo

# 4. Test tạo blog mới
echo "4. Test tạo blog mới:"
NEW_BLOG=$(curl -s -X POST "http://127.0.0.1:8001/api/v1/blogs" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Blog - Sync Check",
    "content": "Nội dung test blog để kiểm tra đồng bộ",
    "excerpt": "Test excerpt",
    "is_published": true
  }')
echo "$NEW_BLOG" | jq .
BLOG_ID=$(echo "$NEW_BLOG" | jq -r '.id // empty')
echo "Blog ID: $BLOG_ID"
echo

# 5. Test tạo course mới
echo "5. Test tạo course mới:"
NEW_COURSE=$(curl -s -X POST "http://127.0.0.1:8001/api/v1/courses" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Course - Sync Check",
    "description": "Khóa học test để kiểm tra đồng bộ",
    "is_published": true
  }')
echo "$NEW_COURSE" | jq .
COURSE_ID=$(echo "$NEW_COURSE" | jq -r '.id // empty')
echo "Course ID: $COURSE_ID"
echo

# 6. Test categories và tags
echo "6. Test Blog Categories:"
curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://127.0.0.1:8001/api/v1/blog-categories" | jq .
echo

echo "7. Test Blog Tags:"
curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://127.0.0.1:8001/api/v1/blog-tags" | jq .
echo

echo "=== KẾT THÚC KIỂM TRA API ==="