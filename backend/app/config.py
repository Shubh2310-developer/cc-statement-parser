"""Configuration management for the application."""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "CC Statement Parser"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # API
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173", "https://*.vercel.app"]
    ENVIRONMENT: str = "development"  # development, staging, production

    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".pdf"}
    UPLOAD_DIR: Path = Path("data/uploads")
    PROCESSED_DIR: Path = Path("data/processed")

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///data/db/cc_parser.db"

    # OCR Settings
    OCR_ENABLED: bool = True
    OCR_LANGUAGE: str = "eng"
    OCR_DPI: int = 300
    OCR_TEXT_THRESHOLD: int = 100  # Minimum text length before OCR

    # Extraction
    EXTRACTION_TIMEOUT: int = 60  # seconds
    CONFIDENCE_THRESHOLD: float = 0.7

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_DIR: Path = Path("logs")

    # Security
    MASK_CARD_NUMBERS: bool = True
    ENCRYPT_STORAGE: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Ensure directories exist
def init_directories():
    """Create necessary directories."""
    settings = get_settings()
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
    Path("data/db").mkdir(parents=True, exist_ok=True)
