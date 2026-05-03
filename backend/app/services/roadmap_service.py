"""
Roadmap generation and persistence service.

This module interacts with an optional Groq LLM to produce personalized
learning steps for missing skills. When the LLM is unavailable or times out,
it falls back to a deterministic template. Roadmaps are saved per-user in the
`roadmaps` collection.
"""

import datetime
import json
import logging
import threading
import requests
from config import Config
from app.database.connection import get_db


class RoadmapService:
    """Service responsible for creating and storing learning roadmaps.

    If a Groq API key is configured (`Config.GROQ_API_KEY`), this service
    will attempt to use the LLM for tailored roadmap content. Otherwise it
    provides a simple fallback template that is deterministic and quick.
    """

    GROQ_API_URL = "https://api.groq.com/v1/models/{model}/outputs"

    def __init__(self):
        self.db = get_db()
        self.roadmaps_collection = self.db['roadmaps']
        self.ai_enabled = bool(Config.GROQ_API_KEY)
        self.model_name = Config.AI_MODEL_NAME
        if self.ai_enabled:
            self.model_url = self.GROQ_API_URL.format(model=self.model_name)

    def _strip_response_text(self, text):
        if not isinstance(text, str):
            return text
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("\n", 1)[0]
        return text.strip()

    def _call_model(self, prompt, max_output_tokens=1200):
        headers = {
            "Authorization": f"Bearer {Config.GROQ_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "input": prompt,
            "max_output_tokens": max_output_tokens,
            "temperature": 0.2,
        }
        response = requests.post(self.model_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        body = response.json()

        output = body.get("output")
        if isinstance(output, list) and output:
            first = output[0]
            content = first.get("content")
            if isinstance(content, list):
                for chunk in content:
                    if isinstance(chunk, dict) and "text" in chunk:
                        return self._strip_response_text(chunk["text"])
                    if isinstance(chunk, str):
                        return self._strip_response_text(chunk)
        if isinstance(body.get("text"), str):
            return self._strip_response_text(body["text"])
        return None

    def _generate_with_timeout(self, prompt, timeout=20):
        """Call the LLM's generate routine but enforce a wall-clock timeout."""
        result = [None]
        error = [None]

        def worker():
            try:
                result[0] = self._call_model(prompt)
            except Exception as e:
                error[0] = e

        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()
        thread.join(timeout)

        if thread.is_alive():
            logging.warning(f"LLM call timed out after {timeout}s")
            return None
        if error[0]:
            raise error[0]
        return result[0]

    def generate_roadmap_steps(self, missing_skills, user_skills, career_goal):
        """Generate a JSON-serializable list of roadmap steps for the user."""
        if not self.ai_enabled:
            logging.warning("AI disabled. Falling back to template roadmap.")
            return self._generate_fallback_steps(missing_skills)

        if not missing_skills:
            return []

        prompt = f"""
You are an expert career coach for technical learners.
A student wants to become a: "{career_goal}".
They already know: {', '.join(user_skills) if user_skills else 'Nothing yet'}.
They are missing the following skills to reach their goal: {', '.join(missing_skills)}.

For each missing skill, create a roadmap consisting of 3 modules (Beginner, Intermediate, Advanced).
Tailor the description and module titles strictly to the user's career goal.

Respond ONLY with a JSON array in exactly this schema (do NOT include markdown code fences):
[
    {{
        "step_number": 1,
        "target_skill": "<missing_skill>",
        "module_title": "Mastering <skill> for <career_goal>",
        "description": "<A thorough, personalized sentence explaining why and how to learn this.>",
        "status": "pending",
        "modules": [
            {{"level": "Beginner", "title": "<specific module name>", "status": "pending", "youtube_search_url": "https://www.youtube.com/results?search_query=<specific module name>+tutorial"}},
            {{"level": "Intermediate", "title": "<specific module name>", "status": "pending", "youtube_search_url": "https://www.youtube.com/results?search_query=<specific module name>+tutorial"}},
            {{"level": "Advanced", "title": "<specific module name>", "status": "pending", "youtube_search_url": "https://www.youtube.com/results?search_query=<specific module name>+tutorial"}}
        ]
    }}
]
"""

        try:
            response_text = self._generate_with_timeout(prompt, timeout=20)
            if response_text is None:
                logging.warning("LLM call timed out. Falling back to template.")
                return self._generate_fallback_steps(missing_skills)

            steps = json.loads(response_text)
            for i, step in enumerate(steps):
                step['step_number'] = i + 1
            return steps
        except Exception as e:
            logging.error(f"LLM roadmap generation failed: {e}. Falling back to template.")
            return self._generate_fallback_steps(missing_skills)

    def _generate_fallback_steps(self, missing_skills):
        """Create a deterministic fallback roadmap when AI is unavailable."""
        steps = []
        for i, skill in enumerate(missing_skills):
            steps.append({
                "step_number": i + 1,
                "target_skill": skill,
                "module_title": f"Master {skill}",
                "description": f"Learn the core fundamentals and advanced applications of {skill}.",
                "status": "pending",
                "modules": [
                    {"level": "Beginner", "title": f"Introduction to {skill}", "status": "pending", "youtube_search_url": f"https://www.youtube.com/results?search_query={skill}+beginner+tutorial"},
                    {"level": "Intermediate", "title": f"Intermediate {skill} Patterns", "status": "pending", "youtube_search_url": f"https://www.youtube.com/results?search_query={skill}+intermediate+tutorial"},
                    {"level": "Advanced", "title": f"Advanced {skill} Building", "status": "pending", "youtube_search_url": f"https://www.youtube.com/results?search_query={skill}+advanced+tutorial"}
                ]
            })
        return steps

    def save_user_roadmap(self, user_id, missing_skills, generated_steps):
        """Persist or update the user's roadmap document in MongoDB.

        The method stores a timestamp in `updated_at` to help clients show when
        the roadmap was last refreshed.
        """
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
        """Retrieve the roadmap for `user_id`, omitting the internal `_id` field."""
        return self.roadmaps_collection.find_one({"user_id": user_id}, {"_id": 0})
