"""Add operational replay and recovery snapshots.

Revision ID: 20260515_0016
Revises: 20260515_0015
Create Date: 2026-05-16
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260515_0016"
down_revision: str | None = "20260515_0015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "route_assignments",
        sa.Column("replay_recovery_state", sa.String(80), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("replay_preparation_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("rollback_preparation_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("replay_eligibility_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("replay_blocker_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("recovery_coordination_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("replay_recovery_audit_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("replay_prepared_at", sa.DateTime(timezone=True)),
    )
    op.add_column(
        "route_assignments",
        sa.Column("rollback_prepared_at", sa.DateTime(timezone=True)),
    )
    op.add_column(
        "route_assignments",
        sa.Column("replay_blocked_at", sa.DateTime(timezone=True)),
    )
    op.create_index(
        op.f("ix_route_assignments_replay_recovery_state"),
        "route_assignments",
        ["replay_recovery_state"],
        unique=False,
    )
    op.create_index(
        op.f("ix_route_assignments_replay_prepared_at"),
        "route_assignments",
        ["replay_prepared_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_route_assignments_rollback_prepared_at"),
        "route_assignments",
        ["rollback_prepared_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_route_assignments_rollback_prepared_at"),
        table_name="route_assignments",
    )
    op.drop_index(
        op.f("ix_route_assignments_replay_prepared_at"),
        table_name="route_assignments",
    )
    op.drop_index(
        op.f("ix_route_assignments_replay_recovery_state"),
        table_name="route_assignments",
    )
    for column_name in (
        "replay_blocked_at",
        "rollback_prepared_at",
        "replay_prepared_at",
        "replay_recovery_audit_snapshot",
        "recovery_coordination_snapshot",
        "replay_blocker_snapshot",
        "replay_eligibility_snapshot",
        "rollback_preparation_snapshot",
        "replay_preparation_snapshot",
        "replay_recovery_state",
    ):
        op.drop_column("route_assignments", column_name)
