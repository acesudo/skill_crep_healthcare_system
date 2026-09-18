"""Health, readiness, and model information route handlers.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from src.api.dependencies import get_inference_service
from src.api.schemas import HealthResponse, ModelInfoResponse, ReadyResponse
from src.api.services.inference_service import InferenceService

router = APIRouter(tags=["Health & System"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness check",
    description="Returns service liveness status. Indicates the web process is running.",
)
async def get_health() -> HealthResponse:
    """Liveness probe."""
    return HealthResponse(status="ok")


@router.get(
    "/ready",
    response_model=ReadyResponse,
    summary="Readiness check",
    description="Verifies that all required ML artifacts are loaded and ready to serve inference.",
)
async def get_readiness(
    request: Request,
) -> ReadyResponse:
    """Readiness probe checking ML models in application state."""
    inference_service: InferenceService = getattr(request.app.state, "inference_service", None)
    if inference_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML inference engine is not ready. Model artifacts are not loaded.",
        )

    model_version = str(inference_service.metadata.get("model_version", "v1.0.0"))
    dataset_version = str(inference_service.metadata.get("dataset_version", "v1.0.0"))

    return ReadyResponse(
        status="ready",
        model_version=model_version,
        dataset_version=dataset_version,
    )


@router.get(
    "/model-info",
    response_model=ModelInfoResponse,
    summary="Model metadata descriptor",
    description="Returns public non-sensitive configuration parameters for the active ML model.",
)
async def get_model_info(
    inference_service: InferenceService = Depends(get_inference_service),
) -> ModelInfoResponse:
    """Returns safe metadata about the deployed model version and labels."""
    return inference_service.get_model_info()
