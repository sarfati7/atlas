"""PostgreSQL repository implementation."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from atlas.adapters.repository.interface import AbstractRepository
from atlas.adapters.repository.models import (
    AuditLogModel,
    TeamModel,
    UserConfigurationModel,
    UserModel,
    UserTeamLink,
)
from atlas.domain.entities import AuditLog, Team, User, UserConfiguration
from atlas.domain.entities.user import UserRole


class PostgreSQLRepository(AbstractRepository):
    """
    PostgreSQL repository for database operations.

    Works with any SQLAlchemy-compatible database (PostgreSQL, SQLite).
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with async database session."""
        self._session = session

    # -------------------------------------------------------------------------
    # User operations
    # -------------------------------------------------------------------------

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        statement = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return self._user_to_entity(model) if model else None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        statement = select(UserModel).where(UserModel.email == email)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return self._user_to_entity(model) if model else None

    async def get_user_by_username(self, username: str) -> Optional[User]:
        statement = select(UserModel).where(UserModel.username == username)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return self._user_to_entity(model) if model else None

    async def save_user(self, user: User) -> User:
        existing = await self._session.get(UserModel, user.id)
        if existing:
            existing.email = user.email
            existing.username = user.username
            existing.role = user.role.value
            existing.updated_at = user.updated_at
            if user.password_hash:
                existing.password_hash = user.password_hash
            self._session.add(existing)
        else:
            model = UserModel(
                id=user.id,
                email=user.email,
                username=user.username,
                password_hash=user.password_hash or "",
                role=user.role.value,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            self._session.add(model)
        await self._session.commit()

        statement = select(UserModel).where(UserModel.id == user.id)
        result = await self._session.execute(statement)
        saved_model = result.scalar_one()
        return self._user_to_entity(saved_model)

    async def delete_user(self, user_id: UUID) -> bool:
        model = await self._session.get(UserModel, user_id)
        if not model:
            return False
        await self._session.delete(model)
        await self._session.commit()
        return True

    async def list_users(self) -> list[User]:
        statement = select(UserModel)
        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [self._user_to_entity(m) for m in models]

    def _user_to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            username=model.username,
            password_hash=model.password_hash if model.password_hash else None,
            role=UserRole(model.role) if model.role else UserRole.USER,
            team_ids=[team.id for team in model.teams] if model.teams else [],
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    # -------------------------------------------------------------------------
    # Team operations
    # -------------------------------------------------------------------------

    async def get_team_by_id(self, team_id: UUID) -> Optional[Team]:
        statement = select(TeamModel).where(TeamModel.id == team_id)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return self._team_to_entity(model) if model else None

    async def get_team_by_name(self, name: str) -> Optional[Team]:
        statement = select(TeamModel).where(TeamModel.name == name)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return self._team_to_entity(model) if model else None

    async def save_team(self, team: Team) -> Team:
        existing = await self._session.get(TeamModel, team.id)
        if existing:
            existing.name = team.name
            existing.updated_at = team.updated_at
            self._session.add(existing)
        else:
            model = TeamModel(
                id=team.id,
                name=team.name,
                created_at=team.created_at,
                updated_at=team.updated_at,
            )
            self._session.add(model)
        await self._session.commit()

        statement = select(TeamModel).where(TeamModel.id == team.id)
        result = await self._session.execute(statement)
        saved_model = result.scalar_one()
        return self._team_to_entity(saved_model)

    async def delete_team(self, team_id: UUID) -> bool:
        model = await self._session.get(TeamModel, team_id)
        if not model:
            return False
        await self._session.delete(model)
        await self._session.commit()
        return True

    async def list_teams(self) -> list[Team]:
        statement = select(TeamModel)
        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [self._team_to_entity(m) for m in models]

    async def get_user_teams(self, user_id: UUID) -> list[Team]:
        statement = (
            select(TeamModel).join(UserTeamLink).where(UserTeamLink.user_id == user_id)
        )
        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [self._team_to_entity(m) for m in models]

    def _team_to_entity(self, model: TeamModel) -> Team:
        return Team(
            id=model.id,
            name=model.name,
            member_ids=[member.id for member in model.members] if model.members else [],
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    # -------------------------------------------------------------------------
    # Configuration operations
    # -------------------------------------------------------------------------

    async def get_configuration_by_user_id(
        self, user_id: UUID
    ) -> Optional[UserConfiguration]:
        statement = select(UserConfigurationModel).where(
            UserConfigurationModel.user_id == user_id
        )
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return self._config_to_entity(model) if model else None

    async def get_configuration_by_id(
        self, config_id: UUID
    ) -> Optional[UserConfiguration]:
        statement = select(UserConfigurationModel).where(
            UserConfigurationModel.id == config_id
        )
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return self._config_to_entity(model) if model else None

    async def save_configuration(
        self, config: UserConfiguration
    ) -> UserConfiguration:
        existing = await self._session.get(UserConfigurationModel, config.id)

        if existing:
            existing.git_path = config.git_path
            existing.current_commit_sha = config.current_commit_sha
            existing.updated_at = datetime.utcnow()
            self._session.add(existing)
        else:
            stmt = select(UserConfigurationModel).where(
                UserConfigurationModel.user_id == config.user_id
            )
            result = await self._session.execute(stmt)
            existing_for_user = result.scalar_one_or_none()

            if existing_for_user:
                existing_for_user.git_path = config.git_path
                existing_for_user.current_commit_sha = config.current_commit_sha
                existing_for_user.updated_at = datetime.utcnow()
                self._session.add(existing_for_user)
                await self._session.commit()
                return self._config_to_entity(existing_for_user)
            else:
                model = UserConfigurationModel(
                    id=config.id,
                    user_id=config.user_id,
                    git_path=config.git_path,
                    current_commit_sha=config.current_commit_sha,
                    created_at=config.created_at,
                    updated_at=config.updated_at,
                )
                self._session.add(model)

        await self._session.commit()

        statement = select(UserConfigurationModel).where(
            UserConfigurationModel.user_id == config.user_id
        )
        result = await self._session.execute(statement)
        saved_model = result.scalar_one()
        return self._config_to_entity(saved_model)

    async def delete_configuration(self, config_id: UUID) -> bool:
        model = await self._session.get(UserConfigurationModel, config_id)
        if not model:
            return False
        await self._session.delete(model)
        await self._session.commit()
        return True

    def _config_to_entity(self, model: UserConfigurationModel) -> UserConfiguration:
        return UserConfiguration(
            id=model.id,
            user_id=model.user_id,
            git_path=model.git_path,
            current_commit_sha=model.current_commit_sha,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    # -------------------------------------------------------------------------
    # Audit log operations
    # -------------------------------------------------------------------------

    async def save_audit_log(self, log: AuditLog) -> AuditLog:
        model = AuditLogModel(
            id=log.id,
            user_id=log.user_id,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            details=log.details,
            created_at=log.created_at,
        )
        self._session.add(model)
        await self._session.commit()

        statement = select(AuditLogModel).where(AuditLogModel.id == log.id)
        result = await self._session.execute(statement)
        saved_model = result.scalar_one()
        return self._audit_log_to_entity(saved_model)

    async def get_audit_logs(
        self,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditLog]:
        statement = select(AuditLogModel)

        if resource_type is not None:
            statement = statement.where(AuditLogModel.resource_type == resource_type)
        if resource_id is not None:
            statement = statement.where(AuditLogModel.resource_id == resource_id)
        if user_id is not None:
            statement = statement.where(AuditLogModel.user_id == user_id)

        statement = statement.order_by(AuditLogModel.created_at.desc())
        statement = statement.offset(offset).limit(limit)

        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [self._audit_log_to_entity(m) for m in models]

    async def count_audit_logs(
        self,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
    ) -> int:
        from sqlalchemy import func

        statement = select(func.count(AuditLogModel.id))

        if resource_type is not None:
            statement = statement.where(AuditLogModel.resource_type == resource_type)
        if resource_id is not None:
            statement = statement.where(AuditLogModel.resource_id == resource_id)
        if user_id is not None:
            statement = statement.where(AuditLogModel.user_id == user_id)

        result = await self._session.execute(statement)
        return result.scalar_one()

    def _audit_log_to_entity(self, model: AuditLogModel) -> AuditLog:
        return AuditLog(
            id=model.id,
            user_id=model.user_id,
            action=model.action,
            resource_type=model.resource_type,
            resource_id=model.resource_id,
            details=model.details if model.details else {},
            created_at=model.created_at,
        )
