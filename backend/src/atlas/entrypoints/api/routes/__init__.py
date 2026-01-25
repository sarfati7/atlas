"""API route modules."""

from atlas.entrypoints.api.routes.admin_audit import router as admin_audit_router
from atlas.entrypoints.api.routes.admin_teams import router as admin_teams_router
from atlas.entrypoints.api.routes.admin_users import router as admin_users_router
from atlas.entrypoints.api.routes.auth import router as auth_router
from atlas.entrypoints.api.routes.catalog import router as catalog_router
from atlas.entrypoints.api.routes.configuration import router as configuration_router
from atlas.entrypoints.api.routes.profile import router as profile_router
from atlas.entrypoints.api.routes.webhooks import router as webhooks_router

__all__ = [
    "admin_audit_router",
    "admin_teams_router",
    "admin_users_router",
    "auth_router",
    "catalog_router",
    "configuration_router",
    "profile_router",
    "webhooks_router",
]
