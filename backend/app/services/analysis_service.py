"""
Services for analyzing student skills and producing personalized roadmaps.

This module provides `AnalysisService` which coordinates database lookups,
AI-powered similarity matching, scoring, and roadmap generation. It acts as
the high-level orchestration layer used by routes when a student submits
their skills and career goal.
"""

from app.database.connection import get_db
from app.ai_module.similarity import SimilarityEngine
from app.services.roadmap_service import RoadmapService


def _normalize_field_name(value):
    """Normalize career field labels to a comparison-safe string.

    Normalization includes replacing dashes/underscores with spaces, lowercasing,
    and collapsing repeated whitespace. This helps match user-provided career
    goals like "data-scientist" with stored values like "Data Scientist".
    """
    return " ".join((value or "").replace("-", " ").replace("_", " ").lower().split())


class AnalysisService:
    """High-level service that performs skill analysis for students.

    Responsibilities:
    - Resolve a career record from the database
    - Use `SimilarityEngine` to compute missing/covered skills and readiness
    - Generate a step-by-step learning roadmap via `RoadmapService`
    - Persist results to the user record and return a structured response
    """

    def __init__(self):
        self.db = get_db()
        self.users_collection = self.db['users']
        self.careers_collection = self.db['careers']
        # Acquire a shared AI similarity engine instance for embeddings/matching
        self.ai_engine = SimilarityEngine.get_instance()
        self.roadmap_service = RoadmapService()

    def _resolve_career(self, career_goal):
        """Resolve a career by exact or normalized comparison.

        The method first attempts a fast exact match (case-sensitive). If that
        fails it tries a normalized comparison to tolerate common user input
        variations (hyphens, underscores, differing case).
        Returns the career document or `None` if no match is found.
        """
        normalized_goal = _normalize_field_name(career_goal)
        careers = list(self.careers_collection.find({}, {"_id": 0}))

        # Fast exact match first.
        for career in careers:
            if career.get("career_name") == career_goal:
                return career

        # Fallback normalized match for flexible user input handling.
        for career in careers:
            if _normalize_field_name(career.get("career_name", "")) == normalized_goal:
                return career

        return None

    def analyze_student_skills(self, user_id, submitted_skills, career_goal):
        """Main entrypoint for analyzing a student's skillset.

        Steps performed:
        1. Resolve the requested `career_goal` from the careers collection.
        2. Use `SimilarityEngine` to compute covered and missing skills and a
           readiness score.
        3. Generate and persist a learning roadmap for the user.
        4. Update the user's document with skills and readiness score.

        Returns a tuple `(response_dict, http_status_code)` suitable for
        returning from Flask routes.
        """
        from bson.objectid import ObjectId

        # 1. Look up career and bail out with helpful suggestions if missing
        career = self._resolve_career(career_goal)
        if not career:
            available_fields = [c.get("career_name") for c in self.careers_collection.find({}, {"career_name": 1, "_id": 0})]
            return {
                "error": f"Career goal '{career_goal}' not found in database",
                "available_careers": available_fields
            }, 404

        resolved_career_name = career.get("career_name", career_goal)

        required_skills = career.get("required_skills", [])

        # 2. Use AI Engine to bridge gap between user skills and required skills
        analysis_result = self.ai_engine.bridge_skill_gap(
            user_skills=submitted_skills,
            required_skills=required_skills
        )

        missing_skills = analysis_result["missing_skills"]
        readiness_score = analysis_result["readiness_score"]

        # 3. Generate Roadmap steps (LLM-powered when available)
        roadmap_steps = self.roadmap_service.generate_roadmap_steps(
            missing_skills=missing_skills,
            user_skills=submitted_skills,
            career_goal=resolved_career_name
        )
        # Persist the user's roadmap document
        roadmap = self.roadmap_service.save_user_roadmap(
            user_id=str(user_id),
            missing_skills=missing_skills,
            generated_steps=roadmap_steps
        )

        # 4. Update User record with analysis results for quick access in UI
        self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "skills": submitted_skills,
                "career_goal": resolved_career_name,
                "readiness_score": readiness_score
            }}
        )

        # Return a concise payload the frontend can consume immediately
        return {
            "message": "Analysis completed successfully",
            "career_goal": resolved_career_name,
            "readiness_score": readiness_score,
            "covered_skills": analysis_result["covered_skills"],
            "missing_skills": missing_skills,
            "ai_detected_matches": analysis_result["ai_matches"],
            "roadmap": roadmap_steps
        }, 200
