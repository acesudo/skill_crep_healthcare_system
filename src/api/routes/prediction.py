"""Single message operational triage route controller.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from src.api.dependencies import get_inference_service
from src.api.schemas import PredictRequest, PredictResponse
from src.api.services.inference_service import InferenceService

router = APIRouter(tags=["Triage Inference"])


@router.post(
    "/predict",
    response_model=PredictResponse,
    status_code=status.HTTP_200_OK,
    summary="Triage a single patient message",
    description=(
        "Processes an incoming patient-support message, classifies operational category "
        "and urgency, calculates conservative bottleneck confidence, evaluates the operational "
        "threshold tau (0.70), assigns the destination queue or human review queue, and attaches "
        "linear feature explanations."
    ),
    responses={
        200: {
            "description": "Successful classification or low-confidence escalation result.",
            "model": PredictResponse,
        },
        422: {
            "description": "Validation Error (e.g. empty message_text or exceeds max length).",
        },
        503: {
            "description": "ML inference engine not ready / models not loaded.",
        },
    },
)
async def predict_single_message(
    payload: PredictRequest,
    inference_service: InferenceService = Depends(get_inference_service),
) -> PredictResponse:
    """Classifies a single patient inquiry."""
    try:
        return inference_service.predict_single(
            message_text=payload.message_text,
            message_id=payload.message_id,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference execution failure: {str(exc)}",
        )
