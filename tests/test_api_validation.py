"""Unit tests for request validation, boundary constraints, and CORS headers.
"""

from fastapi.testclient import TestClient
import pytest
from src.api.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_predict_empty_message_validation(client):
    response = client.post("/predict", json={"message_text": ""})
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "INVALID_INPUT"
    assert "detail" in data


def test_predict_whitespace_message_validation(client):
    response = client.post("/predict", json={"message_text": "     "})
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "INVALID_INPUT"
    assert "whitespace" in data["detail"]


def test_predict_oversized_message_validation(client):
    huge_message = "repeat words " * 600  # > 4000 characters
    response = client.post("/predict", json={"message_text": huge_message})
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "INVALID_INPUT"


def test_predict_forbids_extra_fields(client):
    response = client.post(
        "/predict",
        json={
            "message_text": "Need to check my lab report status.",
            "unauthorized_field": "injected_data",
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "INVALID_INPUT"
    assert "extra" in data["detail"].lower()


def test_cors_preflight_headers(client):
    response = client.options(
        "/predict",
        headers={
            "Origin": "http://localhost:8501",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:8501"
