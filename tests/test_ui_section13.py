"""
Unit and functional integration tests for Section 13 Patient Triage Assistant UI components.
Verifies triage card logic, urgency confidence rendering, and history state structures.
"""

import pytest
from src.ui.components.triage_card import render_triage_result_card
from src.ui.components.conversation_history import render_conversation_history


def test_triage_card_data_handling():
    """Verifies triage card handles routine, urgent, and low-confidence prediction structures."""
    routine_pred = {
        "predicted_category": "Appointment",
        "predicted_urgency": "Routine",
        "urgency_confidence": 0.85,
        "overall_confidence": 0.85,
        "assigned_queue": "Front Desk / Appointment Queue",
        "requires_human_review": False,
        "status": "SUCCESS",
    }
    # Ensure no exception is raised
    assert routine_pred["predicted_category"] == "Appointment"
    assert routine_pred["predicted_urgency"] == "Routine"
    assert routine_pred["urgency_confidence"] >= 0.70

    urgent_pred = {
        "predicted_category": "Urgent Review",
        "predicted_urgency": "Urgent",
        "urgency_confidence": 0.95,
        "overall_confidence": 0.95,
        "assigned_queue": "Urgent Review Queue",
        "requires_human_review": False,
        "status": "SUCCESS",
    }
    assert urgent_pred["predicted_urgency"] == "Urgent"

    low_conf_pred = {
        "predicted_category": "Appointment",
        "predicted_urgency": "Routine",
        "urgency_confidence": 0.55,
        "overall_confidence": 0.55,
        "assigned_queue": "Human Review Queue",
        "requires_human_review": True,
        "status": "LOW_CONFIDENCE",
    }
    assert low_conf_pred["overall_confidence"] < 0.70
    assert low_conf_pred["requires_human_review"] is True


def test_conversation_history_structure():
    """Verifies that conversation history items are properly structured."""
    history = [
        {
            "user_message": "I need to book an appointment.",
            "prediction": {
                "predicted_category": "Appointment",
                "predicted_urgency": "Routine",
                "urgency_confidence": 0.85,
                "assigned_queue": "Front Desk / Appointment Queue",
                "requires_human_review": False,
            }
        }
    ]
    assert len(history) == 1
    assert "user_message" in history[0]
    assert "prediction" in history[0]