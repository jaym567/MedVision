"""
Configuration Management

Uses pydantic-settings for type-safe configuration from environment variables.
Supports multiple environments (development, staging, production).
"""

from typing import List, Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings are validated at startup, preventing runtime configuration errors.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    
    # Application Settings
    APP_NAME: str = "MedVision AI"
    APP_VERSION: str = "0.1.0"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"]
    )
    
    # Database Configuration
    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL connection string"
    )
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Security
    JWT_SECRET_KEY: str = Field(..., min_length=32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Storage
    LOCAL_STORAGE_ROOT: str = "/app/storage"
    MAX_UPLOAD_SIZE_MB: int = 500
    
    # AI Configuration (Future)
    ENABLE_MOCK_MODELS: bool = True
    DEFAULT_MODEL_KEY: str = "chest_xray_classifier"
    MODEL_STORAGE_PATH: str = "/app/models"
    INFERENCE_DEVICE: Literal["cpu", "cuda"] = "cpu"
    
    # LLM Configuration (Future)
    LLM_PROVIDER: str = "openai"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 2000
    
    # RAG Configuration (Future)
    ENABLE_RAG: bool = False
    VECTOR_DB_PATH: str = "/app/vector_db"
    
    # Logging
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    ENABLE_METRICS: bool = True
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.APP_ENV == "production"
    
    @property
    def max_upload_size_bytes(self) -> int:
        """Convert max upload size to bytes."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


# Global settings instance
settings = Settings()