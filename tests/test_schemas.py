"""
sentinel-ui: tests/test_schemas.py
Automated validation tests for strict Pydantic schema contracts.
"""

import pytest
from pydantic import ValidationError
from schemas import UserCreateRequest, UserMetadata

def test_valid_user_schema_creation():
    """Ensure valid payloads pass strict schema validation with correct defaults and nesting."""
    payload = {
        "name": "Onder Yurtsever",
        "email": "yurtsever.onder@gmail.com",
        "role": "admin",
        "metadata": {
            "department": "Red Team",
            "clearance_level": 5,
            "tags": ["enterprise", "lead"]
        }
    }
    user = UserCreateRequest(**payload)
    assert user.name == "Onder Yurtsever"
    assert user.email == "yurtsever.onder@gmail.com"
    assert user.role == "admin"
    assert user.metadata.clearance_level == 5
    assert user.is_active is True

def test_invalid_email_rejection():
    """Ensure malformed email addresses are strictly rejected."""
    with pytest.raises(ValidationError):
        UserCreateRequest(
            name="Test User",
            email="not-an-email-address",
            role="auditor"
        )

def test_invalid_role_rejection():
    """Ensure unwhitelisted roles trigger validation errors via custom validators."""
    with pytest.raises(ValidationError):
        UserCreateRequest(
            name="Test User",
            email="test@sentinel.internal",
            role="super_hacker_unauthorized"
        )

def test_nested_clearance_boundaries():
    """Ensure nested clearance level boundaries (1-5) are strictly enforced."""
    with pytest.raises(ValidationError):
        UserCreateRequest(
            name="Test User",
            email="test@sentinel.internal",
            metadata=UserMetadata(clearance_level=10)  # Exceeds max limit of 5
        )