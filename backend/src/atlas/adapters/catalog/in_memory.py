"""In-memory catalog repository - Implements catalog storage for testing."""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from atlas.adapters.catalog.interface import AbstractCatalogRepository
from atlas.domain.entities import ConfigurationVersion


class InMemoryCatalogRepository(AbstractCatalogRepository):
    """
    In-memory implementation of catalog repository.

    Uses a dictionary to store content for testing without external dependencies.
    """

    def __init__(self) -> None:
        """Initialize empty in-memory storage."""
        self._contents: dict[str, str] = {}
        self._commit_shas: dict[str, str] = {}

    async def get_content(self, path: str) -> Optional[str]:
        """Retrieve file content by path."""
        return self._contents.get(path)

    async def save_content(self, path: str, content: str, message: str) -> str:
        """Save content (create or update file)."""
        self._contents[path] = content
        sha = uuid4().hex[:7]
        self._commit_shas[path] = sha
        return sha

    async def delete_content(self, path: str, message: str) -> str:
        """Delete a file."""
        self._contents.pop(path, None)
        sha = uuid4().hex[:7]
        self._commit_shas.pop(path, None)
        return sha

    async def list_contents(self, directory: str) -> list[str]:
        """List all file paths in a directory."""
        if not directory.endswith("/"):
            directory = directory + "/"
        return [path for path in self._contents.keys() if path.startswith(directory)]

    async def exists(self, path: str) -> bool:
        """Check if a file exists at the given path."""
        return path in self._contents

    async def get_commit_sha(self, path: str) -> Optional[str]:
        """Get the latest commit SHA for a file."""
        return self._commit_shas.get(path)

    async def get_version_history(
        self,
        path: str,
        limit: int = 50,
    ) -> list[ConfigurationVersion]:
        """Get version history (returns single version if file exists)."""
        if path not in self._contents:
            return []
        return [
            ConfigurationVersion(
                commit_sha=self._commit_shas.get(path, "in-memory-sha"),
                message="In-memory content",
                author="test",
                timestamp=datetime.utcnow(),
            )
        ]

    async def get_content_at_version(
        self,
        path: str,
        commit_sha: str,
    ) -> Optional[str]:
        """Get content at version (returns current content)."""
        return self._contents.get(path)

    def clear(self) -> None:
        """Clear all stored content (useful for tests)."""
        self._contents.clear()
        self._commit_shas.clear()
