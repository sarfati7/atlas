"""Configuration service - Orchestrates git content + database metadata."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from atlas.domain.entities import ConfigurationVersion, UserConfiguration
from atlas.domain.interfaces import (
    AbstractConfigurationRepository,
    AbstractContentRepository,
)


class ConfigurationNotFoundError(Exception):
    """Raised when configuration doesn't exist for user."""

    pass


class VersionNotFoundError(Exception):
    """Raised when requested version (commit SHA) doesn't exist."""

    pass


class ConfigurationService:
    """
    Service layer for configuration operations.

    Orchestrates git content storage with database metadata tracking.
    Git stores actual claude.md content; database stores user-to-path mapping.
    """

    def __init__(
        self,
        config_repo: AbstractConfigurationRepository,
        content_repo: AbstractContentRepository,
    ) -> None:
        self._config_repo = config_repo
        self._content_repo = content_repo

    def _get_user_config_path(self, user_id: UUID) -> str:
        """Generate git path for user's configuration."""
        return f"configs/users/{user_id}/claude.md"

    async def get_configuration(self, user_id: UUID) -> tuple[str, UserConfiguration]:
        """
        Get user's current configuration content and metadata.

        Returns tuple of (content, metadata).
        Returns empty content if user has no configuration yet.
        """
        config = await self._config_repo.get_by_user_id(user_id)

        if config is None:
            # No config exists yet - return empty content with placeholder metadata
            path = self._get_user_config_path(user_id)
            return "", UserConfiguration(
                id=uuid4(),
                user_id=user_id,
                git_path=path,
                current_commit_sha="",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

        # Fetch content from git
        content = await self._content_repo.get_content(config.git_path)
        return content or "", config

    async def save_configuration(
        self,
        user_id: UUID,
        content: str,
        message: Optional[str] = None,
    ) -> UserConfiguration:
        """
        Save configuration content with git versioning.

        Creates or updates the configuration, committing to git and
        updating database metadata.
        """
        path = self._get_user_config_path(user_id)
        commit_message = message or f"Update configuration for user {user_id}"

        # Save to git (creates new commit)
        commit_sha = await self._content_repo.save_content(
            path=path,
            content=content,
            message=commit_message,
        )

        # Get or create database record
        config = await self._config_repo.get_by_user_id(user_id)
        if config is None:
            config = UserConfiguration(
                id=uuid4(),
                user_id=user_id,
                git_path=path,
                current_commit_sha=commit_sha,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        else:
            config = UserConfiguration(
                id=config.id,
                user_id=config.user_id,
                git_path=config.git_path,
                current_commit_sha=commit_sha,
                created_at=config.created_at,
                updated_at=datetime.utcnow(),
            )

        # Save metadata to database
        return await self._config_repo.save(config)

    async def get_version_history(
        self,
        user_id: UUID,
        limit: int = 50,
    ) -> list[ConfigurationVersion]:
        """
        Get version history for user's configuration.

        Returns empty list if no configuration exists yet.
        """
        config = await self._config_repo.get_by_user_id(user_id)
        if config is None:
            return []

        return await self._content_repo.get_version_history(
            path=config.git_path,
            limit=limit,
        )

    async def rollback_to_version(
        self,
        user_id: UUID,
        commit_sha: str,
    ) -> UserConfiguration:
        """
        Rollback configuration to a previous version.

        Gets content from historical commit and saves as new commit.
        """
        config = await self._config_repo.get_by_user_id(user_id)
        if config is None:
            raise ConfigurationNotFoundError(f"No configuration for user {user_id}")

        # Get content from historical commit
        old_content = await self._content_repo.get_content_at_version(
            path=config.git_path,
            commit_sha=commit_sha,
        )
        if old_content is None:
            raise VersionNotFoundError(f"Version {commit_sha} not found")

        # Save as new commit (creates new version pointing to old content)
        return await self.save_configuration(
            user_id=user_id,
            content=old_content,
            message=f"Rollback to version {commit_sha[:7]}",
        )

    async def import_configuration(
        self,
        user_id: UUID,
        content: str,
    ) -> UserConfiguration:
        """
        Import configuration from uploaded file content.

        Same as save_configuration but with different commit message.
        """
        return await self.save_configuration(
            user_id=user_id,
            content=content,
            message="Import configuration from local file",
        )
