"""Entity-model conversion utilities for PostgreSQL adapter."""

import json

from atlas.adapters.postgresql.models import (
    CatalogItemModel,
    TeamModel,
    UserModel,
)
from atlas.domain.entities import CatalogItem, Team, User


def user_model_to_entity(model: UserModel) -> User:
    """Convert UserModel to User domain entity."""
    return User(
        id=model.id,
        email=model.email,
        username=model.username,
        team_ids=[team.id for team in model.teams] if model.teams else [],
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def user_entity_to_model(entity: User) -> UserModel:
    """Convert User domain entity to UserModel."""
    return UserModel(
        id=entity.id,
        email=entity.email,
        username=entity.username,
        password_hash="",  # Set separately during auth
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def team_model_to_entity(model: TeamModel) -> Team:
    """Convert TeamModel to Team domain entity."""
    return Team(
        id=model.id,
        name=model.name,
        member_ids=[member.id for member in model.members] if model.members else [],
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def team_entity_to_model(entity: Team) -> TeamModel:
    """Convert Team domain entity to TeamModel."""
    return TeamModel(
        id=entity.id,
        name=entity.name,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def catalog_item_model_to_entity(model: CatalogItemModel) -> CatalogItem:
    """Convert CatalogItemModel to CatalogItem domain entity."""
    tags = json.loads(model.tags) if model.tags else []
    return CatalogItem(
        id=model.id,
        type=model.type,
        name=model.name,
        description=model.description,
        git_path=model.git_path,
        author_id=model.author_id,
        team_id=model.team_id,
        tags=tags,
        usage_count=model.usage_count,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def catalog_item_entity_to_model(entity: CatalogItem) -> CatalogItemModel:
    """Convert CatalogItem domain entity to CatalogItemModel."""
    return CatalogItemModel(
        id=entity.id,
        type=entity.type,
        name=entity.name,
        description=entity.description,
        git_path=entity.git_path,
        author_id=entity.author_id,
        team_id=entity.team_id,
        tags=json.dumps(entity.tags),
        usage_count=entity.usage_count,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )
