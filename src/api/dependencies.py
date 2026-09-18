"""FastAPI dependency injection providers for application state and services.
"""

from fastapi import HTTPException, Request, status
from src.api.config import Settings, get_settings
from src.api.services.inference_service import InferenceService


def get_app_settings() -> Settings:
    """Returns application configuration settings."""
    return get_settings()


def get_inference_service(request: Request) -> InferenceService:
    """Dependency retrieving the loaded singleton InferenceService from application state.
    Raises 503 Service Unavailable if models failed to load.
    """
    service: InferenceService = getattr(request.app.state, "inference_service", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML inference engine is not ready. Models are not loaded.",
        )
    return service
