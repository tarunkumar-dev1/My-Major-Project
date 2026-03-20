import logging

try:
    from sentence_transformers import SentenceTransformer, util
    AI_ENABLED = True
except Exception as e:
    logging.warning(f"SentenceTransformers failed to load. AI semantic matching disabled. Fallback to exact match only. Error: {str(e)}")
    AI_ENABLED = False

class SimilarityEngine:
    _instance = None
    
    @classmethod
    def get_instance(cls, model_name="all-MiniLM-L6-v2"):
        """Singleton pattern to avoid reloading the model into memory multiple times."""
        if cls._instance is None:
            cls._instance = cls(model_name)
        return cls._instance

    def __init__(self, model_name):
        self.ai_enabled = AI_ENABLED
        if self.ai_enabled:
            # This will download the model on the first run, taking ~80MB, and store it in cache.
            logging.info(f"Loading AI Model: {model_name}...")
            self.model = SentenceTransformer(model_name)
            logging.info("AI Model loaded successfully.")
        else:
            logging.warning("Initializing SimilarityEngine in Fallback Mode (No AI).")

    def calculate_similarity_matrix(self, user_skills, required_skills):
        """
        Takes a list of user skills and a list of required skills.
        Returns a matrix mapping what user skills roughly match what required skills.
        """
        if not self.ai_enabled or not user_skills or not required_skills:
            return []

        # Encode both lists into embedding vectors
        user_embeddings = self.model.encode(user_skills, convert_to_tensor=True)
        required_embeddings = self.model.encode(required_skills, convert_to_tensor=True)
        
        # Calculate cosine similarities (returns a matrix of [len(user_skills), len(required_skills)])
        cosine_scores = util.cos_sim(user_embeddings, required_embeddings)
        
        matches = []
        # Find best match for each required skill from the user's skillset
        for i, req_skill in enumerate(required_skills):
            # Get the scores for this required skill against all user skills
            scores = cosine_scores[:, i].tolist()
            best_score_idx = scores.index(max(scores))
            best_score = scores[best_score_idx]
            
            # Map it
            matches.append({
                "required_skill": req_skill,
                "best_user_match": user_skills[best_score_idx],
                "similarity_score": round(best_score, 4)
            })
            
        return matches
        
    def bridge_skill_gap(self, user_skills, required_skills, threshold=0.55):
        """
        Determines the exact missing skills by combining exact text overlaps
        and high-confidence AI similarity matches.
        """
        user_skills_lower = [s.lower().strip() for s in user_skills]
        required_skills_lower = [s.lower().strip() for s in required_skills]
        
        # 1. Exact matches (Fast tracked)
        exact_matches = set(user_skills_lower).intersection(set(required_skills_lower))
        
        # Determine what's left to evaluate
        remaining_required = [req for req in required_skills if req.lower().strip() not in exact_matches]
        remaining_user = [usr for usr in user_skills if usr.lower().strip() not in exact_matches]
        
        ai_merged_matches = []
        missing_skills = []
        
        # 2. AI Semantic similarity for the remaining skills
        if self.ai_enabled and remaining_required and remaining_user:
            similarity_results = self.calculate_similarity_matrix(remaining_user, remaining_required)
            
            for result in similarity_results:
                if result['similarity_score'] >= threshold:
                    ai_merged_matches.append(result['required_skill'])
                else:
                    missing_skills.append(result['required_skill'])
        else:
            # If AI is disabled or user had no remaining skills, everything remaining required is missing
            missing_skills = remaining_required
            
        covered_skills = list(exact_matches) + ai_merged_matches
        
        # 3. Calculate Readiness Percentage
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
