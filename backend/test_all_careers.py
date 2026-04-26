import requests
import json

BASE = "http://localhost:5000/api"

# Login
r = requests.post(f"{BASE}/auth/login", json={"email": "ultimate@example.com", "password": "password123"})
token = r.json().get("token")
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

careers = [
    "Machine Learning Engineer",
    "Data Scientist",
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "DevOps Engineer",
    "Cloud Architect",
    "Cybersecurity Analyst"
]

print(f"{'Career':30s} | {'Status':6s} | {'Score':5s} | {'Missing':7s} | {'Roadmap':7s}")
print("-" * 80)

for career in careers:
    try:
        r = requests.post(f"{BASE}/student/submit-skills",
            json={"skills": ["Python", "SQL"], "career_goal": career},
            headers=headers,
            timeout=30
        )
        data = r.json()
        status = r.status_code
        score = data.get("readiness_score", "N/A")
        missing = data.get("missing_skills", [])
        roadmap = data.get("roadmap", [])
        error = data.get("error", "")
        
        if status == 200:
            print(f"{career:30s} | {'OK':6s} | {score:>4}% | {len(missing):>7d} | {len(roadmap):>7d}")
        else:
            print(f"{career:30s} | {'FAIL':6s} | {status:>5} | Error: {error}")
    except requests.exceptions.Timeout:
        print(f"{career:30s} | {'HANG':6s} | Request timed out after 30s")
    except Exception as e:
        print(f"{career:30s} | {'ERR':6s} | {str(e)[:50]}")
