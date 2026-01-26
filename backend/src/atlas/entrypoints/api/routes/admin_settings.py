"""Admin settings routes - Configure application-level settings like GitHub integration."""

from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from atlas.adapters.authorization import AuthorizationError
from atlas.domain.entities.user import User
from atlas.entrypoints.dependencies import (
    AuthorizationSvc,
    CurrentUser,
    Repo,
)

router = APIRouter(prefix="/admin/settings", tags=["admin-settings"])


# -----------------------------------------------------------------------------
# Request/Response schemas
# -----------------------------------------------------------------------------


class GitHubSettingsResponse(BaseModel):
    """GitHub settings response (token is masked)."""

    repo: Optional[str] = None
    token_configured: bool = False
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None


class GitHubSettingsRequest(BaseModel):
    """Request to update GitHub settings."""

    repo: str
    token: str


class ConnectionTestResponse(BaseModel):
    """Response from testing GitHub connection."""

    success: bool
    message: str
    repo_name: Optional[str] = None


# -----------------------------------------------------------------------------
# Admin dependency
# -----------------------------------------------------------------------------


async def require_admin(
    current_user: CurrentUser,
    auth_service: AuthorizationSvc,
) -> User:
    """Dependency that requires admin role."""
    try:
        await auth_service.require_admin(current_user)
    except AuthorizationError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return current_user


RequireAdmin = Annotated[User, Depends(require_admin)]


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------


@router.get("/github", response_model=GitHubSettingsResponse)
async def get_github_settings(
    admin: RequireAdmin,
    repo: Repo,
) -> GitHubSettingsResponse:
    """
    Get current GitHub integration settings.

    Requires admin role.
    Token is never returned, only whether it's configured.
    """
    github_repo = await repo.get_app_setting("github_repo")
    token_metadata = await repo.get_app_setting_metadata("github_token")

    updated_by_username = None
    if token_metadata and token_metadata.get("updated_by"):
        user = await repo.get_user_by_id(token_metadata["updated_by"])
        if user:
            updated_by_username = user.username

    return GitHubSettingsResponse(
        repo=github_repo,
        token_configured=token_metadata is not None,
        updated_at=token_metadata["updated_at"] if token_metadata else None,
        updated_by=updated_by_username,
    )


@router.put("/github", response_model=GitHubSettingsResponse)
async def update_github_settings(
    body: GitHubSettingsRequest,
    admin: RequireAdmin,
    repo: Repo,
) -> GitHubSettingsResponse:
    """
    Update GitHub integration settings.

    Requires admin role.
    Both repo and token are required.
    """
    # Validate repo format (owner/repo)
    if "/" not in body.repo or body.repo.count("/") != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid repo format. Use 'owner/repo' format.",
        )

    # Save settings
    await repo.set_app_setting("github_repo", body.repo, is_secret=False, user_id=admin.id)
    await repo.set_app_setting("github_token", body.token, is_secret=True, user_id=admin.id)

    return GitHubSettingsResponse(
        repo=body.repo,
        token_configured=True,
        updated_at=datetime.utcnow(),
        updated_by=admin.username,
    )


@router.post("/github/test", response_model=ConnectionTestResponse)
async def test_github_connection(
    admin: RequireAdmin,
    repo: Repo,
) -> ConnectionTestResponse:
    """
    Test the GitHub connection with current settings.

    Requires admin role.
    Attempts to access the configured repository.
    """
    github_repo = await repo.get_app_setting("github_repo")
    github_token = await repo.get_app_setting("github_token")

    if not github_repo or not github_token:
        return ConnectionTestResponse(
            success=False,
            message="GitHub settings not configured",
        )

    try:
        from github import Github, GithubException

        gh = Github(github_token)
        gh_repo = gh.get_repo(github_repo)

        # Try to access repo name to verify connection
        repo_name = gh_repo.full_name

        return ConnectionTestResponse(
            success=True,
            message="Successfully connected to GitHub repository",
            repo_name=repo_name,
        )
    except GithubException as e:
        if e.status == 401:
            message = "Invalid GitHub token"
        elif e.status == 404:
            message = f"Repository '{github_repo}' not found or not accessible"
        else:
            message = f"GitHub API error: {e.data.get('message', str(e))}"

        return ConnectionTestResponse(
            success=False,
            message=message,
        )
    except Exception as e:
        return ConnectionTestResponse(
            success=False,
            message=f"Connection failed: {str(e)}",
        )


@router.delete("/github", status_code=status.HTTP_204_NO_CONTENT)
async def delete_github_settings(
    admin: RequireAdmin,
    repo: Repo,
) -> None:
    """
    Remove GitHub integration settings.

    Requires admin role.
    After deletion, the system will fall back to environment variables if configured.
    """
    await repo.delete_app_setting("github_repo")
    await repo.delete_app_setting("github_token")
