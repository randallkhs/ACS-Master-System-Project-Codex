"""Add external dispatch adapter snapshots.

Revision ID: 20260515_0011
Revises: 20260515_0010
Create Date: 2026-05-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260515_0011"
down_revision: str | None = "20260515_0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "route_assignments",
        sa.Column("external_adapter_state", sa.String(80), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("external_adapter_request_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("external_adapter_payload_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("external_adapter_lifecycle_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("external_adapter_evidence_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("external_adapter_audit_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("external_adapter_prepared_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("external_adapter_failed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        op.f("ix_route_assignments_external_adapter_state"),
        "route_assignments",
        ["external_adapter_state"],
        unique=False,
    )
    op.create_index(
        op.f("ix_route_assignments_external_adapter_prepared_at"),
        "route_assignments",
        ["external_adapter_prepared_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_route_assignments_external_adapter_prepared_at"),
        table_name="route_assignments",
    )
    op.drop_index(
        op.f("ix_route_assignments_external_adapter_state"),
        table_name="route_assignments",
    )
    for column_name in (
        "external_adapter_failed_at",
        "external_adapter_prepared_at",
        "external_adapter_audit_snapshot",
        "external_adapter_evidence_snapshot",
        "external_adapter_lifecycle_snapshot",
        "external_adapter_payload_snapshot",
        "external_adapter_request_snapshot",
        "external_adapter_state",
    ):
        op.drop_column("route_assignments", column_name)
