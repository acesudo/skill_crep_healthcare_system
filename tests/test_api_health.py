"""Unit tests for health, readiness, and model metadata endpoints.
"""

from fastapi.testclient import TestClient
import pytest
from src.api.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "X-Request-ID" in response.headers


def test_ready_endpoint(client):
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["model_version"] == "v1.0.0"
    assert data["dataset_version"] == "v1.0.0"


def test_ready_endpoint_unready_state(client):
    original_service = app.state.inference_service
    try:
        app.state.inference_service = None
        response = client.get("/ready")
        assert response.status_code == 503
        data = response.json()
        assert "not ready" in data["detail"]
    finally:
        app.state.inference_service = original_service


def test_model_info_endpoint(client):
    response = client.get("/model-info")
    assert response.status_code == 200
    data = response.json()
    assert data["model_version"] == "v1.0.0"
    assert data["threshold"] == 0.70
    assert len(data["category_labels"]) == 6
    assert len(data["urgency_labels"]) == 2
    assert "Appointment" in data["category_labels"]
    assert "Urgent" in data["urgency_labels"]
    assert data["feature_count"] == 2500
