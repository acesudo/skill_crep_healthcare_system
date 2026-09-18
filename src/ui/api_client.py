"""HTTP API client abstraction for communication between Streamlit and FastAPI.
Encapsulates connection error handling, timeouts, and JSON serialization.
"""

from typing import Any, Dict, Optional
import httpx
from src.ui.config import ui_config


class FastAPIClient:
    """Synchronous HTTP client for interacting with the PS-1 FastAPI backend."""

    def __init__(self, base_url: Optional[str] = None, timeout: Optional[float] = None):
        self.base_url = (base_url or ui_config.fastapi_base_url).rstrip("/")
        self.timeout = timeout or ui_config.request_timeout_seconds

    def _request(
        self,
        method: str,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Internal helper handling connection errors, HTTP status errors, and timeouts."""
        url = f"{self.base_url}{path}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(
                    method=method,
                    url=url,
                    json=json_data,
                    files=files,
                )

                if response.is_success:
                    return {
                        "success": True,
                        "status_code": response.status_code,
                        "data": response.json(),
                        "error": None,
                    }

                # Try to extract detail from structured error payload
                try:
                    err_json = response.json()
                    detail = err_json.get("detail", str(response.text))
                except Exception:
                    detail = response.text or f"HTTP {response.status_code}"

                return {
                    "success": False,
                    "status_code": response.status_code,
                    "data": None,
                    "error": detail,
                }

        except httpx.ConnectError:
            return {
                "success": False,
                "status_code": 503,
                "data": None,
                "error": (
                    f"Cannot connect to backend at {self.base_url}. "
                    "Ensure the FastAPI server is running (`python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000`)."
                ),
            }
        except httpx.TimeoutException:
            return {
                "success": False,
                "status_code": 504,
                "data": None,
                "error": f"Request timed out after {self.timeout}s to {url}.",
            }
        except Exception as exc:
            return {
                "success": False,
                "status_code": 500,
                "data": None,
                "error": f"Unexpected communication error: {str(exc)}",
            }

    def health(self) -> Dict[str, Any]:
        """Queries GET /health."""
        return self._request("GET", "/health")

    def ready(self) -> Dict[str, Any]:
        """Queries GET /ready."""
        return self._request("GET", "/ready")

    def model_info(self) -> Dict[str, Any]:
        """Queries GET /model-info."""
        return self._request("GET", "/model-info")

    def predict_single(
        self,
        message_text: str,
        message_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Queries POST /predict."""
        payload = {"message_text": message_text}
        if message_id and message_id.strip():
            payload["message_id"] = message_id.strip()

        return self._request("POST", "/predict", json_data=payload)

    def predict_batch(
        self,
        file_bytes: bytes,
        filename: str = "batch.csv",
    ) -> Dict[str, Any]:
        """Queries POST /predict/batch with multipart CSV upload."""
        files = {"file": (filename, file_bytes, "text/csv")}
        return self._request("POST", "/predict/batch", files=files)
