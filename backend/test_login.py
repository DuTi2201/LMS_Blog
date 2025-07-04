import json
import urllib.request
import urllib.parse

# Test login with admin@lms.com
data = json.dumps({
    'username': 'admin@lms.com', 
    'password': 'admin123'
}).encode('utf-8')

req = urllib.request.Request(
    'http://localhost:8001/api/v1/auth/login', 
    data=data, 
    headers={'Content-Type': 'application/json'}
)

try:
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode('utf-8'))
    print('Status:', response.status)
    print('Response:', json.dumps(result, indent=2))
    
    # Test users API if login successful
    if response.status == 200 and 'access_token' in result:
        token = result['access_token']
        print('\nTesting users API with token...')
        
        users_req = urllib.request.Request(
            'http://localhost:8001/api/v1/users/',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        users_response = urllib.request.urlopen(users_req)
        users_result = json.loads(users_response.read().decode('utf-8'))
        print('Users API Status:', users_response.status)
        print('Users API Response:', json.dumps(users_result, indent=2))
        
except urllib.error.HTTPError as e:
    print('HTTP Error:', e.code)
    print('Error response:', e.read().decode('utf-8'))
except Exception as e:
    print('Error:', str(e))