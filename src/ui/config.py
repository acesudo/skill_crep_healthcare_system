"""Frontend configuration management for Streamlit operational dashboard.
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class UIConfig:
    """Streamlit dashboard runtime settings."""

    fastapi_base_url: str = os.getenv("FASTAPI_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    app_title: str = "Patient Message Triage & Urgency Classifier"
    app_subtitle: str = "Operational Healthcare Support Dashboard"
    app_version: str = "v1.0.0"
    request_timeout_seconds: float = 15.0


ui_config = UIConfig()
