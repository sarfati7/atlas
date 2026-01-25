"""RBAC authorization service - Role-based access control implementation."""

from fastapi import HTTPException, status

from atlas.adapters.authorization.interface import AbstractAuthorizationService
from atlas.domain.entities import CatalogItem, User


class RBACAuthorizationService(AbstractAuthorizationService):
    """
    Role-based access control implementation.

    Authorization rules:
    - Admins can manage teams, users, and catalog items
    - All users can view catalog items and teams
    - Non-admins receive 403 Forbidden on admin-only operations
    """

    async def can_view_item(self, user: User, item: CatalogItem) -> bool:
        """All users can view catalog items."""
        return True

    async def can_edit_item(self, user: User, item: CatalogItem) -> bool:
        """Only admins can edit catalog items."""
        return user.is_admin

    async def can_delete_item(self, user: User, item: CatalogItem) -> bool:
        """Only admins can delete catalog items."""
        return user.is_admin

    async def can_create_item(self, user: User) -> bool:
        """Only admins can create catalog items."""
        return user.is_admin

    async def can_manage_team(self, user: User, team_id: str) -> bool:
        """Only admins can manage teams."""
        return user.is_admin

    async def can_view_team(self, user: User, team_id: str) -> bool:
        """All users can view team details."""
        return True

    # -------------------------------------------------------------------------
    # Role-based authorization
    # -------------------------------------------------------------------------

    async def is_admin(self, user: User) -> bool:
        """Check if user has admin role."""
        return user.is_admin

    async def require_admin(self, user: User) -> None:
        """Raise HTTPException(403) if user is not an admin."""
        if not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin role required",
            )

    async def can_manage_users(self, user: User) -> bool:
        """Only admins can manage other users."""
        return user.is_admin
