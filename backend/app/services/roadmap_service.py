import datetime
from app.database.connection import get_db

class RoadmapService:
    def __init__(self):
        self.db = get_db()
        self.roadmaps_collection = self.db['roadmaps']

    def generate_roadmap_steps(self, missing_skills):
        """Generates a structured learning sequence for missing skills."""
        steps = []
        for i, skill in enumerate(missing_skills):
            steps.append({
                "step_number": i + 1,
                "title": f"Master {skill}",
                "description": f"Learn the core fundamentals and advanced applications of {skill}.",
                "modules": [
                    {"level": "Beginner", "title": f"Introduction to {skill}", "status": "pending"},
                    {"level": "Intermediate", "title": f"Intermediate {skill} Patterns", "status": "pending"},
                    {"level": "Advanced", "title": f"Advanced {skill} Building", "status": "pending"}
                ],
                "status": "pending"
            })
        return steps

    def save_user_roadmap(self, user_id, missing_skills, generated_steps):
        """Saves or updates the user's roadmap in the database."""
        roadmap_doc = {
            "user_id": user_id,
            "missing_skills": missing_skills,
            "generated_steps": generated_steps,
            "updated_at": datetime.datetime.utcnow()
        }
        
        self.roadmaps_collection.update_one(
            {"user_id": user_id},
            {"$set": roadmap_doc},
            upsert=True
        )
        return roadmap_doc

    def get_user_roadmap(self, user_id):
        """Retrieves a user's current roadmap."""
        return self.roadmaps_collection.find_one({"user_id": user_id}, {"_id": 0})
