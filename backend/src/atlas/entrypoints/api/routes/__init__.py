"""API route modules."""

from atlas.entrypoints.api.routes.auth import router as auth_router
from atlas.entrypoints.api.routes.catalog import router as catalog_router
from atlas.entrypoints.api.routes.sync import router as sync_router
from atlas.entrypoints.api.routes.webhooks import router as webhooks_router

__all__ = ["auth_router", "catalog_router", "webhooks_router", "sync_router"]
