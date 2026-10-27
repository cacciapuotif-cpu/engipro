"""
Application configuration management.
"""
from pydantic_settings import BaseSettings
from typing import Optional
import sys


_INSECURE_DEFAULT_KEY = "your-secret-key-change-in-production"


class Settings(BaseSettings):
    """Application settings."""

    # Project
    PROJECT_NAME: str = "EngiPro"
    PROJECT_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Environment
    ENV: str = "development"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://engipro:engipro123@localhost:5432/engipro"
    SQLALCHEMY_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # MinIO
    MINIO_URL: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_BUCKET: str = "engipro"
    MINIO_SECURE: bool = False

    # JWT
    SECRET_KEY: str = _INSECURE_DEFAULT_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8   # 8 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Security
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_MAX_LENGTH: int = 128

    # CORS — override with comma-separated domains in production
    # e.g. CORS_ORIGINS=["https://app.example.com","https://admin.example.com"]
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:3001", "http://localhost"]

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 5000
    RATE_LIMIT_PERIOD_SECONDS: int = 3600

    # File Upload
    MAX_UPLOAD_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB

    # 2FA (optional)
    TWO_FACTOR_ENABLED: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Refuse to start in production with the default insecure key
if settings.ENV == "production" and settings.SECRET_KEY == _INSECURE_DEFAULT_KEY:
    print(
        "FATAL: SECRET_KEY is set to the insecure default value. "
        "Set a strong SECRET_KEY environment variable before starting in production.",
        file=sys.stderr,
    )
    sys.exit(1)
