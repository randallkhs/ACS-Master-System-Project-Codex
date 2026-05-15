"""Add work order and visit generation traceability.

Revision ID: 20260515_0006
Revises: 20260515_0005
Create Date: 2026-05-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260515_0006"
down_revision: str | None = "20260515_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "work_orders",
        sa.Column("job_creation_record_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "work_orders",
        sa.Column("review_item_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column("work_orders", sa.Column("audit_correlation_id", sa.String(120), nullable=True))
    op.add_column("work_orders", sa.Column("generation_snapshot", sa.JSON(), nullable=True))
    op.add_column("work_orders", sa.Column("intake_snapshot", sa.JSON(), nullable=True))
    op.add_column("work_orders", sa.Column("orchestration_snapshot", sa.JSON(), nullable=True))
    op.add_column(
        "work_orders",
        sa.Column("dispatch_eligibility_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column("work_orders", sa.Column("review_linkage_snapshot", sa.JSON(), nullable=True))
    op.add_column(
        "work_orders",
        sa.Column("deterministic_evidence_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column("work_orders", sa.Column("lifecycle_metadata", sa.JSON(), nullable=True))
    op.add_column(
        "work_orders",
        sa.Column("generated_from_job_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_work_orders_job_creation_record_id_job_creation_records",
        "work_orders",
        "job_creation_records",
        ["job_creation_record_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_work_orders_review_item_id_review_items",
        "work_orders",
        "review_items",
        ["review_item_id"],
        ["id"],
    )
    for column_name in ("job_creation_record_id", "review_item_id", "audit_correlation_id"):
        op.create_index(f"ix_work_orders_{column_name}", "work_orders", [column_name])

    op.add_column(
        "visits",
        sa.Column("work_order_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column("visits", sa.Column("audit_correlation_id", sa.String(120), nullable=True))
    op.add_column("visits", sa.Column("generation_snapshot", sa.JSON(), nullable=True))
    op.add_column("visits", sa.Column("work_order_snapshot", sa.JSON(), nullable=True))
    op.add_column("visits", sa.Column("review_linkage_snapshot", sa.JSON(), nullable=True))
    op.add_column(
        "visits",
        sa.Column("deterministic_evidence_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column("visits", sa.Column("lifecycle_metadata", sa.JSON(), nullable=True))
    op.add_column(
        "visits",
        sa.Column("generated_from_work_order_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_visits_work_order_id_work_orders",
        "visits",
        "work_orders",
        ["work_order_id"],
        ["id"],
    )
    for column_name in ("work_order_id", "audit_correlation_id"):
        op.create_index(f"ix_visits_{column_name}", "visits", [column_name])


def downgrade() -> None:
    for column_name in ("audit_correlation_id", "work_order_id"):
        op.drop_index(f"ix_visits_{column_name}", table_name="visits")
    op.drop_constraint("fk_visits_work_order_id_work_orders", "visits", type_="foreignkey")
    for column_name in (
        "generated_from_work_order_at",
        "lifecycle_metadata",
        "deterministic_evidence_snapshot",
        "review_linkage_snapshot",
        "work_order_snapshot",
        "generation_snapshot",
        "audit_correlation_id",
        "work_order_id",
    ):
        op.drop_column("visits", column_name)

    for column_name in ("audit_correlation_id", "review_item_id", "job_creation_record_id"):
        op.drop_index(f"ix_work_orders_{column_name}", table_name="work_orders")
    op.drop_constraint(
        "fk_work_orders_review_item_id_review_items",
        "work_orders",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_work_orders_job_creation_record_id_job_creation_records",
        "work_orders",
        type_="foreignkey",
    )
    for column_name in (
        "generated_from_job_at",
        "lifecycle_metadata",
        "deterministic_evidence_snapshot",
        "review_linkage_snapshot",
        "dispatch_eligibility_snapshot",
        "orchestration_snapshot",
        "intake_snapshot",
        "generation_snapshot",
        "audit_correlation_id",
        "review_item_id",
        "job_creation_record_id",
    ):
        op.drop_column("work_orders", column_name)
