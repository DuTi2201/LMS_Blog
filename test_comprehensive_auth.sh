#!/bin/bash

echo "=== KIỂM TRA ĐỒNG BỘ BACKEND-FRONTEND-DATABASE ==="
echo

# 1. Kiểm tra Backend Health
echo "1. Kiểm tra Backend Health:"
curl -s http://127.0.0.1:8001/health | jq .
echo

# 2. Kiểm tra đăng nhập bằng email-password (Admin)
echo "2. Đăng nhập bằng email-password (Admin):"
ADMIN_RESPONSE=$(curl -s -X POST "http://127.0.0.1:8001/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@lms.com&password=admin123")
echo "$ADMIN_RESPONSE" | jq .
ADMIN_TOKEN=$(echo "$ADMIN_RESPONSE" | jq -r '.access_token // empty')
echo "Admin Token: ${ADMIN_TOKEN:0:50}..."
echo

# 3. Kiểm tra thông tin user hiện tại
echo "3. Kiểm tra thông tin user hiện tại:"
if [ ! -z "$ADMIN_TOKEN" ]; then
  curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
    "http://127.0.0.1:8001/api/v1/auth/me" | jq .
else
  echo "❌ Không có token để kiểm tra"
fi
echo

# 4. Kiểm tra danh sách courses (Learning Path)
echo "4. Kiểm tra danh sách courses (Learning Path):"
if [ ! -z "$ADMIN_TOKEN" ]; then
  curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
    "http://127.0.0.1:8001/api/v1/courses?skip=0&limit=5" | jq .
else
  echo "❌ Không có token để kiểm tra"
fi
echo

# 5. Kiểm tra danh sách users (Quản lý người dùng)
echo "5. Kiểm tra danh sách users (Quản lý người dùng):"
if [ ! -z "$ADMIN_TOKEN" ]; then
  curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
    "http://127.0.0.1:8001/api/v1/users?skip=0&limit=5" | jq .
else
  echo "❌ Không có token để kiểm tra"
fi
echo

# 6. Kiểm tra danh sách blogs (Quản lý blog)
echo "6. Kiểm tra danh sách blogs (Quản lý blog):"
if [ ! -z "$ADMIN_TOKEN" ]; then
  curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
    "http://127.0.0.1:8001/api/v1/blogs?skip=0&limit=5" | jq .
else
  echo "❌ Không có token để kiểm tra"
fi
echo

# 7. Test tạo blog post mới (CRUD)
echo "7. Test tạo blog post mới (CRUD):"
if [ ! -z "$ADMIN_TOKEN" ]; then
  NEW_BLOG=$(curl -s -X POST "http://127.0.0.1:8001/api/v1/blogs" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "title": "Test Blog Post - Sync Check",
      "content": "Đây là bài viết test để kiểm tra đồng bộ backend-frontend-database",
      "excerpt": "Test excerpt",
      "is_published": true
    }')
  echo "$NEW_BLOG" | jq .
  BLOG_ID=$(echo "$NEW_BLOG" | jq -r '.id // empty')
  echo "Created Blog ID: $BLOG_ID"
else
  echo "❌ Không có token để kiểm tra"
fi
echo

# 8. Test tạo course mới (CRUD)
echo "8. Test tạo course mới (CRUD):"
if [ ! -z "$ADMIN_TOKEN" ]; then
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
  echo "Created Course ID: $COURSE_ID"
else
  echo "❌ Không có token để kiểm tra"
fi
echo

echo "=== KẾT THÚC KIỂM TRA ==="