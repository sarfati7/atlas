"""GitHub content repository - Implements content storage via GitHub API."""

import asyncio
from typing import Optional

from github import Github, GithubException

from atlas.domain.interfaces import AbstractContentRepository


class GitHubContentRepository(AbstractContentRepository):
    """
    GitHub implementation of content repository.

    Uses PyGithub to interact with a GitHub repository for storing
    content files (skills, MCPs, tools). Actual content is stored
    in git while metadata lives in PostgreSQL.
    """

    def __init__(self, token: str, repo_name: str) -> None:
        """
        Initialize GitHub content repository.

        Args:
            token: GitHub personal access token
            repo_name: Repository in "owner/repo" format
        """
        self._github = Github(token)
        self._repo = self._github.get_repo(repo_name)

    async def get_content(self, path: str) -> Optional[str]:
        """Retrieve file content from GitHub by path."""
        try:
            content = await asyncio.to_thread(self._repo.get_contents, path)
            return content.decoded_content.decode("utf-8")
        except GithubException:
            return None

    async def save_content(self, path: str, content: str, message: str) -> str:
        """
        Save content to GitHub (create or update file).

        Returns the commit SHA.
        """
        try:
            # Try to get existing file for update
            existing = await asyncio.to_thread(self._repo.get_contents, path)
            result = await asyncio.to_thread(
                self._repo.update_file,
                path,
                message,
                content,
                existing.sha,
            )
        except GithubException:
            # File doesn't exist, create it
            result = await asyncio.to_thread(
                self._repo.create_file,
                path,
                message,
                content,
            )
        return result["commit"].sha

    async def delete_content(self, path: str, message: str) -> str:
        """
        Delete a file from GitHub.

        Returns the commit SHA.
        """
        existing = await asyncio.to_thread(self._repo.get_contents, path)
        result = await asyncio.to_thread(
            self._repo.delete_file,
            path,
            message,
            existing.sha,
        )
        return result["commit"].sha

    async def list_contents(self, directory: str) -> list[str]:
        """List all file paths in a directory."""
        try:
            contents = await asyncio.to_thread(self._repo.get_contents, directory)
            # Handle case where contents is a single file
            if not isinstance(contents, list):
                contents = [contents]
            return [c.path for c in contents]
        except GithubException:
            return []

    async def exists(self, path: str) -> bool:
        """Check if a file exists at the given path."""
        try:
            await asyncio.to_thread(self._repo.get_contents, path)
            return True
        except GithubException:
            return False

    async def get_commit_sha(self, path: str) -> Optional[str]:
        """Get the latest commit SHA for a file."""
        try:
            commits = await asyncio.to_thread(
                self._repo.get_commits,
                path=path,
            )
            # Get the most recent commit
            first_commit = await asyncio.to_thread(lambda: next(iter(commits), None))
            if first_commit:
                return first_commit.sha
            return None
        except GithubException:
            return None
