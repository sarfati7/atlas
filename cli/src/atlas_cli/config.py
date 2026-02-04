"""Configuration for Atlas CLI.

Loads settings from environment variables with sensible defaults.
"""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """CLI configuration settings."""

    api_base_url: str
    timeout: float

    def __init__(self) -> None:
        """Initialize configuration from environment."""
        self.api_base_url = os.environ.get(
            "AXENT_API_URL",
            "http://localhost:8000/api/v1",
        )
        self.timeout = float(os.environ.get("AXENT_TIMEOUT", "30.0"))


config = Config()
