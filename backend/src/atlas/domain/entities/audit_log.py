"""AuditLog entity - Tracks who changed what and when."""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AuditLog(BaseModel):
    """
    Audit log domain entity.

    Captures who made a change, what was changed, and when.
    Used for tracking all modifications to system resources.
    """

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    action: str  # e.g., "user.created", "team.updated", "config.saved"
    resource_type: str  # e.g., "user", "team", "configuration"
    resource_id: UUID
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"frozen": True}
