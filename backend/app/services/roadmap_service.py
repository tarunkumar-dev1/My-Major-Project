import datetime
import json
import logging
import google.generativeai as genai
from config import Config
from app.database.connection import get_db

class RoadmapService:
    def __init__(self):
        self.db = get_db()
        self.roadmaps_collection = self.db['roadmaps']
        self.ai_enabled = bool(Config.GEMINI_API_KEY)
        if self.ai_enabled:
            # We use gemini-1.5-flash for fast text generation
            self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_roadmap_steps(self, missing_skills, user_skills, career_goal):
        """Generates a structured learning sequence using Gemini LLM."""
        if not self.ai_enabled:
            logging.warning("AI disabled. Falling back to template roadmap.")
            return self._generate_fallback_steps(missing_skills)
            
        if not missing_skills:
            return []

        prompt = f"""
        You are an expert career coach for tech roles.
        A student wants to become a: "{career_goal}".
        They already know: {', '.join(user_skills) if user_skills else 'Nothing yet'}.
        They are missing the following skills to reach their goal: {', '.join(missing_skills)}.

        For each missing skill, create a roadmap consisting of 3 modules (Beginner, Intermediate, Advanced).
        Tailor the description and module titles strictly to the context of the user's career goal ({career_goal}).
        
        Respond ONLY with a JSON array in exactly this schema (do NOT include markdown code blocks ```json like that):
        [
            {{
                "step_number": 1,
                "target_skill": "<missing_skill>",
                "module_title": "Mastering <skill> for <career_goal>",
                "description": "<A thorough, personalized sentence explaining why and how to learn this.>",
                "status": "pending",
                "modules": [
                    {{"level": "Beginner", "title": "<specific module name>", "status": "pending"}},
                    {{"level": "Intermediate", "title": "<specific module name>", "status": "pending"}},
                    {{"level": "Advanced", "title": "<specific module name>", "status": "pending"}}
                ]
            }}
        ]
        """
        
        try:
            response = self.model.generate_content(prompt)
            json_text = response.text.strip()
            # Clean up markdown if the LLM still returns it
            if json_text.startswith("```"):
                json_text = json_text.split("\n", 1)[1]
            if json_text.endswith("```"):
                json_text = json_text.rsplit("\n", 1)[0]
                
            steps = json.loads(json_text.strip())
            
            # Ensure correct numbering
            for i, step in enumerate(steps):
                step['step_number'] = i + 1
                
            return steps
        except Exception as e:
            logging.error(f"LLM roadmap generation failed: {e}. Falling back to template.")
            return self._generate_fallback_steps(missing_skills)

    def _generate_fallback_steps(self, missing_skills):
        steps = []
        for i, skill in enumerate(missing_skills):
            steps.append({
                "step_number": i + 1,
                "target_skill": skill,
                "module_title": f"Master {skill}",
                "description": f"Learn the core fundamentals and advanced applications of {skill}.",
                "status": "pending",
                "modules": [
                    {"level": "Beginner", "title": f"Introduction to {skill}", "status": "pending"},
                    {"level": "Intermediate", "title": f"Intermediate {skill} Patterns", "status": "pending"},
                    {"level": "Advanced", "title": f"Advanced {skill} Building", "status": "pending"}
                ]
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
