"""
Unit tests for Streamlit UI formatting helpers.
"""

from src.ui.helpers import format_confidence_pct, get_status_badge_style


def test_format_confidence_pct():
    assert format_confidence_pct(0.8523) == "85.2%"
    assert format_confidence_pct(1.0) == "100.0%"
    assert format_confidence_pct(0.0) == "0.0%"
    assert format_confidence_pct("invalid") == "0.0%"


def test_get_status_badge_style():
    icon, label = get_status_badge_style("SUCCESS", False)
    assert icon == "??"
    assert label == "STANDARD ROUTED"

    icon, label = get_status_badge_style("SUCCESS", True)
    assert icon == "??"
    assert label == "HUMAN REVIEW PENDING"

    icon, label = get_status_badge_style("LOW_CONFIDENCE", False)
    assert icon == "??"
    assert label == "HUMAN REVIEW PENDING"

    icon, label = get_status_badge_style("INVALID_INPUT", False)
    assert icon == "??"
    assert label == "INVALID INPUT"

    icon, label = get_status_badge_style("SOMETHING_ELSE", False)
    assert icon == "?"
    assert label == "PROCESSING FAILURE"
