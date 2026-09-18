"""
Unit tests for Streamlit UI configuration resolution and precedence.
"""

import os
from unittest.mock import patch
from src.ui.config import _get_fastapi_base_url
from src.ui.api_client import FastAPIClient


def test_config_precedence_local_fallback():
    """When neither secrets nor env var are set, fall back to localhost."""
    os.environ.pop("FASTAPI_BASE_URL", None)
    with patch("streamlit.secrets", new={}):
        assert _get_fastapi_base_url() == "http://127.0.0.1:8000"


def test_config_precedence_env_var():
    """When env var is set, use it over fallback."""
    os.environ["FASTAPI_BASE_URL"] = "https://env-service.example.com/"
    try:
        with patch("streamlit.secrets", new={}):
            assert _get_fastapi_base_url() == "https://env-service.example.com"
    finally:
        os.environ.pop("FASTAPI_BASE_URL", None)


def test_config_precedence_streamlit_secrets():
    """When Streamlit secret is set, it takes top priority over env var and fallback."""
    os.environ["FASTAPI_BASE_URL"] = "https://env-service.example.com/"
    render_url = "https://skill-crep-healthcare-system.onrender.com/"
    try:
        with patch("streamlit.secrets", new={"FASTAPI_BASE_URL": render_url}):
            resolved = _get_fastapi_base_url()
            assert resolved == "https://skill-crep-healthcare-system.onrender.com"
            client = FastAPIClient(base_url=resolved)
            assert f"{client.base_url}/predict" == "https://skill-crep-healthcare-system.onrender.com/predict"
    finally:
        os.environ.pop("FASTAPI_BASE_URL", None)