from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.job import Job
    from app.models.review_item import ReviewItem
    from app.models.technician import Technician
    from app.models.visit import Visit


class RouteAssignment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "route_assignments"

    route_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    technician_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("technicians.id"),
    )
    job_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("jobs.id"))
    visit_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("visits.id"))
    route_order: Mapped[int | None] = mapped_column(Integer)
    region: Mapped[str | None] = mapped_column(String(80), index=True)
    time_window: Mapped[str | None] = mapped_column(String(20), index=True)
    status: Mapped[str] = mapped_column(String(60), default="PLANNED", nullable=False, index=True)
    route_group_key: Mapped[str | None] = mapped_column(String(160), index=True)
    audit_correlation_id: Mapped[str | None] = mapped_column(String(120), index=True)
    estimated_arrival_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    estimated_drive_time_minutes: Mapped[int | None] = mapped_column(Integer)
    route_grouping_snapshot: Mapped[dict | None] = mapped_column(JSON)
    route_assignment_readiness_snapshot: Mapped[dict | None] = mapped_column(JSON)
    technician_route_compatibility_snapshot: Mapped[dict | None] = mapped_column(JSON)
    dispatch_authorization_snapshot: Mapped[dict | None] = mapped_column(JSON)
    dispatch_execution_boundary_snapshot: Mapped[dict | None] = mapped_column(JSON)
    deterministic_evidence_snapshot: Mapped[dict | None] = mapped_column(JSON)
    authorization_prepared_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    authorized_for_dispatch_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    dispatch_execution_state: Mapped[str | None] = mapped_column(String(60), index=True)
    dispatch_execution_snapshot: Mapped[dict | None] = mapped_column(JSON)
    dispatch_lifecycle_snapshot: Mapped[dict | None] = mapped_column(JSON)
    dispatch_audit_snapshot: Mapped[dict | None] = mapped_column(JSON)
    dispatched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    dispatch_failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    external_adapter_state: Mapped[str | None] = mapped_column(String(80), index=True)
    external_adapter_request_snapshot: Mapped[dict | None] = mapped_column(JSON)
    external_adapter_payload_snapshot: Mapped[dict | None] = mapped_column(JSON)
    external_adapter_lifecycle_snapshot: Mapped[dict | None] = mapped_column(JSON)
    external_adapter_evidence_snapshot: Mapped[dict | None] = mapped_column(JSON)
    external_adapter_audit_snapshot: Mapped[dict | None] = mapped_column(JSON)
    external_adapter_prepared_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        index=True,
    )
    external_adapter_failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    technician: Mapped[Technician | None] = relationship(back_populates="route_assignments")
    job: Mapped[Job | None] = relationship(back_populates="route_assignments")
    visit: Mapped[Visit | None] = relationship(back_populates="route_assignments")
    review_items: Mapped[list[ReviewItem]] = relationship(back_populates="route_assignment")
