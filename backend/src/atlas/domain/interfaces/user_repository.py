"""User repository interface - Abstract contract for user data access."""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from atlas.domain.entities.user import User


class AbstractUserRepository(ABC):
    """
    Abstract repository interface for User entity.

    Implementations must be provided for production (PostgreSQL)
    and testing (in-memory).
    """

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Retrieve a user by their unique identifier."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by their email address."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Retrieve a user by their username."""
        raise NotImplementedError

    @abstractmethod
    async def save(self, user: User) -> User:
        """
        Save a user (create or update).

        Returns the saved user with any generated fields populated.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """
        Delete a user by their ID.

        Returns True if user was deleted, False if not found.
        """
        raise NotImplementedError

    @abstractmethod
    async def list_all(self) -> list[User]:
        """Retrieve all users."""
        raise NotImplementedError

    @abstractmethod
    async def exists(self, user_id: UUID) -> bool:
        """Check if a user exists by their ID."""
        raise NotImplementedError
