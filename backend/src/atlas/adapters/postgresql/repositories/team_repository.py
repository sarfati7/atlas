"""PostgreSQL implementation of Team repository."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from atlas.adapters.postgresql.converters import (
    team_entity_to_model,
    team_model_to_entity,
)
from atlas.adapters.postgresql.models import TeamModel, UserTeamLink
from atlas.domain.entities.team import Team
from atlas.domain.interfaces.team_repository import AbstractTeamRepository


class PostgresTeamRepository(AbstractTeamRepository):
    """PostgreSQL-backed team repository implementation."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with async database session."""
        self._session = session

    async def get_by_id(self, team_id: UUID) -> Optional[Team]:
        """Retrieve a team by its unique identifier."""
        statement = select(TeamModel).where(TeamModel.id == team_id)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return team_model_to_entity(model) if model else None

    async def get_by_name(self, name: str) -> Optional[Team]:
        """Retrieve a team by its name."""
        statement = select(TeamModel).where(TeamModel.name == name)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return team_model_to_entity(model) if model else None

    async def save(self, team: Team) -> Team:
        """Save a team (create or update)."""
        existing = await self._session.get(TeamModel, team.id)
        if existing:
            existing.name = team.name
            existing.updated_at = team.updated_at
            self._session.add(existing)
        else:
            model = team_entity_to_model(team)
            self._session.add(model)
        await self._session.commit()

        # Re-fetch to get updated relationships
        statement = select(TeamModel).where(TeamModel.id == team.id)
        result = await self._session.execute(statement)
        saved_model = result.scalar_one()
        return team_model_to_entity(saved_model)

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
        return [team_model_to_entity(m) for m in models]

    async def get_user_teams(self, user_id: UUID) -> list[Team]:
        """Retrieve all teams that a user belongs to."""
        statement = (
            select(TeamModel)
            .join(UserTeamLink)
            .where(UserTeamLink.user_id == user_id)
        )
        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [team_model_to_entity(m) for m in models]

    async def exists(self, team_id: UUID) -> bool:
        """Check if a team exists by its ID."""
        statement = select(TeamModel.id).where(TeamModel.id == team_id)
        result = await self._session.execute(statement)
        return result.scalar_one_or_none() is not None
