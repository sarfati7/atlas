"""Authorization exceptions - Permission and access control errors."""

from uuid import UUID


class AuthorizationError(Exception):
    """Base exception for all authorization errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class PermissionDeniedError(AuthorizationError):
    """Raised when user lacks permission to perform an action."""

    def __init__(
        self,
        action: str,
        resource: str | None = None,
        user_id: UUID | str | None = None,
    ) -> None:
        self.action = action
        self.resource = resource
        self.user_id = user_id
        message = f"Permission denied for action: {action}"
        if resource:
            message += f" on resource: {resource}"
        super().__init__(message)


class ResourceAccessDeniedError(AuthorizationError):
    """Raised when user cannot access a specific resource."""

    def __init__(self, resource_type: str, resource_id: str | UUID) -> None:
        self.resource_type = resource_type
        self.resource_id = resource_id
        message = f"Access denied to {resource_type}: {resource_id}"
        super().__init__(message)
