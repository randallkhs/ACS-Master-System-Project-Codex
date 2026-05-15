from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.intake_processing_record import IntakeProcessingRecord
    from app.models.job import Job
    from app.models.route_assignment import RouteAssignment
    from app.models.visit import Visit


class ReviewItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "review_items"

    job_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("jobs.id"))
    visit_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("visits.id"))
    route_assignment_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("route_assignments.id"),
    )
    entity_type: Mapped[str | None] = mapped_column(String(120), index=True)
    entity_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), index=True)
    source_system: Mapped[str | None] = mapped_column(String(80), index=True)
    source_id: Mapped[str | None] = mapped_column(String(255), index=True)
    reason_code: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(60), default="open", nullable=False, index=True)
    severity: Mapped[str | None] = mapped_column(String(30), index=True)
    intake_processing_state: Mapped[str | None] = mapped_column(String(60), index=True)
    confidence_score: Mapped[float | None] = mapped_column(Float)
    review_reasons: Mapped[list[dict] | None] = mapped_column(JSON)
    confidence_snapshot: Mapped[dict | None] = mapped_column(JSON)
    warning_snapshot: Mapped[dict | None] = mapped_column(JSON)
    normalization_snapshot: Mapped[dict | None] = mapped_column(JSON)
    validation_snapshot: Mapped[dict | None] = mapped_column(JSON)
    source_snapshot: Mapped[dict | None] = mapped_column(JSON)
    review_metadata: Mapped[dict | None] = mapped_column(JSON)
    audit_correlation_id: Mapped[str | None] = mapped_column(String(120), index=True)
    recommended_action: Mapped[str | None] = mapped_column(Text)
    operator_decision: Mapped[str | None] = mapped_column(Text)
    operator_notes: Mapped[str | None] = mapped_column(Text)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deferred_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    job: Mapped[Job | None] = relationship(back_populates="review_items")
    visit: Mapped[Visit | None] = relationship(back_populates="review_items")
    route_assignment: Mapped[RouteAssignment | None] = relationship(back_populates="review_items")
    intake_processing_records: Mapped[list[IntakeProcessingRecord]] = relationship(
        back_populates="review_item",
    )
