"""Catalog routes - Browse skills, MCPs, and tools."""

import math
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from atlas.domain.entities.catalog_item import CatalogItemType
from atlas.entrypoints.dependencies import ContentRepo, Repo

router = APIRouter(prefix="/catalog", tags=["catalog"])


class CatalogItemSummary(BaseModel):
    """Summary view for catalog list (excludes documentation)."""

    id: UUID
    type: CatalogItemType
    name: str
    description: str
    tags: list[str]
    author_id: UUID
    team_id: Optional[UUID]
    usage_count: int


class PaginatedCatalog(BaseModel):
    """Paginated catalog response."""

    items: list[CatalogItemSummary]
    total: int
    page: int
    size: int
    pages: int


class CatalogItemDetail(BaseModel):
    """Detail view with full documentation from git."""

    id: UUID
    type: CatalogItemType
    name: str
    description: str
    git_path: str
    tags: list[str]
    author_id: UUID
    team_id: Optional[UUID]
    usage_count: int
    created_at: datetime
    updated_at: datetime
    documentation: str  # README content from git


def _get_readme_path(git_path: str) -> str:
    """
    Derive README path from item's git path.

    Convention: If item is at skills/my-skill/config.yaml,
    look for skills/my-skill/README.md
    """
    if "/" in git_path:
        directory = git_path.rsplit("/", 1)[0]
        return f"{directory}/README.md"
    return "README.md"


@router.get("", response_model=PaginatedCatalog)
async def list_catalog(
    repo: Repo,
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    size: int = Query(default=20, ge=1, le=100, description="Items per page (max 100)"),
    type: Optional[CatalogItemType] = Query(default=None, description="Filter by type"),
    q: Optional[str] = Query(default=None, min_length=1, description="Search keyword"),
) -> PaginatedCatalog:
    """
    List catalog items with pagination, filtering, and search.

    - **page**: Page number starting from 1
    - **size**: Number of items per page (1-100)
    - **type**: Filter by item type (skill, mcp, tool)
    - **q**: Search in name, description, and tags (case-insensitive)

    Returns all skills, MCPs, and tools available company-wide.
    """
    offset = (page - 1) * size

    result = await repo.list_catalog_items_paginated(
        offset=offset,
        limit=size,
        item_type=type,
        search_query=q,
    )

    pages = math.ceil(result.total / size) if result.total > 0 else 1

    items = [
        CatalogItemSummary(
            id=item.id,
            type=item.type,
            name=item.name,
            description=item.description,
            tags=item.tags,
            author_id=item.author_id,
            team_id=item.team_id,
            usage_count=item.usage_count,
        )
        for item in result.items
    ]

    return PaginatedCatalog(
        items=items,
        total=result.total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/{item_id}", response_model=CatalogItemDetail)
async def get_catalog_item(
    item_id: UUID,
    repo: Repo,
    content_repo: ContentRepo,
) -> CatalogItemDetail:
    """
    Get catalog item details including full documentation.

    Documentation is fetched from the git repository (README.md in item's directory).
    Returns 404 if item does not exist.

    - **item_id**: UUID of the catalog item
    """
    # Get metadata from database
    item = await repo.get_catalog_item_by_id(item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catalog item not found",
        )

    # Attempt to fetch documentation from git
    readme_path = _get_readme_path(item.git_path)
    documentation = ""
    try:
        content = await content_repo.get_content(readme_path)
        if content is not None:
            documentation = content
    except Exception:
        # Log error but don't fail - documentation is optional
        # Item metadata is still valuable without docs
        pass

    return CatalogItemDetail(
        id=item.id,
        type=item.type,
        name=item.name,
        description=item.description,
        git_path=item.git_path,
        tags=item.tags,
        author_id=item.author_id,
        team_id=item.team_id,
        usage_count=item.usage_count,
        created_at=item.created_at,
        updated_at=item.updated_at,
        documentation=documentation,
    )
