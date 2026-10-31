"""
sentinel-ui: config.py
Enterprise configuration management using modern Pydantic V2 SettingsConfigDict.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    environment: str = Field(default="dev", validation_alias="ENVIRONMENT")
    debug: bool = Field(default=True, validation_alias="DEBUG")
    
    # Environment-specific Base URLs
    base_url: str = Field(default="http://localhost:8000/api/v1", validation_alias="BASE_URL")
    llm_timeout: int = Field(default=30, validation_alias="LLM_TIMEOUT")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

def get_settings() -> Settings:
    """Factory function to load and return environment-specific settings."""
    settings = Settings()
    
    if settings.environment == "dev":
        settings.base_url = "http://localhost:8000/api/v1"
        settings.debug = True
    elif settings.environment == "staging":
        settings.base_url = "https://staging-api.sentinel-security.internal/v1"
        settings.debug = False
    elif settings.environment == "prod":
        settings.base_url = "https://api.sentinel-security.com/v1"
        settings.debug = False
        
    return settings