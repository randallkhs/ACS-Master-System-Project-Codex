"""Add dispatch execution snapshots.

Revision ID: 20260515_0010
Revises: 20260515_0009
Create Date: 2026-05-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260515_0010"
down_revision: str | None = "20260515_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "route_assignments",
        sa.Column("dispatch_execution_state", sa.String(60), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("dispatch_execution_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("dispatch_lifecycle_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("dispatch_audit_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("dispatched_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("dispatch_failed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        op.f("ix_route_assignments_dispatch_execution_state"),
        "route_assignments",
        ["dispatch_execution_state"],
        unique=False,
    )
    op.create_index(
        op.f("ix_route_assignments_dispatched_at"),
        "route_assignments",
        ["dispatched_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_route_assignments_dispatched_at"), table_name="route_assignments")
    op.drop_index(
        op.f("ix_route_assignments_dispatch_execution_state"),
        table_name="route_assignments",
    )
    for column_name in (
        "dispatch_failed_at",
        "dispatched_at",
        "dispatch_audit_snapshot",
        "dispatch_lifecycle_snapshot",
        "dispatch_execution_snapshot",
        "dispatch_execution_state",
    ):
        op.drop_column("route_assignments", column_name)
