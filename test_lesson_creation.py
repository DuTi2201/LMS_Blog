#!/usr/bin/env python3
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

def test_login():
    """Test login with admin credentials"""
    login_data = {
        "username": "vuvanduong802@gmail.com",
        "password": "admin123"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    print(f"Login Status: {response.status_code}")
    if response.status_code == 200:
        token_data = response.json()
        print(f"Access Token: {token_data.get('access_token', 'N/A')[:50]}...")
        return token_data.get('access_token')
    else:
        print(f"Login Error: {response.text}")
        return None

def test_get_courses(token):
    """Get available courses"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/courses/", headers=headers)
    
    print(f"\nGet Courses Status: {response.status_code}")
    if response.status_code == 200:
        courses = response.json()
        print(f"Found {len(courses)} courses")
        if courses:
            print(f"First course: {courses[0].get('title', 'N/A')} (ID: {courses[0].get('id', 'N/A')})")
            return courses[0]
    else:
        print(f"Get Courses Error: {response.text}")
    return None

def test_get_modules(course_id, token):
    """Get modules for a course"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/courses/{course_id}/modules", headers=headers)
    
    print(f"\nGet Modules Status: {response.status_code}")
    if response.status_code == 200:
        modules = response.json()
        print(f"Found {len(modules)} modules")
        if modules:
            print(f"First module: {modules[0].get('title', 'N/A')} (ID: {modules[0].get('id', 'N/A')})")
            return modules[0]
    else:
        print(f"Get Modules Error: {response.text}")
    return None

def test_create_lesson(module_id, token):
    """Test creating a lesson"""
    lesson_data = {
        "title": "Test Lesson from Python",
        "content": "This is a test lesson created via API",
        "lesson_type": "text",
        "order_index": 1,
        "is_published": True
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/modules/{module_id}/lessons",
        json=lesson_data,
        headers=headers
    )
    
    print(f"\nCreate Lesson Status: {response.status_code}")
    if response.status_code == 201:
        lesson = response.json()
        print(f"Created lesson: {lesson.get('title', 'N/A')} (ID: {lesson.get('id', 'N/A')})")
        return lesson
    else:
        print(f"Create Lesson Error: {response.text}")
    return None

def test_get_lessons(module_id, token):
    """Get lessons for a module"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/modules/{module_id}/lessons", headers=headers)
    
    print(f"\nGet Lessons Status: {response.status_code}")
    if response.status_code == 200:
        lessons = response.json()
        print(f"Found {len(lessons)} lessons")
        for lesson in lessons:
            print(f"  - {lesson.get('title', 'N/A')} (ID: {lesson.get('id', 'N/A')})")
        return lessons
    else:
        print(f"Get Lessons Error: {response.text}")
    return None

if __name__ == "__main__":
    print("Testing Lesson Creation Flow...")
    
    # Step 1: Login
    token = test_login()
    if not token:
        print("Failed to login. Exiting.")
        exit(1)
    
    # Step 2: Get courses
    course = test_get_courses(token)
    if not course:
        print("No courses found. Exiting.")
        exit(1)
    
    # Step 3: Get modules
    module = test_get_modules(course['id'], token)
    if not module:
        print("No modules found. Exiting.")
        exit(1)
    
    # Step 4: Get existing lessons
    print("\n=== Before creating lesson ===")
    test_get_lessons(module['id'], token)
    
    # Step 5: Create lesson
    print("\n=== Creating lesson ===")
    new_lesson = test_create_lesson(module['id'], token)
    
    # Step 6: Get lessons again to verify
    print("\n=== After creating lesson ===")
    test_get_lessons(module['id'], token)
    
    print("\nTest completed!")