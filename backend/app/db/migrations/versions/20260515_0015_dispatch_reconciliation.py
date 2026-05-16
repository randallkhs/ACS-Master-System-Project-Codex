"""Add dispatch reconciliation snapshots.

Revision ID: 20260515_0015
Revises: 20260515_0014
Create Date: 2026-05-16
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260515_0015"
down_revision: str | None = "20260515_0014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "route_assignments",
        sa.Column("dispatch_reconciliation_state", sa.String(80), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("dispatch_consistency_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("dispatch_divergence_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("dispatch_mismatch_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("dispatch_reconciliation_blocker_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("dispatch_reconciliation_audit_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("dispatch_reconciliation_prepared_at", sa.DateTime(timezone=True)),
    )
    op.add_column(
        "route_assignments",
        sa.Column("dispatch_consistency_verified_at", sa.DateTime(timezone=True)),
    )
    op.add_column(
        "route_assignments",
        sa.Column("dispatch_reconciliation_blocked_at", sa.DateTime(timezone=True)),
    )
    op.create_index(
        op.f("ix_route_assignments_dispatch_reconciliation_state"),
        "route_assignments",
        ["dispatch_reconciliation_state"],
        unique=False,
    )
    op.create_index(
        op.f("ix_route_assignments_dispatch_reconciliation_prepared_at"),
        "route_assignments",
        ["dispatch_reconciliation_prepared_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_route_assignments_dispatch_consistency_verified_at"),
        "route_assignments",
        ["dispatch_consistency_verified_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_route_assignments_dispatch_consistency_verified_at"),
        table_name="route_assignments",
    )
    op.drop_index(
        op.f("ix_route_assignments_dispatch_reconciliation_prepared_at"),
        table_name="route_assignments",
    )
    op.drop_index(
        op.f("ix_route_assignments_dispatch_reconciliation_state"),
        table_name="route_assignments",
    )
    for column_name in (
        "dispatch_reconciliation_blocked_at",
        "dispatch_consistency_verified_at",
        "dispatch_reconciliation_prepared_at",
        "dispatch_reconciliation_audit_snapshot",
        "dispatch_reconciliation_blocker_snapshot",
        "dispatch_mismatch_snapshot",
        "dispatch_divergence_snapshot",
        "dispatch_consistency_snapshot",
        "dispatch_reconciliation_state",
    ):
        op.drop_column("route_assignments", column_name)
