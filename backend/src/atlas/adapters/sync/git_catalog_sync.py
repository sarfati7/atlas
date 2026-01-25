"""Git-to-database sync service implementation."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from atlas.domain.entities.catalog_item import CatalogItem, CatalogItemType
from atlas.domain.interfaces.content_repository import AbstractContentRepository
from atlas.domain.interfaces.repository import AbstractRepository
from atlas.domain.interfaces.sync_service import AbstractSyncService, SyncResult


class GitCatalogSyncService(AbstractSyncService):
    """
    Synchronizes git content with database catalog metadata.

    Compares files in git (skills/, mcps/, tools/) with CatalogItem records
    in the database and creates/updates/deletes records to match git state.
    """

    # Directory prefixes mapped to catalog item types
    DIRECTORY_TYPE_MAP: dict[str, CatalogItemType] = {
        "skills/": CatalogItemType.SKILL,
        "mcps/": CatalogItemType.MCP,
        "tools/": CatalogItemType.TOOL,
    }

    def __init__(
        self,
        content_repo: AbstractContentRepository,
        repo: AbstractRepository,
        default_author_id: UUID,
    ) -> None:
        """
        Initialize sync service.

        Args:
            content_repo: Repository for git content operations
            repo: Repository for database operations
            default_author_id: UUID to use as author for items created via sync
        """
        self._content_repo = content_repo
        self._repo = repo
        self._default_author_id = default_author_id

    async def sync_all(self) -> SyncResult:
        """
        Full sync: compare all git files with database and reconcile.

        1. List all files from git in skills/, mcps/, tools/
        2. Get all existing catalog items from database
        3. Compare and reconcile:
           - Files in git but not in DB -> create CatalogItem
           - Files in DB but not in git -> delete CatalogItem
           - Files in both -> update if modified
        """
        created = 0
        updated = 0
        deleted = 0
        errors: list[str] = []

        # Collect all git paths
        git_paths: set[str] = set()
        for directory in self.DIRECTORY_TYPE_MAP.keys():
            try:
                paths = await self._content_repo.list_contents(directory)
                git_paths.update(paths)
            except Exception as e:
                errors.append(f"Failed to list {directory}: {e}")

        # Get all existing catalog items
        try:
            existing_items = await self._repo.list_catalog_items()
        except Exception as e:
            errors.append(f"Failed to list catalog items: {e}")
            return SyncResult(created=0, updated=0, deleted=0, errors=errors)

        # Build lookup map by git_path
        existing_by_path: dict[str, CatalogItem] = {
            item.git_path: item for item in existing_items
        }
        existing_paths = set(existing_by_path.keys())

        # Files to create (in git but not in DB)
        paths_to_create = git_paths - existing_paths
        for path in paths_to_create:
            try:
                item_type = self._path_to_type(path)
                if item_type is None:
                    continue  # Skip files not in recognized directories
                item = self._create_catalog_item(path, item_type)
                await self._repo.save_catalog_item(item)
                created += 1
            except Exception as e:
                errors.append(f"Failed to create item for {path}: {e}")

        # Files to delete (in DB but not in git)
        paths_to_delete = existing_paths - git_paths
        for path in paths_to_delete:
            try:
                item = existing_by_path[path]
                await self._repo.delete_catalog_item(item.id)
                deleted += 1
            except Exception as e:
                errors.append(f"Failed to delete item for {path}: {e}")

        # Files that exist in both - update if modified
        paths_to_check = git_paths & existing_paths
        for path in paths_to_check:
            try:
                existing_item = existing_by_path[path]
                # Check if content has changed by comparing commit SHAs
                current_sha = await self._content_repo.get_commit_sha(path)
                # If we can detect a change, update the timestamp
                # For now, we just touch updated_at on each sync
                # A more sophisticated approach would store and compare SHAs
                existing_item.updated_at = datetime.utcnow()
                await self._repo.save_catalog_item(existing_item)
                updated += 1
            except Exception as e:
                errors.append(f"Failed to update item for {path}: {e}")

        return SyncResult(created=created, updated=updated, deleted=deleted, errors=errors)

    async def sync_paths(self, paths: list[str]) -> SyncResult:
        """
        Partial sync: sync only specified paths.

        More efficient than full sync when webhook provides changed paths.
        """
        created = 0
        updated = 0
        deleted = 0
        errors: list[str] = []

        for path in paths:
            try:
                item_type = self._path_to_type(path)
                if item_type is None:
                    continue  # Skip files not in recognized directories

                # Check if file exists in git
                file_exists = await self._content_repo.exists(path)

                # Check if item exists in database
                existing_item = await self._repo.get_catalog_item_by_git_path(path)

                if file_exists and existing_item is None:
                    # Create new item
                    item = self._create_catalog_item(path, item_type)
                    await self._repo.save_catalog_item(item)
                    created += 1
                elif file_exists and existing_item is not None:
                    # Update existing item
                    existing_item.updated_at = datetime.utcnow()
                    await self._repo.save_catalog_item(existing_item)
                    updated += 1
                elif not file_exists and existing_item is not None:
                    # Delete item
                    await self._repo.delete_catalog_item(existing_item.id)
                    deleted += 1
                # else: file doesn't exist and item doesn't exist - nothing to do

            except Exception as e:
                errors.append(f"Failed to sync {path}: {e}")

        return SyncResult(created=created, updated=updated, deleted=deleted, errors=errors)

    def _path_to_type(self, path: str) -> Optional[CatalogItemType]:
        """Map a file path to its catalog item type based on directory prefix."""
        for prefix, item_type in self.DIRECTORY_TYPE_MAP.items():
            if path.startswith(prefix):
                return item_type
        return None

    def _extract_name(self, path: str) -> str:
        """Extract name from path (filename without extension)."""
        # Get filename from path
        filename = path.rsplit("/", 1)[-1]
        # Remove extension
        if "." in filename:
            return filename.rsplit(".", 1)[0]
        return filename

    def _create_catalog_item(self, path: str, item_type: CatalogItemType) -> CatalogItem:
        """Create a new CatalogItem entity from a git path."""
        name = self._extract_name(path)
        return CatalogItem(
            type=item_type,
            name=name,
            description="",  # Description will be populated when content is parsed
            git_path=path,
            author_id=self._default_author_id,
        )
