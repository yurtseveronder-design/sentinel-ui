"""
sentinel-ui: tests/test_auth.py
Security tests for API key verification and JWT validation.
"""

import base64
import json
import time

import pytest

from auth import SecurityManager


@pytest.fixture(autouse=True)
def auth_env(monkeypatch):
    monkeypatch.setenv("SENTINEL_API_KEYS", "test-key-live, test-key-dev")
    monkeypatch.setenv("SENTINEL_JWT_SECRET", "unit-test-secret")


def _b64(obj) -> str:
    return base64.urlsafe_b64encode(json.dumps(obj).encode()).rstrip(b"=").decode()


def test_valid_api_key_acceptance():
    assert SecurityManager.verify_api_key("test-key-live") is True
    assert SecurityManager.verify_api_key("test-key-dev") is True


def test_invalid_api_key_rejection():
    assert SecurityManager.verify_api_key("sk_invalid_fake_key") is False
    assert SecurityManager.verify_api_key("") is False
    assert SecurityManager.verify_api_key(None) is False
    assert SecurityManager.verify_api_key("test-key") is False  # prefix only


def test_old_hardcoded_keys_no_longer_work():
    assert SecurityManager.verify_api_key("sk_sentinel_live_998877") is False
    assert SecurityManager.verify_api_key("sk_sentinel_dev_112233") is False


def test_no_keys_configured_rejects_everything(monkeypatch):
    monkeypatch.delenv("SENTINEL_API_KEYS", raising=False)
    assert SecurityManager.verify_api_key("test-key-live") is False
    monkeypatch.setenv("SENTINEL_API_KEYS", "")
    assert SecurityManager.verify_api_key("") is False


def test_valid_jwt_token_decoding():
    token = SecurityManager.create_jwt_token("auditor_user", "security_auditor")
    payload = SecurityManager.verify_jwt_token(token)
    assert payload is not None
    assert payload["sub"] == "auditor_user"
    assert payload["role"] == "security_auditor"


def test_invalid_jwt_token_rejection():
    assert SecurityManager.verify_jwt_token("malformed.token.string") is None
    assert SecurityManager.verify_jwt_token(None) is None
    assert SecurityManager.verify_jwt_token("") is None


def test_previous_fake_tokens_are_rejected():
    # These used to be accepted (the second one as an admin).
    assert SecurityManager.verify_jwt_token("valid_jwt_token_12345") is None
    assert SecurityManager.verify_jwt_token("header.payload.anything") is None


def test_token_signed_with_wrong_secret_is_rejected():
    token = SecurityManager.create_jwt_token("u", "admin", secret="another-secret")
    assert SecurityManager.verify_jwt_token(token) is None


def test_expired_token_is_rejected():
    token = SecurityManager.create_jwt_token("u", "admin", ttl_seconds=-10)
    assert SecurityManager.verify_jwt_token(token) is None


def test_tampered_payload_is_rejected():
    token = SecurityManager.create_jwt_token("u", "viewer")
    header, _payload, signature = token.split(".")
    forged = _b64({"sub": "u", "role": "admin", "exp": int(time.time()) + 3600})
    assert SecurityManager.verify_jwt_token(f"{header}.{forged}.{signature}") is None


def test_alg_none_is_rejected():
    header = _b64({"alg": "none", "typ": "JWT"})
    payload = _b64({"sub": "u", "role": "admin", "exp": int(time.time()) + 3600})
    assert SecurityManager.verify_jwt_token(f"{header}.{payload}.") is None


def test_token_missing_claims_is_rejected():
    import hashlib
    import hmac

    header = _b64({"alg": "HS256", "typ": "JWT"})
    payload = _b64({"exp": int(time.time()) + 3600})  # no sub / role
    sig = hmac.new(b"unit-test-secret", f"{header}.{payload}".encode(), hashlib.sha256).digest()
    token = f"{header}.{payload}." + base64.urlsafe_b64encode(sig).rstrip(b"=").decode()
    assert SecurityManager.verify_jwt_token(token) is None


def test_jwt_without_configured_secret_is_rejected(monkeypatch):
    token = SecurityManager.create_jwt_token("u", "admin")
    monkeypatch.delenv("SENTINEL_JWT_SECRET", raising=False)
    assert SecurityManager.verify_jwt_token(token) is None
