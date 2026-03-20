from app.database.connection import get_db
from app.ai_module.similarity import SimilarityEngine
from app.services.roadmap_service import RoadmapService

class AnalysisService:
    def __init__(self):
        self.db = get_db()
        self.users_collection = self.db['users']
        self.careers_collection = self.db['careers']
        self.ai_engine = SimilarityEngine.get_instance()
        self.roadmap_service = RoadmapService()

    def analyze_student_skills(self, user_id, submitted_skills, career_goal):
        """
        Core logic to analyze skills:
        1. Fetch career
        2. Bridge gap using AI
        3. Save metrics & generate roadmap
        """
        from bson.objectid import ObjectId
        
        # 1. Look up career
        career = self.careers_collection.find_one({"career_name": career_goal})
        if not career:
            return {"error": f"Career goal '{career_goal}' not found in database"}, 404
            
        required_skills = career.get("required_skills", [])
        
        # 2. Use AI Engine to bridge gap
        analysis_result = self.ai_engine.bridge_skill_gap(
            user_skills=submitted_skills,
            required_skills=required_skills
        )
        
        missing_skills = analysis_result["missing_skills"]
        readiness_score = analysis_result["readiness_score"]
        
        # 3. Generate Roadmap
        roadmap_steps = self.roadmap_service.generate_roadmap_steps(missing_skills)
        roadmap = self.roadmap_service.save_user_roadmap(
            user_id=str(user_id),
            missing_skills=missing_skills,
            generated_steps=roadmap_steps
        )
        
        # 4. Update User record
        self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "skills": submitted_skills,
                "career_goal": career_goal,
                "readiness_score": readiness_score
            }}
        )
        
        return {
            "message": "Analysis completed successfully",
            "career_goal": career_goal,
            "readiness_score": readiness_score,
            "covered_skills": analysis_result["covered_skills"],
            "missing_skills": missing_skills,
            "ai_detected_matches": analysis_result["ai_matches"],
            "roadmap": roadmap_steps
        }, 200
