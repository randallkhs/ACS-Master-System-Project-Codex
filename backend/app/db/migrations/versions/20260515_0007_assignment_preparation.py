"""Add assignment and scheduling preparation snapshots.

Revision ID: 20260515_0007
Revises: 20260515_0006
Create Date: 2026-05-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260515_0007"
down_revision: str | None = "20260515_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("visits", sa.Column("assignment_readiness_snapshot", sa.JSON(), nullable=True))
    op.add_column(
        "visits",
        sa.Column("technician_compatibility_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column("visits", sa.Column("scheduling_readiness_snapshot", sa.JSON(), nullable=True))
    op.add_column("visits", sa.Column("operational_readiness_snapshot", sa.JSON(), nullable=True))
    op.add_column(
        "visits",
        sa.Column("assignment_prepared_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "visits",
        sa.Column("scheduling_prepared_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    for column_name in (
        "scheduling_prepared_at",
        "assignment_prepared_at",
        "operational_readiness_snapshot",
        "scheduling_readiness_snapshot",
        "technician_compatibility_snapshot",
        "assignment_readiness_snapshot",
    ):
        op.drop_column("visits", column_name)
