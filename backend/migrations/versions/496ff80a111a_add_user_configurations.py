"""add user_configurations table

Revision ID: 496ff80a111a
Revises: 71bef503e77c
Create Date: 2026-01-24 03:56:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "496ff80a111a"
down_revision: Union[str, Sequence[str], None] = "71bef503e77c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create user_configurations table."""
    op.create_table(
        "user_configurations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("git_path", sa.String(), nullable=False),
        sa.Column("current_commit_sha", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_user_configurations_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_configurations")),
    )
    op.create_index(
        op.f("ix_user_configurations_user_id"),
        "user_configurations",
        ["user_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_user_configurations_git_path"),
        "user_configurations",
        ["git_path"],
        unique=True,
    )


def downgrade() -> None:
    """Drop user_configurations table."""
    op.drop_index(
        op.f("ix_user_configurations_git_path"), table_name="user_configurations"
    )
    op.drop_index(
        op.f("ix_user_configurations_user_id"), table_name="user_configurations"
    )
    op.drop_table("user_configurations")
