"""UserConfiguration entity - Represents a user's configuration file."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


@dataclass
class ConfigurationVersion:
    """Represents a version (commit) of a configuration file."""

    commit_sha: str
    message: str
    author: str
    timestamp: datetime


class UserConfiguration(BaseModel):
    """
    UserConfiguration domain entity.

    Tracks metadata about a user's claude.md configuration file.
    Actual content is stored in git; this tracks the git path and current version.
    """

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    git_path: str  # e.g., "configs/users/{user_id}/claude.md"
    current_commit_sha: str = ""  # Empty until first save
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"frozen": False}

    def update_commit(self, commit_sha: str) -> None:
        """Update the current commit SHA after saving content."""
        self.current_commit_sha = commit_sha
        self.updated_at = datetime.utcnow()
