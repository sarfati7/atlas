"""FastAPI dependency injection setup."""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from atlas.adapters.auth.jwt_auth_service import JWTAuthService
from atlas.adapters.authorization.permissive import PermissiveAuthorizationService
from atlas.adapters.github.content_repository import GitHubContentRepository
from atlas.adapters.postgresql.repositories import (
    PostgresCatalogRepository,
    PostgresConfigurationRepository,
    PostgresTeamRepository,
    PostgresUserRepository,
)
from atlas.application.services import ConfigurationService
from atlas.adapters.postgresql.session import AsyncSession, get_session
from atlas.adapters.sync import GitCatalogSyncService
from atlas.config import settings
from atlas.domain.entities.user import User
from atlas.domain.interfaces import (
    AbstractAuthService,
    AbstractAuthorizationService,
    AbstractCatalogRepository,
    AbstractConfigurationRepository,
    AbstractContentRepository,
    AbstractEmailService,
    AbstractSyncService,
    AbstractTeamRepository,
    AbstractUserRepository,
)

# OAuth2 scheme for Bearer token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


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


async def get_configuration_repository(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> AbstractConfigurationRepository:
    """Provide configuration repository implementation."""
    return PostgresConfigurationRepository(session)


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


# Configuration service

async def get_configuration_service(
    config_repo: Annotated[AbstractConfigurationRepository, Depends(get_configuration_repository)],
    content_repo: Annotated[AbstractContentRepository, Depends(get_content_repository)],
) -> ConfigurationService:
    """Provide configuration service implementation."""
    return ConfigurationService(config_repo, content_repo)


# Email service (conditional on config)

async def get_email_service() -> AbstractEmailService:
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
    # Fallback to console for development without SMTP config
    from atlas.adapters.email.console_email_service import ConsoleEmailService
    return ConsoleEmailService()


# Authentication service (JWT + password hashing)

def get_auth_service() -> AbstractAuthService:
    """
    Provide authentication service implementation.

    Returns JWTAuthService configured with application settings.
    """
    return JWTAuthService(
        secret_key=settings.secret_key,
        access_token_expire_minutes=settings.access_token_expire_minutes,
        refresh_token_expire_days=settings.refresh_token_expire_days,
    )


# Current user dependencies

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[AbstractAuthService, Depends(get_auth_service)],
    user_repo: Annotated[AbstractUserRepository, Depends(get_user_repository)],
) -> User:
    """
    Get the current authenticated user from JWT token.

    Validates the Bearer token and returns the associated User entity.

    Raises:
        HTTPException 401: If token is invalid, expired, or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify token and extract payload
    payload = auth_service.verify_token(token)
    if payload is None:
        raise credentials_exception

    # Extract user ID from token subject
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    # Fetch user from repository
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception

    return user


async def get_current_user_optional(
    token: Annotated[Optional[str], Depends(OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False))],
    auth_service: Annotated[AbstractAuthService, Depends(get_auth_service)],
    user_repo: Annotated[AbstractUserRepository, Depends(get_user_repository)],
) -> Optional[User]:
    """
    Get the current authenticated user if a valid token is provided.

    Unlike get_current_user, this returns None instead of raising 401
    when no token is provided or the token is invalid.

    Useful for routes that work both with and without authentication.
    """
    if token is None:
        return None

    # Verify token and extract payload
    payload = auth_service.verify_token(token)
    if payload is None:
        return None

    # Extract user ID from token subject
    user_id_str = payload.get("sub")
    if user_id_str is None:
        return None

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        return None

    # Fetch user from repository
    user = await user_repo.get_by_id(user_id)
    return user


# Type aliases for cleaner route signatures
UserRepo = Annotated[AbstractUserRepository, Depends(get_user_repository)]
TeamRepo = Annotated[AbstractTeamRepository, Depends(get_team_repository)]
CatalogRepo = Annotated[AbstractCatalogRepository, Depends(get_catalog_repository)]
ContentRepo = Annotated[AbstractContentRepository, Depends(get_content_repository)]
AuthorizationSvc = Annotated[AbstractAuthorizationService, Depends(get_authorization_service)]
AuthenticationSvc = Annotated[AbstractAuthService, Depends(get_auth_service)]
EmailSvc = Annotated[AbstractEmailService, Depends(get_email_service)]
SyncService = Annotated[AbstractSyncService, Depends(get_sync_service)]
ConfigRepo = Annotated[AbstractConfigurationRepository, Depends(get_configuration_repository)]
ConfigService = Annotated[ConfigurationService, Depends(get_configuration_service)]

# Current user type aliases
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentUserOptional = Annotated[Optional[User], Depends(get_current_user_optional)]

# Backwards compatibility - AuthService was previously used for authorization
AuthService = AuthorizationSvc
