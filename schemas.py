"""
sentinel-ui: schemas.py
Strict enterprise Pydantic V2 data models featuring email validation, nested objects, 
optional fields, and custom field validators.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, field_validator

class UserMetadata(BaseModel):
    """Nested metadata model for granular user profiling."""
    department: Optional[str] = Field(default="Security Operations", description="Internal department")
    clearance_level: int = Field(default=1, ge=1, le=5, description="Security clearance (1 to 5)")
    tags: List[str] = Field(default_factory=list, description="Associated security tags")

class UserCreateRequest(BaseModel):
    """Strict schema contract for user creation requests."""
    name: str = Field(..., min_length=2, max_length=100, description="User full name")
    email: EmailStr = Field(..., description="Strictly validated RFC-compliant email address")
    role: str = Field(default="auditor", description="Assigned system access role")
    metadata: Optional[UserMetadata] = Field(default_factory=UserMetadata, description="Nested user metadata")
    is_active: bool = Field(default=True, description="Account status flag")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Enforce strict whitelist validation on user roles."""
        allowed_roles = {"auditor", "admin", "analyst", "security_auditor"}
        if v.lower() not in allowed_roles:
            raise ValueError(f"Invalid role '{v}'. Must be one of: {allowed_roles}")
        return v.lower()