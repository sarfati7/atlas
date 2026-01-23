"""FastAPI dependency injection setup."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends

from atlas.adapters.authorization.permissive import PermissiveAuthorizationService
from atlas.adapters.github.content_repository import GitHubContentRepository
from atlas.adapters.postgresql.repositories import (
    PostgresCatalogRepository,
    PostgresTeamRepository,
    PostgresUserRepository,
)
from atlas.adapters.postgresql.session import AsyncSession, get_session
from atlas.adapters.sync import GitCatalogSyncService
from atlas.config import settings
from atlas.domain.interfaces import (
    AbstractAuthorizationService,
    AbstractCatalogRepository,
    AbstractContentRepository,
    AbstractSyncService,
    AbstractTeamRepository,
    AbstractUserRepository,
)


# Repository dependencies

async def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> AbstractUserRepository:
    """Provide user repository implementation."""
    return PostgresUserRepository(session)


async def get_team_repository(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> AbstractTeamRepository:
    """Provide team repository implementation."""
    return PostgresTeamRepository(session)


async def get_catalog_repository(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> AbstractCatalogRepository:
    """Provide catalog repository implementation."""
    return PostgresCatalogRepository(session)


# Content repository (conditional on config)

async def get_content_repository() -> AbstractContentRepository:
    """
    Provide content repository implementation.

    Returns GitHubContentRepository if GitHub settings are configured,
    otherwise falls back to InMemoryContentRepository for development.
    """
    if settings.github_token and settings.github_repo:
        return GitHubContentRepository(settings.github_token, settings.github_repo)
    # Fallback to in-memory for development without GitHub config
    from atlas.adapters.in_memory.content_repository import InMemoryContentRepository
    return InMemoryContentRepository()


# Authorization service

async def get_authorization_service() -> AbstractAuthorizationService:
    """
    Provide authorization service implementation.

    Currently returns PermissiveAuthorizationService (allows all).
    Will be replaced with actual RBAC in Phase 9.
    """
    return PermissiveAuthorizationService()


# Sync service

# System author ID for items created via sync (webhook/automated)
SYSTEM_AUTHOR_ID = UUID("00000000-0000-0000-0000-000000000000")


async def get_sync_service(
    content_repo: Annotated[AbstractContentRepository, Depends(get_content_repository)],
    catalog_repo: Annotated[AbstractCatalogRepository, Depends(get_catalog_repository)],
) -> AbstractSyncService:
    """
    Provide sync service implementation.

    Uses system author ID for items created via webhook or automated sync.
    """
    return GitCatalogSyncService(content_repo, catalog_repo, SYSTEM_AUTHOR_ID)


# Type aliases for cleaner route signatures
UserRepo = Annotated[AbstractUserRepository, Depends(get_user_repository)]
TeamRepo = Annotated[AbstractTeamRepository, Depends(get_team_repository)]
CatalogRepo = Annotated[AbstractCatalogRepository, Depends(get_catalog_repository)]
ContentRepo = Annotated[AbstractContentRepository, Depends(get_content_repository)]
AuthService = Annotated[AbstractAuthorizationService, Depends(get_authorization_service)]
SyncService = Annotated[AbstractSyncService, Depends(get_sync_service)]
