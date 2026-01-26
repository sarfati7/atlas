"""Configuration routes - Manage user's claude.md configuration."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, UploadFile, status
from pydantic import BaseModel

from atlas.adapters.catalog.exceptions import CatalogPermissionError
from atlas.application.services import ConfigurationNotFoundError, VersionNotFoundError
from atlas.entrypoints.dependencies import Atlas, CurrentUser

router = APIRouter(prefix="/configuration", tags=["configuration"])


class ConfigurationResponse(BaseModel):
    """Response containing configuration content and metadata."""

    content: str
    commit_sha: str
    updated_at: datetime


class ConfigurationUpdateRequest(BaseModel):
    """Request to update configuration content."""

    content: str
    message: Optional[str] = None


class VersionResponse(BaseModel):
    """Single version in history."""

    commit_sha: str
    message: str
    author: str
    timestamp: datetime


class VersionHistoryResponse(BaseModel):
    """Version history response."""

    versions: list[VersionResponse]
    total: int


@router.get("/me", response_model=ConfigurationResponse)
async def get_my_configuration(
    current_user: CurrentUser,
    atlas: Atlas,
) -> ConfigurationResponse:
    """
    Get current user's configuration.

    Returns empty content if user has not created a configuration yet.
    """
    content, config = await atlas.get_user_configuration(current_user.id)
    return ConfigurationResponse(
        content=content,
        commit_sha=config.current_commit_sha,
        updated_at=config.updated_at,
    )


@router.put("/me", response_model=ConfigurationResponse)
async def update_my_configuration(
    body: ConfigurationUpdateRequest,
    current_user: CurrentUser,
    atlas: Atlas,
) -> ConfigurationResponse:
    """
    Update current user's configuration.

    Creates a new git commit with the updated content.
    Optionally accepts a custom commit message.
    """
    try:
        config = await atlas.save_user_configuration(
            user_id=current_user.id,
            content=body.content,
            message=body.message,
        )
    except CatalogPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message,
        )

    return ConfigurationResponse(
        content=body.content,
        commit_sha=config.current_commit_sha,
        updated_at=config.updated_at,
    )


@router.get("/me/history", response_model=VersionHistoryResponse)
async def get_configuration_history(
    current_user: CurrentUser,
    atlas: Atlas,
    limit: int = Query(default=50, ge=1, le=100, description="Max versions to return"),
) -> VersionHistoryResponse:
    """
    Get version history of user's configuration.

    Returns list of all commits (versions) for the configuration file.
    """
    versions = await atlas.get_configuration_versions(
        user_id=current_user.id,
        limit=limit,
    )

    return VersionHistoryResponse(
        versions=[
            VersionResponse(
                commit_sha=v.commit_sha,
                message=v.message,
                author=v.author,
                timestamp=v.timestamp,
            )
            for v in versions
        ],
        total=len(versions),
    )


@router.post("/me/rollback/{commit_sha}", response_model=ConfigurationResponse)
async def rollback_configuration(
    commit_sha: str,
    current_user: CurrentUser,
    atlas: Atlas,
) -> ConfigurationResponse:
    """
    Rollback configuration to a previous version.

    Creates a new commit with the content from the specified version.
    """
    try:
        config = await atlas.rollback_configuration_to_version(
            user_id=current_user.id,
            commit_sha=commit_sha,
        )
    except ConfigurationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No configuration found for user",
        )
    except VersionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {commit_sha} not found",
        )
    except CatalogPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message,
        )

    content, _ = await atlas.get_user_configuration(current_user.id)

    return ConfigurationResponse(
        content=content,
        commit_sha=config.current_commit_sha,
        updated_at=config.updated_at,
    )


@router.post("/me/import", response_model=ConfigurationResponse)
async def import_configuration(
    file: UploadFile,
    current_user: CurrentUser,
    atlas: Atlas,
) -> ConfigurationResponse:
    """
    Import configuration from uploaded .md file.

    Accepts a markdown file and saves it as the user's configuration.
    """
    if not file.filename or not file.filename.endswith(".md"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a .md file",
        )

    content_bytes = await file.read()

    if len(content_bytes) > 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 1MB",
        )

    try:
        content_str = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be valid UTF-8 text",
        )

    try:
        config = await atlas.import_user_configuration(
            user_id=current_user.id,
            content=content_str,
        )
    except CatalogPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message,
        )

    return ConfigurationResponse(
        content=content_str,
        commit_sha=config.current_commit_sha,
        updated_at=config.updated_at,
    )
