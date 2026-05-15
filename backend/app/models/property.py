from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.job import Job


class Property(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "properties"

    customer_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("customers.id"),
    )
    property_name: Mapped[str | None] = mapped_column(String(200))
    street_address: Mapped[str | None] = mapped_column(String(255), index=True)
    unit_number: Mapped[str | None] = mapped_column(String(50))
    building_number: Mapped[str | None] = mapped_column(String(50))
    city: Mapped[str | None] = mapped_column(String(120))
    state: Mapped[str | None] = mapped_column(String(2), index=True)
    postal_code: Mapped[str | None] = mapped_column(String(20))
    access_notes: Mapped[str | None] = mapped_column(Text)
    parking_notes: Mapped[str | None] = mapped_column(Text)
    gate_code: Mapped[str | None] = mapped_column(String(100))

    customer: Mapped[Customer | None] = relationship(back_populates="properties")
    jobs: Mapped[list[Job]] = relationship(back_populates="property")
