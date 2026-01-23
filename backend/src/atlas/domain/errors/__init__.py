"""Domain errors - Business rule violations and exceptions."""

from atlas.domain.errors.domain_errors import (
    AuthorizationError,
    DomainError,
    EntityNotFoundError,
    ValidationError,
)

__all__ = [
    "DomainError",
    "EntityNotFoundError",
    "ValidationError",
    "AuthorizationError",
]
