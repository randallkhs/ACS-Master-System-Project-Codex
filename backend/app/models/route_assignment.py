from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.job import Job
    from app.models.review_item import ReviewItem
    from app.models.technician import Technician
    from app.models.visit import Visit


class RouteAssignment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "route_assignments"

    route_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    technician_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("technicians.id"),
    )
    job_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("jobs.id"))
    visit_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("visits.id"))
    route_order: Mapped[int | None] = mapped_column(Integer)
    region: Mapped[str | None] = mapped_column(String(80), index=True)
    time_window: Mapped[str | None] = mapped_column(String(20), index=True)
    status: Mapped[str] = mapped_column(String(60), default="PLANNED", nullable=False, index=True)
    route_group_key: Mapped[str | None] = mapped_column(String(160), index=True)
    audit_correlation_id: Mapped[str | None] = mapped_column(String(120), index=True)
    estimated_arrival_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    estimated_drive_time_minutes: Mapped[int | None] = mapped_column(Integer)
    route_grouping_snapshot: Mapped[dict | None] = mapped_column(JSON)
    route_assignment_readiness_snapshot: Mapped[dict | None] = mapped_column(JSON)
    technician_route_compatibility_snapshot: Mapped[dict | None] = mapped_column(JSON)
    dispatch_authorization_snapshot: Mapped[dict | None] = mapped_column(JSON)
    dispatch_execution_boundary_snapshot: Mapped[dict | None] = mapped_column(JSON)
    deterministic_evidence_snapshot: Mapped[dict | None] = mapped_column(JSON)
    authorization_prepared_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    authorized_for_dispatch_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    dispatch_execution_state: Mapped[str | None] = mapped_column(String(60), index=True)
    dispatch_execution_snapshot: Mapped[dict | None] = mapped_column(JSON)
    dispatch_lifecycle_snapshot: Mapped[dict | None] = mapped_column(JSON)
    dispatch_audit_snapshot: Mapped[dict | None] = mapped_column(JSON)
    dispatched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    dispatch_failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    external_adapter_state: Mapped[str | None] = mapped_column(String(80), index=True)
    external_adapter_request_snapshot: Mapped[dict | None] = mapped_column(JSON)
    external_adapter_payload_snapshot: Mapped[dict | None] = mapped_column(JSON)
    external_adapter_lifecycle_snapshot: Mapped[dict | None] = mapped_column(JSON)
    external_adapter_evidence_snapshot: Mapped[dict | None] = mapped_column(JSON)
    external_adapter_audit_snapshot: Mapped[dict | None] = mapped_column(JSON)
    external_adapter_prepared_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        index=True,
    )
    external_adapter_failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    external_confirmation_state: Mapped[str | None] = mapped_column(String(80), index=True)
    external_confirmation_snapshot: Mapped[dict | None] = mapped_column(JSON)
    external_confirmation_lifecycle_snapshot: Mapped[dict | None] = mapped_column(JSON)
    external_confirmation_audit_snapshot: Mapped[dict | None] = mapped_column(JSON)
    external_failure_snapshot: Mapped[dict | None] = mapped_column(JSON)
    retry_preparation_snapshot: Mapped[dict | None] = mapped_column(JSON)
    reconciliation_snapshot: Mapped[dict | None] = mapped_column(JSON)
    external_confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        index=True,
    )
    external_confirmation_failed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
    retry_prepared_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reconciliation_required_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    external_execution_state: Mapped[str | None] = mapped_column(String(80), index=True)
    external_execution_request_snapshot: Mapped[dict | None] = mapped_column(JSON)
    external_execution_provider_snapshot: Mapped[dict | None] = mapped_column(JSON)
    external_execution_evidence_snapshot: Mapped[dict | None] = mapped_column(JSON)
    external_execution_failure_snapshot: Mapped[dict | None] = mapped_column(JSON)
    external_execution_lifecycle_snapshot: Mapped[dict | None] = mapped_column(JSON)
    external_execution_audit_snapshot: Mapped[dict | None] = mapped_column(JSON)
    external_execution_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    external_execution_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        index=True,
    )
    external_execution_failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    dispatch_reconciliation_state: Mapped[str | None] = mapped_column(String(80), index=True)
    dispatch_consistency_snapshot: Mapped[dict | None] = mapped_column(JSON)
    dispatch_divergence_snapshot: Mapped[dict | None] = mapped_column(JSON)
    dispatch_mismatch_snapshot: Mapped[dict | None] = mapped_column(JSON)
    dispatch_reconciliation_blocker_snapshot: Mapped[dict | None] = mapped_column(JSON)
    dispatch_reconciliation_audit_snapshot: Mapped[dict | None] = mapped_column(JSON)
    dispatch_reconciliation_prepared_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        index=True,
    )
    dispatch_consistency_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        index=True,
    )
    dispatch_reconciliation_blocked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
    replay_recovery_state: Mapped[str | None] = mapped_column(String(80), index=True)
    replay_preparation_snapshot: Mapped[dict | None] = mapped_column(JSON)
    rollback_preparation_snapshot: Mapped[dict | None] = mapped_column(JSON)
    replay_eligibility_snapshot: Mapped[dict | None] = mapped_column(JSON)
    replay_blocker_snapshot: Mapped[dict | None] = mapped_column(JSON)
    recovery_coordination_snapshot: Mapped[dict | None] = mapped_column(JSON)
    replay_recovery_audit_snapshot: Mapped[dict | None] = mapped_column(JSON)
    replay_prepared_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        index=True,
    )
    rollback_prepared_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        index=True,
    )
    replay_blocked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    governance_state: Mapped[str | None] = mapped_column(String(80), index=True)
    governance_approval_snapshot: Mapped[dict | None] = mapped_column(JSON)
    intervention_authorization_snapshot: Mapped[dict | None] = mapped_column(JSON)
    replay_authorization_snapshot: Mapped[dict | None] = mapped_column(JSON)
    rollback_authorization_snapshot: Mapped[dict | None] = mapped_column(JSON)
    reconciliation_approval_snapshot: Mapped[dict | None] = mapped_column(JSON)
    governance_blocker_snapshot: Mapped[dict | None] = mapped_column(JSON)
    governance_audit_snapshot: Mapped[dict | None] = mapped_column(JSON)
    governance_approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        index=True,
    )
    governance_rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    intervention_required_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        index=True,
    )
    governance_blocked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    technician: Mapped[Technician | None] = relationship(back_populates="route_assignments")
    job: Mapped[Job | None] = relationship(back_populates="route_assignments")
    visit: Mapped[Visit | None] = relationship(back_populates="route_assignments")
    review_items: Mapped[list[ReviewItem]] = relationship(back_populates="route_assignment")
