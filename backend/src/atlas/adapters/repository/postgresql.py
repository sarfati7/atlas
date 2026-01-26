"""PostgreSQL repository implementation."""

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import instance_state
from sqlmodel.ext.asyncio.session import AsyncSession

from atlas.adapters.repository.interface import AbstractRepository
from atlas.adapters.repository.models import (
    AppSettingsModel,
    AuditLogModel,
    TeamModel,
    UsageEventModel,
    UserConfigurationModel,
    UserModel,
    UserTeamLink,
)
from atlas.domain.entities import AuditLog, Team, User, UsageEvent, UsageStat, UserConfiguration
from atlas.domain.entities.catalog_item import CatalogItemType
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
        # Check if teams relationship is loaded to avoid lazy loading in async context
        state = instance_state(model)
        teams_loaded = "teams" in state.dict
        team_ids = [team.id for team in model.teams] if teams_loaded and model.teams else []

        return User(
            id=model.id,
            email=model.email,
            username=model.username,
            password_hash=model.password_hash if model.password_hash else None,
            role=UserRole(model.role) if model.role else UserRole.USER,
            team_ids=team_ids,
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
        # Check if members relationship is loaded to avoid lazy loading in async context
        state = instance_state(model)
        members_loaded = "members" in state.dict
        member_ids = [member.id for member in model.members] if members_loaded and model.members else []

        return Team(
            id=model.id,
            name=model.name,
            member_ids=member_ids,
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

    # -------------------------------------------------------------------------
    # Usage event operations
    # -------------------------------------------------------------------------

    async def save_usage_event(self, event: UsageEvent) -> UsageEvent:
        model = UsageEventModel(
            id=event.id,
            user_id=event.user_id,
            item_id=event.item_id,
            item_type=event.item_type.value,
            action=event.action,
            event_metadata=event.metadata,
            created_at=event.created_at,
        )
        self._session.add(model)
        await self._session.commit()

        statement = select(UsageEventModel).where(UsageEventModel.id == event.id)
        result = await self._session.execute(statement)
        saved_model = result.scalar_one()
        return self._usage_event_to_entity(saved_model)

    async def get_usage_events(
        self,
        user_id: Optional[UUID] = None,
        item_id: Optional[UUID] = None,
        item_type: Optional[CatalogItemType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[UsageEvent]:
        statement = select(UsageEventModel)

        if user_id is not None:
            statement = statement.where(UsageEventModel.user_id == user_id)
        if item_id is not None:
            statement = statement.where(UsageEventModel.item_id == item_id)
        if item_type is not None:
            statement = statement.where(UsageEventModel.item_type == item_type.value)
        if start_date is not None:
            statement = statement.where(UsageEventModel.created_at >= start_date)
        if end_date is not None:
            statement = statement.where(UsageEventModel.created_at <= end_date)

        statement = statement.order_by(UsageEventModel.created_at.desc())
        statement = statement.offset(offset).limit(limit)

        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [self._usage_event_to_entity(m) for m in models]

    async def get_usage_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        group_by: Literal["user", "item", "day"] = "day",
    ) -> list[UsageStat]:
        if group_by == "user":
            key_column = UsageEventModel.user_id
            statement = select(
                key_column,
                func.count(UsageEventModel.id).label("count"),
            ).group_by(key_column)
        elif group_by == "item":
            statement = select(
                UsageEventModel.item_id,
                func.count(UsageEventModel.id).label("count"),
                UsageEventModel.item_type,
            ).group_by(UsageEventModel.item_id, UsageEventModel.item_type)
        else:  # day
            statement = select(
                func.date(UsageEventModel.created_at).label("date"),
                func.count(UsageEventModel.id).label("count"),
            ).group_by(func.date(UsageEventModel.created_at))

        if start_date is not None:
            statement = statement.where(UsageEventModel.created_at >= start_date)
        if end_date is not None:
            statement = statement.where(UsageEventModel.created_at <= end_date)

        result = await self._session.execute(statement)
        rows = result.all()

        stats = []
        for row in rows:
            if group_by == "item":
                stats.append(UsageStat(
                    key=str(row[0]),
                    count=row[1],
                    item_type=row[2],
                ))
            else:
                stats.append(UsageStat(
                    key=str(row[0]),
                    count=row[1],
                ))
        return stats

    async def count_usage_events(
        self,
        user_id: Optional[UUID] = None,
        item_id: Optional[UUID] = None,
        item_type: Optional[CatalogItemType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        statement = select(func.count(UsageEventModel.id))

        if user_id is not None:
            statement = statement.where(UsageEventModel.user_id == user_id)
        if item_id is not None:
            statement = statement.where(UsageEventModel.item_id == item_id)
        if item_type is not None:
            statement = statement.where(UsageEventModel.item_type == item_type.value)
        if start_date is not None:
            statement = statement.where(UsageEventModel.created_at >= start_date)
        if end_date is not None:
            statement = statement.where(UsageEventModel.created_at <= end_date)

        result = await self._session.execute(statement)
        return result.scalar_one()

    def _usage_event_to_entity(self, model: UsageEventModel) -> UsageEvent:
        return UsageEvent(
            id=model.id,
            user_id=model.user_id,
            item_id=model.item_id,
            item_type=CatalogItemType(model.item_type),
            action=model.action,
            metadata=model.event_metadata if model.event_metadata else {},
            created_at=model.created_at,
        )

    # -------------------------------------------------------------------------
    # App settings operations
    # -------------------------------------------------------------------------

    async def get_app_setting(self, key: str) -> Optional[str]:
        """Get a single app setting value by key."""
        from atlas.adapters.repository.encryption import decrypt_value

        statement = select(AppSettingsModel).where(AppSettingsModel.key == key)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        if model.is_secret:
            return decrypt_value(model.value)
        return model.value

    async def set_app_setting(
        self,
        key: str,
        value: str,
        is_secret: bool = False,
        user_id: Optional[UUID] = None,
    ) -> None:
        """Set an app setting value."""
        from atlas.adapters.repository.encryption import encrypt_value

        stored_value = encrypt_value(value) if is_secret else value

        existing = await self._session.get(AppSettingsModel, key)
        if existing:
            existing.value = stored_value
            existing.is_secret = is_secret
            existing.updated_at = datetime.utcnow()
            existing.updated_by = user_id
            self._session.add(existing)
        else:
            model = AppSettingsModel(
                key=key,
                value=stored_value,
                is_secret=is_secret,
                updated_at=datetime.utcnow(),
                updated_by=user_id,
            )
            self._session.add(model)

        await self._session.commit()

    async def get_all_app_settings(self) -> dict[str, str]:
        """Get all app settings as a dictionary."""
        from atlas.adapters.repository.encryption import decrypt_value

        statement = select(AppSettingsModel)
        result = await self._session.execute(statement)
        models = result.scalars().all()

        settings_dict = {}
        for model in models:
            if model.is_secret:
                settings_dict[model.key] = decrypt_value(model.value)
            else:
                settings_dict[model.key] = model.value

        return settings_dict

    async def delete_app_setting(self, key: str) -> bool:
        """Delete an app setting by key."""
        model = await self._session.get(AppSettingsModel, key)
        if not model:
            return False
        await self._session.delete(model)
        await self._session.commit()
        return True

    async def get_app_setting_metadata(self, key: str) -> Optional[dict]:
        """Get app setting metadata without decrypting the value."""
        statement = select(AppSettingsModel).where(AppSettingsModel.key == key)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return {
            "key": model.key,
            "is_secret": model.is_secret,
            "updated_at": model.updated_at,
            "updated_by": model.updated_by,
        }
