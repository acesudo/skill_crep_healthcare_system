"""Batch CSV operational triage route controller.
"""

import csv
import io
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from src.api.config import Settings
from src.api.dependencies import get_app_settings, get_inference_service
from src.api.schemas import BatchPredictResponse
from src.api.services.inference_service import InferenceService

router = APIRouter(tags=["Batch Triage"])


@router.post(
    "/predict/batch",
    response_model=BatchPredictResponse,
    status_code=status.HTTP_200_OK,
    summary="Batch triage patient messages via CSV upload",
    description=(
        "Accepts a CSV file upload containing patient-support messages, validates columns "
        "and file limits, executes operational triage per row, and returns a structured "
        "summary containing successful, low-confidence, and invalid records."
    ),
    responses={
        200: {
            "description": "Batch processing completed successfully.",
            "model": BatchPredictResponse,
        },
        400: {
            "description": "Invalid file format, empty CSV, or missing required columns.",
        },
        413: {
            "description": "Payload Too Large: File size or row count exceeds configured limit.",
        },
        503: {
            "description": "ML inference engine not ready / models not loaded.",
        },
    },
)
async def predict_batch_messages(
    file: UploadFile = File(..., description="CSV file containing 'message_text' column"),
    inference_service: InferenceService = Depends(get_inference_service),
    settings: Settings = Depends(get_app_settings),
) -> BatchPredictResponse:
    """Ingests, parses, and evaluates a batch of patient inquiries from a CSV file."""
    # 1. File extension validation
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only .csv files are supported.",
        )

    # 2. File size validation (stream reading into memory buffer up to max bytes)
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    content = await file.read()

    if not content or len(content.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded CSV file is empty.",
        )

    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Uploaded file exceeds maximum size of {settings.max_upload_size_mb} MB.",
        )

    # 3. Decode CSV content
    try:
        text_content = content.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text_content = content.decode("latin-1")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to decode CSV file. Ensure valid UTF-8 or ASCII encoding.",
            )

    # 4. Parse CSV records
    f_in = io.StringIO(text_content.strip())
    reader = csv.reader(f_in)
    try:
        raw_headers = next(reader, None)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Malformed CSV header: {str(exc)}",
        )

    if not raw_headers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file contains no headers or data rows.",
        )

    # Normalize header names (lowercase, stripped)
    header_map: Dict[str, int] = {
        col.strip().lower(): idx for idx, col in enumerate(raw_headers)
    }

    if "message_text" not in header_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Required column 'message_text' was not found in CSV headers.",
        )

    text_idx = header_map["message_text"]
    id_idx = header_map.get("message_id")

    records: List[Dict[str, Any]] = []
    row_count = 0

    for row in reader:
        if not row or all(c.strip() == "" for c in row):
            continue  # Skip blank lines

        row_count += 1
        if row_count > settings.max_batch_rows:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"CSV row count exceeds maximum allowed batch limit of {settings.max_batch_rows} rows.",
            )

        msg_text = row[text_idx] if text_idx < len(row) else None
        msg_id = (
            row[id_idx].strip()
            if (id_idx is not None and id_idx < len(row) and row[id_idx].strip())
            else None
        )

        records.append({
            "row_index": row_count,
            "message_text": msg_text,
            "message_id": msg_id,
        })

    if not records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV contains no data rows to process.",
        )

    # 5. Run inference through inference service
    return inference_service.predict_batch(records)
