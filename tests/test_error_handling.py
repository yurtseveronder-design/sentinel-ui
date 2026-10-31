"""
sentinel-ui: tests/test_error_handling.py
Automated tests for enterprise error handling and request/response body logging.
"""

import pytest
from logger import EnterpriseErrorHandler, logger

def test_enterprise_error_logging(caplog):
    """Ensure API failures correctly capture and log request/response bodies."""
    with caplog.at_level("ERROR"):
        EnterpriseErrorHandler.log_api_failure(
            endpoint="/users",
            method="POST",
            status_code=400,
            request_body={"name": "Onder", "email": "invalid-email"},
            response_body={"error": "Validation failed", "field": "email"},
            error_message="Invalid email format"
        )
        
    # Verify log output contains critical debugging details
    assert "API Request Failure Detected" in caplog.text
    assert "/users" in caplog.text
    assert "invalid-email" in caplog.text
    assert "Validation failed" in caplog.text