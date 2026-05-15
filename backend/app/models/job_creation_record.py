from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.intake_processing_record import IntakeProcessingRecord
    from app.models.job import Job


class JobCreationRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "job_creation_records"
    __table_args__ = (
        UniqueConstraint(
            "intake_processing_record_id",
            name="uq_job_creation_records_intake_processing_record_id",
        ),
    )

    intake_processing_record_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("intake_processing_records.id"),
        nullable=False,
        index=True,
    )
    job_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("jobs.id"),
        nullable=False,
        index=True,
    )
    review_item_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("review_items.id"),
        index=True,
    )
    lifecycle_state: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    audit_correlation_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)

    creation_snapshot: Mapped[dict | None] = mapped_column(JSON)
    intake_snapshot: Mapped[dict | None] = mapped_column(JSON)
    orchestration_snapshot: Mapped[dict | None] = mapped_column(JSON)
    dispatch_eligibility_snapshot: Mapped[dict | None] = mapped_column(JSON)
    review_linkage_snapshot: Mapped[dict | None] = mapped_column(JSON)
    deterministic_evidence_snapshot: Mapped[dict | None] = mapped_column(JSON)
    lifecycle_metadata: Mapped[dict | None] = mapped_column(JSON)
    created_from_intake_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    intake_processing_record: Mapped[IntakeProcessingRecord] = relationship(
        back_populates="job_creation_records",
    )
    job: Mapped[Job] = relationship(back_populates="job_creation_records")
