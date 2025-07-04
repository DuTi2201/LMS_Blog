#!/usr/bin/env python3
import urllib.request
import urllib.error
import json

def test_backend_api():
    try:
        # Test backend API
        url = 'http://localhost:8001/api/v1/blogs/'
        
        print(f"Testing: {url}")
        
        # Create request with headers
        req = urllib.request.Request(url)
        req.add_header('Origin', 'http://localhost:3000')
        req.add_header('Content-Type', 'application/json')
        
        response = urllib.request.urlopen(req)
        
        print(f"Status Code: {response.getcode()}")
        print(f"Response Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        content = response.read().decode('utf-8')
        print(f"\nResponse Content (first 500 chars):")
        print(content[:500])
        
        # Check for CORS headers
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
        }
        
        print(f"\nCORS Headers:")
        for key, value in cors_headers.items():
            print(f"  {key}: {value}")
            
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        print(f"Response Headers:")
        for key, value in e.headers.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_backend_api()