"""
Helper formatting utilities for the Streamlit UI.
"""

from typing import Tuple


def format_confidence_pct(val: float) -> str:
    """Formats float confidence [0, 1] to percentage string."""
    try:
        return f"{float(val) * 100:.1f}%"
    except (ValueError, TypeError):
        return "0.0%"


def get_status_badge_style(status: str, requires_review: bool) -> Tuple[str, str]:
    """Returns icon and label for triage prediction status."""
    if status == "SUCCESS" and not requires_review:
        return "??", "STANDARD ROUTED"
    elif status == "LOW_CONFIDENCE" or requires_review:
        return "??", "HUMAN REVIEW PENDING"
    elif status == "INVALID_INPUT":
        return "??", "INVALID INPUT"
    else:
        return "?", "PROCESSING FAILURE"
