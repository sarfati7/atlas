"""Domain error hierarchy - Base exceptions for business rule violations."""

from typing import Any
from uuid import UUID


class DomainError(Exception):
    """Base exception for all domain errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class EntityNotFoundError(DomainError):
    """Raised when an entity cannot be found."""

    def __init__(self, entity_type: str, entity_id: UUID | str) -> None:
        self.entity_type = entity_type
        self.entity_id = entity_id
        message = f"{entity_type} with id '{entity_id}' not found"
        super().__init__(message)


class ValidationError(DomainError):
    """Raised when domain validation fails."""

    def __init__(self, message: str, field: str | None = None) -> None:
        self.field = field
        full_message = f"Validation error on '{field}': {message}" if field else message
        super().__init__(full_message)


class AuthorizationError(DomainError):
    """Raised when a user is not authorized to perform an action."""

    def __init__(
        self,
        message: str,
        user_id: UUID | str | None = None,
        resource: str | None = None,
        action: str | None = None,
    ) -> None:
        self.user_id = user_id
        self.resource = resource
        self.action = action
        super().__init__(message)
