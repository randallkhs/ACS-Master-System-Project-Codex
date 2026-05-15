from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.job import Job
    from app.models.property import Property


class Customer(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "customers"

    display_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    company_name: Mapped[str | None] = mapped_column(String(200))
    phone: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(254))
    billing_contact: Mapped[str | None] = mapped_column(Text)
    property_manager_contact: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list[str] | None] = mapped_column(JSON)
    notes: Mapped[str | None] = mapped_column(Text)

    properties: Mapped[list[Property]] = relationship(back_populates="customer")
    jobs: Mapped[list[Job]] = relationship(back_populates="customer")
