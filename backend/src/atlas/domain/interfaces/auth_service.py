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
        """
        Hash a plain-text password for storage.

        Args:
            password: Plain-text password

        Returns:
            Hashed password string (includes algorithm info)
        """
        raise NotImplementedError

    @abstractmethod
    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            password: Plain-text password to verify
            password_hash: Stored hash to compare against

        Returns:
            True if password matches, False otherwise
        """
        raise NotImplementedError

    @abstractmethod
    def create_access_token(self, user_id: UUID, email: str) -> str:
        """
        Create a short-lived access token for API authentication.

        Args:
            user_id: User's unique identifier
            email: User's email address

        Returns:
            Encoded JWT access token
        """
        raise NotImplementedError

    @abstractmethod
    def create_refresh_token(self, user_id: UUID) -> str:
        """
        Create a long-lived refresh token for obtaining new access tokens.

        Args:
            user_id: User's unique identifier

        Returns:
            Encoded JWT refresh token
        """
        raise NotImplementedError

    @abstractmethod
    def verify_token(self, token: str) -> Optional[dict]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token string

        Returns:
            Token payload dict if valid, None if invalid/expired
        """
        raise NotImplementedError

    @abstractmethod
    def create_password_reset_token(self, user_id: UUID) -> str:
        """
        Create a time-limited token for password reset.

        Args:
            user_id: User's unique identifier

        Returns:
            URL-safe password reset token
        """
        raise NotImplementedError

    @abstractmethod
    def verify_password_reset_token(self, token: str, max_age_seconds: int = 3600) -> Optional[UUID]:
        """
        Verify a password reset token and extract user ID.

        Args:
            token: Password reset token
            max_age_seconds: Maximum token age (default 1 hour)

        Returns:
            User ID if token is valid, None if invalid/expired
        """
        raise NotImplementedError
