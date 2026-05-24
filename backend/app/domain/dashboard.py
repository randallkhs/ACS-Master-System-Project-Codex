from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
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
class ManualReviewTaxonomyMetadataItem:
    key: str
    label: str
    category: str
    source: str
    randall_authorized_phase_0_baseline: bool
    legal_or_insurance_policy: bool
    requires_alfonso_owner_review: bool
    reason: str


@dataclass(frozen=True, slots=True)
class ManualReviewTaxonomyMetadata:
    randall_authorized_phase_0_baseline: bool
    source: str
    legal_or_insurance_policy: bool
    requires_alfonso_owner_review: bool
    baseline_note: str
    group_definitions: tuple[ManualReviewTaxonomyMetadataItem, ...]


@dataclass(frozen=True, slots=True)
class ManualReviewFilterOption:
    key: str
    label: str
    count: int
    description: str


@dataclass(frozen=True, slots=True)
class ManualReviewSortOption:
    key: str
    label: str
    description: str


@dataclass(frozen=True, slots=True)
class ManualReviewResultWindowMetadata:
    total_count: int
    visible_count: int
    result_limit: int
    has_more: bool
    sort_key: str
    generated_at: datetime


@dataclass(frozen=True, slots=True)
class ManualReviewDecisionReadiness:
    label: str
    summary: str
    reason_codes: tuple[str, ...]
    evidence_references: tuple[str, ...]
    is_active_decision_need: bool
    is_resolution_candidate: bool


@dataclass(frozen=True, slots=True)
class ManualReviewActionPreflight:
    label: str
    summary: str
    blocker_codes: tuple[str, ...]
    required_future_controls: tuple[str, ...]
    evidence_references: tuple[str, ...]
    is_currently_executable: bool
    requires_operator_identity: bool
    requires_audit_reason: bool


@dataclass(frozen=True, slots=True)
class ManualReviewFutureActionPreview:
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


@dataclass(frozen=True, slots=True)
class ManualReviewCommandContract:
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


@dataclass(frozen=True, slots=True)
class ManualReviewAuditLedgerDryRun:
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


@dataclass(frozen=True, slots=True)
class ManualReviewSafetyGate:
    key: str
    label: str
    passed: bool
    required: bool
    reason: str


@dataclass(frozen=True, slots=True)
class ManualReviewCommandValidation:
    label: str
    summary: str
    candidate_future_command_type: str
    validation_status: str
    validation_blockers: tuple[str, ...]
    validation_warnings: tuple[str, ...]
    safety_gates: tuple[ManualReviewSafetyGate, ...]
    audit_correlation_references: tuple[str, ...]
    evidence_references: tuple[str, ...]
    is_currently_executable: bool
    phase_allows_execution: bool
    execution_unavailable_reason: str
    requires_audit_reason: bool
    requires_operator_identity: bool
    requires_role_authorization: bool
    requires_idempotency_key: bool
    requires_immutable_event_recording: bool
    requires_post_action_consistency_check: bool
    requires_water_emergency_scope_check: bool
    requires_linked_entity_context: bool


@dataclass(frozen=True, slots=True)
class ManualReviewPermissionReadiness:
    label: str
    summary: str
    candidate_future_command_type: str
    future_required_roles: tuple[str, ...]
    future_forbidden_roles: tuple[str, ...]
    future_required_permissions: tuple[str, ...]
    required_permission_labels: tuple[str, ...]
    identity_requirement_labels: tuple[str, ...]
    audit_correlation_references: tuple[str, ...]
    evidence_references: tuple[str, ...]
    is_currently_executable: bool
    phase_allows_execution: bool
    execution_unavailable_reason: str
    identity_unavailable_reason: str
    future_operator_identity_required: bool
    future_operator_id_required: bool
    future_operator_display_name_required: bool
    future_operator_email_required: bool
    future_authentication_provider_boundary: str
    future_role_authorization_required: bool
    future_permission_set_required: bool
    future_audit_actor_required: bool
    future_audit_reason_required: bool
    future_idempotency_key_required: bool
    future_immutable_event_required: bool
    future_post_action_consistency_check_required: bool
    impersonation_allowed: bool
    service_account_allowed: bool
    technician_action_allowed: bool
    requires_water_emergency_scope_check: bool


@dataclass(frozen=True, slots=True)
class ManualReviewMutationBoundaryLock:
    manual_review_mutations_enabled: bool
    action_execution_phase: str
    currently_executable_count: int
    mutation_endpoints_available: bool
    auth_required_before_execution: bool
    rbac_required_before_execution: bool
    audit_envelope_required_before_execution: bool
    idempotency_required_before_execution: bool
    immutable_event_required_before_execution: bool
    post_action_consistency_required_before_execution: bool


@dataclass(frozen=True, slots=True)
class ManualReviewFutureTransitionPrerequisite:
    key: str
    label: str
    category: str
    status: str
    requires_alfonso_owner_review: bool
    reason: str


@dataclass(frozen=True, slots=True)
class ManualReviewExecutionReadinessAudit:
    summary: str
    total_review_items: int
    active_review_items: int
    resolved_archived_review_items: int
    water_emergency_related_review_items: int
    dispatch_related_review_items: int
    items_with_missing_entity_context: int
    items_with_conflict_blockers: int
    items_with_missing_data_blockers: int
    items_with_future_action_preview_labels: int
    items_with_command_contract_labels: int
    items_with_dry_run_labels: int
    items_with_safety_gate_matrix_labels: int
    items_with_permission_readiness_labels: int
    items_blocked_by_phase_execution: int
    currently_executable_count: int
    required_future_auth_count: int
    required_future_rbac_count: int
    required_future_operator_identity_count: int
    required_future_audit_reason_count: int
    required_future_idempotency_key_count: int
    required_future_immutable_event_count: int
    required_future_post_action_consistency_check_count: int
    mutation_boundary: ManualReviewMutationBoundaryLock
    future_transition_prerequisites: tuple[ManualReviewFutureTransitionPrerequisite, ...]
    owner_review_guardrail_labels: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ManualReviewQueueItem:
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
    decision_readiness: ManualReviewDecisionReadiness
    action_preflight: ManualReviewActionPreflight
    future_action_preview: ManualReviewFutureActionPreview
    command_contract: ManualReviewCommandContract
    audit_ledger_dry_run: ManualReviewAuditLedgerDryRun
    command_validation: ManualReviewCommandValidation
    permission_readiness: ManualReviewPermissionReadiness
    evidence_references: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ManualReviewQueueReadModel:
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
    status_counts: tuple[CountBucket, ...]
    reason_counts: tuple[CountBucket, ...]
    severity_counts: tuple[CountBucket, ...]
    group_counts: tuple[CountBucket, ...]
    decision_readiness_counts: tuple[CountBucket, ...]
    action_preflight_counts: tuple[CountBucket, ...]
    future_action_preview_counts: tuple[CountBucket, ...]
    command_contract_counts: tuple[CountBucket, ...]
    audit_ledger_dry_run_counts: tuple[CountBucket, ...]
    command_validation_counts: tuple[CountBucket, ...]
    permission_readiness_counts: tuple[CountBucket, ...]
    execution_readiness_audit: ManualReviewExecutionReadinessAudit
    age_bucket_counts: tuple[CountBucket, ...]
    audit_correlation_count: int
    taxonomy_metadata: ManualReviewTaxonomyMetadata
    available_filters: tuple[ManualReviewFilterOption, ...]
    sort_options: tuple[ManualReviewSortOption, ...]
    result_window_metadata: ManualReviewResultWindowMetadata
    items: tuple[ManualReviewQueueItem, ...]


@dataclass(frozen=True, slots=True)
class ManualReviewReasonEvidenceContext:
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


@dataclass(frozen=True, slots=True)
class ManualReviewDetailLinkedEntityContext:
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


@dataclass(frozen=True, slots=True)
class ManualReviewDetailReadModel:
    generated_at: datetime
    review_item: ManualReviewQueueItem
    reason_context: ManualReviewReasonEvidenceContext
    decision_readiness: ManualReviewDecisionReadiness
    action_preflight: ManualReviewActionPreflight
    future_action_preview: ManualReviewFutureActionPreview
    command_contract: ManualReviewCommandContract
    audit_ledger_dry_run: ManualReviewAuditLedgerDryRun
    command_validation: ManualReviewCommandValidation
    permission_readiness: ManualReviewPermissionReadiness
    linked_entity_context: ManualReviewDetailLinkedEntityContext
    data_gap_counts: tuple[CountBucket, ...]
    audit_correlation_ids: tuple[str, ...]
    taxonomy_metadata: ManualReviewTaxonomyMetadata
    timeline_summary: OperationalEventTimelineSummary


@dataclass(frozen=True, slots=True)
class WaterEmergencyEquipmentSummary:
    equipment_onsite_count: int
    moisture_tracking_required_count: int
    work_orders_with_equipment_notes_count: int
    records_missing_equipment_context_count: int
    inventory_entity_available: bool
    unknown_counts: tuple[CountBucket, ...]


@dataclass(frozen=True, slots=True)
class WaterEmergencyVisitChainSummary:
    total_visits: int
    multi_visit_record_count: int
    open_records_without_visits_count: int
    scheduled_visit_count: int
    completed_visit_count: int
    visit_status_counts: tuple[CountBucket, ...]


@dataclass(frozen=True, slots=True)
class WaterEmergencyDryingStageSummary:
    stage_counts: tuple[CountBucket, ...]
    active_stage_counts: tuple[CountBucket, ...]
    missing_stage_count: int
    moisture_tracking_required_count: int


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
class WaterEmergencyJobReference:
    job_id: UUID
    job_type: str | None
    status: str
    review_status: str | None
    priority: str | None
    requested_date: date | None
    scheduled_date: date | None
    source_system: str | None
    source_event_id: str | None


@dataclass(frozen=True, slots=True)
class WaterEmergencyWorkOrderReference:
    work_order_id: UUID
    work_order_number: str | None
    status: str
    dispatch_status: str | None
    assigned_technician_id: UUID | None
    audit_correlation_id: str | None


@dataclass(frozen=True, slots=True)
class WaterEmergencyVisitReference:
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


@dataclass(frozen=True, slots=True)
class WaterEmergencyReviewIndicator:
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


@dataclass(frozen=True, slots=True)
class WaterEmergencyEquipmentNote:
    work_order_id: UUID
    required_equipment_notes: str


@dataclass(frozen=True, slots=True)
class WaterEmergencyDetailEquipmentContext:
    equipment_onsite: bool
    moisture_tracking_required: bool
    inventory_entity_available: bool
    required_equipment_notes: tuple[WaterEmergencyEquipmentNote, ...]
    unknown_indicators: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class WaterEmergencyVisitChain:
    total_visits: int
    completed_visit_count: int
    open_visit_count: int
    first_visit_at: datetime | None
    latest_visit_at: datetime | None
    next_scheduled_visit_at: datetime | None
    visit_status_counts: tuple[CountBucket, ...]


@dataclass(frozen=True, slots=True)
class WaterEmergencyDetailDryingStageContext:
    status: str
    current_stage: str | None
    next_required_action: str | None
    moisture_tracking_required: bool
    missing_indicators: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class WaterEmergencyReviewExceptionSummary:
    total_review_count: int
    open_review_count: int
    deferred_review_count: int
    resolved_review_count: int
    archived_review_count: int
    critical_unresolved_count: int
    escalation_indicator_count: int
    review_reason_counts: tuple[CountBucket, ...]
    blocker_reason_counts: tuple[CountBucket, ...]
    unknown_counts: tuple[CountBucket, ...]
    review_item_ids: tuple[UUID, ...]
    audit_correlation_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class WaterEmergencyReviewExceptionContext:
    total_review_count: int
    open_review_count: int
    deferred_review_count: int
    resolved_review_count: int
    archived_review_count: int
    critical_unresolved_count: int
    escalation_indicator_count: int
    review_reason_counts: tuple[CountBucket, ...]
    blocker_reason_counts: tuple[CountBucket, ...]
    unknown_indicators: tuple[str, ...]
    review_item_ids: tuple[UUID, ...]
    audit_correlation_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class WaterEmergencyNextStepReadiness:
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


@dataclass(frozen=True, slots=True)
class WaterEmergencyNextStepReadinessSummary:
    total_records: int
    needs_attention_count: int
    closed_without_active_action_count: int
    label_counts: tuple[CountBucket, ...]
    blocker_counts: tuple[CountBucket, ...]
    records: tuple[WaterEmergencyNextStepReadiness, ...]


@dataclass(frozen=True, slots=True)
class WaterEmergencyQueueItem:
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


@dataclass(frozen=True, slots=True)
class WaterEmergencyOperatorQueueSummary:
    total_records: int
    active_attention_count: int
    closed_or_resolved_count: int
    critical_attention_count: int
    queue_group_counts: tuple[CountBucket, ...]
    attention_label_counts: tuple[CountBucket, ...]
    items: tuple[WaterEmergencyQueueItem, ...]


@dataclass(frozen=True, slots=True)
class WaterEmergencyAgingFollowUpItem:
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


@dataclass(frozen=True, slots=True)
class WaterEmergencyAgingFollowUpSummary:
    total_records: int
    active_timing_risk_count: int
    closed_or_resolved_count: int
    followup_due_count: int
    followup_overdue_count: int
    stale_evidence_count: int
    unknown_timing_count: int
    label_counts: tuple[CountBucket, ...]
    age_bucket_counts: tuple[CountBucket, ...]
    followup_bucket_counts: tuple[CountBucket, ...]
    items: tuple[WaterEmergencyAgingFollowUpItem, ...]


@dataclass(frozen=True, slots=True)
class WaterEmergencyFilterOption:
    key: str
    label: str
    count: int
    description: str


@dataclass(frozen=True, slots=True)
class WaterEmergencySortOption:
    key: str
    label: str
    description: str


@dataclass(frozen=True, slots=True)
class WaterEmergencyViewStateItem:
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


@dataclass(frozen=True, slots=True)
class WaterEmergencyViewStateSummary:
    total_records: int
    active_record_count: int
    closed_or_resolved_count: int
    available_filters: tuple[WaterEmergencyFilterOption, ...]
    sort_options: tuple[WaterEmergencySortOption, ...]
    group_counts: tuple[CountBucket, ...]
    items: tuple[WaterEmergencyViewStateItem, ...]


@dataclass(frozen=True, slots=True)
class WaterEmergencyGovernanceMetadataItem:
    key: str
    label: str
    category: str
    source: str
    randall_authorized_phase_0_baseline: bool
    legal_or_insurance_policy: bool
    requires_alfonso_owner_review: bool
    reason: str


@dataclass(frozen=True, slots=True)
class WaterEmergencyGovernanceMetadata:
    randall_authorized_phase_0_baseline: bool
    source: str
    legal_or_insurance_policy: bool
    requires_alfonso_owner_review: bool
    baseline_note: str
    timing_heuristic_note: str
    provisional_filter_groups: tuple[WaterEmergencyGovernanceMetadataItem, ...]
    provisional_attention_labels: tuple[WaterEmergencyGovernanceMetadataItem, ...]
    provisional_timing_labels: tuple[WaterEmergencyGovernanceMetadataItem, ...]
    provisional_readiness_labels: tuple[WaterEmergencyGovernanceMetadataItem, ...]
    owner_review_required_items: tuple[WaterEmergencyGovernanceMetadataItem, ...]
    future_role_visibility_roles: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class WaterEmergencyResultWindowMetadata:
    total_count: int
    visible_count: int
    result_limit: int
    has_more: bool
    sort_key: str
    generated_at: datetime


@dataclass(frozen=True, slots=True)
class WaterEmergencyDetailReadModel:
    generated_at: datetime
    record: WaterEmergencyRecordSummary
    job: WaterEmergencyJobReference | None
    work_orders: tuple[WaterEmergencyWorkOrderReference, ...]
    visits: tuple[WaterEmergencyVisitReference, ...]
    review_indicators: tuple[WaterEmergencyReviewIndicator, ...]
    equipment_context: WaterEmergencyDetailEquipmentContext
    visit_chain: WaterEmergencyVisitChain
    drying_stage_context: WaterEmergencyDetailDryingStageContext
    review_exception_context: WaterEmergencyReviewExceptionContext
    next_step_readiness: WaterEmergencyNextStepReadiness
    data_gap_counts: tuple[CountBucket, ...]
    audit_correlation_ids: tuple[str, ...]
    timeline_summary: OperationalEventTimelineSummary


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
    equipment_summary: WaterEmergencyEquipmentSummary
    visit_chain_summary: WaterEmergencyVisitChainSummary
    drying_stage_summary: WaterEmergencyDryingStageSummary
    review_exception_summary: WaterEmergencyReviewExceptionSummary
    next_step_summary: WaterEmergencyNextStepReadinessSummary
    operator_queue_summary: WaterEmergencyOperatorQueueSummary
    aging_followup_summary: WaterEmergencyAgingFollowUpSummary
    view_state_summary: WaterEmergencyViewStateSummary
    governance_metadata: WaterEmergencyGovernanceMetadata
    result_window_metadata: WaterEmergencyResultWindowMetadata
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
