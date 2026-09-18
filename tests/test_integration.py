"""
Section 12 - End-to-End Integration Tests.
Verifies the complete pipeline contract from FastAPIClient down through FastAPI routes,
InferenceService, LogisticRegression models, Confidence bottleneck, and Human Review.
"""

import io
import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.ui.api_client import FastAPIClient


@pytest.fixture
def integration_client():
    """Initializes a real FastAPI TestClient executing lifespan events."""
    with TestClient(app) as tc:
        yield tc


def test_e2e_health_and_readiness_lifecycle(integration_client):
    """Verifies that health, readiness, and model-info endpoints conform to UI expectations."""
    # 1. GET /health
    resp = integration_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"

    # 2. GET /ready
    resp_ready = integration_client.get("/ready")
    assert resp_ready.status_code == 200
    data_ready = resp_ready.json()
    assert data_ready["status"] == "ready"
    assert data_ready["model_version"] == "v1.0.0"

    # 3. GET /model-info
    resp_info = integration_client.get("/model-info")
    assert resp_info.status_code == 200
    data_info = resp_info.json()
    assert len(data_info["category_labels"]) == 6
    assert len(data_info["urgency_labels"]) == 2
    assert data_info["threshold"] == 0.70


def test_e2e_single_message_workflow_and_explainability(integration_client):
    """Verifies complete single-message triage pipeline, confidence evaluation, and explanations."""
    payload = {"message_text": "I need to urgently reschedule my surgery appointment for tomorrow morning."}
    resp = integration_client.post("/predict", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    # Schema checks
    assert "message_id" in data
    assert data["predicted_category"] == "Appointment"
    assert data["predicted_urgency"] in ["Routine", "Urgent"]
    assert "overall_confidence" in data
    assert "assigned_queue" in data
    assert "requires_human_review" in data
    assert "status" in data
    assert "explanation" in data

    # Explainability checks
    exp = data["explanation"]
    assert "category_features" in exp
    assert "urgency_features" in exp
    assert isinstance(exp["category_features"], list)
    assert len(exp["category_features"]) > 0
    assert "feature" in exp["category_features"][0]
    assert "contribution" in exp["category_features"][0]


def test_e2e_confidence_gate_and_human_review_escalation(integration_client):
    """Verifies that low-confidence messages trigger status=LOW_CONFIDENCE and route to Human Review."""
    # A short, vague message designed to produce low joint confidence (< 0.70)
    payload = {"message_text": "hello i need help with something"}
    resp = integration_client.post("/predict", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["overall_confidence"] < 0.70
    assert data["status"] == "LOW_CONFIDENCE"
    assert data["requires_human_review"] is True
    assert data["assigned_queue"] == "Human Review Queue"


def test_e2e_batch_triage_csv_with_mixed_and_invalid_rows(integration_client):
    """Verifies batch CSV upload containing valid, low-confidence, and empty records."""
    csv_content = (
        "message_id,message_text\n"
        "E2E-001,I want to schedule an appointment for Monday.\n"
        "E2E-002,I was charged twice for my hospital bill.\n"
        "E2E-003,The patient portal is not working.\n"
        "E2E-004,Please send me my latest medical report.\n"
        "E2E-005,I need help with something.\n"
        "E2E-006,\n"
    )

    files = {"file": ("test_batch.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    resp = integration_client.post("/predict/batch", files=files)
    assert resp.status_code == 200
    data = resp.json()

    assert data["total_records"] == 6
    assert data["invalid_records"] == 1  # Row E2E-006 is empty
    assert len(data["results"]) == 6

    # Verify invalid row details
    invalid_item = [r for r in data["results"] if r["status"] == "INVALID_INPUT"][0]
    assert invalid_item["row_index"] == 6
    assert "Empty or missing" in invalid_item["error_detail"]


def test_e2e_validation_errors(integration_client):
    """Verifies graceful HTTP 422 error handling for invalid payloads."""
    # Blank string
    resp = integration_client.post("/predict", json={"message_text": ""})
    assert resp.status_code == 422

    # Whitespace only
    resp = integration_client.post("/predict", json={"message_text": "   \n  \t  "})
    assert resp.status_code == 422

    # Oversized string (> 4000 chars)
    resp = integration_client.post("/predict", json={"message_text": "x" * 4001})
    assert resp.status_code == 422
