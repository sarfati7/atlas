"""Repository exceptions - Database and storage related errors."""

from typing import Any
from uuid import UUID


class RepositoryError(Exception):
    """Base exception for all repository errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class EntityNotFoundError(RepositoryError):
    """Raised when an entity cannot be found in the repository."""

    def __init__(self, entity_type: str, identifier: UUID | str | Any) -> None:
        self.entity_type = entity_type
        self.identifier = identifier
        message = f"{entity_type} with identifier '{identifier}' not found"
        super().__init__(message)


class DuplicateEntityError(RepositoryError):
    """Raised when attempting to create an entity that already exists."""

    def __init__(self, entity_type: str, field: str, value: Any) -> None:
        self.entity_type = entity_type
        self.field = field
        self.value = value
        message = f"{entity_type} with {field}='{value}' already exists"
        super().__init__(message)


class ConnectionError(RepositoryError):
    """Raised when database connection fails."""

    def __init__(self, message: str = "Failed to connect to database") -> None:
        super().__init__(message)
