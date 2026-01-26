"""Authentication service interface - Abstract contract for auth operations."""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID


class AbstractAuthService(ABC):
    """
    Abstract authentication service interface.

    Defines operations for password hashing, token management,
    and password reset functionality.
    """

    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Hash a plain-text password for storage."""
        raise NotImplementedError

    @abstractmethod
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        raise NotImplementedError

    @abstractmethod
    def create_access_token(self, user_id: UUID, email: str) -> str:
        """Create a short-lived access token for API authentication."""
        raise NotImplementedError

    @abstractmethod
    def create_refresh_token(self, user_id: UUID) -> str:
        """Create a long-lived refresh token for obtaining new access tokens."""
        raise NotImplementedError

    @abstractmethod
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode a JWT token."""
        raise NotImplementedError

    @abstractmethod
    def create_password_reset_token(self, user_id: UUID) -> str:
        """Create a time-limited token for password reset."""
        raise NotImplementedError

    @abstractmethod
    def verify_password_reset_token(
        self, token: str, max_age_seconds: int = 3600
    ) -> Optional[UUID]:
        """Verify a password reset token and extract user ID."""
        raise NotImplementedError
