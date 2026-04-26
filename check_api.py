import requests

base_url = 'http://127.0.0.1:5000/api'

# 1. Login
res = requests.post(f"{base_url}/auth/login", json={
    "email": "ultimate@example.com",
    "password": "password123"
})
data = res.json()
token = data.get('token')

headers = {"Authorization": f"Bearer {token}"}

# 2. Submit skills
print("Submitting skills...")
submit = requests.post(f"{base_url}/student/submit-skills", json={
    "skills": ["Git"],
    "career_goal": "DevOps Engineer"
}, headers=headers)
print("Submit Status:", submit.status_code)

# 3. Get roadmap
print("Fetching roadmap...")
get_rm = requests.get(f"{base_url}/student/roadmap", headers=headers)
print("Roadmap JSON:")
import json
print(json.dumps(get_rm.json(), indent=2))
