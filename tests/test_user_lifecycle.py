import pytest
from utils.data_factory import UserDataFactory

def test_user_lifecycle_workflow(api_client):
    """
    E2E API Test: Create user using data factory, validate response, and clean up.
    """
    # 1. Generate payload via data factory
    new_user_payload = UserDataFactory.generate_random_user("Onder QA")
    
    # 2. POST Request (Create)
    response = api_client.post("/users", json=new_user_payload)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    
    data = response.json()
    assert data["name"] == new_user_payload["name"]
    assert "id" in data
    
    user_id = data["id"]
    
    # 3. DELETE Request (Teardown validation)
    delete_response = api_client.delete(f"/users/{user_id}")
    assert delete_response.status_code in [200, 204], f"Failed to delete user {user_id}"