"""
Application Configuration Settings.
Loads configuration from environment variables or .env file.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Private Synthetic Data Generator for HR Records"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    SECRET_KEY: str = Field(
        default="hr-privacy-super-secret-production-key-change-in-prod-8f92b7c4d1e0",
        env="SECRET_KEY"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database configuration (PostgreSQL by default, auto-fallback to SQLite for easy local dev)
    DATABASE_URL: str = Field(
        default="sqlite:///./private_synthetic_hr.db",
        env="DATABASE_URL"
    )
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:80",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]
    
    # File Storage
    UPLOAD_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../backend/data/uploads"))
    SYNTHETIC_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../backend/data/synthetic"))
    MAX_UPLOAD_SIZE_MB: int = 25
    ALLOWED_EXTENSIONS: List[str] = [".csv", ".xlsx", ".xls"]
    
    # Differential Privacy Defaults
    DEFAULT_EPSILON: float = 1.0
    DEFAULT_DELTA: float = 1e-5
    MAX_GLOBAL_EPSILON_BUDGET: float = 10.0
    DEFAULT_CLIP_NORM: float = 1.0
    DEFAULT_NOISE_MULTIPLIER: float = 1.1
    
    # Demo and Seed Admin
    FIRST_SUPERUSER_EMAIL: str = "admin@hrprivacy.org"
    FIRST_SUPERUSER_PASSWORD: str = "Admin@123456"
    FIRST_ANALYST_EMAIL: str = "analyst@hrprivacy.org"
    FIRST_ANALYST_PASSWORD: str = "Analyst@123456"
    FIRST_VIEWER_EMAIL: str = "viewer@hrprivacy.org"
    FIRST_VIEWER_PASSWORD: str = "Viewer@123456"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.SYNTHETIC_DIR, exist_ok=True)
