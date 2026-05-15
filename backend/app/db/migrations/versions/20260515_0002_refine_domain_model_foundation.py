"""Refine domain model foundation.

Revision ID: 20260515_0002
Revises: 20260515_0001
Create Date: 2026-05-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260515_0002"
down_revision: str | None = "20260515_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("customers", sa.Column("billing_contact", sa.Text(), nullable=True))
    op.add_column("customers", sa.Column("property_manager_contact", sa.Text(), nullable=True))
    op.add_column("customers", sa.Column("tags", sa.JSON(), nullable=True))

    op.add_column("technicians", sa.Column("vehicle_label", sa.String(length=120), nullable=True))
    op.add_column(
        "technicians",
        sa.Column("availability_status", sa.String(length=60), nullable=True),
    )
    op.create_index(
        "ix_technicians_availability_status",
        "technicians",
        ["availability_status"],
    )

    op.create_table(
        "work_order_technicians",
        sa.Column("work_order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("technician_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["technician_id"], ["technicians.id"]),
        sa.ForeignKeyConstraint(["work_order_id"], ["work_orders.id"]),
        sa.PrimaryKeyConstraint("work_order_id", "technician_id"),
    )
    op.create_table(
        "visit_technicians",
        sa.Column("visit_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("technician_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["technician_id"], ["technicians.id"]),
        sa.ForeignKeyConstraint(["visit_id"], ["visits.id"]),
        sa.PrimaryKeyConstraint("visit_id", "technician_id"),
    )

    op.add_column(
        "route_assignments",
        sa.Column("estimated_drive_time_minutes", sa.Integer(), nullable=True),
    )

    op.add_column("review_items", sa.Column("entity_type", sa.String(length=120), nullable=True))
    op.add_column(
        "review_items",
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_review_items_entity_type", "review_items", ["entity_type"])
    op.create_index("ix_review_items_entity_id", "review_items", ["entity_id"])

    op.alter_column(
        "audit_logs",
        "occurred_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "audit_logs",
        "occurred_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=None,
        existing_nullable=False,
    )

    op.drop_index("ix_review_items_entity_id", table_name="review_items")
    op.drop_index("ix_review_items_entity_type", table_name="review_items")
    op.drop_column("review_items", "entity_id")
    op.drop_column("review_items", "entity_type")

    op.drop_column("route_assignments", "estimated_drive_time_minutes")

    op.drop_table("visit_technicians")
    op.drop_table("work_order_technicians")

    op.drop_index("ix_technicians_availability_status", table_name="technicians")
    op.drop_column("technicians", "availability_status")
    op.drop_column("technicians", "vehicle_label")

    op.drop_column("customers", "tags")
    op.drop_column("customers", "property_manager_contact")
    op.drop_column("customers", "billing_contact")
