"""PostgreSQL implementation of Catalog repository."""

import json
from typing import Optional
from uuid import UUID

from sqlalchemy import or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from atlas.adapters.postgresql.converters import (
    catalog_item_entity_to_model,
    catalog_item_model_to_entity,
)
from atlas.adapters.postgresql.models import CatalogItemModel
from atlas.domain.entities.catalog_item import CatalogItem, CatalogItemType
from atlas.domain.interfaces.catalog_repository import AbstractCatalogRepository


class PostgresCatalogRepository(AbstractCatalogRepository):
    """PostgreSQL-backed catalog repository implementation."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with async database session."""
        self._session = session

    async def get_by_id(self, item_id: UUID) -> Optional[CatalogItem]:
        """Retrieve a catalog item by its unique identifier."""
        statement = select(CatalogItemModel).where(CatalogItemModel.id == item_id)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return catalog_item_model_to_entity(model) if model else None

    async def get_by_git_path(self, git_path: str) -> Optional[CatalogItem]:
        """Retrieve a catalog item by its git file path."""
        statement = select(CatalogItemModel).where(CatalogItemModel.git_path == git_path)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return catalog_item_model_to_entity(model) if model else None

    async def save(self, item: CatalogItem) -> CatalogItem:
        """Save a catalog item (create or update)."""
        existing = await self._session.get(CatalogItemModel, item.id)
        if existing:
            existing.type = item.type
            existing.name = item.name
            existing.description = item.description
            existing.git_path = item.git_path
            existing.author_id = item.author_id
            existing.team_id = item.team_id
            existing.tags = json.dumps(item.tags)
            existing.usage_count = item.usage_count
            existing.updated_at = item.updated_at
            self._session.add(existing)
        else:
            model = catalog_item_entity_to_model(item)
            self._session.add(model)
        await self._session.commit()

        # Re-fetch to confirm saved
        statement = select(CatalogItemModel).where(CatalogItemModel.id == item.id)
        result = await self._session.execute(statement)
        saved_model = result.scalar_one()
        return catalog_item_model_to_entity(saved_model)

    async def delete(self, item_id: UUID) -> bool:
        """Delete a catalog item by its ID."""
        model = await self._session.get(CatalogItemModel, item_id)
        if not model:
            return False
        await self._session.delete(model)
        await self._session.commit()
        return True

    async def list_by_type(self, item_type: CatalogItemType) -> list[CatalogItem]:
        """Retrieve all catalog items of a specific type."""
        statement = select(CatalogItemModel).where(CatalogItemModel.type == item_type)
        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [catalog_item_model_to_entity(m) for m in models]

    async def list_all(self) -> list[CatalogItem]:
        """Retrieve all catalog items."""
        statement = select(CatalogItemModel)
        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [catalog_item_model_to_entity(m) for m in models]

    async def search(self, query: str) -> list[CatalogItem]:
        """Search catalog items by name, description, or tags."""
        search_pattern = f"%{query}%"
        statement = select(CatalogItemModel).where(
            or_(
                CatalogItemModel.name.ilike(search_pattern),
                CatalogItemModel.description.ilike(search_pattern),
                CatalogItemModel.tags.ilike(search_pattern),
            )
        )
        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [catalog_item_model_to_entity(m) for m in models]

    async def list_by_author(self, author_id: UUID) -> list[CatalogItem]:
        """Retrieve all catalog items created by a specific user."""
        statement = select(CatalogItemModel).where(
            CatalogItemModel.author_id == author_id
        )
        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [catalog_item_model_to_entity(m) for m in models]

    async def list_by_team(self, team_id: UUID) -> list[CatalogItem]:
        """Retrieve all catalog items belonging to a specific team."""
        statement = select(CatalogItemModel).where(
            CatalogItemModel.team_id == team_id
        )
        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [catalog_item_model_to_entity(m) for m in models]

    async def list_by_tag(self, tag: str) -> list[CatalogItem]:
        """Retrieve all catalog items with a specific tag."""
        # Search for tag in JSON array stored as string
        search_pattern = f'%"{tag.lower().strip()}"%'
        statement = select(CatalogItemModel).where(
            CatalogItemModel.tags.ilike(search_pattern)
        )
        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [catalog_item_model_to_entity(m) for m in models]

    async def exists(self, item_id: UUID) -> bool:
        """Check if a catalog item exists by its ID."""
        statement = select(CatalogItemModel.id).where(CatalogItemModel.id == item_id)
        result = await self._session.execute(statement)
        return result.scalar_one_or_none() is not None
