"""Pydantic v2 schemas and data transfer models for the Patient Message Triage API.
Enforces strict healthcare triage API contracts, input validation, and output bounds.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CategoryEnum(str, Enum):
    """6 mutually exclusive operational inquiry categories."""

    APPOINTMENT = "Appointment"
    BILLING = "Billing"
    MEDICATION_REFILL = "Medication Refill"
    REPORT_REQUEST = "Report Request"
    TECHNICAL_ISSUE = "Technical Issue"
    URGENT_REVIEW = "Urgent Review"


class UrgencyEnum(str, Enum):
    """Binary operational prioritization levels."""

    ROUTINE = "Routine"
    URGENT = "Urgent"


class StatusEnum(str, Enum):
    """Standardized lifecycle and processing status indicators."""

    SUCCESS = "SUCCESS"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    INVALID_INPUT = "INVALID_INPUT"
    PROCESSING_FAILURE = "PROCESSING_FAILURE"


class FeatureContribution(BaseModel):
    """Individual linear feature attribution token and contribution weight."""

    model_config = ConfigDict(extra="forbid")

    feature: str = Field(description="Token or n-gram feature driving prediction")
    contribution: float = Field(description="Positive linear contribution weight")


class ExplanationModel(BaseModel):
    """Direct sparse linear feature explanations for category and urgency."""

    model_config = ConfigDict(extra="forbid")

    category_features: List[FeatureContribution] = Field(
        default_factory=list,
        description="Top contributing features for predicted operational category",
    )
    urgency_features: List[FeatureContribution] = Field(
        default_factory=list,
        description="Top contributing features for predicted operational urgency",
    )


class PredictRequest(BaseModel):
    """Incoming single patient message triage request."""

    model_config = ConfigDict(extra="forbid")

    message_text: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="Unstructured patient-support message text",
        examples=["I need to reschedule my Friday appointment with Dr. Smith to next week."],
    )
    message_id: Optional[str] = Field(
        default=None,
        description="Optional client-provided message identifier for correlation",
        examples=["MSG-100402"],
    )

    @field_validator("message_text")
    @classmethod
    def validate_message_text(cls, v: str) -> str:
        """Reject empty or whitespace-only strings."""
        if not v or not v.strip():
            raise ValueError("message_text cannot be empty or solely whitespace.")
        return v.strip()


class PredictResponse(BaseModel):
    """Structured response payload for operational patient message triage."""

    model_config = ConfigDict(extra="forbid")

    message_id: str = Field(description="Message correlation identifier")
    predicted_category: CategoryEnum = Field(description="Assigned operational topic category")
    predicted_urgency: UrgencyEnum = Field(description="Operational turnaround prioritization")
    category_confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Posterior probability for top predicted category",
    )
    urgency_confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Posterior probability for predicted urgency class",
    )
    overall_confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Joint conservative bottleneck confidence: min(C_cat, C_urg)",
    )
    assigned_queue: str = Field(description="Destination operational queue or Human Review Queue")
    requires_human_review: bool = Field(
        description="True if overall_confidence < tau (0.70) or flagged for review"
    )
    status: StatusEnum = Field(description="Operational processing status")
    explanation: ExplanationModel = Field(description="Top linear feature attributions")


class BatchRecordItem(BaseModel):
    """Individual record result within a batch triage evaluation."""

    model_config = ConfigDict(extra="forbid")

    row_index: int = Field(description="1-indexed CSV line number")
    message_id: str = Field(description="Message identifier")
    status: StatusEnum = Field(description="Record processing status")
    predicted_category: Optional[CategoryEnum] = Field(
        default=None, description="Predicted category if successfully processed"
    )
    predicted_urgency: Optional[UrgencyEnum] = Field(
        default=None, description="Predicted urgency if successfully processed"
    )
    category_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    urgency_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    overall_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    assigned_queue: Optional[str] = Field(default=None)
    requires_human_review: Optional[bool] = Field(default=None)
    explanation: Optional[ExplanationModel] = Field(default=None)
    error_detail: Optional[str] = Field(
        default=None, description="Detailed explanation if row failed validation"
    )


class BatchPredictResponse(BaseModel):
    """Batch CSV triage processing summary and individual record results."""

    model_config = ConfigDict(extra="forbid")

    total_records: int = Field(description="Total rows processed from CSV")
    successful_records: int = Field(description="Count of auto-routed high-confidence records")
    low_confidence_records: int = Field(
        description="Count of valid records requiring human review (confidence < tau)"
    )
    invalid_records: int = Field(description="Count of malformed or unprocessable rows")
    results: List[BatchRecordItem] = Field(description="List of individual row evaluation items")


class HealthResponse(BaseModel):
    """Liveness probe health check response."""

    model_config = ConfigDict(extra="forbid")

    status: str = Field(default="ok", description="Service liveness state")


class ReadyResponse(BaseModel):
    """Readiness probe verifying ML model artifact availability."""

    model_config = ConfigDict(extra="forbid")

    status: str = Field(default="ready", description="Model inference engine readiness")
    model_version: str = Field(description="Active ML model version")
    dataset_version: str = Field(description="Underlying training dataset version")


class ModelInfoResponse(BaseModel):
    """Non-sensitive metadata descriptor for the loaded ML models."""

    model_config = ConfigDict(extra="forbid")

    model_version: str = Field(description="Model artifact version")
    dataset_version: str = Field(description="Dataset contract version")
    category_labels: List[str] = Field(description="Supported category classification classes")
    urgency_labels: List[str] = Field(description="Supported urgency classification classes")
    threshold: float = Field(description="Operational confidence threshold tau")
    model_type: str = Field(description="Algorithm architecture description")
    feature_count: int = Field(description="TF-IDF vocabulary feature count")
    training_timestamp: Optional[str] = Field(default=None, description="ISO timestamp of training")


class ErrorResponse(BaseModel):
    """Consistent structured error payload."""

    model_config = ConfigDict(extra="forbid")

    status: StatusEnum = Field(
        default=StatusEnum.PROCESSING_FAILURE, description="Failure status classification"
    )
    detail: str = Field(description="Human-readable error description")
    request_id: Optional[str] = Field(default=None, description="Traceable request identifier")
