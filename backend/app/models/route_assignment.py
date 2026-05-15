from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
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
    estimated_arrival_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    technician: Mapped[Technician | None] = relationship(back_populates="route_assignments")
    job: Mapped[Job | None] = relationship(back_populates="route_assignments")
    visit: Mapped[Visit | None] = relationship(back_populates="route_assignments")
    review_items: Mapped[list[ReviewItem]] = relationship(back_populates="route_assignment")
