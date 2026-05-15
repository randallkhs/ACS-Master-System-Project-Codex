"""Create foundational ACS FSM tables.

Revision ID: 20260515_0001
Revises:
Create Date: 2026-05-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260515_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def uuid_pk() -> sa.Column:
    return sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False)


def timestamp_columns() -> tuple[sa.Column, sa.Column]:
    return (
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def upgrade() -> None:
    op.create_table(
        "customers",
        uuid_pk(),
        sa.Column("display_name", sa.String(length=200), nullable=False),
        sa.Column("company_name", sa.String(length=200), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=254), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        *timestamp_columns(),
    )
    op.create_index("ix_customers_display_name", "customers", ["display_name"])

    op.create_table(
        "technicians",
        uuid_pk(),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=254), nullable=True),
        sa.Column("role", sa.String(length=80), nullable=True),
        sa.Column("fastfield_user_id", sa.String(length=120), nullable=True),
        sa.Column("verizon_connect_ref", sa.String(length=120), nullable=True),
        sa.Column("skills", sa.JSON(), nullable=True),
        sa.Column("service_areas", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        *timestamp_columns(),
    )
    op.create_index("ix_technicians_full_name", "technicians", ["full_name"])
    op.create_index("ix_technicians_is_active", "technicians", ["is_active"])
    op.create_unique_constraint(
        "uq_technicians_fastfield_user_id",
        "technicians",
        ["fastfield_user_id"],
    )
    op.create_unique_constraint(
        "uq_technicians_verizon_connect_ref",
        "technicians",
        ["verizon_connect_ref"],
    )

    op.create_table(
        "properties",
        uuid_pk(),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("property_name", sa.String(length=200), nullable=True),
        sa.Column("street_address", sa.String(length=255), nullable=True),
        sa.Column("unit_number", sa.String(length=50), nullable=True),
        sa.Column("building_number", sa.String(length=50), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("state", sa.String(length=2), nullable=True),
        sa.Column("postal_code", sa.String(length=20), nullable=True),
        sa.Column("access_notes", sa.Text(), nullable=True),
        sa.Column("parking_notes", sa.Text(), nullable=True),
        sa.Column("gate_code", sa.String(length=100), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
    )
    op.create_index("ix_properties_street_address", "properties", ["street_address"])
    op.create_index("ix_properties_state", "properties", ["state"])

    op.create_table(
        "jobs",
        uuid_pk(),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("job_type", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("review_status", sa.String(length=60), nullable=True),
        sa.Column("priority", sa.String(length=60), nullable=True),
        sa.Column("requested_date", sa.Date(), nullable=True),
        sa.Column("scheduled_date", sa.Date(), nullable=True),
        sa.Column("source_system", sa.String(length=80), nullable=True),
        sa.Column("source_event_id", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["property_id"], ["properties.id"]),
    )
    for column_name in (
        "job_type",
        "status",
        "review_status",
        "priority",
        "scheduled_date",
        "source_system",
        "source_event_id",
    ):
        op.create_index(f"ix_jobs_{column_name}", "jobs", [column_name])

    op.create_table(
        "work_orders",
        uuid_pk(),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assigned_technician_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("work_order_number", sa.String(length=80), nullable=True),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("dispatch_status", sa.String(length=60), nullable=True),
        sa.Column("service_instructions", sa.Text(), nullable=True),
        sa.Column("required_forms", sa.Text(), nullable=True),
        sa.Column("required_equipment_notes", sa.Text(), nullable=True),
        sa.Column("technician_notes", sa.Text(), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["assigned_technician_id"], ["technicians.id"]),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"]),
        sa.UniqueConstraint("work_order_number"),
    )
    op.create_index("ix_work_orders_status", "work_orders", ["status"])
    op.create_index("ix_work_orders_dispatch_status", "work_orders", ["dispatch_status"])

    op.create_table(
        "visits",
        uuid_pk(),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("technician_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("visit_type", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("scheduled_start_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scheduled_end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("arrived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"]),
        sa.ForeignKeyConstraint(["technician_id"], ["technicians.id"]),
    )
    op.create_index("ix_visits_visit_type", "visits", ["visit_type"])
    op.create_index("ix_visits_status", "visits", ["status"])
    op.create_index("ix_visits_scheduled_start_at", "visits", ["scheduled_start_at"])

    op.create_table(
        "route_assignments",
        uuid_pk(),
        sa.Column("route_date", sa.Date(), nullable=False),
        sa.Column("technician_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("visit_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("route_order", sa.Integer(), nullable=True),
        sa.Column("region", sa.String(length=80), nullable=True),
        sa.Column("time_window", sa.String(length=20), nullable=True),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("estimated_arrival_at", sa.DateTime(timezone=True), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"]),
        sa.ForeignKeyConstraint(["technician_id"], ["technicians.id"]),
        sa.ForeignKeyConstraint(["visit_id"], ["visits.id"]),
    )
    for column_name in ("route_date", "region", "time_window", "status"):
        op.create_index(f"ix_route_assignments_{column_name}", "route_assignments", [column_name])

    op.create_table(
        "water_emergencies",
        uuid_pk(),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.Column("drying_stage", sa.String(length=120), nullable=True),
        sa.Column("next_required_action", sa.String(length=200), nullable=True),
        sa.Column("equipment_onsite", sa.Boolean(), nullable=False),
        sa.Column("moisture_tracking_required", sa.Boolean(), nullable=False),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"]),
        sa.UniqueConstraint("job_id"),
    )
    op.create_index("ix_water_emergencies_status", "water_emergencies", ["status"])
    op.create_index("ix_water_emergencies_drying_stage", "water_emergencies", ["drying_stage"])

    op.create_table(
        "review_items",
        uuid_pk(),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("visit_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("route_assignment_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reason_code", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("source_snapshot", sa.JSON(), nullable=True),
        sa.Column("recommended_action", sa.Text(), nullable=True),
        sa.Column("operator_decision", sa.Text(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"]),
        sa.ForeignKeyConstraint(["route_assignment_id"], ["route_assignments.id"]),
        sa.ForeignKeyConstraint(["visit_id"], ["visits.id"]),
    )
    op.create_index("ix_review_items_reason_code", "review_items", ["reason_code"])
    op.create_index("ix_review_items_status", "review_items", ["status"])

    op.create_table(
        "audit_logs",
        uuid_pk(),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actor_type", sa.String(length=80), nullable=True),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("entity_type", sa.String(length=120), nullable=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
    )
    for column_name in (
        "occurred_at",
        "actor_type",
        "actor_id",
        "action",
        "entity_type",
        "entity_id",
    ):
        op.create_index(f"ix_audit_logs_{column_name}", "audit_logs", [column_name])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("review_items")
    op.drop_table("water_emergencies")
    op.drop_table("route_assignments")
    op.drop_table("visits")
    op.drop_table("work_orders")
    op.drop_table("jobs")
    op.drop_table("properties")
    op.drop_table("technicians")
    op.drop_table("customers")
