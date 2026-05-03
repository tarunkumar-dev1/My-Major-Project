import json
import logging
import threading
import requests
from config import Config

AI_ENABLED = bool(Config.GROQ_API_KEY)
GROQ_API_URL = "https://api.groq.com/v1/models/{model}/outputs"


def _strip_json_output(text):
    if not isinstance(text, str):
        return text
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
    if text.endswith("```"):
        text = text.rsplit("\n", 1)[0]
    return text.strip()


def _call_with_timeout(func, timeout=10):
    """Calls a function with a timeout. Returns None if it times out or fails."""
    result = [None]
    error = [None]

    def worker():
        try:
            result[0] = func()
        except Exception as e:
            error[0] = e

    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        logging.warning(f"Groq API call timed out after {timeout}s")
        return None
    if error[0]:
        raise error[0]
    return result[0]


def _call_groq_model(prompt, model_name, timeout_tokens=800):
    url = GROQ_API_URL.format(model=model_name)
    headers = {
        "Authorization": f"Bearer {Config.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "input": prompt,
        "max_output_tokens": timeout_tokens,
        "temperature": 0.2,
    }
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    body = response.json()

    output = body.get("output")
    if isinstance(output, list) and output:
        first_output = output[0]
        content = first_output.get("content")
        if isinstance(content, list) and content:
            for chunk in content:
                if isinstance(chunk, dict) and "text" in chunk:
                    return _strip_json_output(chunk["text"])
                if isinstance(chunk, str):
                    return _strip_json_output(chunk)
    if isinstance(body.get("text"), str):
        return _strip_json_output(body["text"])
    return None


class SimilarityEngine:
    _instance = None
    
    @classmethod
    def get_instance(cls, model_name=Config.AI_MODEL_NAME):
        """Singleton pattern to avoid reloading configuration."""
        if cls._instance is None:
            cls._instance = cls(model_name)
        return cls._instance

    def __init__(self, model_name):
        self.ai_enabled = AI_ENABLED
        self.model_name = model_name
        if self.ai_enabled:
            logging.info(f"Using Groq model: {model_name}")
        else:
            logging.warning("Initializing SimilarityEngine in Fallback Mode (No AI).")

    def calculate_similarity_matrix(self, user_skills, required_skills):
        """
        Takes a list of user skills and a list of required skills.
        Returns a matrix mapping what user skills roughly match what required skills
        using Groq semantic scoring.
        """
        if not self.ai_enabled or not user_skills or not required_skills:
            return []

        prompt = f"""
You are a skill-matching assistant. Compare the student skills and required skills
and return a JSON array of objects with the following keys:
- required_skill
- best_user_match
- similarity_score

Use a similarity_score between 0.0 and 1.0. Use the best matching user skill for each required skill.
Return only valid JSON.

User skills: {json.dumps(user_skills)}
Required skills: {json.dumps(required_skills)}
"""

        try:
            response_text = _call_with_timeout(
                lambda: _call_groq_model(prompt, self.model_name, timeout_tokens=700),
                timeout=20,
            )
            if response_text is None:
                logging.warning("Groq similarity call timed out. Falling back.")
                return []

            similarity_data = json.loads(response_text)
            matches = []
            for item in similarity_data:
                matches.append({
                    "required_skill": item.get("required_skill"),
                    "best_user_match": item.get("best_user_match"),
                    "similarity_score": float(item.get("similarity_score", 0.0)),
                })
            return matches
        except Exception as e:
            logging.error(f"Failed to calculate similarity with Groq API: {e}")
            return []
        
    def bridge_skill_gap(self, user_skills, required_skills, threshold=0.75):
        """
        Determines the exact missing skills by combining exact text overlaps
        and high-confidence AI similarity matches.
        """
        user_skills_lower = [s.lower().strip() for s in user_skills]
        required_skills_lower = [s.lower().strip() for s in required_skills]
        
        # 1. Exact matches
        exact_matches = set(user_skills_lower).intersection(set(required_skills_lower))
        
        # Determine what's left
        remaining_required = [req for req in required_skills if req.lower().strip() not in exact_matches]
        remaining_user = [usr for usr in user_skills if usr.lower().strip() not in exact_matches]
        
        ai_merged_matches = []
        missing_skills = []
        
        # 2. AI Semantic similarity
        if self.ai_enabled and remaining_required and remaining_user:
            similarity_results = self.calculate_similarity_matrix(remaining_user, remaining_required)
            
            for result in similarity_results:
                if result['similarity_score'] >= threshold:
                    ai_merged_matches.append(result['required_skill'])
                else:
                    missing_skills.append(result['required_skill'])
        else:
            missing_skills = remaining_required
            
        covered_skills = list(exact_matches) + ai_merged_matches
        
        total_required = len(required_skills)
        readiness_score = 0
        if total_required > 0:
            readiness_score = int((len(covered_skills) / total_required) * 100)
            
        return {
            "readiness_score": readiness_score,
            "covered_skills": covered_skills,
            "missing_skills": missing_skills,
            "ai_matches": ai_merged_matches
        }
