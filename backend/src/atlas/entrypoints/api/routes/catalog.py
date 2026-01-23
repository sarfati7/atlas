"""Catalog routes - Browse skills, MCPs, and tools."""

import math
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query
from pydantic import BaseModel

from atlas.domain.entities.catalog_item import CatalogItemType
from atlas.entrypoints.dependencies import CatalogRepo

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


@router.get("", response_model=PaginatedCatalog)
async def list_catalog(
    catalog_repo: CatalogRepo,
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

    result = await catalog_repo.list_paginated(
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
