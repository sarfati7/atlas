"""FastAPI dependency injection setup."""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from atlas.adapters.auth.jwt_auth_service import JWTAuthService
from atlas.adapters.authorization.permissive import PermissiveAuthorizationService
from atlas.adapters.github.content_repository import GitHubContentRepository
from atlas.adapters.postgresql.repository import Repository
from atlas.adapters.postgresql.session import AsyncSession, get_session
from atlas.adapters.sync import GitCatalogSyncService
from atlas.application.services import ConfigurationService, UserProfileService
from atlas.config import settings
from atlas.domain.entities.user import User
from atlas.domain.interfaces import (
    AbstractAuthService,
    AbstractAuthorizationService,
    AbstractContentRepository,
    AbstractSyncService,
)
from atlas.domain.interfaces.repository import AbstractRepository

# OAuth2 scheme for Bearer token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# -----------------------------------------------------------------------------
# Repository dependency (unified)
# -----------------------------------------------------------------------------

async def get_repository(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> AbstractRepository:
    """Provide unified repository implementation."""
    return Repository(session)


# Type alias for cleaner route signatures
Repo = Annotated[AbstractRepository, Depends(get_repository)]


# -----------------------------------------------------------------------------
# Content repository (GitHub or in-memory based on config)
# -----------------------------------------------------------------------------

async def get_content_repository() -> AbstractContentRepository:
    """
    Provide content repository implementation.

    Returns GitHubContentRepository if GitHub settings are configured,
    otherwise falls back to InMemoryContentRepository for development.
    """
    if settings.github_token and settings.github_repo:
        return GitHubContentRepository(settings.github_token, settings.github_repo)
    from atlas.adapters.in_memory.content_repository import InMemoryContentRepository
    return InMemoryContentRepository()


ContentRepo = Annotated[AbstractContentRepository, Depends(get_content_repository)]


# -----------------------------------------------------------------------------
# Authorization service
# -----------------------------------------------------------------------------

async def get_authorization_service() -> AbstractAuthorizationService:
    """
    Provide authorization service implementation.

    Currently returns PermissiveAuthorizationService (allows all).
    Will be replaced with actual RBAC in Phase 9.
    """
    return PermissiveAuthorizationService()


AuthorizationSvc = Annotated[AbstractAuthorizationService, Depends(get_authorization_service)]


# -----------------------------------------------------------------------------
# Sync service
# -----------------------------------------------------------------------------

SYSTEM_AUTHOR_ID = UUID("00000000-0000-0000-0000-000000000000")


async def get_sync_service(
    content_repo: ContentRepo,
    repo: Repo,
) -> AbstractSyncService:
    """Provide sync service implementation."""
    return GitCatalogSyncService(content_repo, repo, SYSTEM_AUTHOR_ID)


SyncService = Annotated[AbstractSyncService, Depends(get_sync_service)]


# -----------------------------------------------------------------------------
# Configuration service
# -----------------------------------------------------------------------------

async def get_configuration_service(
    repo: Repo,
    content_repo: ContentRepo,
) -> ConfigurationService:
    """Provide configuration service implementation."""
    return ConfigurationService(repo, content_repo)


ConfigService = Annotated[ConfigurationService, Depends(get_configuration_service)]


# -----------------------------------------------------------------------------
# User profile service
# -----------------------------------------------------------------------------

async def get_user_profile_service(
    repo: Repo,
    content_repo: ContentRepo,
) -> UserProfileService:
    """Provide user profile service implementation."""
    return UserProfileService(repo=repo, content_repo=content_repo)


ProfileService = Annotated[UserProfileService, Depends(get_user_profile_service)]


# -----------------------------------------------------------------------------
# Email service
# -----------------------------------------------------------------------------

async def get_email_service():
    """
    Provide email service implementation.

    Returns SMTPEmailService if SMTP settings are configured,
    otherwise falls back to ConsoleEmailService for development.
    """
    if settings.smtp_host:
        from atlas.adapters.email.smtp_email_service import SMTPEmailService
        return SMTPEmailService(
            smtp_host=settings.smtp_host,
            smtp_port=settings.smtp_port,
            smtp_user=settings.smtp_user,
            smtp_password=settings.smtp_password,
            email_from=settings.email_from,
        )
    from atlas.adapters.email.console_email_service import ConsoleEmailService
    return ConsoleEmailService()


EmailSvc = Annotated[AbstractAuthorizationService, Depends(get_email_service)]


# -----------------------------------------------------------------------------
# Authentication service
# -----------------------------------------------------------------------------

def get_auth_service() -> AbstractAuthService:
    """Provide authentication service implementation."""
    return JWTAuthService(
        secret_key=settings.secret_key,
        access_token_expire_minutes=settings.access_token_expire_minutes,
        refresh_token_expire_days=settings.refresh_token_expire_days,
    )


AuthenticationSvc = Annotated[AbstractAuthService, Depends(get_auth_service)]


# -----------------------------------------------------------------------------
# Current user dependencies
# -----------------------------------------------------------------------------

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthenticationSvc,
    repo: Repo,
) -> User:
    """
    Get the current authenticated user from JWT token.

    Validates the Bearer token and returns the associated User entity.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = auth_service.verify_token(token)
    if payload is None:
        raise credentials_exception

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    user = await repo.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception

    return user


async def get_current_user_optional(
    token: Annotated[Optional[str], Depends(OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False))],
    auth_service: AuthenticationSvc,
    repo: Repo,
) -> Optional[User]:
    """
    Get the current authenticated user if a valid token is provided.

    Returns None instead of raising 401 when no token or invalid token.
    """
    if token is None:
        return None

    payload = auth_service.verify_token(token)
    if payload is None:
        return None

    user_id_str = payload.get("sub")
    if user_id_str is None:
        return None

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        return None

    return await repo.get_user_by_id(user_id)


CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentUserOptional = Annotated[Optional[User], Depends(get_current_user_optional)]

# Backwards compatibility alias
AuthService = AuthorizationSvc
