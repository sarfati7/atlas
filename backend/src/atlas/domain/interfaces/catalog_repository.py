"""Catalog repository interface - Abstract contract for catalog item data access."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from atlas.domain.entities.catalog_item import CatalogItem, CatalogItemType


@dataclass
class PaginatedResult:
    """Container for paginated query results."""

    items: list[CatalogItem]
    total: int


class AbstractCatalogRepository(ABC):
    """
    Abstract repository interface for CatalogItem entity.

    Handles metadata storage for skills, MCPs, and tools.
    Actual content is managed by ContentRepository.
    """

    @abstractmethod
    async def get_by_id(self, item_id: UUID) -> Optional[CatalogItem]:
        """Retrieve a catalog item by its unique identifier."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_git_path(self, git_path: str) -> Optional[CatalogItem]:
        """Retrieve a catalog item by its git file path."""
        raise NotImplementedError

    @abstractmethod
    async def save(self, item: CatalogItem) -> CatalogItem:
        """
        Save a catalog item (create or update).

        Returns the saved item with any generated fields populated.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, item_id: UUID) -> bool:
        """
        Delete a catalog item by its ID.

        Returns True if item was deleted, False if not found.
        """
        raise NotImplementedError

    @abstractmethod
    async def list_by_type(self, item_type: CatalogItemType) -> list[CatalogItem]:
        """Retrieve all catalog items of a specific type."""
        raise NotImplementedError

    @abstractmethod
    async def list_all(self) -> list[CatalogItem]:
        """Retrieve all catalog items."""
        raise NotImplementedError

    @abstractmethod
    async def search(self, query: str) -> list[CatalogItem]:
        """
        Search catalog items by name, description, or tags.

        Returns items matching the search query.
        """
        raise NotImplementedError

    @abstractmethod
    async def list_by_author(self, author_id: UUID) -> list[CatalogItem]:
        """Retrieve all catalog items created by a specific user."""
        raise NotImplementedError

    @abstractmethod
    async def list_by_team(self, team_id: UUID) -> list[CatalogItem]:
        """Retrieve all catalog items belonging to a specific team."""
        raise NotImplementedError

    @abstractmethod
    async def list_by_tag(self, tag: str) -> list[CatalogItem]:
        """Retrieve all catalog items with a specific tag."""
        raise NotImplementedError

    @abstractmethod
    async def exists(self, item_id: UUID) -> bool:
        """Check if a catalog item exists by its ID."""
        raise NotImplementedError

    @abstractmethod
    async def list_paginated(
        self,
        offset: int,
        limit: int,
        item_type: Optional[CatalogItemType] = None,
        search_query: Optional[str] = None,
    ) -> PaginatedResult:
        """
        Retrieve paginated catalog items with optional filtering.

        Args:
            offset: Number of items to skip
            limit: Maximum items to return
            item_type: Filter by item type (SKILL, MCP, TOOL)
            search_query: Search in name, description, tags (case-insensitive)

        Returns:
            PaginatedResult with items and total count
        """
        raise NotImplementedError
