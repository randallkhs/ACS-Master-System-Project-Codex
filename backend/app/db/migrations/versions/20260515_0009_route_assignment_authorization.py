"""Add route assignment authorization snapshots.

Revision ID: 20260515_0009
Revises: 20260515_0008
Create Date: 2026-05-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260515_0009"
down_revision: str | None = "20260515_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("route_assignments", sa.Column("route_group_key", sa.String(160), nullable=True))
    op.add_column(
        "route_assignments",
        sa.Column("audit_correlation_id", sa.String(120), nullable=True),
    )
    op.add_column(
        "route_assignments", sa.Column("route_grouping_snapshot", sa.JSON(), nullable=True)
    )
    op.add_column(
        "route_assignments",
        sa.Column("route_assignment_readiness_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("technician_route_compatibility_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("dispatch_authorization_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("dispatch_execution_boundary_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("deterministic_evidence_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("authorization_prepared_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("authorized_for_dispatch_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        op.f("ix_route_assignments_route_group_key"),
        "route_assignments",
        ["route_group_key"],
        unique=False,
    )
    op.create_index(
        op.f("ix_route_assignments_audit_correlation_id"),
        "route_assignments",
        ["audit_correlation_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_route_assignments_audit_correlation_id"), table_name="route_assignments")
    op.drop_index(op.f("ix_route_assignments_route_group_key"), table_name="route_assignments")
    for column_name in (
        "authorized_for_dispatch_at",
        "authorization_prepared_at",
        "deterministic_evidence_snapshot",
        "dispatch_execution_boundary_snapshot",
        "dispatch_authorization_snapshot",
        "technician_route_compatibility_snapshot",
        "route_assignment_readiness_snapshot",
        "route_grouping_snapshot",
        "audit_correlation_id",
        "route_group_key",
    ):
        op.drop_column("route_assignments", column_name)
