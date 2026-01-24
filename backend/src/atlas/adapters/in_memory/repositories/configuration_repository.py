"""In-memory implementation of Configuration repository for testing."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from atlas.domain.entities import UserConfiguration
from atlas.domain.interfaces import AbstractConfigurationRepository


class InMemoryConfigurationRepository(AbstractConfigurationRepository):
    """In-memory configuration repository implementation for testing."""

    def __init__(self) -> None:
        """Initialize with empty storage."""
        self._configs: dict[UUID, UserConfiguration] = {}
        self._by_user: dict[UUID, UUID] = {}  # user_id -> config_id mapping

    def clear(self) -> None:
        """Reset storage (useful in tests)."""
        self._configs.clear()
        self._by_user.clear()

    async def get_by_user_id(self, user_id: UUID) -> Optional[UserConfiguration]:
        """Get configuration for a user."""
        config_id = self._by_user.get(user_id)
        if config_id is None:
            return None
        return self._configs.get(config_id)

    async def get_by_id(self, config_id: UUID) -> Optional[UserConfiguration]:
        """Get configuration by its ID."""
        return self._configs.get(config_id)

    async def save(self, config: UserConfiguration) -> UserConfiguration:
        """Save or update configuration (upsert by user_id)."""
        existing_id = self._by_user.get(config.user_id)

        if existing_id:
            # Update existing - use same ID, update fields
            existing = self._configs[existing_id]
            updated = UserConfiguration(
                id=existing_id,
                user_id=config.user_id,
                git_path=config.git_path,
                current_commit_sha=config.current_commit_sha,
                created_at=existing.created_at,
                updated_at=datetime.utcnow(),
            )
            self._configs[existing_id] = updated
            return updated
        else:
            # Create new
            self._configs[config.id] = config
            self._by_user[config.user_id] = config.id
            return config

    async def delete(self, config_id: UUID) -> bool:
        """Delete configuration by its ID."""
        config = self._configs.get(config_id)
        if config is None:
            return False
        del self._configs[config_id]
        del self._by_user[config.user_id]
        return True
