"""Add external adapter execution snapshots.

Revision ID: 20260515_0014
Revises: 20260515_0013
Create Date: 2026-05-16
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260515_0014"
down_revision: str | None = "20260515_0013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "route_assignments",
        sa.Column("external_execution_state", sa.String(80), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("external_execution_request_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("external_execution_provider_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("external_execution_evidence_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("external_execution_failure_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("external_execution_lifecycle_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("external_execution_audit_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("external_execution_started_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("external_execution_completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("external_execution_failed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        op.f("ix_route_assignments_external_execution_state"),
        "route_assignments",
        ["external_execution_state"],
        unique=False,
    )
    op.create_index(
        op.f("ix_route_assignments_external_execution_completed_at"),
        "route_assignments",
        ["external_execution_completed_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_route_assignments_external_execution_completed_at"),
        table_name="route_assignments",
    )
    op.drop_index(
        op.f("ix_route_assignments_external_execution_state"),
        table_name="route_assignments",
    )
    for column_name in (
        "external_execution_failed_at",
        "external_execution_completed_at",
        "external_execution_started_at",
        "external_execution_audit_snapshot",
        "external_execution_lifecycle_snapshot",
        "external_execution_failure_snapshot",
        "external_execution_evidence_snapshot",
        "external_execution_provider_snapshot",
        "external_execution_request_snapshot",
        "external_execution_state",
    ):
        op.drop_column("route_assignments", column_name)
