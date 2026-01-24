"""PostgreSQL implementation of Configuration repository."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from atlas.adapters.postgresql.models import UserConfigurationModel
from atlas.domain.entities import UserConfiguration
from atlas.domain.interfaces import AbstractConfigurationRepository


class PostgresConfigurationRepository(AbstractConfigurationRepository):
    """PostgreSQL-backed configuration repository implementation."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with async database session."""
        self._session = session

    async def get_by_user_id(self, user_id: UUID) -> Optional[UserConfiguration]:
        """Get configuration for a user."""
        statement = select(UserConfigurationModel).where(
            UserConfigurationModel.user_id == user_id
        )
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def get_by_id(self, config_id: UUID) -> Optional[UserConfiguration]:
        """Get configuration by its ID."""
        statement = select(UserConfigurationModel).where(
            UserConfigurationModel.id == config_id
        )
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def save(self, config: UserConfiguration) -> UserConfiguration:
        """Save or update configuration (upsert by user_id)."""
        existing = await self._session.get(UserConfigurationModel, config.id)

        if existing:
            # Update existing
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
                # Update existing config for user
                existing_for_user.git_path = config.git_path
                existing_for_user.current_commit_sha = config.current_commit_sha
                existing_for_user.updated_at = datetime.utcnow()
                self._session.add(existing_for_user)
                await self._session.commit()
                return self._to_entity(existing_for_user)
            else:
                # Create new
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

        # Re-fetch to get updated values
        statement = select(UserConfigurationModel).where(
            UserConfigurationModel.id == config.id
        )
        result = await self._session.execute(statement)
        saved_model = result.scalar_one_or_none()
        if saved_model:
            return self._to_entity(saved_model)

        # If saved by user_id instead of config.id, fetch that
        statement = select(UserConfigurationModel).where(
            UserConfigurationModel.user_id == config.user_id
        )
        result = await self._session.execute(statement)
        saved_model = result.scalar_one()
        return self._to_entity(saved_model)

    async def delete(self, config_id: UUID) -> bool:
        """Delete configuration by its ID."""
        model = await self._session.get(UserConfigurationModel, config_id)
        if not model:
            return False
        await self._session.delete(model)
        await self._session.commit()
        return True

    def _to_entity(self, model: UserConfigurationModel) -> UserConfiguration:
        """Convert SQLModel to domain entity."""
        return UserConfiguration(
            id=model.id,
            user_id=model.user_id,
            git_path=model.git_path,
            current_commit_sha=model.current_commit_sha,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
