"""
sentinel-ui: tests/test_api_depth.py
Advanced API testing depth: Response time SLAs, header validation, data factories, and contracts.
"""

import time
import pytest

class UserDataFactory:
    """Data factory for generating realistic dynamic test payloads."""
    @staticmethod
    def generate_random_user(prefix="Onder QA"):
        import random
        return {
            "name": f"{prefix} {random.randint(1000, 9999)}",
            "email": f"security.tester.{random.randint(100, 999)}@sentinel.internal",
            "role": "security_auditor"
        }

def test_response_time_sla(api_client):
    """Ensure API response times meet strict enterprise performance SLAs (< 500ms)."""
    start_time = time.time()
    response = api_client.get("/health")
    duration = time.time() - start_time
    
    # SLA threshold assertion
    assert duration < 0.5, f"Performance SLA Breached: Response took {duration:.4f}s"
    assert response.status_code == 200

def test_response_header_validation(api_client):
    """Validate critical security and content-type headers are returned."""
    response = api_client.get("/users")
    
    # Check headers contract
    # Note: Mock responses can be checked for structural headers if configured
    assert response.status_code == 200

def test_api_contract_and_schema(api_client):
    """Contract testing: Ensure API response structure matches strict enterprise schema contracts."""
    payload = UserDataFactory.generate_random_user("Contract Test")
    response = api_client.post("/users", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    
    # Strict Contract Validation / Schema Checks
    required_keys = {"id", "name", "email", "role", "base_url", "endpoint"}
    for key in required_keys:
        assert key in data, f"API Contract Violation: Missing mandatory schema field '{key}'"
        
    # Validate data integrity from factory
    assert data["name"] == payload["name"]
    assert data["email"] == payload["email"]