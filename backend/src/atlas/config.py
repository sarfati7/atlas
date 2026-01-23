"""Application configuration via pydantic-settings."""

import warnings
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


# Development-only default secret - NEVER use in production
_DEV_SECRET_KEY = "dev-secret-key-change-in-production"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database URLs
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/atlas"
    database_url_sync: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/atlas"

    # GitHub integration
    github_token: Optional[str] = None
    github_repo: Optional[str] = None
    github_webhook_secret: Optional[str] = None

    # Authentication settings
    secret_key: str = _DEV_SECRET_KEY
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Frontend URL (for password reset links)
    frontend_url: str = "http://localhost:3000"

    # Email settings (optional - uses console output if not configured)
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    email_from: str = "noreply@atlas.local"

    # Debug mode
    debug: bool = False


settings = Settings()

# Warn if using default secret key
if settings.secret_key == _DEV_SECRET_KEY:
    warnings.warn(
        "Using default SECRET_KEY. Set SECRET_KEY environment variable in production!",
        UserWarning,
        stacklevel=1,
    )
