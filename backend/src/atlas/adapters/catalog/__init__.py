"""Catalog adapter - Git-based catalog storage implementations."""

from atlas.adapters.catalog.exceptions import (
    CatalogConnectionError,
    CatalogError,
    ContentNotFoundError,
    ContentWriteError,
    VersionNotFoundError,
)
from atlas.adapters.catalog.github import GitHubCatalogRepository
from atlas.adapters.catalog.in_memory import InMemoryCatalogRepository
from atlas.adapters.catalog.interface import AbstractCatalogRepository

__all__ = [
    "AbstractCatalogRepository",
    "CatalogConnectionError",
    "CatalogError",
    "ContentNotFoundError",
    "ContentWriteError",
    "GitHubCatalogRepository",
    "InMemoryCatalogRepository",
    "VersionNotFoundError",
]
