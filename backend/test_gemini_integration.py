import unittest
from unittest.mock import patch, MagicMock
import json
from app.ai_module.similarity import SimilarityEngine
from app.services.roadmap_service import RoadmapService
from config import Config

class TestGeminiIntegration(unittest.TestCase):

    @patch('app.ai_module.similarity.genai')
    def test_similarity_engine_mocked_gemini(self, mock_genai):
        """"Test that the SimilarityEngine correctly parses Gemini Embeddings and computes cosine similarity."""
        # Force AI Enabled for test
        engine = SimilarityEngine(model_name="test-model")
        engine.ai_enabled = True
        
        # Mock responses
        mock_genai.embed_content.side_effect = [
            {"embedding": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]}, # User skills: Python, Java
            {"embedding": [[1.0, 0.1, 0.0], [0.1, 1.0, 0.0]]}  # Req skills: Machine Learning, Backend
        ]
        
        user_skills = ["Python", "Java"]
        req_skills = ["Machine Learning", "Backend"]
        
        matches = engine.calculate_similarity_matrix(user_skills, req_skills)
        
        # We expect 2 matches
        self.assertEqual(len(matches), 2)
        # Python [1,0,0] matches Machine Learning [1,0.1,0] best
        self.assertEqual(matches[0]["required_skill"], "Machine Learning")
        self.assertEqual(matches[0]["best_user_match"], "Python")
        
        # Java [0,1,0] matches Backend [0.1, 1, 0] best
        self.assertEqual(matches[1]["required_skill"], "Backend")
        self.assertEqual(matches[1]["best_user_match"], "Java")

    @patch('app.services.roadmap_service.get_db')
    @patch('app.services.roadmap_service.genai')
    def test_roadmap_service_mocked_gemini(self, mock_genai, mock_get_db):
        """Test that RoadmapService correctly parses Gemini text generation JSON."""
        # Set up a mock generative model
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_get_db.return_value = MagicMock()
        
        # Mock LLM returning a valid JSON string wrapped in markdown
        mock_json = '''```json
        [
            {
                "step_number": 1,
                "target_skill": "TensorFlow",
                "module_title": "Mastering TensorFlow for ML Engineer",
                "description": "Learn deep learning.",
                "status": "pending",
                "modules": [
                    {"level": "Beginner", "title": "Intro to Tensors", "status": "pending"},
                    {"level": "Intermediate", "title": "CNNs", "status": "pending"},
                    {"level": "Advanced", "title": "Deployment", "status": "pending"}
                ]
            }
        ]
        ```'''
        mock_response.text = mock_json
        mock_model.generate_content.return_value = mock_response
        
        mock_genai.GenerativeModel.return_value = mock_model
        
        service = RoadmapService()
        service.ai_enabled = True
        service.model = mock_model
        
        steps = service.generate_roadmap_steps(
            missing_skills=["TensorFlow"],
            user_skills=["Python"],
            career_goal="ML Engineer"
        )
        
        self.assertEqual(len(steps), 1)
        self.assertEqual(steps[0]["target_skill"], "TensorFlow")
        self.assertEqual(len(steps[0]["modules"]), 3)
        self.assertEqual(steps[0]["modules"][0]["title"], "Intro to Tensors")

if __name__ == '__main__':
    unittest.main()
