import requests
import time
import json

BASE = 'http://127.0.0.1:5000'

print('1) Checking /health')
try:
    r = requests.get(f"{BASE}/health", timeout=5)
    print('health:', r.status_code, r.json())
except Exception as e:
    print('health check failed:', e)

# Admin login
print('\n2) Admin login')
admin_creds = {'username': 'admin@skillgap.ai', 'password': 'Admin@123!'}
try:
    r = requests.post(f"{BASE}/api/admin/login", json=admin_creds, timeout=5)
    print('admin login status:', r.status_code)
    try:
        print('admin body:', r.json())
    except Exception:
        print('admin body not JSON')
    admin_token = r.json().get('token') if r.ok else None
except Exception as e:
    print('admin login failed:', e)
    admin_token = None

# Signup a transient test user
print('\n3) Signup test user')
email = f"testuser+{int(time.time())}@gmail.com"
signup_payload = {'name': 'Check User', 'email': email, 'password': 'Test@1234'}
try:
    r = requests.post(f"{BASE}/api/auth/signup", json=signup_payload, timeout=5)
    print('signup status:', r.status_code)
    print('signup body:', r.json())
except Exception as e:
    print('signup failed:', e)

# Login test user
print('\n4) Login test user')
try:
    r = requests.post(f"{BASE}/api/auth/login", json={'email': email, 'password': 'Test@1234'}, timeout=5)
    print('login status:', r.status_code)
    body = r.json() if r.ok else r.text
    print('login body:', body)
    user_token = r.json().get('token') if r.ok else None
except Exception as e:
    print('login failed:', e)
    user_token = None

# Fetch careers with user token
print('\n5) Fetch careers with user token')
if user_token:
    headers = {'Authorization': f'Bearer {user_token}'}
    try:
        r = requests.get(f"{BASE}/api/student/careers", headers=headers, timeout=5)
        print('careers status:', r.status_code)
        print('careers body keys:', list(r.json().keys()) if r.ok else r.text)
    except Exception as e:
        print('fetch careers failed:', e)
else:
    print('no user token; skipping careers fetch')

print('\nChecks complete')
