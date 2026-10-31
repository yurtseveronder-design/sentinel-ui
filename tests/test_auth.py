"""
sentinel-ui: tests/test_auth.py
Automated security tests for API key verification and JWT token validation.
"""

import pytest
from auth import SecurityManager

def test_valid_api_key_acceptance():
    """Ensure valid enterprise API keys are successfully authenticated."""
    assert SecurityManager.verify_api_key("sk_sentinel_live_998877") is True
    assert SecurityManager.verify_api_key("sk_sentinel_dev_112233") is True

def test_invalid_api_key_rejection():
    """Ensure malformed or unauthorized API keys are strictly rejected."""
    assert SecurityManager.verify_api_key("sk_invalid_fake_key") is False
    assert SecurityManager.verify_api_key("") is False
    assert SecurityManager.verify_api_key(None) is False

def test_valid_jwt_token_decoding():
    """Ensure properly formatted bearer JWT tokens are successfully decoded and verified."""
    payload = SecurityManager.verify_jwt_token("valid_jwt_token_12345")
    assert payload is not None
    assert payload["sub"] == "auditor_user"
    assert payload["role"] == "security_auditor"

def test_invalid_jwt_token_rejection():
    """Ensure tampered or missing JWT tokens are rejected with None."""
    assert SecurityManager.verify_jwt_token("malformed.token.string") is None
    assert SecurityManager.verify_jwt_token(None) is None