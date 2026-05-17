from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DashboardSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CountBucketResponse(DashboardSchema):
    label: str
    count: int


class OperationalDashboardSummaryResponse(DashboardSchema):
    total_jobs: int
    total_work_orders: int
    total_visits: int
    total_route_assignments: int
    open_manual_reviews: int
    blocked_operations: int
    escalation_indicators: int
    open_water_emergencies: int
    audit_correlation_count: int


class DispatchLifecycleSummaryResponse(DashboardSchema):
    intake_lifecycle_counts: tuple[CountBucketResponse, ...]
    job_status_counts: tuple[CountBucketResponse, ...]
    work_order_status_counts: tuple[CountBucketResponse, ...]
    visit_status_counts: tuple[CountBucketResponse, ...]
    route_status_counts: tuple[CountBucketResponse, ...]
    dispatch_execution_state_counts: tuple[CountBucketResponse, ...]
    dispatch_ready_visits: int
    dispatched_route_assignments: int
    water_emergency_records: int
    water_emergency_separated_intake: int
    blocker_count: int


class ManualReviewSummaryResponse(DashboardSchema):
    total_items: int
    open_items: int
    deferred_items: int
    resolved_items: int
    archived_items: int
    severity_counts: tuple[CountBucketResponse, ...]
    reason_counts: tuple[CountBucketResponse, ...]
    escalation_indicators: int
    audit_correlation_count: int


class WaterEmergencyRecordSummaryResponse(DashboardSchema):
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


class RouteAssignmentSummaryResponse(DashboardSchema):
    total_assignments: int
    status_counts: tuple[CountBucketResponse, ...]
    region_counts: tuple[CountBucketResponse, ...]
    time_window_counts: tuple[CountBucketResponse, ...]
    authorization_state_counts: tuple[CountBucketResponse, ...]
    dispatched_count: int
    awaiting_dispatch_execution_count: int
    blocked_count: int


class ExternalExecutionSummaryResponse(DashboardSchema):
    adapter_state_counts: tuple[CountBucketResponse, ...]
    execution_state_counts: tuple[CountBucketResponse, ...]
    confirmation_state_counts: tuple[CountBucketResponse, ...]
    prepared_count: int
    execution_completed_count: int
    execution_failed_count: int
    confirmation_failed_count: int
    retry_prepared_count: int
    reconciliation_required_count: int


class ReconciliationRecoverySummaryResponse(DashboardSchema):
    reconciliation_state_counts: tuple[CountBucketResponse, ...]
    recovery_state_counts: tuple[CountBucketResponse, ...]
    mismatch_count: int
    divergence_count: int
    replay_prepared_count: int
    rollback_prepared_count: int
    recovery_blocked_count: int


class GovernanceAccountabilitySummaryResponse(DashboardSchema):
    governance_state_counts: tuple[CountBucketResponse, ...]
    accountability_state_counts: tuple[CountBucketResponse, ...]
    operator_approved_count: int
    intervention_required_count: int
    escalation_required_count: int
    incident_prepared_count: int
    accountability_blocked_count: int


class DashboardDispatchSummaryResponse(DashboardSchema):
    route_assignments: RouteAssignmentSummaryResponse
    external_execution: ExternalExecutionSummaryResponse
    reconciliation_recovery: ReconciliationRecoverySummaryResponse
    governance_accountability: GovernanceAccountabilitySummaryResponse


class OperationalTimelineEntryResponse(DashboardSchema):
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


class OperationalEventTimelineSummaryResponse(DashboardSchema):
    total_events: int
    returned_events: int
    mutable_event_count: int
    audit_correlation_ids: tuple[str, ...]
    entries: tuple[OperationalTimelineEntryResponse, ...]


class WaterEmergencyDashboardResponse(DashboardSchema):
    generated_at: datetime
    total_records: int
    open_count: int
    closed_count: int
    status_counts: tuple[CountBucketResponse, ...]
    stage_counts: tuple[CountBucketResponse, ...]
    multi_visit_count: int
    equipment_onsite_count: int
    moisture_tracking_required_count: int
    related_job_count: int
    related_work_order_count: int
    related_visit_count: int
    review_indicator_count: int
    escalation_indicator_count: int
    data_gap_counts: tuple[CountBucketResponse, ...]
    audit_correlation_count: int
    records: tuple[WaterEmergencyRecordSummaryResponse, ...]
    timeline_summary: OperationalEventTimelineSummaryResponse


class DashboardOverviewResponse(DashboardSchema):
    generated_at: datetime
    operational_summary: OperationalDashboardSummaryResponse
    lifecycle_summary: DispatchLifecycleSummaryResponse
    manual_review_summary: ManualReviewSummaryResponse
    dispatch_summary: DashboardDispatchSummaryResponse
    timeline_summary: OperationalEventTimelineSummaryResponse
