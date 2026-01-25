"""Authorization service interface - Abstract contract for permission checks."""

from abc import ABC, abstractmethod

from atlas.domain.entities import CatalogItem, User


class AuthorizationError(Exception):
    """Raised when an authorization check fails."""

    pass


class AbstractAuthorizationService(ABC):
    """
    Abstract authorization service interface.

    Defines permission checks for catalog items, teams, and role-based access.
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
        """Check if user can manage a team."""
        raise NotImplementedError

    @abstractmethod
    async def can_view_team(self, user: User, team_id: str) -> bool:
        """Check if user can view team details."""
        raise NotImplementedError

    # -------------------------------------------------------------------------
    # Role-based authorization
    # -------------------------------------------------------------------------

    @abstractmethod
    async def is_admin(self, user: User) -> bool:
        """Check if user has admin role."""
        raise NotImplementedError

    @abstractmethod
    async def require_admin(self, user: User) -> None:
        """Raise AuthorizationError if user is not an admin."""
        raise NotImplementedError

    @abstractmethod
    async def can_manage_users(self, user: User) -> bool:
        """Check if user can manage other users (view, create, update, delete)."""
        raise NotImplementedError
