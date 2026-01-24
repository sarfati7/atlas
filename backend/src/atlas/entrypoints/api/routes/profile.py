"""Profile routes - User dashboard, available items, and effective configuration."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from atlas.application.services import UserNotFoundError
from atlas.domain.entities import CatalogItemType
from atlas.entrypoints.dependencies import CurrentUser, ProfileService


class EffectiveConfigurationResponse(BaseModel):
    """Effective configuration with inheritance breakdown."""

    content: str
    org_applied: bool
    team_applied: bool
    user_applied: bool


router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/dashboard")
async def get_dashboard(
    current_user: CurrentUser,
    profile_service: ProfileService,
):
    """
    Get current user's dashboard data.

    Returns aggregated view of user's teams, available items count, and config status.
    """
    try:
        return await profile_service.get_dashboard(current_user.id)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


@router.get("/available-items")
async def get_available_items(
    current_user: CurrentUser,
    profile_service: ProfileService,
    type: Optional[CatalogItemType] = Query(default=None, description="Filter by item type"),
):
    """
    Get catalog items available to current user.

    Returns company-wide items plus items from user's teams.
    Optionally filter by type (skill, mcp, tool).
    """
    items = await profile_service.get_available_items(current_user.id)
    if type is not None:
        items = [i for i in items if i.type == type]
    return items


@router.get("/effective-configuration")
async def get_effective_configuration(
    current_user: CurrentUser,
    profile_service: ProfileService,
) -> EffectiveConfigurationResponse:
    """
    Get user's effective configuration with inheritance chain.

    Shows merged configuration from org -> team -> user levels.
    """
    config = await profile_service.get_effective_configuration(current_user.id)
    return EffectiveConfigurationResponse(
        content=config.content,
        org_applied=bool(config.org_content),
        team_applied=bool(config.team_content),
        user_applied=bool(config.user_content),
    )
