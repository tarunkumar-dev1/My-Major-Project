import requests
import json

def test():
    try:
        # 1. Login
        print("Logging in...")
        login_res = requests.post("http://localhost:5000/api/auth/login", json={"email": "ultimate@example.com", "password": "password123"})
        if login_res.status_code != 200:
            print("Login failed:", login_res.text)
            return
            
        token = login_res.json().get("token")
        
        # 2. Submit skills
        print("Submitting skills...")
        res = requests.post("http://localhost:5000/api/student/submit-skills", 
            json={"skills": ["Python", "Java"], "career_goal": "Machine Learning Engineer"},
            headers={"Authorization": f"Bearer {token}"}
        )
        print("Analysis response:", res.status_code)
        
        # 3. Get roadmap
        print("Fetching roadmap...")
        road_res = requests.get("http://localhost:5000/api/student/roadmap", headers={"Authorization": f"Bearer {token}"})
        print("Roadmap response:", road_res.status_code)
        
        roadmap_data = road_res.json()
        print("Steps generated:")
        if "roadmap" in roadmap_data and "generated_steps" in roadmap_data["roadmap"]:
            for step in roadmap_data["roadmap"]["generated_steps"]:
                print(f" - {step.get('target_skill')}: {step.get('module_title')} (Modules: {len(step.get('modules', []))})")
        else:
            print(roadmap_data)
            
        print("\nTest Finished Successfully.")
    except Exception as e:
        print("Test Error:", e)

if __name__ == "__main__":
    test()
