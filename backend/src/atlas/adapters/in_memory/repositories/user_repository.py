"""In-memory implementation of User repository for testing."""

from typing import Optional
from uuid import UUID

from atlas.domain.entities.user import User
from atlas.domain.interfaces.user_repository import AbstractUserRepository


class InMemoryUserRepository(AbstractUserRepository):
    """In-memory user repository implementation for testing."""

    def __init__(self) -> None:
        """Initialize with empty storage."""
        self._users: dict[UUID, User] = {}

    def clear(self) -> None:
        """Reset storage (useful in tests)."""
        self._users.clear()

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Retrieve a user by their unique identifier."""
        return self._users.get(user_id)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by their email address."""
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    async def get_by_username(self, username: str) -> Optional[User]:
        """Retrieve a user by their username."""
        for user in self._users.values():
            if user.username == username:
                return user
        return None

    async def save(self, user: User) -> User:
        """Save a user (create or update)."""
        self._users[user.id] = user
        return user

    async def delete(self, user_id: UUID) -> bool:
        """Delete a user by their ID."""
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False

    async def list_all(self) -> list[User]:
        """Retrieve all users."""
        return list(self._users.values())

    async def exists(self, user_id: UUID) -> bool:
        """Check if a user exists by their ID."""
        return user_id in self._users
