"""
Unit tests for Streamlit UI FastAPIClient against mocks.
"""

from unittest.mock import patch, MagicMock
import httpx
from src.ui.api_client import FastAPIClient


def test_api_client_health_success():
    client = FastAPIClient(base_url="http://testserver")
    mock_resp = MagicMock()
    mock_resp.is_success = True
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"status": "ok", "version": "1.0.0"}

    with patch("httpx.Client.request", return_value=mock_resp):
        res = client.health()
        assert res["success"] is True
        assert res["data"]["status"] == "ok"
        assert res["status_code"] == 200


def test_api_client_connection_error():
    client = FastAPIClient(base_url="http://nonexistent-server:9999")
    with patch("httpx.Client.request", side_effect=httpx.ConnectError("Connection refused")):
        res = client.health()
        assert res["success"] is False
        assert "Cannot connect to backend" in res["error"]
        assert res["status_code"] == 503


def test_api_client_timeout_error():
    client = FastAPIClient(base_url="http://testserver")
    with patch("httpx.Client.request", side_effect=httpx.TimeoutException("Read timed out")):
        res = client.predict_single("test message")
        assert res["success"] is False
        assert "Request timed out" in res["error"]
        assert res["status_code"] == 504


def test_api_client_predict_single_success():
    client = FastAPIClient(base_url="http://testserver")
    mock_resp = MagicMock()
    mock_resp.is_success = True
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "predicted_category": "prescription_refill",
        "predicted_urgency": "non-urgent",
        "overall_confidence": 0.95,
        "status": "SUCCESS",
        "requires_human_review": False,
    }

    with patch("httpx.Client.request", return_value=mock_resp):
        res = client.predict_single("Need refill")
        assert res["success"] is True
        assert res["data"]["predicted_category"] == "prescription_refill"
        assert res["data"]["overall_confidence"] == 0.95


def test_api_client_predict_batch_success():
    client = FastAPIClient(base_url="http://testserver")
    mock_resp = MagicMock()
    mock_resp.is_success = True
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "total_submitted": 2,
        "successful_predictions": 2,
        "results": [
            {"index": 0, "status": "SUCCESS"},
            {"index": 1, "status": "SUCCESS"},
        ],
    }

    with patch("httpx.Client.request", return_value=mock_resp):
        res = client.predict_batch(b"message_text\ntest1\ntest2")
        assert res["success"] is True
        assert res["data"]["total_submitted"] == 2
