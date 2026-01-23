"""initial schema

Revision ID: 71bef503e77c
Revises:
Create Date: 2026-01-23 21:31:39.591158

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "71bef503e77c"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial tables: users, teams, user_team_links, catalog_items."""
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(op.f("ix_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_username"), "users", ["username"], unique=True)

    # Create teams table
    op.create_table(
        "teams",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_teams")),
    )
    op.create_index(op.f("ix_name"), "teams", ["name"], unique=True)

    # Create user_team_links table (many-to-many)
    op.create_table(
        "user_team_links",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("team_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("joined_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["team_id"],
            ["teams.id"],
            name=op.f("fk_user_team_links_team_id_teams"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_user_team_links_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("user_id", "team_id", name=op.f("pk_user_team_links")),
    )

    # Create catalog_items table
    op.create_table(
        "catalog_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("git_path", sa.String(), nullable=False),
        sa.Column("author_id", sa.Uuid(), nullable=False),
        sa.Column("team_id", sa.Uuid(), nullable=True),
        sa.Column("tags", sa.String(), nullable=False),
        sa.Column("usage_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["users.id"],
            name=op.f("fk_catalog_items_author_id_users"),
        ),
        sa.ForeignKeyConstraint(
            ["team_id"],
            ["teams.id"],
            name=op.f("fk_catalog_items_team_id_teams"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_catalog_items")),
    )
    op.create_index(op.f("ix_type"), "catalog_items", ["type"], unique=False)
    op.create_index(
        op.f("ix_catalog_items_name"), "catalog_items", ["name"], unique=False
    )
    op.create_index(
        op.f("ix_catalog_items_git_path"), "catalog_items", ["git_path"], unique=True
    )


def downgrade() -> None:
    """Drop all tables."""
    op.drop_index(op.f("ix_catalog_items_git_path"), table_name="catalog_items")
    op.drop_index(op.f("ix_catalog_items_name"), table_name="catalog_items")
    op.drop_index(op.f("ix_type"), table_name="catalog_items")
    op.drop_table("catalog_items")
    op.drop_table("user_team_links")
    op.drop_index(op.f("ix_name"), table_name="teams")
    op.drop_table("teams")
    op.drop_index(op.f("ix_username"), table_name="users")
    op.drop_index(op.f("ix_email"), table_name="users")
    op.drop_table("users")
