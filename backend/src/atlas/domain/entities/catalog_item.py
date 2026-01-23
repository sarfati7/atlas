"""CatalogItem entity - Represents a skill, MCP, or tool in the catalog."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class CatalogItemType(str, Enum):
    """Type discriminator for catalog items."""

    SKILL = "skill"
    MCP = "mcp"
    TOOL = "tool"


class CatalogItem(BaseModel):
    """
    CatalogItem domain entity.

    Single entity for all catalog items (skills, MCPs, tools) with type discriminator.
    Actual content is stored in git; this entity holds metadata.
    """

    id: UUID = Field(default_factory=uuid4)
    type: CatalogItemType
    name: str
    description: str = ""
    git_path: str
    author_id: UUID
    team_id: Optional[UUID] = None
    tags: list[str] = Field(default_factory=list)
    usage_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"frozen": False}

    def increment_usage(self) -> None:
        """Increment the usage count."""
        self.usage_count += 1
        self.updated_at = datetime.utcnow()

    def add_tag(self, tag: str) -> None:
        """Add a tag to the catalog item."""
        normalized_tag = tag.lower().strip()
        if normalized_tag and normalized_tag not in self.tags:
            self.tags.append(normalized_tag)
            self.updated_at = datetime.utcnow()

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the catalog item."""
        normalized_tag = tag.lower().strip()
        if normalized_tag in self.tags:
            self.tags.remove(normalized_tag)
            self.updated_at = datetime.utcnow()

    def has_tag(self, tag: str) -> bool:
        """Check if item has a specific tag."""
        return tag.lower().strip() in self.tags

    @property
    def is_team_owned(self) -> bool:
        """Check if this item belongs to a team."""
        return self.team_id is not None
