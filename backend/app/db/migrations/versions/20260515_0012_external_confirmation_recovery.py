"""Add external confirmation and recovery snapshots.

Revision ID: 20260515_0012
Revises: 20260515_0011
Create Date: 2026-05-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260515_0012"
down_revision: str | None = "20260515_0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "route_assignments",
        sa.Column("external_confirmation_state", sa.String(80), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("external_confirmation_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("external_confirmation_lifecycle_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("external_confirmation_audit_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("external_failure_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("retry_preparation_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("reconciliation_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("external_confirmed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("external_confirmation_failed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("retry_prepared_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("reconciliation_required_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        op.f("ix_route_assignments_external_confirmation_state"),
        "route_assignments",
        ["external_confirmation_state"],
        unique=False,
    )
    op.create_index(
        op.f("ix_route_assignments_external_confirmed_at"),
        "route_assignments",
        ["external_confirmed_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_route_assignments_external_confirmed_at"),
        table_name="route_assignments",
    )
    op.drop_index(
        op.f("ix_route_assignments_external_confirmation_state"),
        table_name="route_assignments",
    )
    for column_name in (
        "reconciliation_required_at",
        "retry_prepared_at",
        "external_confirmation_failed_at",
        "external_confirmed_at",
        "reconciliation_snapshot",
        "retry_preparation_snapshot",
        "external_failure_snapshot",
        "external_confirmation_audit_snapshot",
        "external_confirmation_lifecycle_snapshot",
        "external_confirmation_snapshot",
        "external_confirmation_state",
    ):
        op.drop_column("route_assignments", column_name)
