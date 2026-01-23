"""Authorization service interface - Abstract contract for permission checks."""

from abc import ABC, abstractmethod

from atlas.domain.entities.catalog_item import CatalogItem
from atlas.domain.entities.user import User


class AbstractAuthorizationService(ABC):
    """
    Abstract authorization service interface.

    Defines permission checks for catalog items (skills, MCPs, tools).
    Phase 1 implementation is permissive (allow all).
    Future phases will implement actual RBAC.
    """

    @abstractmethod
    async def can_view_item(self, user: User, item: CatalogItem) -> bool:
        """Check if user can view a catalog item."""
        raise NotImplementedError

    @abstractmethod
    async def can_edit_item(self, user: User, item: CatalogItem) -> bool:
        """Check if user can edit a catalog item."""
        raise NotImplementedError

    @abstractmethod
    async def can_delete_item(self, user: User, item: CatalogItem) -> bool:
        """Check if user can delete a catalog item."""
        raise NotImplementedError

    @abstractmethod
    async def can_create_item(self, user: User) -> bool:
        """Check if user can create new catalog items."""
        raise NotImplementedError

    @abstractmethod
    async def can_manage_team(self, user: User, team_id: str) -> bool:
        """Check if user can manage a team (add/remove members)."""
        raise NotImplementedError

    @abstractmethod
    async def can_view_team(self, user: User, team_id: str) -> bool:
        """Check if user can view team details."""
        raise NotImplementedError
