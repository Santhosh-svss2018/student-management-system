"""
Core Configuration Module
Loads environment variables using python-dotenv.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


# Locate and load the backend .env file
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_file = BASE_DIR / ".env"

if env_file.exists():
    load_dotenv(dotenv_path=env_file)
else:
    load_dotenv()


class Settings:
    """Application runtime settings loaded from environment variables."""
    PROJECT_NAME: str = "EduManage API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    # MongoDB Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "edumanage")

    # Timeout settings for connection resilience
    MONGODB_SERVER_TIMEOUT_MS: int = int(os.getenv("MONGODB_SERVER_TIMEOUT_MS", "2000"))

    # JWT Authentication Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "edumanage-super-secret-jwt-key-for-development-only-2026")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # CORS Configuration
    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"
    )

    # AI Assistant & Gemini Configuration
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "fallback")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", os.getenv("AI_API_KEY", None))
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", os.getenv("AI_MODEL", "gemini-2.5-flash-lite"))
    AI_API_KEY: Optional[str] = os.getenv("AI_API_KEY", None)
    AI_MODEL: str = os.getenv("AI_MODEL", "gemini-2.5-flash-lite")


settings = Settings()


