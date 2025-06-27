import jwt
import json

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTEwMzk1NDEsInN1YiI6IjEifQ.72LJ9Gb-yLVRvRtVOiHdbhUQjO7dRG3VP3B2VWkB-hU'

# Decode without verification to see payload
payload = jwt.decode(token, options={'verify_signature': False})
print('Token payload:', json.dumps(payload, indent=2))

# Check expiration
import time
current_time = int(time.time())
print(f'Current time: {current_time}')
print(f'Token expires: {payload.get("exp")}')
print(f'Token valid: {current_time < payload.get("exp", 0)}')