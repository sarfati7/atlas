"""Domain interfaces - Abstract contracts for repositories and services."""

from atlas.domain.interfaces.auth_service import AbstractAuthService
from atlas.domain.interfaces.authorization import AbstractAuthorizationService
from atlas.domain.interfaces.catalog_repository import AbstractCatalogRepository
from atlas.domain.interfaces.configuration_repository import (
    AbstractConfigurationRepository,
)
from atlas.domain.interfaces.content_repository import AbstractContentRepository
from atlas.domain.interfaces.email_service import AbstractEmailService
from atlas.domain.interfaces.sync_service import AbstractSyncService, SyncResult
from atlas.domain.interfaces.team_repository import AbstractTeamRepository
from atlas.domain.interfaces.user_repository import AbstractUserRepository

__all__ = [
    "AbstractAuthService",
    "AbstractEmailService",
    "AbstractUserRepository",
    "AbstractTeamRepository",
    "AbstractCatalogRepository",
    "AbstractConfigurationRepository",
    "AbstractContentRepository",
    "AbstractAuthorizationService",
    "AbstractSyncService",
    "SyncResult",
]
