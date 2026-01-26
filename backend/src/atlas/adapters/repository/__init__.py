"""Repository adapter - Database storage implementations."""

from atlas.adapters.repository.exceptions import (
    ConnectionError,
    DuplicateEntityError,
    EntityNotFoundError,
    RepositoryError,
)
from atlas.adapters.repository.interface import AbstractRepository
from atlas.adapters.repository.models import (
    TeamModel,
    UserConfigurationModel,
    UserModel,
    UserTeamLink,
)
from atlas.adapters.repository.postgresql import PostgreSQLRepository
from atlas.adapters.repository.session import AsyncSession, get_session, init_db

__all__ = [
    "AbstractRepository",
    "AsyncSession",
    "ConnectionError",
    "DuplicateEntityError",
    "EntityNotFoundError",
    "PostgreSQLRepository",
    "RepositoryError",
    "TeamModel",
    "UserConfigurationModel",
    "UserModel",
    "UserTeamLink",
    "get_session",
    "init_db",
]
