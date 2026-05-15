"""Add manual review queue foundation fields.

Revision ID: 20260515_0003
Revises: 20260515_0002
Create Date: 2026-05-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260515_0003"
down_revision: str | None = "20260515_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("review_items", sa.Column("source_system", sa.String(length=80), nullable=True))
    op.add_column("review_items", sa.Column("source_id", sa.String(length=255), nullable=True))
    op.add_column("review_items", sa.Column("severity", sa.String(length=30), nullable=True))
    op.add_column(
        "review_items",
        sa.Column("intake_processing_state", sa.String(length=60), nullable=True),
    )
    op.add_column("review_items", sa.Column("review_reasons", sa.JSON(), nullable=True))
    op.add_column("review_items", sa.Column("confidence_snapshot", sa.JSON(), nullable=True))
    op.add_column("review_items", sa.Column("warning_snapshot", sa.JSON(), nullable=True))
    op.add_column("review_items", sa.Column("normalization_snapshot", sa.JSON(), nullable=True))
    op.add_column("review_items", sa.Column("validation_snapshot", sa.JSON(), nullable=True))
    op.add_column("review_items", sa.Column("review_metadata", sa.JSON(), nullable=True))
    op.add_column(
        "review_items",
        sa.Column("audit_correlation_id", sa.String(length=120), nullable=True),
    )
    op.add_column("review_items", sa.Column("operator_notes", sa.Text(), nullable=True))
    op.add_column(
        "review_items",
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "review_items",
        sa.Column("deferred_until", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "audit_logs",
        sa.Column("audit_correlation_id", sa.String(length=120), nullable=True),
    )

    for column_name in (
        "source_system",
        "source_id",
        "severity",
        "intake_processing_state",
        "audit_correlation_id",
    ):
        op.create_index(f"ix_review_items_{column_name}", "review_items", [column_name])
    op.create_index(
        "ix_audit_logs_audit_correlation_id",
        "audit_logs",
        ["audit_correlation_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_audit_logs_audit_correlation_id", table_name="audit_logs")
    op.drop_column("audit_logs", "audit_correlation_id")

    for column_name in (
        "audit_correlation_id",
        "intake_processing_state",
        "severity",
        "source_id",
        "source_system",
    ):
        op.drop_index(f"ix_review_items_{column_name}", table_name="review_items")

    op.drop_column("review_items", "deferred_until")
    op.drop_column("review_items", "reviewed_at")
    op.drop_column("review_items", "operator_notes")
    op.drop_column("review_items", "audit_correlation_id")
    op.drop_column("review_items", "review_metadata")
    op.drop_column("review_items", "validation_snapshot")
    op.drop_column("review_items", "normalization_snapshot")
    op.drop_column("review_items", "warning_snapshot")
    op.drop_column("review_items", "confidence_snapshot")
    op.drop_column("review_items", "review_reasons")
    op.drop_column("review_items", "intake_processing_state")
    op.drop_column("review_items", "severity")
    op.drop_column("review_items", "source_id")
    op.drop_column("review_items", "source_system")
