"""Team entity - Represents a group of users."""

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Team(BaseModel):
    """
    Team domain entity.

    Represents a group of developers who share skills, MCPs, and tools.
    """

    id: UUID = Field(default_factory=uuid4)
    name: str
    member_ids: list[UUID] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"frozen": False}

    def add_member(self, user_id: UUID) -> None:
        """Add a member to the team."""
        if user_id not in self.member_ids:
            self.member_ids.append(user_id)
            self.updated_at = datetime.utcnow()

    def remove_member(self, user_id: UUID) -> None:
        """Remove a member from the team."""
        if user_id in self.member_ids:
            self.member_ids.remove(user_id)
            self.updated_at = datetime.utcnow()

    def has_member(self, user_id: UUID) -> bool:
        """Check if a user is a member of this team."""
        return user_id in self.member_ids

    @property
    def member_count(self) -> int:
        """Return the number of members in this team."""
        return len(self.member_ids)
