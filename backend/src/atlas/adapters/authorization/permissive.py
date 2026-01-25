"""Permissive authorization service - Allow-all implementation."""

from atlas.adapters.authorization.interface import (
    AbstractAuthorizationService,
    AuthorizationError,
)
from atlas.domain.entities import CatalogItem, User


class PermissiveAuthorizationService(AbstractAuthorizationService):
    """
    Permissive implementation: allows all operations.

    Placeholder until actual RBAC is implemented.
    """

    async def can_view_item(self, user: User, item: CatalogItem) -> bool:
        """Always returns True."""
        return True

    async def can_edit_item(self, user: User, item: CatalogItem) -> bool:
        """Always returns True."""
        return True

    async def can_delete_item(self, user: User, item: CatalogItem) -> bool:
        """Always returns True."""
        return True

    async def can_create_item(self, user: User) -> bool:
        """Always returns True."""
        return True

    async def can_manage_team(self, user: User, team_id: str) -> bool:
        """Always returns True."""
        return True

    async def can_view_team(self, user: User, team_id: str) -> bool:
        """Always returns True."""
        return True

    # -------------------------------------------------------------------------
    # Role-based authorization
    # -------------------------------------------------------------------------

    async def is_admin(self, user: User) -> bool:
        """Check if user has admin role using User.is_admin property."""
        return user.is_admin

    async def require_admin(self, user: User) -> None:
        """Raise AuthorizationError if user is not an admin."""
        if not user.is_admin:
            raise AuthorizationError("Admin role required")

    async def can_manage_users(self, user: User) -> bool:
        """Only admins can manage other users."""
        return user.is_admin
