"""Data schemas and canonical validation models for PS-1 dataset records.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class PatientMessageRecord(BaseModel):
    """Canonical data contract for an operational patient-support message record.
    Adheres strictly to Section 4 Canonical Data Contract.
    """
    message_id: str = Field(..., description="Unique deterministic identifier, e.g. MSG-000001")
    message_text: str = Field(..., min_length=10, max_length=2000, description="Raw synthetic message text")
    category: str = Field(..., description="Operational request category")
    urgency: str = Field(..., description="Operational handling priority: Routine or Urgent")
    department: str = Field(..., description="Assigned operational queue")
    timestamp: str = Field(..., description="ISO 8601 formatted synthetic timestamp")
    generation_source: Optional[str] = Field("synthetic_generator_v1", description="Provenance tracking tag")
    dataset_version: Optional[str] = Field("v1.0.0", description="Dataset release version")

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        allowed = {
            "Appointment",
            "Billing",
            "Medication Refill",
            "Report Request",
            "Technical Issue",
            "Urgent Review",
        }
        if v not in allowed:
            raise ValueError(f"Invalid category '{v}'. Must be one of {allowed}")
        return v

    @field_validator("urgency")
    @classmethod
    def validate_urgency(cls, v: str) -> str:
        allowed = {"Routine", "Urgent"}
        if v not in allowed:
            raise ValueError(f"Invalid urgency '{v}'. Must be one of {allowed}")
        return v

    @field_validator("message_id")
    @classmethod
    def validate_message_id(cls, v: str) -> str:
        if not v.startswith("MSG-") or len(v) != 10:
            raise ValueError(f"Message ID '{v}' must match format 'MSG-XXXXXX' (10 chars)")
        return v
