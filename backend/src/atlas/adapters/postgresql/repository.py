"""Unified PostgreSQL repository implementation."""

import json
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from atlas.adapters.postgresql.models import (
    CatalogItemModel,
    TeamModel,
    UserConfigurationModel,
    UserModel,
    UserTeamLink,
)
from atlas.domain.entities import CatalogItem, CatalogItemType, Team, User, UserConfiguration
from atlas.domain.interfaces.repository import AbstractRepository, PaginatedResult


class Repository(AbstractRepository):
    """
    Unified PostgreSQL repository for all database operations.

    Works with any SQLAlchemy-compatible database (PostgreSQL, SQLite).
    Production uses PostgreSQL, tests can use SQLite in-memory.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with async database session."""
        self._session = session

    # -------------------------------------------------------------------------
    # User operations
    # -------------------------------------------------------------------------

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        statement = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return self._user_to_entity(model) if model else None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        statement = select(UserModel).where(UserModel.email == email)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return self._user_to_entity(model) if model else None

    async def get_user_by_username(self, username: str) -> Optional[User]:
        statement = select(UserModel).where(UserModel.username == username)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return self._user_to_entity(model) if model else None

    async def save_user(self, user: User) -> User:
        existing = await self._session.get(UserModel, user.id)
        if existing:
            existing.email = user.email
            existing.username = user.username
            existing.updated_at = user.updated_at
            if user.password_hash:
                existing.password_hash = user.password_hash
            self._session.add(existing)
        else:
            model = UserModel(
                id=user.id,
                email=user.email,
                username=user.username,
                password_hash=user.password_hash or "",
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            self._session.add(model)
        await self._session.commit()

        statement = select(UserModel).where(UserModel.id == user.id)
        result = await self._session.execute(statement)
        saved_model = result.scalar_one()
        return self._user_to_entity(saved_model)

    async def delete_user(self, user_id: UUID) -> bool:
        model = await self._session.get(UserModel, user_id)
        if not model:
            return False
        await self._session.delete(model)
        await self._session.commit()
        return True

    async def list_users(self) -> list[User]:
        statement = select(UserModel)
        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [self._user_to_entity(m) for m in models]

    def _user_to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            username=model.username,
            password_hash=model.password_hash if model.password_hash else None,
            team_ids=[team.id for team in model.teams] if model.teams else [],
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    # -------------------------------------------------------------------------
    # Team operations
    # -------------------------------------------------------------------------

    async def get_team_by_id(self, team_id: UUID) -> Optional[Team]:
        statement = select(TeamModel).where(TeamModel.id == team_id)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return self._team_to_entity(model) if model else None

    async def get_team_by_name(self, name: str) -> Optional[Team]:
        statement = select(TeamModel).where(TeamModel.name == name)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return self._team_to_entity(model) if model else None

    async def save_team(self, team: Team) -> Team:
        existing = await self._session.get(TeamModel, team.id)
        if existing:
            existing.name = team.name
            existing.updated_at = team.updated_at
            self._session.add(existing)
        else:
            model = TeamModel(
                id=team.id,
                name=team.name,
                created_at=team.created_at,
                updated_at=team.updated_at,
            )
            self._session.add(model)
        await self._session.commit()

        statement = select(TeamModel).where(TeamModel.id == team.id)
        result = await self._session.execute(statement)
        saved_model = result.scalar_one()
        return self._team_to_entity(saved_model)

    async def delete_team(self, team_id: UUID) -> bool:
        model = await self._session.get(TeamModel, team_id)
        if not model:
            return False
        await self._session.delete(model)
        await self._session.commit()
        return True

    async def list_teams(self) -> list[Team]:
        statement = select(TeamModel)
        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [self._team_to_entity(m) for m in models]

    async def get_user_teams(self, user_id: UUID) -> list[Team]:
        statement = (
            select(TeamModel)
            .join(UserTeamLink)
            .where(UserTeamLink.user_id == user_id)
        )
        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [self._team_to_entity(m) for m in models]

    def _team_to_entity(self, model: TeamModel) -> Team:
        return Team(
            id=model.id,
            name=model.name,
            member_ids=[member.id for member in model.members] if model.members else [],
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    # -------------------------------------------------------------------------
    # Catalog operations
    # -------------------------------------------------------------------------

    async def get_catalog_item_by_id(self, item_id: UUID) -> Optional[CatalogItem]:
        statement = select(CatalogItemModel).where(CatalogItemModel.id == item_id)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return self._catalog_item_to_entity(model) if model else None

    async def get_catalog_item_by_git_path(self, git_path: str) -> Optional[CatalogItem]:
        statement = select(CatalogItemModel).where(CatalogItemModel.git_path == git_path)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return self._catalog_item_to_entity(model) if model else None

    async def save_catalog_item(self, item: CatalogItem) -> CatalogItem:
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
            model = CatalogItemModel(
                id=item.id,
                type=item.type,
                name=item.name,
                description=item.description,
                git_path=item.git_path,
                author_id=item.author_id,
                team_id=item.team_id,
                tags=json.dumps(item.tags),
                usage_count=item.usage_count,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            self._session.add(model)
        await self._session.commit()

        statement = select(CatalogItemModel).where(CatalogItemModel.id == item.id)
        result = await self._session.execute(statement)
        saved_model = result.scalar_one()
        return self._catalog_item_to_entity(saved_model)

    async def delete_catalog_item(self, item_id: UUID) -> bool:
        model = await self._session.get(CatalogItemModel, item_id)
        if not model:
            return False
        await self._session.delete(model)
        await self._session.commit()
        return True

    async def list_catalog_items(self) -> list[CatalogItem]:
        statement = select(CatalogItemModel)
        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [self._catalog_item_to_entity(m) for m in models]

    async def list_catalog_items_by_type(self, item_type: CatalogItemType) -> list[CatalogItem]:
        statement = select(CatalogItemModel).where(CatalogItemModel.type == item_type)
        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [self._catalog_item_to_entity(m) for m in models]

    async def list_catalog_items_paginated(
        self,
        offset: int,
        limit: int,
        item_type: Optional[CatalogItemType] = None,
        search_query: Optional[str] = None,
    ) -> PaginatedResult:
        conditions = []

        if item_type is not None:
            conditions.append(CatalogItemModel.type == item_type)

        if search_query:
            search_pattern = f"%{search_query}%"
            conditions.append(
                or_(
                    CatalogItemModel.name.ilike(search_pattern),
                    CatalogItemModel.description.ilike(search_pattern),
                    CatalogItemModel.tags.ilike(search_pattern),
                )
            )

        # Count query
        count_stmt = select(func.count(CatalogItemModel.id))
        if conditions:
            count_stmt = count_stmt.where(*conditions)
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()

        # Select query with pagination
        select_stmt = select(CatalogItemModel).order_by(CatalogItemModel.name)
        if conditions:
            select_stmt = select_stmt.where(*conditions)
        select_stmt = select_stmt.offset(offset).limit(limit)

        result = await self._session.execute(select_stmt)
        models = result.scalars().all()

        return PaginatedResult(
            items=[self._catalog_item_to_entity(m) for m in models],
            total=total,
        )

    async def search_catalog_items(self, query: str) -> list[CatalogItem]:
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
        return [self._catalog_item_to_entity(m) for m in models]

    def _catalog_item_to_entity(self, model: CatalogItemModel) -> CatalogItem:
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

    # -------------------------------------------------------------------------
    # Configuration operations
    # -------------------------------------------------------------------------

    async def get_configuration_by_user_id(self, user_id: UUID) -> Optional[UserConfiguration]:
        statement = select(UserConfigurationModel).where(
            UserConfigurationModel.user_id == user_id
        )
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return self._config_to_entity(model) if model else None

    async def get_configuration_by_id(self, config_id: UUID) -> Optional[UserConfiguration]:
        statement = select(UserConfigurationModel).where(
            UserConfigurationModel.id == config_id
        )
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return self._config_to_entity(model) if model else None

    async def save_configuration(self, config: UserConfiguration) -> UserConfiguration:
        existing = await self._session.get(UserConfigurationModel, config.id)

        if existing:
            existing.git_path = config.git_path
            existing.current_commit_sha = config.current_commit_sha
            existing.updated_at = datetime.utcnow()
            self._session.add(existing)
        else:
            # Check if user already has a config (different ID)
            stmt = select(UserConfigurationModel).where(
                UserConfigurationModel.user_id == config.user_id
            )
            result = await self._session.execute(stmt)
            existing_for_user = result.scalar_one_or_none()

            if existing_for_user:
                existing_for_user.git_path = config.git_path
                existing_for_user.current_commit_sha = config.current_commit_sha
                existing_for_user.updated_at = datetime.utcnow()
                self._session.add(existing_for_user)
                await self._session.commit()
                return self._config_to_entity(existing_for_user)
            else:
                model = UserConfigurationModel(
                    id=config.id,
                    user_id=config.user_id,
                    git_path=config.git_path,
                    current_commit_sha=config.current_commit_sha,
                    created_at=config.created_at,
                    updated_at=config.updated_at,
                )
                self._session.add(model)

        await self._session.commit()

        # Re-fetch
        statement = select(UserConfigurationModel).where(
            UserConfigurationModel.user_id == config.user_id
        )
        result = await self._session.execute(statement)
        saved_model = result.scalar_one()
        return self._config_to_entity(saved_model)

    async def delete_configuration(self, config_id: UUID) -> bool:
        model = await self._session.get(UserConfigurationModel, config_id)
        if not model:
            return False
        await self._session.delete(model)
        await self._session.commit()
        return True

    def _config_to_entity(self, model: UserConfigurationModel) -> UserConfiguration:
        return UserConfiguration(
            id=model.id,
            user_id=model.user_id,
            git_path=model.git_path,
            current_commit_sha=model.current_commit_sha,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
