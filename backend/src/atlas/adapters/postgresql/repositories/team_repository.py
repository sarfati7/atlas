"""PostgreSQL implementation of Team repository."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from atlas.adapters.postgresql.models import TeamModel, UserTeamLink
from atlas.domain.entities.team import Team
from atlas.domain.interfaces.team_repository import AbstractTeamRepository


class PostgresTeamRepository(AbstractTeamRepository):
    """PostgreSQL-backed team repository implementation."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with async database session."""
        self._session = session

    def _model_to_entity(self, model: TeamModel) -> Team:
        """Convert SQLModel to domain entity."""
        return Team(
            id=model.id,
            name=model.name,
            member_ids=[member.id for member in model.members] if model.members else [],
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model(self, entity: Team) -> TeamModel:
        """Convert domain entity to SQLModel."""
        return TeamModel(
            id=entity.id,
            name=entity.name,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, team_id: UUID) -> Optional[Team]:
        """Retrieve a team by its unique identifier."""
        statement = select(TeamModel).where(TeamModel.id == team_id)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_name(self, name: str) -> Optional[Team]:
        """Retrieve a team by its name."""
        statement = select(TeamModel).where(TeamModel.name == name)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def save(self, team: Team) -> Team:
        """Save a team (create or update)."""
        existing = await self._session.get(TeamModel, team.id)
        if existing:
            existing.name = team.name
            existing.updated_at = team.updated_at
            self._session.add(existing)
        else:
            model = self._entity_to_model(team)
            self._session.add(model)
        await self._session.commit()

        # Re-fetch to get updated relationships
        statement = select(TeamModel).where(TeamModel.id == team.id)
        result = await self._session.execute(statement)
        saved_model = result.scalar_one()
        return self._model_to_entity(saved_model)

    async def delete(self, team_id: UUID) -> bool:
        """Delete a team by its ID."""
        model = await self._session.get(TeamModel, team_id)
        if not model:
            return False
        await self._session.delete(model)
        await self._session.commit()
        return True

    async def list_all(self) -> list[Team]:
        """Retrieve all teams."""
        statement = select(TeamModel)
        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [self._model_to_entity(m) for m in models]

    async def get_user_teams(self, user_id: UUID) -> list[Team]:
        """Retrieve all teams that a user belongs to."""
        statement = (
            select(TeamModel)
            .join(UserTeamLink)
            .where(UserTeamLink.user_id == user_id)
        )
        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [self._model_to_entity(m) for m in models]

    async def exists(self, team_id: UUID) -> bool:
        """Check if a team exists by its ID."""
        statement = select(TeamModel.id).where(TeamModel.id == team_id)
        result = await self._session.execute(statement)
        return result.scalar_one_or_none() is not None
