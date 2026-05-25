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


class ManualReviewSafetyGateResponse(DashboardSchema):
    key: str
    label: str
    passed: bool
    required: bool
    reason: str


class ManualReviewCommandValidationResponse(DashboardSchema):
    label: str
    summary: str
    candidate_future_command_type: str
    validation_status: str
    validation_blockers: tuple[str, ...]
    validation_warnings: tuple[str, ...]
    safety_gates: tuple[ManualReviewSafetyGateResponse, ...]
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


class ManualReviewPermissionReadinessResponse(DashboardSchema):
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


class AuthBoundaryOperatorIdentityFieldResponse(DashboardSchema):
    key: str
    label: str
    required_for_future_actions: bool
    persisted_now: bool
    sensitive: bool
    reason: str


class AuthBoundaryRoleCatalogItemResponse(DashboardSchema):
    key: str
    label: str
    phase: str
    manual_review_action_allowed_now: bool
    manual_review_action_allowed_future: bool
    is_service_account_role: bool
    requires_future_authorization: bool
    reason: str


class AuthBoundaryPermissionCatalogItemResponse(DashboardSchema):
    key: str
    label: str
    category: str
    current_enforced: bool
    future_planning_only: bool
    authorizes_actions_now: bool
    reason: str


class AuthConfigurationVariableResponse(DashboardSchema):
    name: str
    scope: str
    safe_placeholder: str
    required_for_future_auth: bool
    contains_secret: bool
    committed_placeholder_allowed: bool
    real_value_must_not_be_committed: bool
    reason: str


class AuthDiagnosticCheckResponse(DashboardSchema):
    key: str
    label: str
    passed: bool
    severity: str
    reason: str


class AuthClaimContractResponse(DashboardSchema):
    key: str
    label: str
    claim_name: str
    required_for_future_auth: bool
    configured_now: bool
    sensitive: bool
    reason: str


class AuthRoleResolutionRuleResponse(DashboardSchema):
    key: str
    label: str
    input_role: str
    resolved_role: str
    manual_review_action_allowed_now: bool
    manual_review_action_allowed_future: bool
    blocked_for_manual_review_actions: bool
    requires_future_rbac: bool
    reason: str


class AuthClaimsExampleFixtureResponse(DashboardSchema):
    key: str
    label: str
    email_domain: str
    roles: tuple[str, ...]
    permissions: tuple[str, ...]
    contains_real_user_data: bool
    contains_token: bool
    contains_secret: bool
    reason: str


class ManualReviewAuthRuntimeSafetyDiagnosticsResponse(DashboardSchema):
    summary: str
    auth_enabled: bool
    auth_provider: str
    auth_provider_configured: bool
    token_verification_enabled: bool
    rbac_enforcement_enabled: bool
    login_ui_available: bool
    auth_headers_required: bool
    auth_headers_emitted_by_frontend: bool
    real_credentials_required_for_future_auth: bool
    committed_credentials_allowed: bool
    service_account_json_tracked: bool
    env_file_tracked: bool
    env_local_file_tracked: bool
    private_key_detected: bool
    placeholder_values_only: bool
    local_dev_auth_mode: str
    runtime_auth_mode: str
    future_provider_selection_required: bool
    randall_controls_provider_configuration: bool
    alfonso_owner_review_required_for_legal_policy: bool
    secret_hygiene_helper: str
    diagnostic_checks: tuple[AuthDiagnosticCheckResponse, ...]


class ManualReviewAuthConfigurationReadinessResponse(DashboardSchema):
    summary: str
    auth_provider_configured: bool
    auth_provider: str
    token_verification_enabled: bool
    rbac_enforcement_enabled: bool
    login_ui_available: bool
    frontend_auth_config_available: bool
    real_credentials_required: bool
    committed_credentials_allowed: bool
    local_dev_auth_mode: str
    future_provider_selection_required: bool
    randall_controls_provider_configuration: bool
    alfonso_owner_review_required_for_legal_policy: bool
    backend_variables: tuple[AuthConfigurationVariableResponse, ...]
    frontend_variables: tuple[AuthConfigurationVariableResponse, ...]
    provider_options: tuple[str, ...]
    runtime_safety_diagnostics: ManualReviewAuthRuntimeSafetyDiagnosticsResponse


class ManualReviewAuthClaimsMappingReadinessResponse(DashboardSchema):
    summary: str
    token_verification_dry_run_available: bool
    token_verification_enabled: bool
    real_token_parsing_enabled: bool
    jwks_fetch_enabled: bool
    auth_headers_required: bool
    auth_headers_emitted_by_frontend: bool
    claim_mapping_configured: bool
    role_claim_configured: bool
    permission_claim_configured: bool
    required_claims_documented: bool
    example_claim_fixture_available: bool
    example_claim_fixture_contains_real_user_data: bool
    service_account_block_rule_documented: bool
    technician_block_rule_documented: bool
    future_auth_required_before_actions: bool
    future_rbac_required_before_actions: bool
    claim_contracts: tuple[AuthClaimContractResponse, ...]
    role_resolution_rules: tuple[AuthRoleResolutionRuleResponse, ...]
    example_claim_fixtures: tuple[AuthClaimsExampleFixtureResponse, ...]


class ManualReviewAuthBoundaryReadinessResponse(DashboardSchema):
    summary: str
    auth_implemented: bool
    rbac_enforced: bool
    login_ui_available: bool
    action_execution_available: bool
    operator_identity_registry_available: bool
    operator_identity_registry_mode: str
    role_catalog_available: bool
    permission_catalog_available: bool
    service_accounts_blocked_for_manual_review_actions: bool
    future_auth_required_before_actions: bool
    future_rbac_required_before_actions: bool
    future_audit_actor_required_before_actions: bool
    production_credentials_required_for_real_auth: bool
    impersonation_allowed: bool
    service_account_allowed_for_manual_review_actions: bool
    operator_identity_fields: tuple[AuthBoundaryOperatorIdentityFieldResponse, ...]
    provisional_roles: tuple[AuthBoundaryRoleCatalogItemResponse, ...]
    future_permissions: tuple[AuthBoundaryPermissionCatalogItemResponse, ...]
    auth_configuration_readiness: ManualReviewAuthConfigurationReadinessResponse
    auth_claims_mapping_readiness: ManualReviewAuthClaimsMappingReadinessResponse


class ManualReviewMutationBoundaryLockResponse(DashboardSchema):
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


class ManualReviewFutureTransitionPrerequisiteResponse(DashboardSchema):
    key: str
    label: str
    category: str
    status: str
    requires_alfonso_owner_review: bool
    reason: str


class ManualReviewExecutionReadinessAuditResponse(DashboardSchema):
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
    mutation_boundary: ManualReviewMutationBoundaryLockResponse
    future_transition_prerequisites: tuple[ManualReviewFutureTransitionPrerequisiteResponse, ...]
    owner_review_guardrail_labels: tuple[str, ...]


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
    command_validation: ManualReviewCommandValidationResponse
    permission_readiness: ManualReviewPermissionReadinessResponse
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
    command_validation_counts: tuple[CountBucketResponse, ...]
    permission_readiness_counts: tuple[CountBucketResponse, ...]
    execution_readiness_audit: ManualReviewExecutionReadinessAuditResponse
    auth_boundary_readiness: ManualReviewAuthBoundaryReadinessResponse
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
    command_validation: ManualReviewCommandValidationResponse
    permission_readiness: ManualReviewPermissionReadinessResponse
    auth_boundary_readiness: ManualReviewAuthBoundaryReadinessResponse
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
