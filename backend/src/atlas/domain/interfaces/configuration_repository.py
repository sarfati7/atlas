"""Configuration repository interface - Abstract contract for configuration metadata access."""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from atlas.domain.entities import UserConfiguration


class AbstractConfigurationRepository(ABC):
    """
    Abstract repository interface for user configuration metadata.

    Handles metadata storage for user configurations.
    Actual content is managed by ContentRepository.
    """

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Optional[UserConfiguration]:
        """
        Get configuration metadata for a user.

        Returns None if user has no configuration yet.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, config_id: UUID) -> Optional[UserConfiguration]:
        """
        Get configuration by its ID.

        Returns None if not found.
        """
        raise NotImplementedError

    @abstractmethod
    async def save(self, config: UserConfiguration) -> UserConfiguration:
        """
        Save or update configuration metadata (upsert by user_id).

        Returns the saved configuration with any generated fields populated.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, config_id: UUID) -> bool:
        """
        Delete configuration metadata.

        Returns True if deleted, False if not found.
        """
        raise NotImplementedError
