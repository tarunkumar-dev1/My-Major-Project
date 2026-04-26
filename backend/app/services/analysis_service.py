from app.database.connection import get_db
from app.ai_module.similarity import SimilarityEngine
from app.services.roadmap_service import RoadmapService


def _normalize_field_name(value):
    """Normalize career field labels to a comparison-safe string."""
    return " ".join((value or "").replace("-", " ").replace("_", " ").lower().split())

class AnalysisService:
    def __init__(self):
        self.db = get_db()
        self.users_collection = self.db['users']
        self.careers_collection = self.db['careers']
        self.ai_engine = SimilarityEngine.get_instance()
        self.roadmap_service = RoadmapService()

    def _resolve_career(self, career_goal):
        """
        Resolve a career by exact or normalized comparison.
        Handles values like "data-scientist", "Data Scientist", and casing differences.
        """
        normalized_goal = _normalize_field_name(career_goal)
        careers = list(self.careers_collection.find({}, {"_id": 0}))

        # Fast exact match first.
        for career in careers:
            if career.get("career_name") == career_goal:
                return career

        # Fallback normalized match.
        for career in careers:
            if _normalize_field_name(career.get("career_name", "")) == normalized_goal:
                return career

        return None

    def analyze_student_skills(self, user_id, submitted_skills, career_goal):
        """
        Core logic to analyze skills:
        1. Fetch career
        2. Bridge gap using AI
        3. Save metrics & generate roadmap
        """
        from bson.objectid import ObjectId
        
        # 1. Look up career
        career = self._resolve_career(career_goal)
        if not career:
            available_fields = [c.get("career_name") for c in self.careers_collection.find({}, {"career_name": 1, "_id": 0})]
            return {
                "error": f"Career goal '{career_goal}' not found in database",
                "available_careers": available_fields
            }, 404

        resolved_career_name = career.get("career_name", career_goal)
            
        required_skills = career.get("required_skills", [])
        
        # 2. Use AI Engine to bridge gap
        analysis_result = self.ai_engine.bridge_skill_gap(
            user_skills=submitted_skills,
            required_skills=required_skills
        )
        
        missing_skills = analysis_result["missing_skills"]
        readiness_score = analysis_result["readiness_score"]
        
        # 3. Generate Roadmap
        roadmap_steps = self.roadmap_service.generate_roadmap_steps(
            missing_skills=missing_skills,
            user_skills=submitted_skills,
            career_goal=resolved_career_name
        )
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
                "career_goal": resolved_career_name,
                "readiness_score": readiness_score
            }}
        )
        
        return {
            "message": "Analysis completed successfully",
            "career_goal": resolved_career_name,
            "readiness_score": readiness_score,
            "covered_skills": analysis_result["covered_skills"],
            "missing_skills": missing_skills,
            "ai_detected_matches": analysis_result["ai_matches"],
            "roadmap": roadmap_steps
        }, 200
