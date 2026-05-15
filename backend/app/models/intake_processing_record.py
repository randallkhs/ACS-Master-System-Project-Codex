from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.review_item import ReviewItem


class IntakeProcessingRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "intake_processing_records"

    source_system: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    source_id: Mapped[str | None] = mapped_column(String(255), index=True)
    lifecycle_state: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    orchestration_state: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    review_item_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("review_items.id"),
        index=True,
    )
    audit_correlation_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)

    dispatch_eligible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    requires_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    blocked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    unsafe: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    water_emergency_separated: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    raw_payload_snapshot: Mapped[dict | None] = mapped_column(JSON)
    orchestration_result_snapshot: Mapped[dict | None] = mapped_column(JSON)
    dispatch_eligibility_snapshot: Mapped[dict | None] = mapped_column(JSON)
    normalized_snapshot: Mapped[dict | None] = mapped_column(JSON)
    validation_snapshot: Mapped[dict | None] = mapped_column(JSON)
    confidence_snapshot: Mapped[dict | None] = mapped_column(JSON)
    review_snapshot: Mapped[dict | None] = mapped_column(JSON)
    warning_snapshot: Mapped[dict | None] = mapped_column(JSON)
    deterministic_evidence_snapshot: Mapped[dict | None] = mapped_column(JSON)
    review_linkage_snapshot: Mapped[dict | None] = mapped_column(JSON)
    lifecycle_metadata: Mapped[dict | None] = mapped_column(JSON)

    approved_for_dispatch_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deferred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    review_item: Mapped[ReviewItem | None] = relationship(
        back_populates="intake_processing_records",
    )
