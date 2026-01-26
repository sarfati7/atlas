"""GitHub catalog repository - Implements catalog storage via GitHub API."""

import asyncio
from datetime import datetime
from typing import Optional

from github import Github, GithubException

from atlas.adapters.catalog.interface import AbstractCatalogRepository
from atlas.domain.entities import ConfigurationVersion


class GitHubCatalogRepository(AbstractCatalogRepository):
    """
    GitHub implementation of catalog repository.

    Uses PyGithub to interact with a GitHub repository for storing
    catalog files (skills, MCPs, tools).
    """

    def __init__(self, token: str, repo_name: str) -> None:
        """
        Initialize GitHub catalog repository.

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
        """Save content to GitHub (create or update file)."""
        try:
            existing = await asyncio.to_thread(self._repo.get_contents, path)
            result = await asyncio.to_thread(
                self._repo.update_file,
                path,
                message,
                content,
                existing.sha,
            )
        except GithubException:
            result = await asyncio.to_thread(
                self._repo.create_file,
                path,
                message,
                content,
            )
        return result["commit"].sha

    async def delete_content(self, path: str, message: str) -> str:
        """Delete a file from GitHub."""
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
            first_commit = await asyncio.to_thread(lambda: next(iter(commits), None))
            if first_commit:
                return first_commit.sha
            return None
        except GithubException:
            return None

    async def get_version_history(
        self,
        path: str,
        limit: int = 50,
    ) -> list[ConfigurationVersion]:
        """Get commit history for a file."""
        try:
            commits = await asyncio.to_thread(
                self._repo.get_commits,
                path=path,
            )
            versions = []
            for i, commit in enumerate(commits):
                if i >= limit:
                    break
                versions.append(
                    ConfigurationVersion(
                        commit_sha=commit.sha,
                        message=commit.commit.message,
                        author=(
                            commit.commit.author.name
                            if commit.commit.author
                            else "Unknown"
                        ),
                        timestamp=(
                            commit.commit.author.date
                            if commit.commit.author
                            else datetime.utcnow()
                        ),
                    )
                )
            return versions
        except GithubException:
            return []

    async def get_content_at_version(
        self,
        path: str,
        commit_sha: str,
    ) -> Optional[str]:
        """Get file content at specific commit SHA."""
        try:
            content = await asyncio.to_thread(
                self._repo.get_contents,
                path,
                ref=commit_sha,
            )
            return content.decoded_content.decode("utf-8")
        except GithubException:
            return None
