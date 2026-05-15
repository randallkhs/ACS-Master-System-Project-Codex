"""Create job creation records.

Revision ID: 20260515_0005
Revises: 20260515_0004
Create Date: 2026-05-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260515_0005"
down_revision: str | None = "20260515_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "job_creation_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("intake_processing_record_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("review_item_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("lifecycle_state", sa.String(length=80), nullable=False),
        sa.Column("audit_correlation_id", sa.String(length=120), nullable=False),
        sa.Column("creation_snapshot", sa.JSON(), nullable=True),
        sa.Column("intake_snapshot", sa.JSON(), nullable=True),
        sa.Column("orchestration_snapshot", sa.JSON(), nullable=True),
        sa.Column("dispatch_eligibility_snapshot", sa.JSON(), nullable=True),
        sa.Column("review_linkage_snapshot", sa.JSON(), nullable=True),
        sa.Column("deterministic_evidence_snapshot", sa.JSON(), nullable=True),
        sa.Column("lifecycle_metadata", sa.JSON(), nullable=True),
        sa.Column("created_from_intake_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["intake_processing_record_id"], ["intake_processing_records.id"]),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"]),
        sa.ForeignKeyConstraint(["review_item_id"], ["review_items.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "intake_processing_record_id",
            name="uq_job_creation_records_intake_processing_record_id",
        ),
    )
    for column_name in (
        "intake_processing_record_id",
        "job_id",
        "review_item_id",
        "lifecycle_state",
        "audit_correlation_id",
    ):
        op.create_index(
            f"ix_job_creation_records_{column_name}",
            "job_creation_records",
            [column_name],
        )


def downgrade() -> None:
    for column_name in (
        "audit_correlation_id",
        "lifecycle_state",
        "review_item_id",
        "job_id",
        "intake_processing_record_id",
    ):
        op.drop_index(f"ix_job_creation_records_{column_name}", table_name="job_creation_records")
    op.drop_table("job_creation_records")
