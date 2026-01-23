"""Domain interfaces - Abstract contracts for repositories and services."""

from atlas.domain.interfaces.authorization import AbstractAuthorizationService
from atlas.domain.interfaces.catalog_repository import AbstractCatalogRepository
from atlas.domain.interfaces.content_repository import AbstractContentRepository
from atlas.domain.interfaces.team_repository import AbstractTeamRepository
from atlas.domain.interfaces.user_repository import AbstractUserRepository

__all__ = [
    "AbstractUserRepository",
    "AbstractTeamRepository",
    "AbstractCatalogRepository",
    "AbstractContentRepository",
    "AbstractAuthorizationService",
]
