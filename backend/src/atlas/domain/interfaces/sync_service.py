"""Sync service interface - Abstract contract for git-to-database synchronization."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SyncResult:
    """Result of a sync operation."""

    created: int  # Number of new catalog items created
    updated: int  # Number of catalog items updated
    deleted: int  # Number of catalog items deleted
    errors: list[str]  # Any errors encountered


class AbstractSyncService(ABC):
    """
    Abstract interface for synchronizing git content with database catalog.

    Implementations handle the reconciliation between git file state
    and CatalogItem records in the database.
    """

    @abstractmethod
    async def sync_all(self) -> SyncResult:
        """
        Full sync: compare all git files with database and reconcile.

        Compares all files in skills/, mcps/, tools/ directories with
        all CatalogItem records and creates/updates/deletes as needed.
        """
        raise NotImplementedError

    @abstractmethod
    async def sync_paths(self, paths: list[str]) -> SyncResult:
        """
        Partial sync: sync only specified paths (from webhook payload).

        More efficient than full sync when changes are known.
        Handles creates, updates, and deletes for the specified paths.
        """
        raise NotImplementedError
