"""Authentication exceptions - Token and credential errors."""

from uuid import UUID


class AuthenticationError(Exception):
    """Base exception for all authentication errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class InvalidTokenError(AuthenticationError):
    """Raised when a token is malformed or has invalid signature."""

    def __init__(self, message: str = "Invalid token") -> None:
        super().__init__(message)


class TokenExpiredError(AuthenticationError):
    """Raised when a token has expired."""

    def __init__(self, message: str = "Token has expired") -> None:
        super().__init__(message)


class InvalidCredentialsError(AuthenticationError):
    """Raised when login credentials are incorrect."""

    def __init__(self, message: str = "Invalid credentials") -> None:
        super().__init__(message)


class PasswordHashError(AuthenticationError):
    """Raised when password hashing or verification fails."""

    def __init__(self, message: str = "Password hashing error") -> None:
        super().__init__(message)
