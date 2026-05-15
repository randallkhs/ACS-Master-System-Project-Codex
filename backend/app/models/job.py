from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.job_creation_record import JobCreationRecord
    from app.models.property import Property
    from app.models.review_item import ReviewItem
    from app.models.route_assignment import RouteAssignment
    from app.models.visit import Visit
    from app.models.water_emergency import WaterEmergency
    from app.models.work_order import WorkOrder


class Job(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "jobs"

    customer_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("customers.id"),
    )
    property_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("properties.id"),
    )

    job_type: Mapped[str | None] = mapped_column(String(100), index=True)
    status: Mapped[str] = mapped_column(String(60), default="NEW", nullable=False, index=True)
    review_status: Mapped[str | None] = mapped_column(String(60), index=True)
    priority: Mapped[str | None] = mapped_column(String(60), index=True)
    requested_date: Mapped[date | None] = mapped_column(Date)
    scheduled_date: Mapped[date | None] = mapped_column(Date, index=True)
    source_system: Mapped[str | None] = mapped_column(String(80), index=True)
    source_event_id: Mapped[str | None] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)

    customer: Mapped[Customer | None] = relationship(back_populates="jobs")
    property: Mapped[Property | None] = relationship(back_populates="jobs")
    work_orders: Mapped[list[WorkOrder]] = relationship(back_populates="job")
    visits: Mapped[list[Visit]] = relationship(back_populates="job")
    route_assignments: Mapped[list[RouteAssignment]] = relationship(back_populates="job")
    review_items: Mapped[list[ReviewItem]] = relationship(back_populates="job")
    water_emergency: Mapped[WaterEmergency | None] = relationship(back_populates="job")
    job_creation_records: Mapped[list[JobCreationRecord]] = relationship(back_populates="job")
