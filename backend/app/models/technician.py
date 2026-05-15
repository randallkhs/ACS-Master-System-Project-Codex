from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.associations import visit_technicians, work_order_technicians
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.route_assignment import RouteAssignment
    from app.models.visit import Visit
    from app.models.work_order import WorkOrder


class Technician(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "technicians"

    full_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(254))
    role: Mapped[str | None] = mapped_column(String(80))
    fastfield_user_id: Mapped[str | None] = mapped_column(String(120), unique=True)
    verizon_connect_ref: Mapped[str | None] = mapped_column(String(120), unique=True)
    skills: Mapped[list[str] | None] = mapped_column(JSON)
    service_areas: Mapped[list[str] | None] = mapped_column(JSON)
    vehicle_label: Mapped[str | None] = mapped_column(String(120))
    availability_status: Mapped[str | None] = mapped_column(String(60), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    work_orders: Mapped[list[WorkOrder]] = relationship(back_populates="assigned_technician")
    assigned_work_orders: Mapped[list[WorkOrder]] = relationship(
        secondary=work_order_technicians,
        back_populates="assigned_technicians",
    )
    visits: Mapped[list[Visit]] = relationship(back_populates="technician")
    assigned_visits: Mapped[list[Visit]] = relationship(
        secondary=visit_technicians,
        back_populates="assigned_technicians",
    )
    route_assignments: Mapped[list[RouteAssignment]] = relationship(back_populates="technician")
