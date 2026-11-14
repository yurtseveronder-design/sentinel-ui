"""
sentinel-ui: logger.py
Enterprise error handling and structured request/response body logging.
"""

import logging
import sys
import hashlib
from typing import Any, Dict, Optional

REDACTED_KEYS = {"prompt", "password", "api_key", "token", "authorization"}


def redact(body: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Replace sensitive values by their length and a short hash, so logs can be correlated but not read."""
    cleaned: Dict[str, Any] = {}
    for key, value in (body or {}).items():
        if key.lower() in REDACTED_KEYS:
            text = str(value)
            cleaned[key] = f"<redacted chars={len(text)} sha256={hashlib.sha256(text.encode()).hexdigest()[:12]}>"
        else:
            cleaned[key] = value
    return cleaned

# Configure enterprise logger
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("sentinel-ui")

class EnterpriseErrorHandler:
    """Captures and logs detailed request/response payloads upon failure."""

    @staticmethod
    def log_api_failure(
        endpoint: str,
        method: str,
        status_code: int,
        request_body: Optional[Dict[str, Any]] = None,
        response_body: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> None:
        """Log structured error context. Prompts and credentials are logged as length + hash only."""
        error_payload = {
            "endpoint": endpoint,
            "method": method.upper(),
            "status_code": status_code,
            "request_body": redact(request_body),
            "response_body": redact(response_body),
            "error": error_message or "Unknown failure"
        }
        logger.error(f"API Request Failure Detected: {error_payload}")