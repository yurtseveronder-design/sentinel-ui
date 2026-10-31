import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV: str = os.getenv("TEST_ENV", "dev")
    
    @property
    def BASE_URL(self) -> str:
        environments = {
            "dev": "https://jsonplaceholder.typicode.com",
            "staging": "https://jsonplaceholder.typicode.com",
            "prod": "https://jsonplaceholder.typicode.com"
        }
        return environments.get(self.ENV, environments["dev"])

settings = Settings()