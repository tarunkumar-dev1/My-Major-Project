"""
Configuration for the SkillGap Flask application.

This module centralizes environment-driven configuration values and
provides safe defaults for local development. Sensitive values should be
provided via environment variables (for example using a `.env` file when
running locally). The `.env` file is loaded automatically below.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file (if present) so local dev is simple.
load_dotenv()


class Config:
    """Application configuration container.

    Attributes are read by Flask via `app.config.from_object(Config)` so names
    should be kept short and descriptive.
    """
    # MongoDB connection string (local default for development)
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/skillgap_db")

    # JWT secret used for signing authentication tokens. Override in production.
    # NOTE: do NOT commit a real secret to source control. Set this in `.env` or
    # your host environment variables (Railway/Vercel/Heroku/etc.).
    JWT_SECRET = os.getenv("JWT_SECRET", "")

    # API key for the Gemini / Generative model integration. Required for LLM features.
    # Keep empty to disable AI features in environments without access.
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    # Admin credentials for the simple admin UI. Provide via environment.
    # Avoid using default credentials in production.
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
    
    # Model configuration (default embedding model name used by the project)
    AI_MODEL_NAME = os.getenv("AI_MODEL_NAME", "models/gemini-embedding-001")
