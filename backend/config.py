import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration."""
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/skillgap_db")
    JWT_SECRET = os.getenv("JWT_SECRET", "fallback_secret_key")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin@skillgap.ai")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@123!")
    
    # Model configuration
    AI_MODEL_NAME = "models/gemini-embedding-001"
