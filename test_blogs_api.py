#!/usr/bin/env python3
import requests
import json

try:
    response = requests.get('http://localhost:8001/api/v1/blogs/')
    print(f'Status Code: {response.status_code}')
    print(f'Headers: {dict(response.headers)}')
    print(f'Content: {response.text}')
    
    if response.text:
        try:
            data = response.json()
            print(f'JSON Data: {json.dumps(data, indent=2)}')
        except json.JSONDecodeError:
            print('Response is not valid JSON')
    else:
        print('Empty response')
        
except Exception as e:
    print(f'Error: {e}')