"""User entity - Represents a platform user."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class User(BaseModel):
    """
    User domain entity.

    Represents a developer who can discover and use skills, MCPs, and tools.
    Users can belong to multiple teams.
    """

    id: UUID = Field(default_factory=uuid4)
    email: str
    username: str
    password_hash: Optional[str] = None
    team_ids: list[UUID] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"frozen": False}

    def add_to_team(self, team_id: UUID) -> None:
        """Add user to a team."""
        if team_id not in self.team_ids:
            self.team_ids.append(team_id)
            self.updated_at = datetime.utcnow()

    def remove_from_team(self, team_id: UUID) -> None:
        """Remove user from a team."""
        if team_id in self.team_ids:
            self.team_ids.remove(team_id)
            self.updated_at = datetime.utcnow()

    def is_member_of(self, team_id: UUID) -> bool:
        """Check if user is a member of a team."""
        return team_id in self.team_ids
