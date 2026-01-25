"""SQLModel table definitions for database storage."""

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import JSON
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    pass


class UserTeamLink(SQLModel, table=True):
    """Link table for User-Team many-to-many relationship."""

    __tablename__ = "user_team_links"

    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    team_id: UUID = Field(foreign_key="teams.id", primary_key=True)
    role: str = Field(default="member")
    joined_at: datetime = Field(default_factory=datetime.utcnow)


class UserModel(SQLModel, table=True):
    """SQLModel table for User entity."""

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    password_hash: str = Field(default="")
    role: str = Field(default="user")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    teams: list["TeamModel"] = Relationship(
        back_populates="members",
        link_model=UserTeamLink,
    )


class TeamModel(SQLModel, table=True):
    """SQLModel table for Team entity."""

    __tablename__ = "teams"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    members: list[UserModel] = Relationship(
        back_populates="teams",
        link_model=UserTeamLink,
    )


class UserConfigurationModel(SQLModel, table=True):
    """SQLModel table for user configuration metadata."""

    __tablename__ = "user_configurations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", unique=True, index=True)
    git_path: str = Field(unique=True)
    current_commit_sha: str = Field(default="")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AuditLogModel(SQLModel, table=True):
    """SQLModel table for audit log entries."""

    __tablename__ = "audit_logs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    action: str
    resource_type: str
    resource_id: UUID
    details: dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
    created_at: datetime = Field(default_factory=datetime.utcnow)
