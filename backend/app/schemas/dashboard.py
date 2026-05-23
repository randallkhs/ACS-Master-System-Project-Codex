from datetime import date, datetime
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


class ManualReviewTaxonomyMetadataItemResponse(DashboardSchema):
    key: str
    label: str
    category: str
    source: str
    randall_authorized_phase_0_baseline: bool
    legal_or_insurance_policy: bool
    requires_alfonso_owner_review: bool
    reason: str


class ManualReviewTaxonomyMetadataResponse(DashboardSchema):
    randall_authorized_phase_0_baseline: bool
    source: str
    legal_or_insurance_policy: bool
    requires_alfonso_owner_review: bool
    baseline_note: str
    group_definitions: tuple[ManualReviewTaxonomyMetadataItemResponse, ...]


class ManualReviewFilterOptionResponse(DashboardSchema):
    key: str
    label: str
    count: int
    description: str


class ManualReviewSortOptionResponse(DashboardSchema):
    key: str
    label: str
    description: str


class ManualReviewResultWindowMetadataResponse(DashboardSchema):
    total_count: int
    visible_count: int
    result_limit: int
    has_more: bool
    sort_key: str
    generated_at: datetime


class ManualReviewDecisionReadinessResponse(DashboardSchema):
    label: str
    summary: str
    reason_codes: tuple[str, ...]
    evidence_references: tuple[str, ...]
    is_active_decision_need: bool
    is_resolution_candidate: bool


class ManualReviewActionPreflightResponse(DashboardSchema):
    label: str
    summary: str
    blocker_codes: tuple[str, ...]
    required_future_controls: tuple[str, ...]
    evidence_references: tuple[str, ...]
    is_currently_executable: bool
    requires_operator_identity: bool
    requires_audit_reason: bool


class ManualReviewFutureActionPreviewResponse(DashboardSchema):
    label: str
    description: str
    expected_outcome_summary: str
    impacted_entity_summary: str
    impacted_entity_references: tuple[str, ...]
    blocker_codes: tuple[str, ...]
    required_future_controls: tuple[str, ...]
    evidence_references: tuple[str, ...]
    is_currently_executable: bool
    requires_operator_identity: bool
    requires_audit_reason: bool


class ManualReviewCommandContractResponse(DashboardSchema):
    label: str
    summary: str
    future_command_candidates: tuple[str, ...]
    required_contract_labels: tuple[str, ...]
    impacted_entity_summary: str
    impacted_entity_references: tuple[str, ...]
    blocker_codes: tuple[str, ...]
    evidence_references: tuple[str, ...]
    is_currently_executable: bool
    not_executable_reason: str
    requires_operator_identity: bool
    requires_role_authorization: bool
    requires_audit_reason: bool
    requires_idempotency_key: bool
    requires_immutable_event_recording: bool
    requires_post_action_consistency_check: bool


class ManualReviewAuditLedgerDryRunResponse(DashboardSchema):
    label: str
    summary: str
    future_command_type_candidates: tuple[str, ...]
    required_labels: tuple[str, ...]
    proposed_future_event_type: str
    proposed_future_event_state: str
    proposed_future_audit_envelope_fields: tuple[str, ...]
    proposed_future_idempotency_scope: str
    proposed_future_consistency_check_summary: str
    audit_correlation_references: tuple[str, ...]
    evidence_references: tuple[str, ...]
    is_currently_executable: bool
    phase_allows_execution: bool
    execution_unavailable_reason: str
    requires_operator_identity: bool
    requires_role_authorization: bool
    requires_audit_reason: bool
    requires_idempotency_key: bool
    requires_immutable_event_recording: bool
    requires_post_action_consistency_check: bool


class ManualReviewQueueItemResponse(DashboardSchema):
    review_item_id: UUID
    status: str
    severity: str | None
    reason_code: str
    visibility_groups: tuple[str, ...]
    primary_group: str
    entity_type: str | None
    entity_id: UUID | None
    job_id: UUID | None
    work_order_id: UUID | None
    visit_id: UUID | None
    route_assignment_id: UUID | None
    water_emergency_id: UUID | None
    created_at: datetime
    updated_at: datetime
    reviewed_at: datetime | None
    deferred_until: datetime | None
    resolved_at: datetime | None
    age_bucket: str
    age_hours: int | None
    blocker_indicator: bool
    attention_indicator: bool
    confidence_score: float | None
    recommended_action: str | None
    audit_correlation_id: str | None
    decision_readiness: ManualReviewDecisionReadinessResponse
    action_preflight: ManualReviewActionPreflightResponse
    future_action_preview: ManualReviewFutureActionPreviewResponse
    command_contract: ManualReviewCommandContractResponse
    audit_ledger_dry_run: ManualReviewAuditLedgerDryRunResponse
    evidence_references: tuple[str, ...]


class ManualReviewQueueResponse(DashboardSchema):
    generated_at: datetime
    total_items: int
    open_items: int
    deferred_items: int
    resolved_items: int
    archived_items: int
    active_attention_count: int
    water_emergency_related_count: int
    dispatch_related_count: int
    blocked_count: int
    status_counts: tuple[CountBucketResponse, ...]
    reason_counts: tuple[CountBucketResponse, ...]
    severity_counts: tuple[CountBucketResponse, ...]
    group_counts: tuple[CountBucketResponse, ...]
    decision_readiness_counts: tuple[CountBucketResponse, ...]
    action_preflight_counts: tuple[CountBucketResponse, ...]
    future_action_preview_counts: tuple[CountBucketResponse, ...]
    command_contract_counts: tuple[CountBucketResponse, ...]
    audit_ledger_dry_run_counts: tuple[CountBucketResponse, ...]
    age_bucket_counts: tuple[CountBucketResponse, ...]
    audit_correlation_count: int
    taxonomy_metadata: ManualReviewTaxonomyMetadataResponse
    available_filters: tuple[ManualReviewFilterOptionResponse, ...]
    sort_options: tuple[ManualReviewSortOptionResponse, ...]
    result_window_metadata: ManualReviewResultWindowMetadataResponse
    items: tuple[ManualReviewQueueItemResponse, ...]


class ManualReviewReasonEvidenceContextResponse(DashboardSchema):
    reason_code: str
    status: str
    severity: str | None
    confidence_score: float | None
    recommended_action: str | None
    review_reason_codes: tuple[str, ...]
    snapshot_keys: tuple[str, ...]
    blocker_indicator: bool
    attention_indicator: bool
    evidence_references: tuple[str, ...]


class ManualReviewDetailLinkedEntityContextResponse(DashboardSchema):
    entity_type: str | None
    entity_id: UUID | None
    job_id: UUID | None
    job_status: str | None
    job_type: str | None
    work_order_id: UUID | None
    work_order_status: str | None
    visit_id: UUID | None
    visit_status: str | None
    route_assignment_id: UUID | None
    route_assignment_status: str | None
    water_emergency_id: UUID | None
    water_emergency_status: str | None
    water_emergency_stage: str | None
    is_water_emergency_related: bool
    is_dispatch_related: bool
    unknown_indicators: tuple[str, ...]
    audit_correlation_ids: tuple[str, ...]


class ManualReviewDetailResponse(DashboardSchema):
    generated_at: datetime
    review_item: ManualReviewQueueItemResponse
    reason_context: ManualReviewReasonEvidenceContextResponse
    decision_readiness: ManualReviewDecisionReadinessResponse
    action_preflight: ManualReviewActionPreflightResponse
    future_action_preview: ManualReviewFutureActionPreviewResponse
    command_contract: ManualReviewCommandContractResponse
    audit_ledger_dry_run: ManualReviewAuditLedgerDryRunResponse
    linked_entity_context: ManualReviewDetailLinkedEntityContextResponse
    data_gap_counts: tuple[CountBucketResponse, ...]
    audit_correlation_ids: tuple[str, ...]
    taxonomy_metadata: ManualReviewTaxonomyMetadataResponse
    timeline_summary: "OperationalEventTimelineSummaryResponse"


class WaterEmergencyEquipmentSummaryResponse(DashboardSchema):
    equipment_onsite_count: int
    moisture_tracking_required_count: int
    work_orders_with_equipment_notes_count: int
    records_missing_equipment_context_count: int
    inventory_entity_available: bool
    unknown_counts: tuple[CountBucketResponse, ...]


class WaterEmergencyVisitChainSummaryResponse(DashboardSchema):
    total_visits: int
    multi_visit_record_count: int
    open_records_without_visits_count: int
    scheduled_visit_count: int
    completed_visit_count: int
    visit_status_counts: tuple[CountBucketResponse, ...]


class WaterEmergencyDryingStageSummaryResponse(DashboardSchema):
    stage_counts: tuple[CountBucketResponse, ...]
    active_stage_counts: tuple[CountBucketResponse, ...]
    missing_stage_count: int
    moisture_tracking_required_count: int


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


class WaterEmergencyJobReferenceResponse(DashboardSchema):
    job_id: UUID
    job_type: str | None
    status: str
    review_status: str | None
    priority: str | None
    requested_date: date | None
    scheduled_date: date | None
    source_system: str | None
    source_event_id: str | None


class WaterEmergencyWorkOrderReferenceResponse(DashboardSchema):
    work_order_id: UUID
    work_order_number: str | None
    status: str
    dispatch_status: str | None
    assigned_technician_id: UUID | None
    audit_correlation_id: str | None


class WaterEmergencyVisitReferenceResponse(DashboardSchema):
    visit_id: UUID
    work_order_id: UUID | None
    technician_id: UUID | None
    visit_type: str | None
    status: str
    scheduled_start_at: datetime | None
    scheduled_end_at: datetime | None
    arrived_at: datetime | None
    completed_at: datetime | None
    audit_correlation_id: str | None


class WaterEmergencyReviewIndicatorResponse(DashboardSchema):
    review_item_id: UUID
    status: str
    severity: str | None
    reason_code: str
    confidence_score: float | None
    entity_type: str | None
    entity_id: UUID | None
    job_id: UUID | None
    visit_id: UUID | None
    audit_correlation_id: str | None
    recommended_action: str | None


class WaterEmergencyEquipmentNoteResponse(DashboardSchema):
    work_order_id: UUID
    required_equipment_notes: str


class WaterEmergencyDetailEquipmentContextResponse(DashboardSchema):
    equipment_onsite: bool
    moisture_tracking_required: bool
    inventory_entity_available: bool
    required_equipment_notes: tuple[WaterEmergencyEquipmentNoteResponse, ...]
    unknown_indicators: tuple[str, ...]


class WaterEmergencyVisitChainResponse(DashboardSchema):
    total_visits: int
    completed_visit_count: int
    open_visit_count: int
    first_visit_at: datetime | None
    latest_visit_at: datetime | None
    next_scheduled_visit_at: datetime | None
    visit_status_counts: tuple[CountBucketResponse, ...]


class WaterEmergencyDetailDryingStageContextResponse(DashboardSchema):
    status: str
    current_stage: str | None
    next_required_action: str | None
    moisture_tracking_required: bool
    missing_indicators: tuple[str, ...]


class WaterEmergencyReviewExceptionSummaryResponse(DashboardSchema):
    total_review_count: int
    open_review_count: int
    deferred_review_count: int
    resolved_review_count: int
    archived_review_count: int
    critical_unresolved_count: int
    escalation_indicator_count: int
    review_reason_counts: tuple[CountBucketResponse, ...]
    blocker_reason_counts: tuple[CountBucketResponse, ...]
    unknown_counts: tuple[CountBucketResponse, ...]
    review_item_ids: tuple[UUID, ...]
    audit_correlation_ids: tuple[str, ...]


class WaterEmergencyReviewExceptionContextResponse(DashboardSchema):
    total_review_count: int
    open_review_count: int
    deferred_review_count: int
    resolved_review_count: int
    archived_review_count: int
    critical_unresolved_count: int
    escalation_indicator_count: int
    review_reason_counts: tuple[CountBucketResponse, ...]
    blocker_reason_counts: tuple[CountBucketResponse, ...]
    unknown_indicators: tuple[str, ...]
    review_item_ids: tuple[UUID, ...]
    audit_correlation_ids: tuple[str, ...]


class WaterEmergencyNextStepReadinessResponse(DashboardSchema):
    water_emergency_id: UUID
    primary_label: str
    labels: tuple[str, ...]
    summary: str
    reason_codes: tuple[str, ...]
    evidence_references: tuple[str, ...]
    current_status: str
    current_stage: str | None
    open_review_count: int
    critical_alert_count: int
    blocker_count: int
    unknown_count: int
    requires_operator_attention: bool
    related_job_id: UUID
    related_work_order_ids: tuple[UUID, ...]
    related_visit_ids: tuple[UUID, ...]
    audit_correlation_ids: tuple[str, ...]


class WaterEmergencyNextStepReadinessSummaryResponse(DashboardSchema):
    total_records: int
    needs_attention_count: int
    closed_without_active_action_count: int
    label_counts: tuple[CountBucketResponse, ...]
    blocker_counts: tuple[CountBucketResponse, ...]
    records: tuple[WaterEmergencyNextStepReadinessResponse, ...]


class WaterEmergencyQueueItemResponse(DashboardSchema):
    water_emergency_id: UUID
    attention_label: str
    queue_group: str
    attention_rank: int
    readiness_labels: tuple[str, ...]
    summary: str
    reason_codes: tuple[str, ...]
    evidence_references: tuple[str, ...]
    current_status: str
    current_stage: str | None
    open_review_count: int
    critical_alert_count: int
    blocker_count: int
    unknown_count: int
    related_job_id: UUID
    related_work_order_ids: tuple[UUID, ...]
    related_visit_ids: tuple[UUID, ...]
    audit_correlation_ids: tuple[str, ...]


class WaterEmergencyOperatorQueueSummaryResponse(DashboardSchema):
    total_records: int
    active_attention_count: int
    closed_or_resolved_count: int
    critical_attention_count: int
    queue_group_counts: tuple[CountBucketResponse, ...]
    attention_label_counts: tuple[CountBucketResponse, ...]
    items: tuple[WaterEmergencyQueueItemResponse, ...]


class WaterEmergencyAgingFollowUpItemResponse(DashboardSchema):
    water_emergency_id: UUID
    time_sensitivity_label: str
    timing_group: str
    timing_rank: int
    age_bucket: str
    followup_bucket: str
    age_hours: int | None
    hours_since_last_visit: int | None
    hours_since_last_review: int | None
    hours_since_last_event: int | None
    opened_at: datetime | None
    last_visit_at: datetime | None
    last_review_at: datetime | None
    last_event_at: datetime | None
    closed_at: datetime | None
    summary: str
    reason_codes: tuple[str, ...]
    missing_timestamp_indicators: tuple[str, ...]
    stale_indicator_count: int
    requires_operator_attention: bool
    related_job_id: UUID
    related_work_order_ids: tuple[UUID, ...]
    related_visit_ids: tuple[UUID, ...]
    audit_correlation_ids: tuple[str, ...]
    evidence_references: tuple[str, ...]


class WaterEmergencyAgingFollowUpSummaryResponse(DashboardSchema):
    total_records: int
    active_timing_risk_count: int
    closed_or_resolved_count: int
    followup_due_count: int
    followup_overdue_count: int
    stale_evidence_count: int
    unknown_timing_count: int
    label_counts: tuple[CountBucketResponse, ...]
    age_bucket_counts: tuple[CountBucketResponse, ...]
    followup_bucket_counts: tuple[CountBucketResponse, ...]
    items: tuple[WaterEmergencyAgingFollowUpItemResponse, ...]


class WaterEmergencyFilterOptionResponse(DashboardSchema):
    key: str
    label: str
    count: int
    description: str


class WaterEmergencySortOptionResponse(DashboardSchema):
    key: str
    label: str
    description: str


class WaterEmergencyViewStateItemResponse(DashboardSchema):
    water_emergency_id: UUID
    filter_groups: tuple[str, ...]
    primary_filter_group: str
    sort_rank: int
    sort_label: str
    queue_group: str
    attention_label: str
    time_sensitivity_label: str
    readiness_label: str
    is_active: bool
    current_status: str
    current_stage: str | None
    open_review_count: int
    critical_alert_count: int
    blocker_count: int
    unknown_count: int
    last_activity_at: datetime | None
    summary: str
    reason_codes: tuple[str, ...]
    related_job_id: UUID
    related_work_order_ids: tuple[UUID, ...]
    related_visit_ids: tuple[UUID, ...]
    audit_correlation_ids: tuple[str, ...]
    evidence_references: tuple[str, ...]


class WaterEmergencyViewStateSummaryResponse(DashboardSchema):
    total_records: int
    active_record_count: int
    closed_or_resolved_count: int
    available_filters: tuple[WaterEmergencyFilterOptionResponse, ...]
    sort_options: tuple[WaterEmergencySortOptionResponse, ...]
    group_counts: tuple[CountBucketResponse, ...]
    items: tuple[WaterEmergencyViewStateItemResponse, ...]


class WaterEmergencyGovernanceMetadataItemResponse(DashboardSchema):
    key: str
    label: str
    category: str
    source: str
    randall_authorized_phase_0_baseline: bool
    legal_or_insurance_policy: bool
    requires_alfonso_owner_review: bool
    reason: str


class WaterEmergencyGovernanceMetadataResponse(DashboardSchema):
    randall_authorized_phase_0_baseline: bool
    source: str
    legal_or_insurance_policy: bool
    requires_alfonso_owner_review: bool
    baseline_note: str
    timing_heuristic_note: str
    provisional_filter_groups: tuple[WaterEmergencyGovernanceMetadataItemResponse, ...]
    provisional_attention_labels: tuple[WaterEmergencyGovernanceMetadataItemResponse, ...]
    provisional_timing_labels: tuple[WaterEmergencyGovernanceMetadataItemResponse, ...]
    provisional_readiness_labels: tuple[WaterEmergencyGovernanceMetadataItemResponse, ...]
    owner_review_required_items: tuple[WaterEmergencyGovernanceMetadataItemResponse, ...]
    future_role_visibility_roles: tuple[str, ...]


class WaterEmergencyResultWindowMetadataResponse(DashboardSchema):
    total_count: int
    visible_count: int
    result_limit: int
    has_more: bool
    sort_key: str
    generated_at: datetime


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
    equipment_summary: WaterEmergencyEquipmentSummaryResponse
    visit_chain_summary: WaterEmergencyVisitChainSummaryResponse
    drying_stage_summary: WaterEmergencyDryingStageSummaryResponse
    review_exception_summary: WaterEmergencyReviewExceptionSummaryResponse
    next_step_summary: WaterEmergencyNextStepReadinessSummaryResponse
    operator_queue_summary: WaterEmergencyOperatorQueueSummaryResponse
    aging_followup_summary: WaterEmergencyAgingFollowUpSummaryResponse
    view_state_summary: WaterEmergencyViewStateSummaryResponse
    governance_metadata: WaterEmergencyGovernanceMetadataResponse
    result_window_metadata: WaterEmergencyResultWindowMetadataResponse
    related_job_count: int
    related_work_order_count: int
    related_visit_count: int
    review_indicator_count: int
    escalation_indicator_count: int
    data_gap_counts: tuple[CountBucketResponse, ...]
    audit_correlation_count: int
    records: tuple[WaterEmergencyRecordSummaryResponse, ...]
    timeline_summary: OperationalEventTimelineSummaryResponse


class WaterEmergencyDetailResponse(DashboardSchema):
    generated_at: datetime
    record: WaterEmergencyRecordSummaryResponse
    job: WaterEmergencyJobReferenceResponse | None
    work_orders: tuple[WaterEmergencyWorkOrderReferenceResponse, ...]
    visits: tuple[WaterEmergencyVisitReferenceResponse, ...]
    review_indicators: tuple[WaterEmergencyReviewIndicatorResponse, ...]
    equipment_context: WaterEmergencyDetailEquipmentContextResponse
    visit_chain: WaterEmergencyVisitChainResponse
    drying_stage_context: WaterEmergencyDetailDryingStageContextResponse
    review_exception_context: WaterEmergencyReviewExceptionContextResponse
    next_step_readiness: WaterEmergencyNextStepReadinessResponse
    data_gap_counts: tuple[CountBucketResponse, ...]
    audit_correlation_ids: tuple[str, ...]
    timeline_summary: OperationalEventTimelineSummaryResponse


class DashboardOverviewResponse(DashboardSchema):
    generated_at: datetime
    operational_summary: OperationalDashboardSummaryResponse
    lifecycle_summary: DispatchLifecycleSummaryResponse
    manual_review_summary: ManualReviewSummaryResponse
    dispatch_summary: DashboardDispatchSummaryResponse
    timeline_summary: OperationalEventTimelineSummaryResponse
