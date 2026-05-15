from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.job import Job
    from app.models.review_item import ReviewItem
    from app.models.route_assignment import RouteAssignment
    from app.models.technician import Technician


class Visit(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "visits"

    job_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("jobs.id"),
        nullable=False,
    )
    technician_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("technicians.id"),
    )
    visit_type: Mapped[str | None] = mapped_column(String(100), index=True)
    status: Mapped[str] = mapped_column(String(60), default="SCHEDULED", nullable=False, index=True)
    scheduled_start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    scheduled_end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    arrived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)

    job: Mapped[Job] = relationship(back_populates="visits")
    technician: Mapped[Technician | None] = relationship(back_populates="visits")
    route_assignments: Mapped[list[RouteAssignment]] = relationship(back_populates="visit")
    review_items: Mapped[list[ReviewItem]] = relationship(back_populates="visit")
