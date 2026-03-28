import logging
import google.generativeai as genai
from config import Config

# Initialize Gemini API
if Config.GEMINI_API_KEY:
    genai.configure(api_key=Config.GEMINI_API_KEY)
    AI_ENABLED = True
else:
    logging.warning("GEMINI_API_KEY is not set. AI clustering will be disabled.")
    AI_ENABLED = False

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
            logging.info(f"Using Gemini Embeddings Model: {model_name}")
        else:
            logging.warning("Initializing SimilarityEngine in Fallback Mode (No AI).")

    def _cosine_similarity(self, v1, v2):
        """Calculates cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(v1, v2))
        magnitude1 = sum(a * a for a in v1) ** 0.5
        magnitude2 = sum(b * b for b in v2) ** 0.5
        if magnitude1 == 0 or magnitude2 == 0:
            return 0
        return dot_product / (magnitude1 * magnitude2)

    def calculate_similarity_matrix(self, user_skills, required_skills):
        """
        Takes a list of user skills and a list of required skills.
        Returns a matrix mapping what user skills roughly match what required skills
        using Gemini Embeddings.
        """
        if not self.ai_enabled or not user_skills or not required_skills:
            return []

        try:
            # Generate embeddings
            user_response = genai.embed_content(
                model=self.model_name,
                content=user_skills,
                task_type="SEMANTIC_SIMILARITY"
            )
            req_response = genai.embed_content(
                model=self.model_name,
                content=required_skills,
                task_type="SEMANTIC_SIMILARITY"
            )
            
            user_embeddings = user_response['embedding']
            req_embeddings = req_response['embedding']
            
            matches = []
            for i, req_skill in enumerate(required_skills):
                best_score = -1
                best_idx = -1
                
                # Compare against all user skills
                for j, user_skill in enumerate(user_skills):
                    score = self._cosine_similarity(user_embeddings[j], req_embeddings[i])
                    if score > best_score:
                        best_score = score
                        best_idx = j
                
                matches.append({
                    "required_skill": req_skill,
                    "best_user_match": user_skills[best_idx],
                    "similarity_score": round(best_score, 4)
                })
                
            return matches
        except Exception as e:
            logging.error(f"Failed to calculate similarity with Gemini API: {e}")
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
