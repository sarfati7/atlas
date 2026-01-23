"""In-memory implementation of Team repository for testing."""

from typing import Optional
from uuid import UUID

from atlas.domain.entities.team import Team
from atlas.domain.interfaces.team_repository import AbstractTeamRepository


class InMemoryTeamRepository(AbstractTeamRepository):
    """In-memory team repository implementation for testing."""

    def __init__(self) -> None:
        """Initialize with empty storage."""
        self._teams: dict[UUID, Team] = {}
        self._memberships: dict[UUID, set[UUID]] = {}  # user_id -> team_ids

    def clear(self) -> None:
        """Reset storage (useful in tests)."""
        self._teams.clear()
        self._memberships.clear()

    def add_user_to_team(self, user_id: UUID, team_id: UUID) -> None:
        """Add a user to a team (helper for test setup)."""
        if user_id not in self._memberships:
            self._memberships[user_id] = set()
        self._memberships[user_id].add(team_id)

    def remove_user_from_team(self, user_id: UUID, team_id: UUID) -> None:
        """Remove a user from a team (helper for test setup)."""
        if user_id in self._memberships:
            self._memberships[user_id].discard(team_id)

    async def get_by_id(self, team_id: UUID) -> Optional[Team]:
        """Retrieve a team by its unique identifier."""
        return self._teams.get(team_id)

    async def get_by_name(self, name: str) -> Optional[Team]:
        """Retrieve a team by its name."""
        for team in self._teams.values():
            if team.name == name:
                return team
        return None

    async def save(self, team: Team) -> Team:
        """Save a team (create or update)."""
        self._teams[team.id] = team
        return team

    async def delete(self, team_id: UUID) -> bool:
        """Delete a team by its ID."""
        if team_id in self._teams:
            del self._teams[team_id]
            # Clean up memberships
            for user_id in list(self._memberships.keys()):
                self._memberships[user_id].discard(team_id)
            return True
        return False

    async def list_all(self) -> list[Team]:
        """Retrieve all teams."""
        return list(self._teams.values())

    async def get_user_teams(self, user_id: UUID) -> list[Team]:
        """Retrieve all teams that a user belongs to."""
        team_ids = self._memberships.get(user_id, set())
        return [self._teams[tid] for tid in team_ids if tid in self._teams]

    async def exists(self, team_id: UUID) -> bool:
        """Check if a team exists by its ID."""
        return team_id in self._teams
