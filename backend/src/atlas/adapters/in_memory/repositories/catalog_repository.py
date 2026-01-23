"""In-memory implementation of Catalog repository for testing."""

from typing import Optional
from uuid import UUID

from atlas.domain.entities.catalog_item import CatalogItem, CatalogItemType
from atlas.domain.interfaces.catalog_repository import AbstractCatalogRepository


class InMemoryCatalogRepository(AbstractCatalogRepository):
    """In-memory catalog repository implementation for testing."""

    def __init__(self) -> None:
        """Initialize with empty storage."""
        self._items: dict[UUID, CatalogItem] = {}

    def clear(self) -> None:
        """Reset storage (useful in tests)."""
        self._items.clear()

    async def get_by_id(self, item_id: UUID) -> Optional[CatalogItem]:
        """Retrieve a catalog item by its unique identifier."""
        return self._items.get(item_id)

    async def get_by_git_path(self, git_path: str) -> Optional[CatalogItem]:
        """Retrieve a catalog item by its git file path."""
        for item in self._items.values():
            if item.git_path == git_path:
                return item
        return None

    async def save(self, item: CatalogItem) -> CatalogItem:
        """Save a catalog item (create or update)."""
        self._items[item.id] = item
        return item

    async def delete(self, item_id: UUID) -> bool:
        """Delete a catalog item by its ID."""
        if item_id in self._items:
            del self._items[item_id]
            return True
        return False

    async def list_by_type(self, item_type: CatalogItemType) -> list[CatalogItem]:
        """Retrieve all catalog items of a specific type."""
        return [item for item in self._items.values() if item.type == item_type]

    async def list_all(self) -> list[CatalogItem]:
        """Retrieve all catalog items."""
        return list(self._items.values())

    async def search(self, query: str) -> list[CatalogItem]:
        """Search catalog items by name, description, or tags."""
        query_lower = query.lower()
        results = []
        for item in self._items.values():
            if (
                query_lower in item.name.lower()
                or query_lower in item.description.lower()
                or any(query_lower in tag.lower() for tag in item.tags)
            ):
                results.append(item)
        return results

    async def list_by_author(self, author_id: UUID) -> list[CatalogItem]:
        """Retrieve all catalog items created by a specific user."""
        return [item for item in self._items.values() if item.author_id == author_id]

    async def list_by_team(self, team_id: UUID) -> list[CatalogItem]:
        """Retrieve all catalog items belonging to a specific team."""
        return [item for item in self._items.values() if item.team_id == team_id]

    async def list_by_tag(self, tag: str) -> list[CatalogItem]:
        """Retrieve all catalog items with a specific tag."""
        normalized_tag = tag.lower().strip()
        return [item for item in self._items.values() if normalized_tag in item.tags]

    async def exists(self, item_id: UUID) -> bool:
        """Check if a catalog item exists by its ID."""
        return item_id in self._items
