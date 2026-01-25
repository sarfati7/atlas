"""UsageEvent entity - Tracks tool usage for analytics."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from atlas.domain.entities.catalog_item import CatalogItemType


class UsageEvent(BaseModel):
    """
    UsageEvent domain entity.

    Tracks when users interact with catalog items (skills, MCPs, tools).
    Used for analytics and usage reporting.
    """

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    item_id: UUID
    item_type: CatalogItemType
    action: str  # e.g., "sync", "view", "execute"
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"frozen": True}


@dataclass(frozen=True)
class UsageStat:
    """
    Aggregated usage statistic.

    Used for grouped analytics (by user, item, or day).
    """

    key: str
    count: int
    item_type: Optional[str] = None
