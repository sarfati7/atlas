"""Manual sync endpoint for administrative catalog synchronization."""

from typing import Annotated

from fastapi import APIRouter, Depends

from atlas.domain.interfaces import AbstractSyncService
from atlas.entrypoints.dependencies import get_sync_service

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/full")
async def full_sync(
    sync_service: Annotated[AbstractSyncService, Depends(get_sync_service)],
) -> dict:
    """
    Trigger a full sync between git content and database catalog.

    This compares ALL files in git with ALL catalog items in database
    and reconciles differences. Useful for:
    - Initial population of catalog after setup
    - Recovering from missed webhooks
    - Manual consistency checks

    Note: In production, this should be protected by admin authentication.
    """
    result = await sync_service.sync_all()

    return {
        "status": "ok",
        "created": result.created,
        "updated": result.updated,
        "deleted": result.deleted,
        "errors": result.errors,
    }
