import requests
import json

response = requests.get('http://localhost:8001/api/v1/blogs/')
print('Status:', response.status_code)
print('Response:')
print(json.dumps(response.json(), indent=2))