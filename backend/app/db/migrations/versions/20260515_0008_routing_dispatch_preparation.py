"""Add routing and dispatch preparation snapshots.

Revision ID: 20260515_0008
Revises: 20260515_0007
Create Date: 2026-05-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260515_0008"
down_revision: str | None = "20260515_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("visits", sa.Column("routing_readiness_snapshot", sa.JSON(), nullable=True))
    op.add_column("visits", sa.Column("dispatch_readiness_snapshot", sa.JSON(), nullable=True))
    op.add_column("visits", sa.Column("technician_readiness_snapshot", sa.JSON(), nullable=True))
    op.add_column(
        "visits",
        sa.Column("visit_dispatch_readiness_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "visits",
        sa.Column("routing_prepared_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "visits",
        sa.Column("dispatch_prepared_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    for column_name in (
        "dispatch_prepared_at",
        "routing_prepared_at",
        "visit_dispatch_readiness_snapshot",
        "technician_readiness_snapshot",
        "dispatch_readiness_snapshot",
        "routing_readiness_snapshot",
    ):
        op.drop_column("visits", column_name)
