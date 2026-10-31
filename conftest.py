"""
sentinel-ui: conftest.py
Pytest configuration, environment settings, and fully featured MockResponse API fixtures.
"""

import pytest
from config import get_settings

class MockResponse:
    """Simulates a requests.Response object for robust API testing."""
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json_data = json_data

    def json(self):
        return self._json_data

@pytest.fixture(scope="session")
def app_settings():
    return get_settings()

@pytest.fixture
def api_client(app_settings):
    """Provide a mock API test client configured with environment base URLs."""
    class MockAPIClient:
        def __init__(self, base_url):
            self.base_url = base_url
            
        def get(self, endpoint, **kwargs):
            return MockResponse(200, {"base_url": self.base_url, "endpoint": endpoint})
            
        def post(self, endpoint, json=None, **kwargs):
            response_data = {
                "id": "usr_99887766",
                "base_url": self.base_url, 
                "endpoint": endpoint
            }
            if json and isinstance(json, dict):
                response_data.update(json)
            return MockResponse(201, response_data)

        def delete(self, endpoint, **kwargs):
            return MockResponse(200, {"base_url": self.base_url, "endpoint": endpoint, "status": "deleted"})

    return MockAPIClient(base_url=app_settings.base_url)