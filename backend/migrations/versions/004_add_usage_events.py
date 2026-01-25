"""add usage_events table

Revision ID: 004_add_usage_events
Revises: 003_add_role_and_audit_log
Create Date: 2026-01-25 15:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004_add_usage_events"
down_revision: Union[str, Sequence[str], None] = "003_add_role_and_audit_log"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create usage_events table with indexes."""
    op.create_table(
        "usage_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("item_id", sa.Uuid(), nullable=False),
        sa.Column("item_type", sa.String(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("event_metadata", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_usage_events_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_usage_events")),
    )

    # Create indexes for common query patterns
    op.create_index(
        op.f("ix_usage_events_user_id"),
        "usage_events",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_usage_events_item_id"),
        "usage_events",
        ["item_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_usage_events_created_at"),
        "usage_events",
        [sa.text("created_at DESC")],
        unique=False,
    )
    # Composite index for item analytics
    op.create_index(
        op.f("ix_usage_events_item_type_created_at"),
        "usage_events",
        ["item_type", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    """Drop usage_events table and indexes."""
    op.drop_index(op.f("ix_usage_events_item_type_created_at"), table_name="usage_events")
    op.drop_index(op.f("ix_usage_events_created_at"), table_name="usage_events")
    op.drop_index(op.f("ix_usage_events_item_id"), table_name="usage_events")
    op.drop_index(op.f("ix_usage_events_user_id"), table_name="usage_events")
    op.drop_table("usage_events")
