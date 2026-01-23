"""PostgreSQL implementation of User repository."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from atlas.adapters.postgresql.models import UserModel, UserTeamLink
from atlas.domain.entities.user import User
from atlas.domain.interfaces.user_repository import AbstractUserRepository


class PostgresUserRepository(AbstractUserRepository):
    """PostgreSQL-backed user repository implementation."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with async database session."""
        self._session = session

    def _model_to_entity(self, model: UserModel) -> User:
        """Convert SQLModel to domain entity."""
        return User(
            id=model.id,
            email=model.email,
            username=model.username,
            team_ids=[team.id for team in model.teams] if model.teams else [],
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model(self, entity: User) -> UserModel:
        """Convert domain entity to SQLModel."""
        return UserModel(
            id=entity.id,
            email=entity.email,
            username=entity.username,
            password_hash="",  # Set separately during auth
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Retrieve a user by their unique identifier."""
        statement = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by their email address."""
        statement = select(UserModel).where(UserModel.email == email)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_username(self, username: str) -> Optional[User]:
        """Retrieve a user by their username."""
        statement = select(UserModel).where(UserModel.username == username)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def save(self, user: User) -> User:
        """Save a user (create or update)."""
        existing = await self._session.get(UserModel, user.id)
        if existing:
            existing.email = user.email
            existing.username = user.username
            existing.updated_at = user.updated_at
            self._session.add(existing)
        else:
            model = self._entity_to_model(user)
            self._session.add(model)
        await self._session.commit()

        # Re-fetch to get updated relationships
        statement = select(UserModel).where(UserModel.id == user.id)
        result = await self._session.execute(statement)
        saved_model = result.scalar_one()
        return self._model_to_entity(saved_model)

    async def delete(self, user_id: UUID) -> bool:
        """Delete a user by their ID."""
        model = await self._session.get(UserModel, user_id)
        if not model:
            return False
        await self._session.delete(model)
        await self._session.commit()
        return True

    async def list_all(self) -> list[User]:
        """Retrieve all users."""
        statement = select(UserModel)
        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [self._model_to_entity(m) for m in models]

    async def exists(self, user_id: UUID) -> bool:
        """Check if a user exists by their ID."""
        statement = select(UserModel.id).where(UserModel.id == user_id)
        result = await self._session.execute(statement)
        return result.scalar_one_or_none() is not None
