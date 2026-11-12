"""
sentinel-ui: auth.py
Authentication for the gateway: API keys and HS256 JWT bearer tokens.

Nothing secret lives in this file. Configure through environment variables:

    SENTINEL_API_KEYS     comma-separated list of accepted API keys
    SENTINEL_JWT_SECRET   HMAC secret used to sign and verify JWTs

If a variable is unset, that authentication method rejects everything
(fail closed). Variables are read on every call, so changes take effect
without re-importing the module.
"""

import base64
import hmac
import hashlib
import json
import os
import time
from typing import Optional

from pydantic import BaseModel


class TokenPayload(BaseModel):
    sub: str
    role: str
    exp: int


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64url_decode(segment: str) -> bytes:
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


class SecurityManager:
    """Validates API keys and JWT tokens for protected endpoints."""

    @staticmethod
    def _configured_api_keys() -> list:
        raw = os.environ.get("SENTINEL_API_KEYS", "")
        return [key.strip() for key in raw.split(",") if key.strip()]

    @staticmethod
    def _jwt_secret() -> Optional[str]:
        secret = os.environ.get("SENTINEL_JWT_SECRET")
        return secret if secret else None

    @classmethod
    def verify_api_key(cls, api_key: Optional[str]) -> bool:
        """Constant-time check of an API key against the configured keys."""
        if not api_key or not isinstance(api_key, str):
            return False
        candidate = api_key.encode("utf-8")
        matched = False
        # Compare against every key (no early exit) so timing does not reveal
        # which key, if any, was close.
        for valid_key in cls._configured_api_keys():
            if hmac.compare_digest(candidate, valid_key.encode("utf-8")):
                matched = True
        return matched

    @classmethod
    def create_jwt_token(
        cls, sub: str, role: str, ttl_seconds: int = 3600, secret: Optional[str] = None
    ) -> str:
        """Issue an HS256 token. Mainly for tests and local development."""
        key = secret or cls._jwt_secret()
        if not key:
            raise RuntimeError("SENTINEL_JWT_SECRET is not set")
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {"sub": sub, "role": role, "exp": int(time.time()) + int(ttl_seconds)}
        signing_input = (
            _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
            + "."
            + _b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
        )
        signature = hmac.new(key.encode(), signing_input.encode(), hashlib.sha256).digest()
        return signing_input + "." + _b64url_encode(signature)

    @classmethod
    def verify_jwt_token(cls, token: Optional[str]) -> Optional[dict]:
        """Verify an HS256 JWT. Returns its claims, or None if anything is wrong.

        Checks: three segments, alg is HS256 (so "none" is refused), signature
        matches, and the token carries sub, role and an unexpired exp.
        """
        secret = cls._jwt_secret()
        if not secret or not token or not isinstance(token, str):
            return None

        parts = token.split(".")
        if len(parts) != 3:
            return None

        try:
            header = json.loads(_b64url_decode(parts[0]))
            if not isinstance(header, dict) or header.get("alg") != "HS256":
                return None

            expected = hmac.new(
                secret.encode(), f"{parts[0]}.{parts[1]}".encode(), hashlib.sha256
            ).digest()
            if not hmac.compare_digest(expected, _b64url_decode(parts[2])):
                return None

            claims = json.loads(_b64url_decode(parts[1]))
        except (ValueError, TypeError):
            return None

        if not isinstance(claims, dict):
            return None
        exp = claims.get("exp")
        if isinstance(exp, bool) or not isinstance(exp, int) or exp <= int(time.time()):
            return None
        if not claims.get("sub") or not claims.get("role"):
            return None
        return claims
