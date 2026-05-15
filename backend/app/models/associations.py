from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models.base import Base

work_order_technicians = Table(
    "work_order_technicians",
    Base.metadata,
    Column(
        "work_order_id",
        PG_UUID(as_uuid=True),
        ForeignKey("work_orders.id"),
        primary_key=True,
    ),
    Column(
        "technician_id",
        PG_UUID(as_uuid=True),
        ForeignKey("technicians.id"),
        primary_key=True,
    ),
)

visit_technicians = Table(
    "visit_technicians",
    Base.metadata,
    Column(
        "visit_id",
        PG_UUID(as_uuid=True),
        ForeignKey("visits.id"),
        primary_key=True,
    ),
    Column(
        "technician_id",
        PG_UUID(as_uuid=True),
        ForeignKey("technicians.id"),
        primary_key=True,
    ),
)
