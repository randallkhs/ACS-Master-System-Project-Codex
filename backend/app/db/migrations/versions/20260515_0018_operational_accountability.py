"""Add operational accountability snapshots.

Revision ID: 20260515_0018
Revises: 20260515_0017
Create Date: 2026-05-16
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260515_0018"
down_revision: str | None = "20260515_0017"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "route_assignments",
        sa.Column("accountability_state", sa.String(80), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("escalation_preparation_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("incident_preparation_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("accountability_evidence_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("escalation_blocker_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("intervention_escalation_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("operational_incident_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("accountability_audit_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "route_assignments",
        sa.Column("escalation_required_at", sa.DateTime(timezone=True)),
    )
    op.add_column(
        "route_assignments",
        sa.Column("incident_prepared_at", sa.DateTime(timezone=True)),
    )
    op.add_column(
        "route_assignments",
        sa.Column("critical_intervention_required_at", sa.DateTime(timezone=True)),
    )
    op.add_column(
        "route_assignments",
        sa.Column("accountability_blocked_at", sa.DateTime(timezone=True)),
    )
    op.create_index(
        op.f("ix_route_assignments_accountability_state"),
        "route_assignments",
        ["accountability_state"],
        unique=False,
    )
    op.create_index(
        op.f("ix_route_assignments_escalation_required_at"),
        "route_assignments",
        ["escalation_required_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_route_assignments_incident_prepared_at"),
        "route_assignments",
        ["incident_prepared_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_route_assignments_critical_intervention_required_at"),
        "route_assignments",
        ["critical_intervention_required_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_route_assignments_critical_intervention_required_at"),
        table_name="route_assignments",
    )
    op.drop_index(
        op.f("ix_route_assignments_incident_prepared_at"),
        table_name="route_assignments",
    )
    op.drop_index(
        op.f("ix_route_assignments_escalation_required_at"),
        table_name="route_assignments",
    )
    op.drop_index(
        op.f("ix_route_assignments_accountability_state"),
        table_name="route_assignments",
    )
    for column_name in (
        "accountability_blocked_at",
        "critical_intervention_required_at",
        "incident_prepared_at",
        "escalation_required_at",
        "accountability_audit_snapshot",
        "operational_incident_snapshot",
        "intervention_escalation_snapshot",
        "escalation_blocker_snapshot",
        "accountability_evidence_snapshot",
        "incident_preparation_snapshot",
        "escalation_preparation_snapshot",
        "accountability_state",
    ):
        op.drop_column("route_assignments", column_name)
