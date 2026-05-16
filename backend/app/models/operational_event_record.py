from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class OperationalEventRecord(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "operational_event_records"

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    event_state: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    entity_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    route_assignment_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), index=True)
    visit_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), index=True)
    work_order_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), index=True)
    job_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), index=True)
    technician_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), index=True)
    audit_correlation_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    previous_state: Mapped[str | None] = mapped_column(String(120))
    new_state: Mapped[str | None] = mapped_column(String(120))
    event_fingerprint: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )
    is_immutable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    event_snapshot: Mapped[dict | None] = mapped_column(JSON)
    transition_snapshot: Mapped[dict | None] = mapped_column(JSON)
    immutable_evidence_snapshot: Mapped[dict | None] = mapped_column(JSON)
    retry_recovery_snapshot: Mapped[dict | None] = mapped_column(JSON)
    reconciliation_snapshot: Mapped[dict | None] = mapped_column(JSON)
    audit_snapshot: Mapped[dict | None] = mapped_column(JSON)
