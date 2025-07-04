import requests
import json

# Test courses API
print("=== Testing Courses API ===")
r = requests.get('http://localhost:8001/api/v1/courses/?skip=0&limit=10')
print(json.dumps(r.json(), indent=2))

# Test modules API
print("\n=== Testing Modules API ===")
r = requests.get('http://localhost:8001/api/v1/courses/550e8400-e29b-41d4-a716-446655440000/modules/')
print(json.dumps(r.json(), indent=2))