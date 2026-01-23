"""Application configuration via pydantic-settings."""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # Debug mode
    debug: bool = False


settings = Settings()
