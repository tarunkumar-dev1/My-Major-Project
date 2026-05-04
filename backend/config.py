"""
Configuration for the SkillGap Flask application.

This module centralizes environment-driven configuration values and
supports local development via a `.env` file loaded with python-dotenv.
Sensitive values should be provided through environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load local environment variables from backend/.env when present.
# Resolve the path explicitly so the app works even when launched from the
# repository root instead of the backend directory.
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")


class Config:
    """Application configuration container used by Flask."""

    # MongoDB connection string (development-friendly default)
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/skillgap_db")

    # JWT secret used to sign authentication tokens.
    JWT_SECRET = os.getenv("JWT_SECRET", "")

    # API key for Groq integrations.
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

    # Frontend origin(s) for CORS. Use comma-separated values or "*".
    FRONTEND_ORIGINS = os.getenv("FRONTEND_ORIGINS", "*")

    # Admin credentials for admin portal login.
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

    # Name or identifier for the AI model selection.
    AI_MODEL_NAME = os.getenv("AI_MODEL_NAME", "llama-3.3-70b-versatile")
