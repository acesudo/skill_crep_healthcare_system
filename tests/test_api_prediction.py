"""Unit tests for single message prediction API, threshold gating, and explainability.
"""

from fastapi.testclient import TestClient
import pytest
from src.api.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_predict_successful_routing(client):
    payload = {
        "message_text": (
            "Hello IT support, the mobile portal app crashes every time I try to submit "
            "my pre-registration paperwork. I am on Chrome mobile browser. Please let me know how to fix this."
        ),
        "message_id": "MSG-TEST-001",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["message_id"] == "MSG-TEST-001"
    assert data["predicted_category"] == "Technical Issue"
    assert data["predicted_urgency"] == "Routine"
    assert data["overall_confidence"] >= 0.70
    assert data["requires_human_review"] is False
    assert data["status"] == "SUCCESS"
    assert data["assigned_queue"] == "Technical Support Queue"
    assert "explanation" in data
    assert len(data["explanation"]["category_features"]) > 0


def test_predict_urgent_detection(client):
    payload = {
        "message_text": (
            "URGENT: severe crushing chest pain, difficulty breathing, and intense dizziness "
            "started one hour ago after surgery. Need immediate clinical doctor review right away."
        ),
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["predicted_urgency"] == "Urgent"
    assert data["urgency_confidence"] >= 0.50
    assert data["message_id"].startswith("MSG-")


def test_predict_low_confidence_escalation(client):
    # Short ambiguous message that produces overall confidence below tau (0.70)
    payload = {
        "message_text": "hello thanks",
        "message_id": "MSG-AMBIGUOUS",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["overall_confidence"] < 0.70
    assert data["requires_human_review"] is True
    assert data["status"] == "LOW_CONFIDENCE"
    assert data["assigned_queue"] == "Human Review Queue"


def test_predict_explanation_format(client):
    payload = {
        "message_text": "I need to refill my monthly blood pressure medication lisinopril urgently.",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    explanation = data["explanation"]
    assert "category_features" in explanation
    assert "urgency_features" in explanation

    cat_feats = explanation["category_features"]
    assert len(cat_feats) <= 5
    for item in cat_feats:
        assert "feature" in item
        assert "contribution" in item
        assert item["contribution"] > 0


def test_inference_consistency_between_api_and_direct_service(client):
    """Verifies that invoking the API produces identical results to calling the InferenceService directly."""
    service = app.state.inference_service
    test_message = "Regarding my billing invoice #49201: why was my insurance copay doubled?"

    # Direct service prediction
    direct_result = service.predict_single(test_message, message_id="CONSISTENCY-01")

    # API prediction
    api_response = client.post(
        "/predict",
        json={"message_text": test_message, "message_id": "CONSISTENCY-01"},
    )
    assert api_response.status_code == 200
    api_data = api_response.json()

    assert api_data["predicted_category"] == direct_result.predicted_category.value
    assert api_data["predicted_urgency"] == direct_result.predicted_urgency.value
    assert api_data["category_confidence"] == direct_result.category_confidence
    assert api_data["urgency_confidence"] == direct_result.urgency_confidence
    assert api_data["overall_confidence"] == direct_result.overall_confidence
    assert api_data["assigned_queue"] == direct_result.assigned_queue
    assert api_data["requires_human_review"] == direct_result.requires_human_review
    assert api_data["status"] == direct_result.status.value
