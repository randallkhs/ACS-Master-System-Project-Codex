"""Create operational event history table.

Revision ID: 20260515_0013
Revises: 20260515_0012
Create Date: 2026-05-16
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260515_0013"
down_revision: str | None = "20260515_0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "operational_event_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(120), nullable=False),
        sa.Column("event_state", sa.String(80), nullable=False),
        sa.Column("entity_type", sa.String(120), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("route_assignment_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("visit_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("work_order_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("technician_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("audit_correlation_id", sa.String(120), nullable=False),
        sa.Column("previous_state", sa.String(120), nullable=True),
        sa.Column("new_state", sa.String(120), nullable=True),
        sa.Column("event_fingerprint", sa.String(255), nullable=False),
        sa.Column("is_immutable", sa.Boolean(), nullable=False),
        sa.Column("event_snapshot", sa.JSON(), nullable=True),
        sa.Column("transition_snapshot", sa.JSON(), nullable=True),
        sa.Column("immutable_evidence_snapshot", sa.JSON(), nullable=True),
        sa.Column("retry_recovery_snapshot", sa.JSON(), nullable=True),
        sa.Column("reconciliation_snapshot", sa.JSON(), nullable=True),
        sa.Column("audit_snapshot", sa.JSON(), nullable=True),
        sa.UniqueConstraint("event_fingerprint"),
    )
    for column_name in (
        "occurred_at",
        "recorded_at",
        "event_type",
        "event_state",
        "entity_type",
        "entity_id",
        "route_assignment_id",
        "visit_id",
        "work_order_id",
        "job_id",
        "technician_id",
        "audit_correlation_id",
        "event_fingerprint",
    ):
        op.create_index(
            f"ix_operational_event_records_{column_name}",
            "operational_event_records",
            [column_name],
        )


def downgrade() -> None:
    for column_name in (
        "event_fingerprint",
        "audit_correlation_id",
        "technician_id",
        "job_id",
        "work_order_id",
        "visit_id",
        "route_assignment_id",
        "entity_id",
        "entity_type",
        "event_state",
        "event_type",
        "recorded_at",
        "occurred_at",
    ):
        op.drop_index(
            f"ix_operational_event_records_{column_name}",
            table_name="operational_event_records",
        )
    op.drop_table("operational_event_records")
