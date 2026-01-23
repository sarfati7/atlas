"""PostgreSQL implementation of Catalog repository."""

import json
from typing import Optional
from uuid import UUID

from sqlalchemy import or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from atlas.adapters.postgresql.models import CatalogItemModel
from atlas.domain.entities.catalog_item import CatalogItem, CatalogItemType
from atlas.domain.interfaces.catalog_repository import AbstractCatalogRepository


class PostgresCatalogRepository(AbstractCatalogRepository):
    """PostgreSQL-backed catalog repository implementation."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with async database session."""
        self._session = session

    def _model_to_entity(self, model: CatalogItemModel) -> CatalogItem:
        """Convert SQLModel to domain entity."""
        tags = json.loads(model.tags) if model.tags else []
        return CatalogItem(
            id=model.id,
            type=model.type,
            name=model.name,
            description=model.description,
            git_path=model.git_path,
            author_id=model.author_id,
            team_id=model.team_id,
            tags=tags,
            usage_count=model.usage_count,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model(self, entity: CatalogItem) -> CatalogItemModel:
        """Convert domain entity to SQLModel."""
        return CatalogItemModel(
            id=entity.id,
            type=entity.type,
            name=entity.name,
            description=entity.description,
            git_path=entity.git_path,
            author_id=entity.author_id,
            team_id=entity.team_id,
            tags=json.dumps(entity.tags),
            usage_count=entity.usage_count,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, item_id: UUID) -> Optional[CatalogItem]:
        """Retrieve a catalog item by its unique identifier."""
        statement = select(CatalogItemModel).where(CatalogItemModel.id == item_id)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_git_path(self, git_path: str) -> Optional[CatalogItem]:
        """Retrieve a catalog item by its git file path."""
        statement = select(CatalogItemModel).where(CatalogItemModel.git_path == git_path)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

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
            model = self._entity_to_model(item)
            self._session.add(model)
        await self._session.commit()

        # Re-fetch to confirm saved
        statement = select(CatalogItemModel).where(CatalogItemModel.id == item.id)
        result = await self._session.execute(statement)
        saved_model = result.scalar_one()
        return self._model_to_entity(saved_model)

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
        return [self._model_to_entity(m) for m in models]

    async def list_all(self) -> list[CatalogItem]:
        """Retrieve all catalog items."""
        statement = select(CatalogItemModel)
        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [self._model_to_entity(m) for m in models]

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
        return [self._model_to_entity(m) for m in models]

    async def list_by_author(self, author_id: UUID) -> list[CatalogItem]:
        """Retrieve all catalog items created by a specific user."""
        statement = select(CatalogItemModel).where(
            CatalogItemModel.author_id == author_id
        )
        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [self._model_to_entity(m) for m in models]

    async def list_by_team(self, team_id: UUID) -> list[CatalogItem]:
        """Retrieve all catalog items belonging to a specific team."""
        statement = select(CatalogItemModel).where(
            CatalogItemModel.team_id == team_id
        )
        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [self._model_to_entity(m) for m in models]

    async def list_by_tag(self, tag: str) -> list[CatalogItem]:
        """Retrieve all catalog items with a specific tag."""
        # Search for tag in JSON array stored as string
        search_pattern = f'%"{tag.lower().strip()}"%'
        statement = select(CatalogItemModel).where(
            CatalogItemModel.tags.ilike(search_pattern)
        )
        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [self._model_to_entity(m) for m in models]

    async def exists(self, item_id: UUID) -> bool:
        """Check if a catalog item exists by its ID."""
        statement = select(CatalogItemModel.id).where(CatalogItemModel.id == item_id)
        result = await self._session.execute(statement)
        return result.scalar_one_or_none() is not None
