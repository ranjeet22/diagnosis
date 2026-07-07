import json
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized configuration management for Diagnōsis backend.
    Uses Pydantic Settings to load and validate configurations from environment variables.
    """
    # Application Settings
    APP_NAME: str = "Diagnōsis"
    APP_ENV: str = "development"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            try:
                # If it looks like a JSON array, parse it
                if v.startswith("[") and v.endswith("]"):
                    return json.loads(v)
                return [x.strip() for x in v.split(",") if x.strip()]
            except Exception:
                return [v]
        return v

    # Central Logging Configuration
    LOG_LEVEL: str = "info"
    LOG_FILE_PATH: str = "logs/app.log"
    LOG_FORMAT: str = "text"  # text or json

    # Storage Settings
    STORAGE_TYPE: str = "local"  # local or gcs
    STORAGE_LOCAL_DIR: str = "storage/uploads"
    STORAGE_MAX_FILE_SIZE_MB: int = 50

    # Google Cloud Configuration
    GCP_PROJECT_ID: str = ""
    GCP_SERVICE_ACCOUNT_KEY_JSON: str = ""

    # Google Cloud Storage
    GCS_BUCKET_NAME: str = ""

    # Google BigQuery
    BQ_DATASET_ID: str = ""

    # Gemini API Integration
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL_NAME: str = "gemini-1.5-pro"

    # Hardware / Acceleration Settings
    GPU_ENABLED: bool = False  # cuDF vs. pandas fallback

    # Future Authentication Configuration
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Instantiate settings for global imports
settings = Settings()
