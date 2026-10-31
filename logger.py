"""
sentinel-ui: logger.py
Enterprise error handling and structured request/response body logging.
"""

import logging
import sys
from typing import Any, Dict, Optional

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
        """Log structured error context including full request and response bodies."""
        error_payload = {
            "endpoint": endpoint,
            "method": method.upper(),
            "status_code": status_code,
            "request_body": request_body or {},
            "response_body": response_body or {},
            "error": error_message or "Unknown failure"
        }
        logger.error(f"API Request Failure Detected: {error_payload}")