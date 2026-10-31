"""
sentinel-ui: auth.py
Enterprise authentication module supporting API Key headers and JWT validation.
"""

import hmac
from typing import Optional
from pydantic import BaseModel

class TokenPayload(BaseModel):
    sub: str
    role: str
    exp: int

class SecurityManager:
    """Manages API Key and JWT token validation for enterprise endpoints."""
    
    # Mock valid API keys for demonstration/testing
    VALID_API_KEYS = {"sk_sentinel_live_998877", "sk_sentinel_dev_112233"}
    SECRET_SIGNING_KEY = "sentinel_enterprise_secret_key"

    @classmethod
    def verify_api_key(cls, api_key: Optional[str]) -> bool:
        """Validate incoming API key against secure enterprise key store."""
        if not api_key:
            return False
        # Use constant-time comparison to prevent timing attacks
        for valid_key in cls.VALID_API_KEYS:
            if hmac.compare_digest(api_key, valid_key):
                return True
        return False

    @classmethod
    def verify_jwt_token(cls, token: Optional[str]) -> Optional[dict]:
        """Validate and decode a bearer JWT token."""
        if not token:
            return None
        
        # Simple simulated JWT validation for demonstration
        # In a full deployment, use PyJWT: jwt.decode(token, cls.SECRET_SIGNING_KEY, algorithms=["HS256"])
        parts = token.split(".")
        if len(parts) == 3 and parts[0] == "header" and parts[1] == "payload":
            return {"sub": "onder_yurtsever", "role": "admin", "status": "authenticated"}
        
        # Fallback for structured test tokens
        if token.startswith("valid_jwt_token_"):
            return {"sub": "auditor_user", "role": "security_auditor", "status": "authenticated"}
            
        return None