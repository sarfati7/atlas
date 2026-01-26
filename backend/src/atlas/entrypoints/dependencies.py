"""FastAPI dependency injection setup."""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from atlas.adapters.authentication import AbstractAuthService, JWTAuthService
from atlas.adapters.authorization import (
    AbstractAuthorizationService,
    RBACAuthorizationService,
)
from atlas.adapters.catalog import GitHubCatalogRepository, AbstractCatalogRepository
from atlas.adapters.repository import AbstractRepository, PostgreSQLRepository, get_session, AsyncSession
from atlas.application.services import AtlasService
from atlas.config import settings
from atlas.domain.entities.user import User

# OAuth2 scheme for Bearer token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# -----------------------------------------------------------------------------
# Repository (database)
# -----------------------------------------------------------------------------


async def get_repository(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> AbstractRepository:
    """Provide repository implementation."""
    return PostgreSQLRepository(session)


Repo = Annotated[AbstractRepository, Depends(get_repository)]


# -----------------------------------------------------------------------------
# Catalog repository (git)
# -----------------------------------------------------------------------------


async def get_catalog_repository(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> AbstractCatalogRepository:
    """
    Provide catalog repository implementation.

    Priority:
    1. Database settings (if configured via admin UI)
    2. Environment variables
    3. In-memory fallback
    """
    # Check database settings first
    repo = PostgreSQLRepository(session)
    db_token = await repo.get_app_setting("github_token")
    db_repo = await repo.get_app_setting("github_repo")

    if db_token and db_repo:
        return GitHubCatalogRepository(db_token, db_repo)

    # Fall back to environment variables
    if settings.github_token and settings.github_repo:
        return GitHubCatalogRepository(settings.github_token, settings.github_repo)

    # No GitHub config, use in-memory
    from atlas.adapters.catalog import InMemoryCatalogRepository
    return InMemoryCatalogRepository()


CatalogRepo = Annotated[AbstractCatalogRepository, Depends(get_catalog_repository)]


# -----------------------------------------------------------------------------
# Atlas service (main application service)
# -----------------------------------------------------------------------------


async def get_atlas_service(
    repo: Repo,
    catalog_repo: CatalogRepo,
) -> AtlasService:
    """Provide the main Atlas service."""
    return AtlasService(repo=repo, catalog_repo=catalog_repo)


Atlas = Annotated[AtlasService, Depends(get_atlas_service)]


# -----------------------------------------------------------------------------
# Authorization service
# -----------------------------------------------------------------------------


async def get_authorization_service() -> AbstractAuthorizationService:
    """Provide authorization service implementation."""
    return RBACAuthorizationService()


AuthorizationSvc = Annotated[
    AbstractAuthorizationService, Depends(get_authorization_service)
]


# -----------------------------------------------------------------------------
# Email service
# -----------------------------------------------------------------------------


async def get_email_service():
    """Provide email service implementation."""
    if settings.smtp_host:
        from atlas.adapters.email import SMTPEmailService
        return SMTPEmailService(
            smtp_host=settings.smtp_host,
            smtp_port=settings.smtp_port,
            smtp_user=settings.smtp_user,
            smtp_password=settings.smtp_password,
            email_from=settings.email_from,
        )
    from atlas.adapters.email import ConsoleEmailService
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
    """Get the current authenticated user from JWT token."""
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
    token: Annotated[
        Optional[str],
        Depends(OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)),
    ],
    auth_service: AuthenticationSvc,
    repo: Repo,
) -> Optional[User]:
    """Get the current authenticated user if a valid token is provided."""
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


# -----------------------------------------------------------------------------
# Admin authorization dependency
# -----------------------------------------------------------------------------


async def require_admin(
    current_user: CurrentUser,
    auth_service: AuthorizationSvc,
) -> None:
    """Dependency that enforces admin role. Raises 403 if not admin."""
    await auth_service.require_admin(current_user)


RequireAdmin = Annotated[None, Depends(require_admin)]
