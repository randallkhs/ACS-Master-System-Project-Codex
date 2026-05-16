from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.associations import visit_technicians
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.job import Job
    from app.models.review_item import ReviewItem
    from app.models.route_assignment import RouteAssignment
    from app.models.technician import Technician
    from app.models.work_order import WorkOrder


class Visit(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "visits"

    job_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("jobs.id"),
        nullable=False,
    )
    work_order_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("work_orders.id"),
        index=True,
    )
    technician_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("technicians.id"),
    )
    visit_type: Mapped[str | None] = mapped_column(String(100), index=True)
    status: Mapped[str] = mapped_column(String(60), default="SCHEDULED", nullable=False, index=True)
    audit_correlation_id: Mapped[str | None] = mapped_column(String(120), index=True)
    scheduled_start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    scheduled_end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    arrived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)
    generation_snapshot: Mapped[dict | None] = mapped_column(JSON)
    work_order_snapshot: Mapped[dict | None] = mapped_column(JSON)
    review_linkage_snapshot: Mapped[dict | None] = mapped_column(JSON)
    deterministic_evidence_snapshot: Mapped[dict | None] = mapped_column(JSON)
    lifecycle_metadata: Mapped[dict | None] = mapped_column(JSON)
    generated_from_work_order_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    assignment_readiness_snapshot: Mapped[dict | None] = mapped_column(JSON)
    technician_compatibility_snapshot: Mapped[dict | None] = mapped_column(JSON)
    scheduling_readiness_snapshot: Mapped[dict | None] = mapped_column(JSON)
    operational_readiness_snapshot: Mapped[dict | None] = mapped_column(JSON)
    assignment_prepared_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    scheduling_prepared_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    job: Mapped[Job] = relationship(back_populates="visits")
    work_order: Mapped[WorkOrder | None] = relationship(back_populates="visits")
    technician: Mapped[Technician | None] = relationship(back_populates="visits")
    assigned_technicians: Mapped[list[Technician]] = relationship(
        secondary=visit_technicians,
        back_populates="assigned_visits",
    )
    route_assignments: Mapped[list[RouteAssignment]] = relationship(back_populates="visit")
    review_items: Mapped[list[ReviewItem]] = relationship(back_populates="visit")
