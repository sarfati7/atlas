"""FastAPI application setup and configuration."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from atlas.entrypoints.api.routes import (
    admin_audit_router,
    admin_users_router,
    auth_router,
    catalog_router,
    configuration_router,
    profile_router,
    webhooks_router,
)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI app instance with all routes and middleware.
    """
    app = FastAPI(
        title="Atlas API",
        description="Agent management platform for companies using AI agents",
        version="0.1.0",
    )

    # Configure rate limiter
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Include routers with /api/v1 prefix
    app.include_router(admin_audit_router, prefix="/api/v1")
    app.include_router(admin_users_router, prefix="/api/v1")
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(catalog_router, prefix="/api/v1")
    app.include_router(configuration_router, prefix="/api/v1")
    app.include_router(profile_router, prefix="/api/v1")
    app.include_router(webhooks_router, prefix="/api/v1")

    @app.get("/health")
    async def health_check() -> dict:
        """Health check endpoint."""
        return {"status": "healthy"}

    return app


# Create app instance for uvicorn
app = create_app()
