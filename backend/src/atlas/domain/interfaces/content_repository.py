"""Content repository interface - Abstract contract for git content operations."""

from abc import ABC, abstractmethod
from typing import Optional


class AbstractContentRepository(ABC):
    """
    Abstract repository interface for git content operations.

    Manages the actual file content stored in git (skills, MCPs, tools).
    Metadata is managed by CatalogRepository.
    """

    @abstractmethod
    async def get_content(self, path: str) -> Optional[str]:
        """
        Retrieve file content from git by path.

        Returns None if file does not exist.
        """
        raise NotImplementedError

    @abstractmethod
    async def save_content(self, path: str, content: str, message: str) -> str:
        """
        Save content to git (create or update file).

        Args:
            path: File path in git repository (e.g., "skills/my-skill.md")
            content: File content to save
            message: Commit message

        Returns:
            Commit SHA of the created commit.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_content(self, path: str, message: str) -> str:
        """
        Delete a file from git.

        Args:
            path: File path to delete
            message: Commit message

        Returns:
            Commit SHA of the created commit.
        """
        raise NotImplementedError

    @abstractmethod
    async def list_contents(self, directory: str) -> list[str]:
        """
        List all file paths in a directory.

        Returns list of relative file paths within the directory.
        """
        raise NotImplementedError

    @abstractmethod
    async def exists(self, path: str) -> bool:
        """Check if a file exists at the given path."""
        raise NotImplementedError

    @abstractmethod
    async def get_commit_sha(self, path: str) -> Optional[str]:
        """
        Get the latest commit SHA for a file.

        Returns None if file does not exist.
        """
        raise NotImplementedError
