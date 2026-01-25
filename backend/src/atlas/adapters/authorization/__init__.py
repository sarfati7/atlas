"""Authorization adapter - Permission checking implementations."""

from atlas.adapters.authorization.exceptions import (
    AuthorizationError,
    PermissionDeniedError,
    ResourceAccessDeniedError,
)
from atlas.adapters.authorization.interface import AbstractAuthorizationService
from atlas.adapters.authorization.permissive import PermissiveAuthorizationService
from atlas.adapters.authorization.rbac import RBACAuthorizationService

__all__ = [
    "AbstractAuthorizationService",
    "AuthorizationError",
    "PermissionDeniedError",
    "PermissiveAuthorizationService",
    "RBACAuthorizationService",
    "ResourceAccessDeniedError",
]
