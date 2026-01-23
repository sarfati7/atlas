"""API route modules."""

from atlas.entrypoints.api.routes.webhooks import router as webhooks_router

__all__ = ["webhooks_router"]
