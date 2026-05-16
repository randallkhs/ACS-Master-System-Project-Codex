"""Add operational governance snapshots.

Revision ID: 20260515_0017
Revises: 20260515_0016
Create Date: 2026-05-16
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260515_0017"
down_revision: str | None = "20260515_0016"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "route_assignments",
        sa.Column("governance_state", sa.String(80), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("governance_approval_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("intervention_authorization_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("replay_authorization_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("rollback_authorization_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("reconciliation_approval_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("governance_blocker_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("governance_audit_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("governance_approved_at", sa.DateTime(timezone=True)),
    )
    op.add_column(
        "route_assignments",
        sa.Column("governance_rejected_at", sa.DateTime(timezone=True)),
    )
    op.add_column(
        "route_assignments",
        sa.Column("intervention_required_at", sa.DateTime(timezone=True)),
    )
    op.add_column(
        "route_assignments",
        sa.Column("governance_blocked_at", sa.DateTime(timezone=True)),
    )
    op.create_index(
        op.f("ix_route_assignments_governance_state"),
        "route_assignments",
        ["governance_state"],
        unique=False,
    )
    op.create_index(
        op.f("ix_route_assignments_governance_approved_at"),
        "route_assignments",
        ["governance_approved_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_route_assignments_intervention_required_at"),
        "route_assignments",
        ["intervention_required_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_route_assignments_intervention_required_at"),
        table_name="route_assignments",
    )
    op.drop_index(
        op.f("ix_route_assignments_governance_approved_at"),
        table_name="route_assignments",
    )
    op.drop_index(
        op.f("ix_route_assignments_governance_state"),
        table_name="route_assignments",
    )
    for column_name in (
        "governance_blocked_at",
        "intervention_required_at",
        "governance_rejected_at",
        "governance_approved_at",
        "governance_audit_snapshot",
        "governance_blocker_snapshot",
        "reconciliation_approval_snapshot",
        "rollback_authorization_snapshot",
        "replay_authorization_snapshot",
        "intervention_authorization_snapshot",
        "governance_approval_snapshot",
        "governance_state",
    ):
        op.drop_column("route_assignments", column_name)
