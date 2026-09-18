"""Application configuration management using environment variables.
"""

import os
from functools import lru_cache
from typing import List
from pydantic import BaseModel, Field


def _get_cors_origins() -> List[str]:
    """Resolves allowed CORS origins from FRONTEND_ORIGIN, CORS_ALLOWED_ORIGINS, or defaults."""
    default_origins = [
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    origins = set(default_origins)

    # 1. Check comma-separated CORS_ALLOWED_ORIGINS
    env_cors = os.getenv("CORS_ALLOWED_ORIGINS", "")
    if env_cors.strip():
        for o in env_cors.split(","):
            if o.strip():
                origins.add(o.strip())

    # 2. Check individual or comma-separated FRONTEND_ORIGIN (e.g. Render / Streamlit Cloud URL)
    frontend_origin = os.getenv("FRONTEND_ORIGIN", "")
    if frontend_origin.strip():
        for o in frontend_origin.split(","):
            if o.strip():
                origins.add(o.strip())

    return list(origins)


class Settings(BaseModel):
    """Immutable application settings for FastAPI backend."""

    app_name: str = Field(default="Patient Message Triage API")
    app_env: str = Field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    api_version: str = Field(default="v1")
    model_version: str = Field(default_factory=lambda: os.getenv("MODEL_VERSION", "v1.0.0"))
    model_base_path: str = Field(default_factory=lambda: os.getenv("MODEL_BASE_PATH", "models"))
    confidence_threshold: float = Field(
        default_factory=lambda: float(os.getenv("CONFIDENCE_THRESHOLD", "0.70"))
    )
    max_message_length: int = Field(
        default_factory=lambda: int(os.getenv("MAX_MESSAGE_LENGTH", "4000"))
    )
    max_batch_rows: int = Field(
        default_factory=lambda: int(os.getenv("MAX_BATCH_ROWS", "1000"))
    )
    max_upload_size_mb: int = Field(
        default_factory=lambda: int(os.getenv("MAX_UPLOAD_SIZE_MB", "5"))
    )
    cors_allowed_origins: List[str] = Field(default_factory=_get_cors_origins)


@lru_cache()
def get_settings() -> Settings:
    """Returns cached singleton application settings."""
    return Settings()