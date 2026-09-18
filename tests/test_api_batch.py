"""Unit tests for batch CSV prediction route controller.
"""

from fastapi.testclient import TestClient
import pytest
from src.api.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_batch_valid_csv(client):
    csv_content = (
        "message_id,message_text\n"
        "MSG-B1,Can I reschedule my appointment with the doctor for next week?\n"
        "MSG-B2,I need to refill my prescription for blood pressure pills as soon as possible.\n"
        "MSG-B3,The website portal login is giving me an error code and failing to load.\n"
    )
    response = client.post(
        "/predict/batch",
        files={"file": ("test_batch.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["total_records"] == 3
    assert data["invalid_records"] == 0
    assert len(data["results"]) == 3
    assert data["results"][0]["message_id"] == "MSG-B1"
    assert data["results"][1]["message_id"] == "MSG-B2"


def test_batch_handles_invalid_row(client):
    csv_content = (
        "message_id,message_text\n"
        "MSG-VALID,Regarding my billing statement: please send an itemized invoice.\n"
        "MSG-EMPTY,\n"
        "MSG-VALID-2,Urgent lab report request needed for surgery tomorrow morning.\n"
    )
    response = client.post(
        "/predict/batch",
        files={"file": ("test_invalid_rows.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["total_records"] == 3
    assert data["invalid_records"] == 1
    assert data["results"][1]["status"] == "INVALID_INPUT"
    assert "Empty or missing" in data["results"][1]["error_detail"]


def test_batch_rejects_non_csv_extension(client):
    response = client.post(
        "/predict/batch",
        files={"file": ("data.json", '{"text": "hello"}', "application/json")},
    )
    assert response.status_code == 400
    data = response.json()
    assert "Only .csv files are supported" in data["detail"]


def test_batch_rejects_empty_file(client):
    response = client.post(
        "/predict/batch",
        files={"file": ("empty.csv", "", "text/csv")},
    )
    assert response.status_code == 400
    data = response.json()
    assert "empty" in data["detail"].lower()


def test_batch_rejects_missing_message_text_column(client):
    csv_content = (
        "id,patient_comment\n"
        "1,Hello I need an appointment\n"
    )
    response = client.post(
        "/predict/batch",
        files={"file": ("bad_headers.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 400
    data = response.json()
    assert "Required column 'message_text' was not found" in data["detail"]
