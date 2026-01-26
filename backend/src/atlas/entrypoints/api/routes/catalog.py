"""Catalog routes - Browse skills, MCPs, and tools from git."""

import math
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from atlas.application.services.atlas_service import CatalogScope
from atlas.domain.entities.catalog_item import CatalogItemType
from atlas.entrypoints.dependencies import Atlas, CurrentUserOptional

router = APIRouter(prefix="/catalog", tags=["catalog"])


class CatalogItemSummary(BaseModel):
    """Summary view for catalog list."""

    id: str
    type: CatalogItemType
    name: str
    description: str
    tags: list[str]
    scope: CatalogScope
    scope_id: Optional[UUID] = None


class PaginatedCatalog(BaseModel):
    """Paginated catalog response."""

    items: list[CatalogItemSummary]
    total: int
    page: int
    size: int
    pages: int


class CatalogItemResponse(BaseModel):
    """Detail view with full documentation from git."""

    id: str
    type: CatalogItemType
    name: str
    description: str
    git_path: str
    tags: list[str]
    documentation: str
    scope: CatalogScope
    scope_id: Optional[UUID] = None


@router.get("", response_model=PaginatedCatalog)
async def list_catalog(
    atlas: Atlas,
    current_user: CurrentUserOptional,
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    size: int = Query(default=20, ge=1, le=100, description="Items per page (max 100)"),
    type: Optional[CatalogItemType] = Query(default=None, description="Filter by type"),
    q: Optional[str] = Query(default=None, min_length=1, description="Search keyword"),
) -> PaginatedCatalog:
    """
    List catalog items with pagination, filtering, and search.

    Visibility rules:
    - org/* items: visible to everyone
    - teams/{id}/* items: visible only to team members
    - users/{id}/* items: visible only to that user

    Anonymous users only see org-level items.
    """
    offset = (page - 1) * size

    # Get user context for visibility filtering
    user_id = current_user.id if current_user else None
    team_ids = current_user.team_ids if current_user else []

    items, total = await atlas.list_catalog_items(
        user_id=user_id,
        team_ids=team_ids,
        item_type=type,
        search_query=q,
        offset=offset,
        limit=size,
    )

    pages = math.ceil(total / size) if total > 0 else 1

    return PaginatedCatalog(
        items=[
            CatalogItemSummary(
                id=item.id,
                type=item.type,
                name=item.name,
                description=item.description,
                tags=item.tags,
                scope=item.scope,
                scope_id=item.scope_id,
            )
            for item in items
        ],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/{item_id}", response_model=CatalogItemResponse)
async def get_catalog_item(
    item_id: str,
    atlas: Atlas,
    current_user: CurrentUserOptional,
) -> CatalogItemResponse:
    """
    Get catalog item details including full documentation.

    Checks visibility based on user's team membership.
    """
    user_id = current_user.id if current_user else None
    team_ids = current_user.team_ids if current_user else []

    item = await atlas.get_catalog_item(
        item_id=item_id,
        user_id=user_id,
        team_ids=team_ids,
    )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catalog item not found",
        )

    return CatalogItemResponse(
        id=item.id,
        type=item.type,
        name=item.name,
        description=item.description,
        git_path=item.git_path,
        tags=item.tags,
        documentation=item.documentation,
        scope=item.scope,
        scope_id=item.scope_id,
    )


@router.post("/refresh", status_code=status.HTTP_204_NO_CONTENT)
async def refresh_catalog_cache(
    atlas: Atlas,
) -> None:
    """
    Force refresh the catalog cache.

    Useful after pushing changes to git repository.
    """
    await atlas.refresh_catalog_cache()
