"""Repository interface - Abstract contract for database operations."""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from atlas.domain.entities import AuditLog, Team, User, UserConfiguration


class AbstractRepository(ABC):
    """
    Abstract repository interface for database operations.

    Single interface for User, Team, and UserConfiguration entities.
    Implementations: PostgreSQL (production), SQLite (tests).
    """

    # -------------------------------------------------------------------------
    # User operations
    # -------------------------------------------------------------------------

    @abstractmethod
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Retrieve a user by their unique identifier."""
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by their email address."""
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Retrieve a user by their username."""
        raise NotImplementedError

    @abstractmethod
    async def save_user(self, user: User) -> User:
        """Save a user (create or update)."""
        raise NotImplementedError

    @abstractmethod
    async def delete_user(self, user_id: UUID) -> bool:
        """Delete a user. Returns True if deleted, False if not found."""
        raise NotImplementedError

    @abstractmethod
    async def list_users(self) -> list[User]:
        """Retrieve all users."""
        raise NotImplementedError

    # -------------------------------------------------------------------------
    # Team operations
    # -------------------------------------------------------------------------

    @abstractmethod
    async def get_team_by_id(self, team_id: UUID) -> Optional[Team]:
        """Retrieve a team by its unique identifier."""
        raise NotImplementedError

    @abstractmethod
    async def get_team_by_name(self, name: str) -> Optional[Team]:
        """Retrieve a team by its name."""
        raise NotImplementedError

    @abstractmethod
    async def save_team(self, team: Team) -> Team:
        """Save a team (create or update)."""
        raise NotImplementedError

    @abstractmethod
    async def delete_team(self, team_id: UUID) -> bool:
        """Delete a team. Returns True if deleted, False if not found."""
        raise NotImplementedError

    @abstractmethod
    async def list_teams(self) -> list[Team]:
        """Retrieve all teams."""
        raise NotImplementedError

    @abstractmethod
    async def get_user_teams(self, user_id: UUID) -> list[Team]:
        """Retrieve all teams that a user belongs to."""
        raise NotImplementedError

    # -------------------------------------------------------------------------
    # Configuration operations
    # -------------------------------------------------------------------------

    @abstractmethod
    async def get_configuration_by_user_id(
        self, user_id: UUID
    ) -> Optional[UserConfiguration]:
        """Get configuration for a user. Returns None if no configuration."""
        raise NotImplementedError

    @abstractmethod
    async def get_configuration_by_id(
        self, config_id: UUID
    ) -> Optional[UserConfiguration]:
        """Get configuration by its ID."""
        raise NotImplementedError

    @abstractmethod
    async def save_configuration(
        self, config: UserConfiguration
    ) -> UserConfiguration:
        """Save or update configuration (upsert by user_id)."""
        raise NotImplementedError

    @abstractmethod
    async def delete_configuration(self, config_id: UUID) -> bool:
        """Delete configuration. Returns True if deleted, False if not found."""
        raise NotImplementedError

    # -------------------------------------------------------------------------
    # Audit log operations
    # -------------------------------------------------------------------------

    @abstractmethod
    async def save_audit_log(self, log: AuditLog) -> AuditLog:
        """Save an audit log entry."""
        raise NotImplementedError

    @abstractmethod
    async def get_audit_logs(
        self,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditLog]:
        """Get audit logs with optional filters, ordered by created_at DESC."""
        raise NotImplementedError

    @abstractmethod
    async def count_audit_logs(
        self,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
    ) -> int:
        """Count audit logs with optional filters."""
        raise NotImplementedError
