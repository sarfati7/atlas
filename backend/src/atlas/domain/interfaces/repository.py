"""Unified repository interface - Abstract contract for all data access."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from atlas.domain.entities import CatalogItem, CatalogItemType, Team, User, UserConfiguration


@dataclass
class PaginatedResult:
    """Container for paginated query results."""

    items: list[CatalogItem]
    total: int


class AbstractRepository(ABC):
    """
    Unified repository interface for all database operations.

    Single interface for User, Team, CatalogItem, and UserConfiguration entities.
    Implementations: PostgreSQL (production), SQLite (tests via same class).
    """

    # -------------------------------------------------------------------------
    # User operations
    # -------------------------------------------------------------------------

    @abstractmethod
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Retrieve a user by their unique identifier."""
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by their email address."""
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Retrieve a user by their username."""
        raise NotImplementedError

    @abstractmethod
    async def save_user(self, user: User) -> User:
        """Save a user (create or update)."""
        raise NotImplementedError

    @abstractmethod
    async def delete_user(self, user_id: UUID) -> bool:
        """Delete a user. Returns True if deleted, False if not found."""
        raise NotImplementedError

    @abstractmethod
    async def list_users(self) -> list[User]:
        """Retrieve all users."""
        raise NotImplementedError

    # -------------------------------------------------------------------------
    # Team operations
    # -------------------------------------------------------------------------

    @abstractmethod
    async def get_team_by_id(self, team_id: UUID) -> Optional[Team]:
        """Retrieve a team by its unique identifier."""
        raise NotImplementedError

    @abstractmethod
    async def get_team_by_name(self, name: str) -> Optional[Team]:
        """Retrieve a team by its name."""
        raise NotImplementedError

    @abstractmethod
    async def save_team(self, team: Team) -> Team:
        """Save a team (create or update)."""
        raise NotImplementedError

    @abstractmethod
    async def delete_team(self, team_id: UUID) -> bool:
        """Delete a team. Returns True if deleted, False if not found."""
        raise NotImplementedError

    @abstractmethod
    async def list_teams(self) -> list[Team]:
        """Retrieve all teams."""
        raise NotImplementedError

    @abstractmethod
    async def get_user_teams(self, user_id: UUID) -> list[Team]:
        """Retrieve all teams that a user belongs to."""
        raise NotImplementedError

    # -------------------------------------------------------------------------
    # Catalog operations
    # -------------------------------------------------------------------------

    @abstractmethod
    async def get_catalog_item_by_id(self, item_id: UUID) -> Optional[CatalogItem]:
        """Retrieve a catalog item by its unique identifier."""
        raise NotImplementedError

    @abstractmethod
    async def get_catalog_item_by_git_path(self, git_path: str) -> Optional[CatalogItem]:
        """Retrieve a catalog item by its git file path."""
        raise NotImplementedError

    @abstractmethod
    async def save_catalog_item(self, item: CatalogItem) -> CatalogItem:
        """Save a catalog item (create or update)."""
        raise NotImplementedError

    @abstractmethod
    async def delete_catalog_item(self, item_id: UUID) -> bool:
        """Delete a catalog item. Returns True if deleted, False if not found."""
        raise NotImplementedError

    @abstractmethod
    async def list_catalog_items(self) -> list[CatalogItem]:
        """Retrieve all catalog items."""
        raise NotImplementedError

    @abstractmethod
    async def list_catalog_items_by_type(self, item_type: CatalogItemType) -> list[CatalogItem]:
        """Retrieve all catalog items of a specific type."""
        raise NotImplementedError

    @abstractmethod
    async def list_catalog_items_paginated(
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
        """
        raise NotImplementedError

    @abstractmethod
    async def search_catalog_items(self, query: str) -> list[CatalogItem]:
        """Search catalog items by name, description, or tags."""
        raise NotImplementedError

    # -------------------------------------------------------------------------
    # Configuration operations
    # -------------------------------------------------------------------------

    @abstractmethod
    async def get_configuration_by_user_id(self, user_id: UUID) -> Optional[UserConfiguration]:
        """Get configuration for a user. Returns None if no configuration."""
        raise NotImplementedError

    @abstractmethod
    async def get_configuration_by_id(self, config_id: UUID) -> Optional[UserConfiguration]:
        """Get configuration by its ID."""
        raise NotImplementedError

    @abstractmethod
    async def save_configuration(self, config: UserConfiguration) -> UserConfiguration:
        """Save or update configuration (upsert by user_id)."""
        raise NotImplementedError

    @abstractmethod
    async def delete_configuration(self, config_id: UUID) -> bool:
        """Delete configuration. Returns True if deleted, False if not found."""
        raise NotImplementedError
