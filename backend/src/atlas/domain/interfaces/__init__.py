"""Domain interfaces - Abstract contracts for repositories and services."""

from atlas.domain.interfaces.auth_service import AbstractAuthService
from atlas.domain.interfaces.authorization import AbstractAuthorizationService
from atlas.domain.interfaces.content_repository import AbstractContentRepository
from atlas.domain.interfaces.email_service import AbstractEmailService
from atlas.domain.interfaces.repository import AbstractRepository
from atlas.domain.interfaces.sync_service import AbstractSyncService, SyncResult

__all__ = [
    "AbstractAuthService",
    "AbstractAuthorizationService",
    "AbstractContentRepository",
    "AbstractEmailService",
    "AbstractRepository",
    "AbstractSyncService",
    "SyncResult",
]
