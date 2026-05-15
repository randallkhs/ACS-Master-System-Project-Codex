"""Create intake processing records.

Revision ID: 20260515_0004
Revises: 20260515_0003
Create Date: 2026-05-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260515_0004"
down_revision: str | None = "20260515_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "intake_processing_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_system", sa.String(length=80), nullable=False),
        sa.Column("source_id", sa.String(length=255), nullable=True),
        sa.Column("lifecycle_state", sa.String(length=80), nullable=False),
        sa.Column("orchestration_state", sa.String(length=80), nullable=False),
        sa.Column("review_item_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("audit_correlation_id", sa.String(length=120), nullable=False),
        sa.Column("dispatch_eligible", sa.Boolean(), nullable=False),
        sa.Column("requires_review", sa.Boolean(), nullable=False),
        sa.Column("blocked", sa.Boolean(), nullable=False),
        sa.Column("unsafe", sa.Boolean(), nullable=False),
        sa.Column("water_emergency_separated", sa.Boolean(), nullable=False),
        sa.Column("raw_payload_snapshot", sa.JSON(), nullable=True),
        sa.Column("orchestration_result_snapshot", sa.JSON(), nullable=True),
        sa.Column("dispatch_eligibility_snapshot", sa.JSON(), nullable=True),
        sa.Column("normalized_snapshot", sa.JSON(), nullable=True),
        sa.Column("validation_snapshot", sa.JSON(), nullable=True),
        sa.Column("confidence_snapshot", sa.JSON(), nullable=True),
        sa.Column("review_snapshot", sa.JSON(), nullable=True),
        sa.Column("warning_snapshot", sa.JSON(), nullable=True),
        sa.Column("deterministic_evidence_snapshot", sa.JSON(), nullable=True),
        sa.Column("review_linkage_snapshot", sa.JSON(), nullable=True),
        sa.Column("lifecycle_metadata", sa.JSON(), nullable=True),
        sa.Column("approved_for_dispatch_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deferred_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["review_item_id"], ["review_items.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    for column_name in (
        "source_system",
        "source_id",
        "lifecycle_state",
        "orchestration_state",
        "review_item_id",
        "audit_correlation_id",
    ):
        op.create_index(
            f"ix_intake_processing_records_{column_name}",
            "intake_processing_records",
            [column_name],
        )


def downgrade() -> None:
    for column_name in (
        "audit_correlation_id",
        "review_item_id",
        "orchestration_state",
        "lifecycle_state",
        "source_id",
        "source_system",
    ):
        op.drop_index(
            f"ix_intake_processing_records_{column_name}",
            table_name="intake_processing_records",
        )
    op.drop_table("intake_processing_records")
