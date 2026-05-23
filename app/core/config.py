import os
from pathlib import Path
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Automatically tracks down the exact directory of this config.py file (app/core)
CORE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    model_config = SettingsConfigDict(
        # Steps out of core/ and targets app/.env perfectly every time
        env_file=os.path.join(CORE_DIR.parent, ".env"),
        extra="ignore"
    )

# This will now initialize without a single hitch anywhere in your app!
settings = Settings()

def get_settings() -> Settings:
    return settings
