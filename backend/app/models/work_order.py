from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.associations import work_order_technicians
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.job import Job
    from app.models.technician import Technician


class WorkOrder(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "work_orders"

    job_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("jobs.id"),
        nullable=False,
    )
    assigned_technician_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("technicians.id"),
    )
    work_order_number: Mapped[str | None] = mapped_column(String(80), unique=True)
    status: Mapped[str] = mapped_column(String(60), default="NEW", nullable=False, index=True)
    dispatch_status: Mapped[str | None] = mapped_column(String(60), index=True)
    service_instructions: Mapped[str | None] = mapped_column(Text)
    required_forms: Mapped[str | None] = mapped_column(Text)
    required_equipment_notes: Mapped[str | None] = mapped_column(Text)
    technician_notes: Mapped[str | None] = mapped_column(Text)

    job: Mapped[Job] = relationship(back_populates="work_orders")
    assigned_technician: Mapped[Technician | None] = relationship(back_populates="work_orders")
    assigned_technicians: Mapped[list[Technician]] = relationship(
        secondary=work_order_technicians,
        back_populates="assigned_work_orders",
    )
