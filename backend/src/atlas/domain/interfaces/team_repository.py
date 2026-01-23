"""Team repository interface - Abstract contract for team data access."""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from atlas.domain.entities.team import Team


class AbstractTeamRepository(ABC):
    """
    Abstract repository interface for Team entity.

    Implementations must be provided for production (PostgreSQL)
    and testing (in-memory).
    """

    @abstractmethod
    async def get_by_id(self, team_id: UUID) -> Optional[Team]:
        """Retrieve a team by its unique identifier."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Team]:
        """Retrieve a team by its name."""
        raise NotImplementedError

    @abstractmethod
    async def save(self, team: Team) -> Team:
        """
        Save a team (create or update).

        Returns the saved team with any generated fields populated.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, team_id: UUID) -> bool:
        """
        Delete a team by its ID.

        Returns True if team was deleted, False if not found.
        """
        raise NotImplementedError

    @abstractmethod
    async def list_all(self) -> list[Team]:
        """Retrieve all teams."""
        raise NotImplementedError

    @abstractmethod
    async def get_user_teams(self, user_id: UUID) -> list[Team]:
        """Retrieve all teams that a user belongs to."""
        raise NotImplementedError

    @abstractmethod
    async def exists(self, team_id: UUID) -> bool:
        """Check if a team exists by its ID."""
        raise NotImplementedError
