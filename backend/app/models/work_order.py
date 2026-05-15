from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.associations import work_order_technicians
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.job import Job
    from app.models.job_creation_record import JobCreationRecord
    from app.models.technician import Technician
    from app.models.visit import Visit


class WorkOrder(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "work_orders"

    job_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("jobs.id"),
        nullable=False,
    )
    job_creation_record_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("job_creation_records.id"),
        index=True,
    )
    review_item_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("review_items.id"),
        index=True,
    )
    assigned_technician_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("technicians.id"),
    )
    work_order_number: Mapped[str | None] = mapped_column(String(80), unique=True)
    status: Mapped[str] = mapped_column(String(60), default="NEW", nullable=False, index=True)
    dispatch_status: Mapped[str | None] = mapped_column(String(60), index=True)
    audit_correlation_id: Mapped[str | None] = mapped_column(String(120), index=True)
    service_instructions: Mapped[str | None] = mapped_column(Text)
    required_forms: Mapped[str | None] = mapped_column(Text)
    required_equipment_notes: Mapped[str | None] = mapped_column(Text)
    technician_notes: Mapped[str | None] = mapped_column(Text)
    generation_snapshot: Mapped[dict | None] = mapped_column(JSON)
    intake_snapshot: Mapped[dict | None] = mapped_column(JSON)
    orchestration_snapshot: Mapped[dict | None] = mapped_column(JSON)
    dispatch_eligibility_snapshot: Mapped[dict | None] = mapped_column(JSON)
    review_linkage_snapshot: Mapped[dict | None] = mapped_column(JSON)
    deterministic_evidence_snapshot: Mapped[dict | None] = mapped_column(JSON)
    lifecycle_metadata: Mapped[dict | None] = mapped_column(JSON)
    generated_from_job_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    job: Mapped[Job] = relationship(back_populates="work_orders")
    job_creation_record: Mapped[JobCreationRecord | None] = relationship(
        back_populates="work_orders",
    )
    assigned_technician: Mapped[Technician | None] = relationship(back_populates="work_orders")
    assigned_technicians: Mapped[list[Technician]] = relationship(
        secondary=work_order_technicians,
        back_populates="assigned_work_orders",
    )
    visits: Mapped[list[Visit]] = relationship(back_populates="work_order")
