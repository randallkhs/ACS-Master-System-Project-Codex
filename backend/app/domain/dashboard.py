from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CountBucket:
    label: str
    count: int


@dataclass(frozen=True, slots=True)
class OperationalDashboardSummary:
    total_jobs: int
    total_work_orders: int
    total_visits: int
    total_route_assignments: int
    open_manual_reviews: int
    blocked_operations: int
    escalation_indicators: int
    open_water_emergencies: int
    audit_correlation_count: int


@dataclass(frozen=True, slots=True)
class DispatchLifecycleSummary:
    intake_lifecycle_counts: tuple[CountBucket, ...]
    job_status_counts: tuple[CountBucket, ...]
    work_order_status_counts: tuple[CountBucket, ...]
    visit_status_counts: tuple[CountBucket, ...]
    route_status_counts: tuple[CountBucket, ...]
    dispatch_execution_state_counts: tuple[CountBucket, ...]
    dispatch_ready_visits: int
    dispatched_route_assignments: int
    water_emergency_records: int
    water_emergency_separated_intake: int
    blocker_count: int


@dataclass(frozen=True, slots=True)
class ManualReviewSummary:
    total_items: int
    open_items: int
    deferred_items: int
    resolved_items: int
    archived_items: int
    severity_counts: tuple[CountBucket, ...]
    reason_counts: tuple[CountBucket, ...]
    escalation_indicators: int
    audit_correlation_count: int


@dataclass(frozen=True, slots=True)
class WaterEmergencyRecordSummary:
    water_emergency_id: UUID
    job_id: UUID
    status: str
    drying_stage: str | None
    next_required_action: str | None
    is_open: bool
    equipment_onsite: bool
    moisture_tracking_required: bool
    opened_at: datetime | None
    closed_at: datetime | None
    related_work_order_ids: tuple[UUID, ...]
    related_visit_ids: tuple[UUID, ...]
    open_review_count: int
    timeline_event_count: int
    audit_correlation_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class WaterEmergencyDashboardReadModel:
    generated_at: datetime
    total_records: int
    open_count: int
    closed_count: int
    status_counts: tuple[CountBucket, ...]
    stage_counts: tuple[CountBucket, ...]
    multi_visit_count: int
    equipment_onsite_count: int
    moisture_tracking_required_count: int
    related_job_count: int
    related_work_order_count: int
    related_visit_count: int
    review_indicator_count: int
    escalation_indicator_count: int
    data_gap_counts: tuple[CountBucket, ...]
    audit_correlation_count: int
    records: tuple[WaterEmergencyRecordSummary, ...]
    timeline_summary: OperationalEventTimelineSummary


@dataclass(frozen=True, slots=True)
class RouteAssignmentSummary:
    total_assignments: int
    status_counts: tuple[CountBucket, ...]
    region_counts: tuple[CountBucket, ...]
    time_window_counts: tuple[CountBucket, ...]
    authorization_state_counts: tuple[CountBucket, ...]
    dispatched_count: int
    awaiting_dispatch_execution_count: int
    blocked_count: int


@dataclass(frozen=True, slots=True)
class ExternalExecutionSummary:
    adapter_state_counts: tuple[CountBucket, ...]
    execution_state_counts: tuple[CountBucket, ...]
    confirmation_state_counts: tuple[CountBucket, ...]
    prepared_count: int
    execution_completed_count: int
    execution_failed_count: int
    confirmation_failed_count: int
    retry_prepared_count: int
    reconciliation_required_count: int


@dataclass(frozen=True, slots=True)
class ReconciliationRecoverySummary:
    reconciliation_state_counts: tuple[CountBucket, ...]
    recovery_state_counts: tuple[CountBucket, ...]
    mismatch_count: int
    divergence_count: int
    replay_prepared_count: int
    rollback_prepared_count: int
    recovery_blocked_count: int


@dataclass(frozen=True, slots=True)
class GovernanceAccountabilitySummary:
    governance_state_counts: tuple[CountBucket, ...]
    accountability_state_counts: tuple[CountBucket, ...]
    operator_approved_count: int
    intervention_required_count: int
    escalation_required_count: int
    incident_prepared_count: int
    accountability_blocked_count: int


@dataclass(frozen=True, slots=True)
class DashboardDispatchSummary:
    route_assignments: RouteAssignmentSummary
    external_execution: ExternalExecutionSummary
    reconciliation_recovery: ReconciliationRecoverySummary
    governance_accountability: GovernanceAccountabilitySummary


@dataclass(frozen=True, slots=True)
class OperationalTimelineEntry:
    occurred_at: datetime
    event_type: str
    event_state: str
    entity_type: str
    entity_id: UUID
    route_assignment_id: UUID | None
    visit_id: UUID | None
    work_order_id: UUID | None
    job_id: UUID | None
    technician_id: UUID | None
    audit_correlation_id: str
    previous_state: str | None
    new_state: str | None
    is_immutable: bool


@dataclass(frozen=True, slots=True)
class OperationalEventTimelineSummary:
    total_events: int
    returned_events: int
    mutable_event_count: int
    audit_correlation_ids: tuple[str, ...]
    entries: tuple[OperationalTimelineEntry, ...]


@dataclass(frozen=True, slots=True)
class DashboardOverviewReadModel:
    generated_at: datetime
    operational_summary: OperationalDashboardSummary
    lifecycle_summary: DispatchLifecycleSummary
    manual_review_summary: ManualReviewSummary
    dispatch_summary: DashboardDispatchSummary
    timeline_summary: OperationalEventTimelineSummary
