"""
Configuration for the SkillGap application.

This module centralizes environment-driven configuration values so the
application can be configured via a `.env` file or environment variables in
different deployment environments (development, staging, production).
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file into `os.environ` when present.
load_dotenv()


class Config:
    """Application configuration container.

    Attributes exposed here are consumed by Flask's `app.config.from_object()`
    call. Values default to sensible development-friendly fallbacks but should
    be overridden in production via environment variables.
    """

    # Connection string to MongoDB. Expected format: mongodb://host:port/db
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/skillgap_db")

    # Secret used to sign JWT tokens. Replace with a secure random value in prod.
    JWT_SECRET = os.getenv("JWT_SECRET", "fallback_secret_key")

    # API key for the Gemini (or other AI) service. Keep secret in production.
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    # Optional frontend origin(s) for direct browser access to the backend.
    # Comma-separated list such as "https://myapp.vercel.app,https://www.myapp.com".
    FRONTEND_ORIGINS = os.getenv("FRONTEND_ORIGINS", "*")

    # Default admin credentials used for initial seeding/local development.
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin@skillgap.ai")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@123!")
    
    # Name or identifier for the AI model to use for embeddings / analysis.
    # For local development this may be a mock or offline model name.
    AI_MODEL_NAME = "models/gemini-embedding-001"
