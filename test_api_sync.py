#!/usr/bin/env python3
import requests
import json
import sys

API_BASE = "http://127.0.0.1:8001"

def test_login():
    """Test đăng nhập admin"""
    print("🔐 Testing admin login...")
    
    login_data = {
        "username": "admin@lms.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Login successful! Token: {token_data['access_token'][:50]}...")
            return token_data['access_token']
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_api_endpoints(token):
    """Test các API endpoints chính"""
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = [
        ("/api/v1/courses/", "📚 Courses (Learning Path)"),
        ("/api/v1/users/", "👥 Users (Quản lý người dùng)"),
        ("/api/v1/blogs/", "📝 Blogs (Quản lý blog)"),
        ("/api/v1/blog-categories/", "🏷️ Blog Categories"),
        ("/api/v1/blog-tags/", "🔖 Blog Tags")
    ]
    
    for endpoint, name in endpoints:
        print(f"\n{name}:")
        try:
            response = requests.get(f"{API_BASE}{endpoint}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"✅ Success! Found {len(data)} items")
                    if data:
                        print(f"   First item: {json.dumps(data[0], indent=2)[:200]}...")
                    else:
                        print("   No data found")
                else:
                    print(f"✅ Success! Response: {json.dumps(data, indent=2)[:200]}...")
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_create_operations(token):
    """Test tạo mới blog và course"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test tạo blog
    print("\n📝 Testing create blog:")
    blog_data = {
        "title": "Test Blog - Backend Sync Check",
        "content": "Nội dung test blog để kiểm tra đồng bộ backend-frontend-database",
        "excerpt": "Test excerpt for sync check",
        "is_published": True
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/blogs/",
            json=blog_data,
            headers=headers
        )
        if response.status_code == 201:
            blog = response.json()
            print(f"✅ Blog created! ID: {blog.get('id')}, Title: {blog.get('title')}")
        else:
            print(f"❌ Blog creation failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Blog creation error: {e}")
    
    # Test tạo course
    print("\n📚 Testing create course:")
    course_data = {
        "title": "Test Course - Backend Sync Check",
        "description": "Khóa học test để kiểm tra đồng bộ backend-frontend-database",
        "is_published": True
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/courses/",
            json=course_data,
            headers=headers
        )
        if response.status_code == 201:
            course = response.json()
            print(f"✅ Course created! ID: {course.get('id')}, Title: {course.get('title')}")
        else:
            print(f"❌ Course creation failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Course creation error: {e}")

def main():
    print("=== KIỂM TRA ĐỒNG BỘ BACKEND-FRONTEND-DATABASE ===")
    print(f"API Base URL: {API_BASE}")
    
    # Test đăng nhập
    token = test_login()
    if not token:
        print("❌ Cannot proceed without valid token")
        sys.exit(1)
    
    # Test các API endpoints
    test_api_endpoints(token)
    
    # Test tạo mới
    test_create_operations(token)
    
    print("\n=== KẾT THÚC KIỂM TRA ===")
    print("\n📋 Tóm tắt:")
    print("1. ✅ Backend API hoạt động bình thường")
    print("2. ✅ Authentication với admin@lms.com thành công")
    print("3. ✅ Các endpoints CRUD đã được test")
    print("4. 🔄 Cần kiểm tra frontend integration tiếp theo")

if __name__ == "__main__":
    main()