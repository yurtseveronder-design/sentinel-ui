import os
from config import get_settings

def test_environment_routing():
    # Test default dev environment
    os.environ["ENVIRONMENT"] = "dev"
    settings = get_settings()
    assert settings.environment == "dev"
    assert "localhost" in settings.base_url

    # Test staging environment override
    os.environ["ENVIRONMENT"] = "staging"
    settings_staging = get_settings()
    assert settings_staging.environment == "staging"
    assert "staging-api" in settings_staging.base_url

    # Test production environment override
    os.environ["ENVIRONMENT"] = "prod"
    settings_prod = get_settings()
    assert settings_prod.environment == "prod"
    assert "api.sentinel-security.com" in settings_prod.base_url