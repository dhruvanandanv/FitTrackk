import os
from typing import List
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEV_DEFAULT_SECRET = "fittrack-super-secret-key-change-in-production-2026-secure-32chars"


class Settings(BaseSettings):
    PROJECT_NAME: str = "FitTrack"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./fittrack.db"
    
    # Security
    SECRET_KEY: str = DEV_DEFAULT_SECRET
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    CORS_ORIGINS: str = "*"  # comma-separated origins or "*"
    
    # External APIs (Optional)
    USDA_API_KEY: str = ""
    AI_API_KEY: str = ""
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        is_prod = self.ENVIRONMENT.lower() == "production"
        
        # Ensure JWT_SECRET_KEY defaults to SECRET_KEY if left empty or default
        if not self.JWT_SECRET_KEY or self.JWT_SECRET_KEY == DEV_DEFAULT_SECRET:
            self.JWT_SECRET_KEY = self.SECRET_KEY
            
        if is_prod:
            if not self.SECRET_KEY or self.SECRET_KEY == DEV_DEFAULT_SECRET or len(self.SECRET_KEY) < 32:
                raise ValueError(
                    "CRITICAL SECURITY CONFIGURATION: In production mode (ENVIRONMENT=production), "
                    "SECRET_KEY must be set to a secure, random string (minimum 32 characters) via environment variables. "
                    "Default development secrets cannot be used in production."
                )
            if self.DATABASE_URL.startswith("sqlite"):
                raise ValueError(
                    "CRITICAL DATABASE CONFIGURATION: In production mode (ENVIRONMENT=production), "
                    "a managed database (such as Neon PostgreSQL) must be configured via DATABASE_URL. "
                    "SQLite cannot be used in production."
                )
        return self

    @property
    def cors_origins_list(self) -> List[str]:
        if not self.CORS_ORIGINS or self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def normalized_database_url(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        if ("neon.tech" in url) and ("sslmode=" not in url):
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}sslmode=require"
        return url


settings = Settings()
