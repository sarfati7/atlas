"""Permissive authorization service - Allow-all implementation for Phase 1."""

from atlas.domain.entities import CatalogItem, User
from atlas.domain.interfaces import AbstractAuthorizationService


class PermissiveAuthorizationService(AbstractAuthorizationService):
    """
    Phase 1 implementation: allows all operations.

    This provides the authorization abstraction from day one,
    making it easy to implement actual RBAC in a later phase
    without changing the calling code.

    All methods return True, effectively disabling authorization
    checks while maintaining the interface contract.
    """

    async def can_view_item(self, user: User, item: CatalogItem) -> bool:
        """Check if user can view a catalog item. Always returns True."""
        # TODO: Implement actual RBAC in Phase 9
        return True

    async def can_edit_item(self, user: User, item: CatalogItem) -> bool:
        """Check if user can edit a catalog item. Always returns True."""
        return True

    async def can_delete_item(self, user: User, item: CatalogItem) -> bool:
        """Check if user can delete a catalog item. Always returns True."""
        return True

    async def can_create_item(self, user: User) -> bool:
        """Check if user can create new catalog items. Always returns True."""
        return True

    async def can_manage_team(self, user: User, team_id: str) -> bool:
        """Check if user can manage a team. Always returns True."""
        return True

    async def can_view_team(self, user: User, team_id: str) -> bool:
        """Check if user can view team details. Always returns True."""
        return True
