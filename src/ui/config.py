"""Frontend configuration management for Streamlit operational dashboard.
Supports Streamlit Cloud Secrets, OS environment variables, and local fallback.
"""

import os
from dataclasses import dataclass


def _get_fastapi_base_url() -> str:
    """Resolves the FastAPI backend base URL with priority:
    1. Streamlit Cloud Secret: st.secrets["FASTAPI_BASE_URL"]
    2. OS Environment Variable: os.getenv("FASTAPI_BASE_URL")
    3. Local Development Fallback: http://127.0.0.1:8000
    """
    # 1. Streamlit Cloud Secrets
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "FASTAPI_BASE_URL" in st.secrets:
            secret_url = str(st.secrets["FASTAPI_BASE_URL"]).strip()
            if secret_url:
                return secret_url.rstrip("/")
    except Exception:
        # Gracefully proceed if st.secrets is not initialized or secrets.toml is missing
        pass

    # 2. Operating System Environment Variable
    env_url = os.getenv("FASTAPI_BASE_URL", "").strip()
    if env_url:
        return env_url.rstrip("/")

    # 3. Local Development Fallback
    return "http://127.0.0.1:8000"


@dataclass(frozen=True)
class UIConfig:
    """Streamlit dashboard runtime settings."""

    fastapi_base_url: str = _get_fastapi_base_url()
    app_title: str = "Patient Message Triage & Urgency Classifier"
    app_subtitle: str = "Operational Healthcare Support Dashboard"
    app_version: str = "v1.0.0"
    request_timeout_seconds: float = 15.0


ui_config = UIConfig()