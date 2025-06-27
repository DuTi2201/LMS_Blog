#!/usr/bin/env python3
import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

def make_request(url, method="GET", data=None):
    """Make HTTP request using urllib"""
    try:
        if data:
            data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=data, method=method)
            req.add_header('Content-Type', 'application/json')
        else:
            req = urllib.request.Request(url, method=method)
        
        with urllib.request.urlopen(req) as response:
            return response.getcode(), json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except Exception as e:
        return None, str(e)

def test_blog_categories():
    """Test blog categories API"""
    print("Testing blog categories...")
    
    # Create categories
    categories = [
        {"name": "Technology", "description": "Technology related posts"},
        {"name": "Programming", "description": "Programming tutorials and tips"},
        {"name": "Web Development", "description": "Web development articles"}
    ]
    
    for category in categories:
        status, response = make_request(f"{BASE_URL}/blog-categories/", "POST", category)
        if status == 200:
            print(f"✓ Created category: {category['name']}")
        else:
            print(f"✗ Failed to create category: {category['name']} - {status}")
            print(response)
    
    # Get categories
    status, response = make_request(f"{BASE_URL}/blog-categories/")
    if status == 200:
        categories = response
        print(f"✓ Retrieved {len(categories)} categories")
        return categories
    else:
        print(f"✗ Failed to get categories - {status}")
        return []

def test_blog_tags():
    """Test blog tags API"""
    print("\nTesting blog tags...")
    
    # Create tags
    tags = [
        {"name": "python"},
        {"name": "javascript"},
        {"name": "react"},
        {"name": "fastapi"}
    ]
    
    for tag in tags:
        status, response = make_request(f"{BASE_URL}/blog-tags/", "POST", tag)
        if status == 200:
            print(f"✓ Created tag: {tag['name']}")
        else:
            print(f"✗ Failed to create tag: {tag['name']} - {status}")
            print(response)
    
    # Get tags
    status, response = make_request(f"{BASE_URL}/blog-tags/")
    if status == 200:
        tags = response
        print(f"✓ Retrieved {len(tags)} tags")
        return tags
    else:
        print(f"✗ Failed to get tags - {status}")
        return []

def test_blog_posts():
    """Test blog posts API"""
    print("\nTesting blog posts...")
    
    # Get posts
    status, response = make_request(f"{BASE_URL}/blogs/?skip=0&limit=10")
    if status == 200:
        posts = response
        print(f"✓ Retrieved {len(posts)} blog posts")
        return posts
    else:
        print(f"✗ Failed to get blog posts - {status}")
        print(response)
        return []

def main():
    print("Testing LMS Backend API...\n")
    
    try:
        # Test health check
        status, response = make_request(f"{BASE_URL.replace('/api/v1', '')}/health")
        if status == 200:
            print("✓ Backend is running")
        else:
            print("✗ Backend health check failed")
            return
        
        # Test APIs
        categories = test_blog_categories()
        tags = test_blog_tags()
        posts = test_blog_posts()
        
        print("\n=== API Test Summary ===")
        print(f"Categories: {len(categories)}")
        print(f"Tags: {len(tags)}")
        print(f"Posts: {len(posts)}")
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    main()