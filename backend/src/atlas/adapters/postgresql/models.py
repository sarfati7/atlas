"""SQLModel table definitions for PostgreSQL storage."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from atlas.domain.entities.catalog_item import CatalogItemType

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


class CatalogItemModel(SQLModel, table=True):
    """SQLModel table for CatalogItem entity (single-table with type discriminator)."""

    __tablename__ = "catalog_items"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    type: CatalogItemType = Field(index=True)
    name: str = Field(index=True)
    description: str = Field(default="")
    git_path: str = Field(unique=True)
    author_id: UUID = Field(foreign_key="users.id")
    team_id: Optional[UUID] = Field(default=None, foreign_key="teams.id")
    tags: str = Field(default="")  # JSON string for array
    usage_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserConfigurationModel(SQLModel, table=True):
    """SQLModel table for user configuration metadata."""

    __tablename__ = "user_configurations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", unique=True, index=True)
    git_path: str = Field(unique=True)  # e.g., "configs/users/{uuid}/claude.md"
    current_commit_sha: str = Field(default="")  # Empty until first save
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
