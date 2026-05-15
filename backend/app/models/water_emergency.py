from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.job import Job


class WaterEmergency(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "water_emergencies"

    job_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("jobs.id"),
        nullable=False,
        unique=True,
    )
    status: Mapped[str] = mapped_column(String(80), default="NEW", nullable=False, index=True)
    drying_stage: Mapped[str | None] = mapped_column(String(120), index=True)
    next_required_action: Mapped[str | None] = mapped_column(String(200))
    equipment_onsite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    moisture_tracking_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)

    job: Mapped[Job] = relationship(back_populates="water_emergency")
