export type CountBucket = {
  label: string;
  count: number;
};

export type OperationalDashboardSummaryResponse = {
  total_jobs: number;
  total_work_orders: number;
  total_visits: number;
  total_route_assignments: number;
  open_manual_reviews: number;
  blocked_operations: number;
  escalation_indicators: number;
  open_water_emergencies: number;
  audit_correlation_count: number;
};

export type DispatchLifecycleSummaryResponse = {
  intake_lifecycle_counts: CountBucket[];
  job_status_counts: CountBucket[];
  work_order_status_counts: CountBucket[];
  visit_status_counts: CountBucket[];
  route_status_counts: CountBucket[];
  dispatch_execution_state_counts: CountBucket[];
  dispatch_ready_visits: number;
  dispatched_route_assignments: number;
  water_emergency_records: number;
  water_emergency_separated_intake: number;
  blocker_count: number;
};

export type ManualReviewSummaryResponse = {
  total_items: number;
  open_items: number;
  deferred_items: number;
  resolved_items: number;
  archived_items: number;
  severity_counts: CountBucket[];
  reason_counts: CountBucket[];
  escalation_indicators: number;
  audit_correlation_count: number;
};

export type ManualReviewTaxonomyMetadataItemResponse = {
  key: string;
  label: string;
  category: string;
  source: string;
  randall_authorized_phase_0_baseline: boolean;
  legal_or_insurance_policy: boolean;
  requires_alfonso_owner_review: boolean;
  reason: string;
};

export type ManualReviewTaxonomyMetadataResponse = {
  randall_authorized_phase_0_baseline: boolean;
  source: string;
  legal_or_insurance_policy: boolean;
  requires_alfonso_owner_review: boolean;
  baseline_note: string;
  group_definitions: ManualReviewTaxonomyMetadataItemResponse[];
};

export type ManualReviewFilterOptionResponse = {
  key: string;
  label: string;
  count: number;
  description: string;
};

export type ManualReviewSortOptionResponse = {
  key: string;
  label: string;
  description: string;
};

export type ManualReviewResultWindowMetadataResponse = {
  total_count: number;
  visible_count: number;
  result_limit: number;
  has_more: boolean;
  sort_key: string;
  generated_at: string;
};

export type ManualReviewDecisionReadinessResponse = {
  label: string;
  summary: string;
  reason_codes: string[];
  evidence_references: string[];
  is_active_decision_need: boolean;
  is_resolution_candidate: boolean;
};

export type ManualReviewActionPreflightResponse = {
  label: string;
  summary: string;
  blocker_codes: string[];
  required_future_controls: string[];
  evidence_references: string[];
  is_currently_executable: boolean;
  requires_operator_identity: boolean;
  requires_audit_reason: boolean;
};

export type ManualReviewFutureActionPreviewResponse = {
  label: string;
  description: string;
  expected_outcome_summary: string;
  impacted_entity_summary: string;
  impacted_entity_references: string[];
  blocker_codes: string[];
  required_future_controls: string[];
  evidence_references: string[];
  is_currently_executable: boolean;
  requires_operator_identity: boolean;
  requires_audit_reason: boolean;
};

export type ManualReviewCommandContractResponse = {
  label: string;
  summary: string;
  future_command_candidates: string[];
  required_contract_labels: string[];
  impacted_entity_summary: string;
  impacted_entity_references: string[];
  blocker_codes: string[];
  evidence_references: string[];
  is_currently_executable: boolean;
  not_executable_reason: string;
  requires_operator_identity: boolean;
  requires_role_authorization: boolean;
  requires_audit_reason: boolean;
  requires_idempotency_key: boolean;
  requires_immutable_event_recording: boolean;
  requires_post_action_consistency_check: boolean;
};

export type ManualReviewAuditLedgerDryRunResponse = {
  label: string;
  summary: string;
  future_command_type_candidates: string[];
  required_labels: string[];
  proposed_future_event_type: string;
  proposed_future_event_state: string;
  proposed_future_audit_envelope_fields: string[];
  proposed_future_idempotency_scope: string;
  proposed_future_consistency_check_summary: string;
  audit_correlation_references: string[];
  evidence_references: string[];
  is_currently_executable: boolean;
  phase_allows_execution: boolean;
  execution_unavailable_reason: string;
  requires_operator_identity: boolean;
  requires_role_authorization: boolean;
  requires_audit_reason: boolean;
  requires_idempotency_key: boolean;
  requires_immutable_event_recording: boolean;
  requires_post_action_consistency_check: boolean;
};

export type ManualReviewSafetyGateResponse = {
  key: string;
  label: string;
  passed: boolean;
  required: boolean;
  reason: string;
};

export type ManualReviewCommandValidationResponse = {
  label: string;
  summary: string;
  candidate_future_command_type: string;
  validation_status: string;
  validation_blockers: string[];
  validation_warnings: string[];
  safety_gates: ManualReviewSafetyGateResponse[];
  audit_correlation_references: string[];
  evidence_references: string[];
  is_currently_executable: boolean;
  phase_allows_execution: boolean;
  execution_unavailable_reason: string;
  requires_audit_reason: boolean;
  requires_operator_identity: boolean;
  requires_role_authorization: boolean;
  requires_idempotency_key: boolean;
  requires_immutable_event_recording: boolean;
  requires_post_action_consistency_check: boolean;
  requires_water_emergency_scope_check: boolean;
  requires_linked_entity_context: boolean;
};

export type ManualReviewPermissionReadinessResponse = {
  label: string;
  summary: string;
  candidate_future_command_type: string;
  future_required_roles: string[];
  future_forbidden_roles: string[];
  future_required_permissions: string[];
  required_permission_labels: string[];
  identity_requirement_labels: string[];
  audit_correlation_references: string[];
  evidence_references: string[];
  is_currently_executable: boolean;
  phase_allows_execution: boolean;
  execution_unavailable_reason: string;
  identity_unavailable_reason: string;
  future_operator_identity_required: boolean;
  future_operator_id_required: boolean;
  future_operator_display_name_required: boolean;
  future_operator_email_required: boolean;
  future_authentication_provider_boundary: string;
  future_role_authorization_required: boolean;
  future_permission_set_required: boolean;
  future_audit_actor_required: boolean;
  future_audit_reason_required: boolean;
  future_idempotency_key_required: boolean;
  future_immutable_event_required: boolean;
  future_post_action_consistency_check_required: boolean;
  impersonation_allowed: boolean;
  service_account_allowed: boolean;
  technician_action_allowed: boolean;
  requires_water_emergency_scope_check: boolean;
};

export type AuthBoundaryOperatorIdentityFieldResponse = {
  key: string;
  label: string;
  required_for_future_actions: boolean;
  persisted_now: boolean;
  sensitive: boolean;
  reason: string;
};

export type AuthBoundaryRoleCatalogItemResponse = {
  key: string;
  label: string;
  phase: string;
  manual_review_action_allowed_now: boolean;
  manual_review_action_allowed_future: boolean;
  is_service_account_role: boolean;
  requires_future_authorization: boolean;
  reason: string;
};

export type AuthBoundaryPermissionCatalogItemResponse = {
  key: string;
  label: string;
  category: string;
  current_enforced: boolean;
  future_planning_only: boolean;
  authorizes_actions_now: boolean;
  reason: string;
};

export type AuthConfigurationVariableResponse = {
  name: string;
  scope: string;
  safe_placeholder: string;
  required_for_future_auth: boolean;
  contains_secret: boolean;
  committed_placeholder_allowed: boolean;
  real_value_must_not_be_committed: boolean;
  reason: string;
};

export type AuthDiagnosticCheckResponse = {
  key: string;
  label: string;
  passed: boolean;
  severity: string;
  reason: string;
};

export type AuthClaimContractResponse = {
  key: string;
  label: string;
  claim_name: string;
  required_for_future_auth: boolean;
  configured_now: boolean;
  sensitive: boolean;
  reason: string;
};

export type AuthRoleResolutionRuleResponse = {
  key: string;
  label: string;
  input_role: string;
  resolved_role: string;
  manual_review_action_allowed_now: boolean;
  manual_review_action_allowed_future: boolean;
  blocked_for_manual_review_actions: boolean;
  requires_future_rbac: boolean;
  reason: string;
};

export type AuthClaimsExampleFixtureResponse = {
  key: string;
  label: string;
  email_domain: string;
  roles: string[];
  permissions: string[];
  contains_real_user_data: boolean;
  contains_token: boolean;
  contains_secret: boolean;
  reason: string;
};

export type ManualReviewAuthRuntimeSafetyDiagnosticsResponse = {
  summary: string;
  auth_enabled: boolean;
  auth_provider: string;
  auth_provider_configured: boolean;
  token_verification_enabled: boolean;
  rbac_enforcement_enabled: boolean;
  login_ui_available: boolean;
  auth_headers_required: boolean;
  auth_headers_emitted_by_frontend: boolean;
  real_credentials_required_for_future_auth: boolean;
  committed_credentials_allowed: boolean;
  service_account_json_tracked: boolean;
  env_file_tracked: boolean;
  env_local_file_tracked: boolean;
  private_key_detected: boolean;
  placeholder_values_only: boolean;
  local_dev_auth_mode: string;
  runtime_auth_mode: string;
  future_provider_selection_required: boolean;
  randall_controls_provider_configuration: boolean;
  alfonso_owner_review_required_for_legal_policy: boolean;
  secret_hygiene_helper: string;
  diagnostic_checks: AuthDiagnosticCheckResponse[];
};

export type ManualReviewAuthConfigurationReadinessResponse = {
  summary: string;
  auth_provider_configured: boolean;
  auth_provider: string;
  token_verification_enabled: boolean;
  rbac_enforcement_enabled: boolean;
  login_ui_available: boolean;
  frontend_auth_config_available: boolean;
  real_credentials_required: boolean;
  committed_credentials_allowed: boolean;
  local_dev_auth_mode: string;
  future_provider_selection_required: boolean;
  randall_controls_provider_configuration: boolean;
  alfonso_owner_review_required_for_legal_policy: boolean;
  backend_variables: AuthConfigurationVariableResponse[];
  frontend_variables: AuthConfigurationVariableResponse[];
  provider_options: string[];
  runtime_safety_diagnostics: ManualReviewAuthRuntimeSafetyDiagnosticsResponse;
};

export type ManualReviewAuthClaimsMappingReadinessResponse = {
  summary: string;
  token_verification_dry_run_available: boolean;
  token_verification_enabled: boolean;
  real_token_parsing_enabled: boolean;
  jwks_fetch_enabled: boolean;
  auth_headers_required: boolean;
  auth_headers_emitted_by_frontend: boolean;
  claim_mapping_configured: boolean;
  role_claim_configured: boolean;
  permission_claim_configured: boolean;
  required_claims_documented: boolean;
  example_claim_fixture_available: boolean;
  example_claim_fixture_contains_real_user_data: boolean;
  service_account_block_rule_documented: boolean;
  technician_block_rule_documented: boolean;
  future_auth_required_before_actions: boolean;
  future_rbac_required_before_actions: boolean;
  claim_contracts: AuthClaimContractResponse[];
  role_resolution_rules: AuthRoleResolutionRuleResponse[];
  example_claim_fixtures: AuthClaimsExampleFixtureResponse[];
};

export type RouteProtectionMatrixItemResponse = {
  route_or_section_key: string;
  label: string;
  type: "api_route" | "frontend_page" | "frontend_section" | "future_action";
  route_or_section: string;
  currently_public_in_phase_0: boolean;
  future_auth_required: boolean;
  future_rbac_required: boolean;
  future_required_roles: string[];
  future_required_permissions: string[];
  future_denied_roles: string[];
  water_emergency_sensitive: boolean;
  manual_review_sensitive: boolean;
  mutation_sensitive: boolean;
  owner_review_required_if_legal_or_insurance: boolean;
  enforcement_enabled: boolean;
  phase_allows_enforcement: boolean;
  reason: string;
};

export type AccessDecisionDryRunResponse = {
  summary: string;
  access_decision_dry_run_enabled: boolean;
  enforcement_enabled: boolean;
  phase_allows_enforcement: boolean;
  token_verification_enabled: boolean;
  rbac_enforcement_enabled: boolean;
  route_guarding_enabled: boolean;
  simulated_decisions_only: boolean;
  currently_denied_by_auth: boolean;
  currently_denied_by_rbac: boolean;
  future_auth_required_count: number;
  future_rbac_required_count: number;
  future_manual_review_protected_surface_count: number;
  future_water_emergency_protected_surface_count: number;
  future_mutation_surface_count: number;
  unknown_permission_mapping_count: number;
};

export type ManualReviewRouteProtectionReadinessResponse = {
  summary: string;
  route_protection_matrix_available: boolean;
  access_decision_dry_run: AccessDecisionDryRunResponse;
  matrix_items: RouteProtectionMatrixItemResponse[];
};

export type AuthRbacEnforcementBoundaryLockResponse = {
  auth_enforcement_enabled: boolean;
  token_verification_enabled: boolean;
  real_token_parsing_enabled: boolean;
  jwks_fetch_enabled: boolean;
  rbac_enforcement_enabled: boolean;
  route_guarding_enabled: boolean;
  login_ui_available: boolean;
  user_management_available: boolean;
  action_execution_available: boolean;
  mutation_endpoints_available: boolean;
  phase_allows_auth_enforcement: boolean;
  phase_allows_rbac_enforcement: boolean;
  phase_allows_route_guarding: boolean;
  phase_allows_manual_review_actions: boolean;
};

export type AuthRbacTransitionPrerequisiteResponse = {
  key: string;
  label: string;
  blocker_group: string;
  status: string;
  satisfied_now: boolean;
  requires_alfonso_owner_review: boolean;
  reason: string;
};

export type AuthRbacReadinessAuditResponse = {
  summary: string;
  auth_implemented: boolean;
  auth_enabled: boolean;
  token_verification_enabled: boolean;
  real_token_parsing_enabled: boolean;
  jwks_fetch_enabled: boolean;
  rbac_enforced: boolean;
  route_guarding_enabled: boolean;
  login_ui_available: boolean;
  auth_headers_required: boolean;
  auth_headers_emitted_by_frontend: boolean;
  operator_identity_registry_available: boolean;
  role_catalog_available: boolean;
  permission_catalog_available: boolean;
  claims_mapping_available: boolean;
  route_protection_matrix_available: boolean;
  access_decision_dry_run_available: boolean;
  auth_core_module_available: boolean;
  disabled_token_verifier_available: boolean;
  optional_auth_context_available: boolean;
  token_verification_result: string;
  route_protection_enforced: boolean;
  current_routes_require_auth: boolean;
  secret_hygiene_helper_available: boolean;
  committed_credentials_allowed: boolean;
  service_account_manual_review_allowed: boolean;
  technician_manual_review_action_allowed: boolean;
  future_auth_required_before_actions: boolean;
  future_rbac_required_before_actions: boolean;
  future_audit_actor_required_before_actions: boolean;
  future_provider_selection_required: boolean;
  future_real_credentials_required: boolean;
  route_protection_enforcement_required_before_actions: boolean;
  manual_review_action_execution_available: boolean;
  water_emergency_action_execution_available: boolean;
  manual_review_action_authority_granted: boolean;
  water_emergency_action_authority_granted: boolean;
  readiness_gap_count: number;
  owner_review_required_count: number;
  enforcement_boundary_lock: AuthRbacEnforcementBoundaryLockResponse;
  future_transition_prerequisites: AuthRbacTransitionPrerequisiteResponse[];
};

export type ManualReviewAuthBoundaryReadinessResponse = {
  summary: string;
  auth_implemented: boolean;
  rbac_enforced: boolean;
  login_ui_available: boolean;
  action_execution_available: boolean;
  operator_identity_registry_available: boolean;
  operator_identity_registry_mode: string;
  role_catalog_available: boolean;
  permission_catalog_available: boolean;
  service_accounts_blocked_for_manual_review_actions: boolean;
  future_auth_required_before_actions: boolean;
  future_rbac_required_before_actions: boolean;
  future_audit_actor_required_before_actions: boolean;
  production_credentials_required_for_real_auth: boolean;
  impersonation_allowed: boolean;
  service_account_allowed_for_manual_review_actions: boolean;
  operator_identity_fields: AuthBoundaryOperatorIdentityFieldResponse[];
  provisional_roles: AuthBoundaryRoleCatalogItemResponse[];
  future_permissions: AuthBoundaryPermissionCatalogItemResponse[];
  auth_configuration_readiness: ManualReviewAuthConfigurationReadinessResponse;
  auth_claims_mapping_readiness: ManualReviewAuthClaimsMappingReadinessResponse;
  route_protection_readiness: ManualReviewRouteProtectionReadinessResponse;
  auth_rbac_readiness_audit: AuthRbacReadinessAuditResponse;
};

export type ManualReviewMutationBoundaryLockResponse = {
  manual_review_mutations_enabled: boolean;
  action_execution_phase: string;
  currently_executable_count: number;
  mutation_endpoints_available: boolean;
  auth_required_before_execution: boolean;
  rbac_required_before_execution: boolean;
  audit_envelope_required_before_execution: boolean;
  idempotency_required_before_execution: boolean;
  immutable_event_required_before_execution: boolean;
  post_action_consistency_required_before_execution: boolean;
};

export type ManualReviewFutureTransitionPrerequisiteResponse = {
  key: string;
  label: string;
  category: string;
  status: string;
  requires_alfonso_owner_review: boolean;
  reason: string;
};

export type ManualReviewExecutionReadinessAuditResponse = {
  summary: string;
  total_review_items: number;
  active_review_items: number;
  resolved_archived_review_items: number;
  water_emergency_related_review_items: number;
  dispatch_related_review_items: number;
  items_with_missing_entity_context: number;
  items_with_conflict_blockers: number;
  items_with_missing_data_blockers: number;
  items_with_future_action_preview_labels: number;
  items_with_command_contract_labels: number;
  items_with_dry_run_labels: number;
  items_with_safety_gate_matrix_labels: number;
  items_with_permission_readiness_labels: number;
  items_blocked_by_phase_execution: number;
  currently_executable_count: number;
  required_future_auth_count: number;
  required_future_rbac_count: number;
  required_future_operator_identity_count: number;
  required_future_audit_reason_count: number;
  required_future_idempotency_key_count: number;
  required_future_immutable_event_count: number;
  required_future_post_action_consistency_check_count: number;
  mutation_boundary: ManualReviewMutationBoundaryLockResponse;
  future_transition_prerequisites: ManualReviewFutureTransitionPrerequisiteResponse[];
  owner_review_guardrail_labels: string[];
};

export type ManualReviewQueueItemResponse = {
  review_item_id: string;
  status: string;
  severity: string | null;
  reason_code: string;
  visibility_groups: string[];
  primary_group: string;
  entity_type: string | null;
  entity_id: string | null;
  job_id: string | null;
  work_order_id: string | null;
  visit_id: string | null;
  route_assignment_id: string | null;
  water_emergency_id: string | null;
  created_at: string;
  updated_at: string;
  reviewed_at: string | null;
  deferred_until: string | null;
  resolved_at: string | null;
  age_bucket: string;
  age_hours: number | null;
  blocker_indicator: boolean;
  attention_indicator: boolean;
  confidence_score: number | null;
  recommended_action: string | null;
  audit_correlation_id: string | null;
  evidence_references: string[];
  decision_readiness: ManualReviewDecisionReadinessResponse;
  action_preflight: ManualReviewActionPreflightResponse;
  future_action_preview: ManualReviewFutureActionPreviewResponse;
  command_contract: ManualReviewCommandContractResponse;
  audit_ledger_dry_run: ManualReviewAuditLedgerDryRunResponse;
  command_validation: ManualReviewCommandValidationResponse;
  permission_readiness: ManualReviewPermissionReadinessResponse;
};

export type ManualReviewQueueResponse = {
  generated_at: string;
  total_items: number;
  open_items: number;
  deferred_items: number;
  resolved_items: number;
  archived_items: number;
  active_attention_count: number;
  water_emergency_related_count: number;
  dispatch_related_count: number;
  blocked_count: number;
  status_counts: CountBucket[];
  reason_counts: CountBucket[];
  severity_counts: CountBucket[];
  group_counts: CountBucket[];
  age_bucket_counts: CountBucket[];
  decision_readiness_counts: CountBucket[];
  action_preflight_counts: CountBucket[];
  future_action_preview_counts: CountBucket[];
  command_contract_counts: CountBucket[];
  audit_ledger_dry_run_counts: CountBucket[];
  command_validation_counts: CountBucket[];
  permission_readiness_counts: CountBucket[];
  execution_readiness_audit: ManualReviewExecutionReadinessAuditResponse;
  auth_boundary_readiness: ManualReviewAuthBoundaryReadinessResponse;
  audit_correlation_count: number;
  taxonomy_metadata: ManualReviewTaxonomyMetadataResponse;
  available_filters: ManualReviewFilterOptionResponse[];
  sort_options: ManualReviewSortOptionResponse[];
  result_window_metadata: ManualReviewResultWindowMetadataResponse;
  items: ManualReviewQueueItemResponse[];
};

export type ManualReviewReasonEvidenceContextResponse = {
  reason_code: string;
  status: string;
  severity: string | null;
  confidence_score: number | null;
  recommended_action: string | null;
  review_reason_codes: string[];
  snapshot_keys: string[];
  blocker_indicator: boolean;
  attention_indicator: boolean;
  evidence_references: string[];
};

export type ManualReviewDetailLinkedEntityContextResponse = {
  entity_type: string | null;
  entity_id: string | null;
  job_id: string | null;
  job_status: string | null;
  job_type: string | null;
  work_order_id: string | null;
  work_order_status: string | null;
  visit_id: string | null;
  visit_status: string | null;
  route_assignment_id: string | null;
  route_assignment_status: string | null;
  water_emergency_id: string | null;
  water_emergency_status: string | null;
  water_emergency_stage: string | null;
  is_water_emergency_related: boolean;
  is_dispatch_related: boolean;
  unknown_indicators: string[];
  audit_correlation_ids: string[];
};

export type RouteAssignmentSummaryResponse = {
  total_assignments: number;
  status_counts: CountBucket[];
  region_counts: CountBucket[];
  time_window_counts: CountBucket[];
  authorization_state_counts: CountBucket[];
  dispatched_count: number;
  awaiting_dispatch_execution_count: number;
  blocked_count: number;
};

export type ExternalExecutionSummaryResponse = {
  adapter_state_counts: CountBucket[];
  execution_state_counts: CountBucket[];
  confirmation_state_counts: CountBucket[];
  prepared_count: number;
  execution_completed_count: number;
  execution_failed_count: number;
  confirmation_failed_count: number;
  retry_prepared_count: number;
  reconciliation_required_count: number;
};

export type ReconciliationRecoverySummaryResponse = {
  reconciliation_state_counts: CountBucket[];
  recovery_state_counts: CountBucket[];
  mismatch_count: number;
  divergence_count: number;
  replay_prepared_count: number;
  rollback_prepared_count: number;
  recovery_blocked_count: number;
};

export type GovernanceAccountabilitySummaryResponse = {
  governance_state_counts: CountBucket[];
  accountability_state_counts: CountBucket[];
  operator_approved_count: number;
  intervention_required_count: number;
  escalation_required_count: number;
  incident_prepared_count: number;
  accountability_blocked_count: number;
};

export type DashboardDispatchSummaryResponse = {
  route_assignments: RouteAssignmentSummaryResponse;
  external_execution: ExternalExecutionSummaryResponse;
  reconciliation_recovery: ReconciliationRecoverySummaryResponse;
  governance_accountability: GovernanceAccountabilitySummaryResponse;
};

export type OperationalTimelineEntryResponse = {
  occurred_at: string;
  event_type: string;
  event_state: string;
  entity_type: string;
  entity_id: string;
  route_assignment_id: string | null;
  visit_id: string | null;
  work_order_id: string | null;
  job_id: string | null;
  technician_id: string | null;
  audit_correlation_id: string;
  previous_state: string | null;
  new_state: string | null;
  is_immutable: boolean;
};

export type OperationalEventTimelineSummaryResponse = {
  total_events: number;
  returned_events: number;
  mutable_event_count: number;
  audit_correlation_ids: string[];
  entries: OperationalTimelineEntryResponse[];
};

export type WaterEmergencyRecordSummaryResponse = {
  water_emergency_id: string;
  job_id: string;
  status: string;
  drying_stage: string | null;
  next_required_action: string | null;
  is_open: boolean;
  equipment_onsite: boolean;
  moisture_tracking_required: boolean;
  opened_at: string | null;
  closed_at: string | null;
  related_work_order_ids: string[];
  related_visit_ids: string[];
  open_review_count: number;
  timeline_event_count: number;
  audit_correlation_ids: string[];
};

export type WaterEmergencyJobReferenceResponse = {
  job_id: string;
  job_type: string | null;
  status: string;
  review_status: string | null;
  priority: string | null;
  requested_date: string | null;
  scheduled_date: string | null;
  source_system: string | null;
  source_event_id: string | null;
};

export type WaterEmergencyWorkOrderReferenceResponse = {
  work_order_id: string;
  work_order_number: string | null;
  status: string;
  dispatch_status: string | null;
  assigned_technician_id: string | null;
  audit_correlation_id: string | null;
};

export type WaterEmergencyVisitReferenceResponse = {
  visit_id: string;
  work_order_id: string | null;
  technician_id: string | null;
  visit_type: string | null;
  status: string;
  scheduled_start_at: string | null;
  scheduled_end_at: string | null;
  arrived_at: string | null;
  completed_at: string | null;
  audit_correlation_id: string | null;
};

export type WaterEmergencyReviewIndicatorResponse = {
  review_item_id: string;
  status: string;
  severity: string | null;
  reason_code: string;
  confidence_score: number | null;
  entity_type: string | null;
  entity_id: string | null;
  job_id: string | null;
  visit_id: string | null;
  audit_correlation_id: string | null;
  recommended_action: string | null;
};

export type WaterEmergencyEquipmentSummaryResponse = {
  equipment_onsite_count: number;
  moisture_tracking_required_count: number;
  work_orders_with_equipment_notes_count: number;
  records_missing_equipment_context_count: number;
  inventory_entity_available: boolean;
  unknown_counts: CountBucket[];
};

export type WaterEmergencyVisitChainSummaryResponse = {
  total_visits: number;
  multi_visit_record_count: number;
  open_records_without_visits_count: number;
  scheduled_visit_count: number;
  completed_visit_count: number;
  visit_status_counts: CountBucket[];
};

export type WaterEmergencyDryingStageSummaryResponse = {
  stage_counts: CountBucket[];
  active_stage_counts: CountBucket[];
  missing_stage_count: number;
  moisture_tracking_required_count: number;
};

export type WaterEmergencyEquipmentNoteResponse = {
  work_order_id: string;
  required_equipment_notes: string;
};

export type WaterEmergencyDetailEquipmentContextResponse = {
  equipment_onsite: boolean;
  moisture_tracking_required: boolean;
  inventory_entity_available: boolean;
  required_equipment_notes: WaterEmergencyEquipmentNoteResponse[];
  unknown_indicators: string[];
};

export type WaterEmergencyVisitChainResponse = {
  total_visits: number;
  completed_visit_count: number;
  open_visit_count: number;
  first_visit_at: string | null;
  latest_visit_at: string | null;
  next_scheduled_visit_at: string | null;
  visit_status_counts: CountBucket[];
};

export type WaterEmergencyDetailDryingStageContextResponse = {
  status: string;
  current_stage: string | null;
  next_required_action: string | null;
  moisture_tracking_required: boolean;
  missing_indicators: string[];
};

export type WaterEmergencyReviewExceptionSummaryResponse = {
  total_review_count: number;
  open_review_count: number;
  deferred_review_count: number;
  resolved_review_count: number;
  archived_review_count: number;
  critical_unresolved_count: number;
  escalation_indicator_count: number;
  review_reason_counts: CountBucket[];
  blocker_reason_counts: CountBucket[];
  unknown_counts: CountBucket[];
  review_item_ids: string[];
  audit_correlation_ids: string[];
};

export type WaterEmergencyReviewExceptionContextResponse = {
  total_review_count: number;
  open_review_count: number;
  deferred_review_count: number;
  resolved_review_count: number;
  archived_review_count: number;
  critical_unresolved_count: number;
  escalation_indicator_count: number;
  review_reason_counts: CountBucket[];
  blocker_reason_counts: CountBucket[];
  unknown_indicators: string[];
  review_item_ids: string[];
  audit_correlation_ids: string[];
};

export type WaterEmergencyNextStepReadinessResponse = {
  water_emergency_id: string;
  primary_label: string;
  labels: string[];
  summary: string;
  reason_codes: string[];
  evidence_references: string[];
  current_status: string;
  current_stage: string | null;
  open_review_count: number;
  critical_alert_count: number;
  blocker_count: number;
  unknown_count: number;
  requires_operator_attention: boolean;
  related_job_id: string;
  related_work_order_ids: string[];
  related_visit_ids: string[];
  audit_correlation_ids: string[];
};

export type WaterEmergencyNextStepReadinessSummaryResponse = {
  total_records: number;
  needs_attention_count: number;
  closed_without_active_action_count: number;
  label_counts: CountBucket[];
  blocker_counts: CountBucket[];
  records: WaterEmergencyNextStepReadinessResponse[];
};

export type WaterEmergencyQueueItemResponse = {
  water_emergency_id: string;
  attention_label: string;
  queue_group: string;
  attention_rank: number;
  readiness_labels: string[];
  summary: string;
  reason_codes: string[];
  evidence_references: string[];
  current_status: string;
  current_stage: string | null;
  open_review_count: number;
  critical_alert_count: number;
  blocker_count: number;
  unknown_count: number;
  related_job_id: string;
  related_work_order_ids: string[];
  related_visit_ids: string[];
  audit_correlation_ids: string[];
};

export type WaterEmergencyOperatorQueueSummaryResponse = {
  total_records: number;
  active_attention_count: number;
  closed_or_resolved_count: number;
  critical_attention_count: number;
  queue_group_counts: CountBucket[];
  attention_label_counts: CountBucket[];
  items: WaterEmergencyQueueItemResponse[];
};

export type WaterEmergencyAgingFollowUpItemResponse = {
  water_emergency_id: string;
  time_sensitivity_label: string;
  timing_group: string;
  timing_rank: number;
  age_bucket: string;
  followup_bucket: string;
  age_hours: number | null;
  hours_since_last_visit: number | null;
  hours_since_last_review: number | null;
  hours_since_last_event: number | null;
  opened_at: string | null;
  last_visit_at: string | null;
  last_review_at: string | null;
  last_event_at: string | null;
  closed_at: string | null;
  summary: string;
  reason_codes: string[];
  missing_timestamp_indicators: string[];
  stale_indicator_count: number;
  requires_operator_attention: boolean;
  related_job_id: string;
  related_work_order_ids: string[];
  related_visit_ids: string[];
  audit_correlation_ids: string[];
  evidence_references: string[];
};

export type WaterEmergencyAgingFollowUpSummaryResponse = {
  total_records: number;
  active_timing_risk_count: number;
  closed_or_resolved_count: number;
  followup_due_count: number;
  followup_overdue_count: number;
  stale_evidence_count: number;
  unknown_timing_count: number;
  label_counts: CountBucket[];
  age_bucket_counts: CountBucket[];
  followup_bucket_counts: CountBucket[];
  items: WaterEmergencyAgingFollowUpItemResponse[];
};

export type WaterEmergencyFilterOptionResponse = {
  key: string;
  label: string;
  count: number;
  description: string;
};

export type WaterEmergencySortOptionResponse = {
  key: string;
  label: string;
  description: string;
};

export type WaterEmergencyViewStateItemResponse = {
  water_emergency_id: string;
  filter_groups: string[];
  primary_filter_group: string;
  sort_rank: number;
  sort_label: string;
  queue_group: string;
  attention_label: string;
  time_sensitivity_label: string;
  readiness_label: string;
  is_active: boolean;
  current_status: string;
  current_stage: string | null;
  open_review_count: number;
  critical_alert_count: number;
  blocker_count: number;
  unknown_count: number;
  last_activity_at: string | null;
  summary: string;
  reason_codes: string[];
  related_job_id: string;
  related_work_order_ids: string[];
  related_visit_ids: string[];
  audit_correlation_ids: string[];
  evidence_references: string[];
};

export type WaterEmergencyViewStateSummaryResponse = {
  total_records: number;
  active_record_count: number;
  closed_or_resolved_count: number;
  available_filters: WaterEmergencyFilterOptionResponse[];
  sort_options: WaterEmergencySortOptionResponse[];
  group_counts: CountBucket[];
  items: WaterEmergencyViewStateItemResponse[];
};

export type WaterEmergencyGovernanceMetadataItemResponse = {
  key: string;
  label: string;
  category: string;
  source: string;
  randall_authorized_phase_0_baseline: boolean;
  legal_or_insurance_policy: boolean;
  requires_alfonso_owner_review: boolean;
  reason: string;
};

export type WaterEmergencyGovernanceMetadataResponse = {
  randall_authorized_phase_0_baseline: boolean;
  source: string;
  legal_or_insurance_policy: boolean;
  requires_alfonso_owner_review: boolean;
  baseline_note: string;
  timing_heuristic_note: string;
  provisional_filter_groups: WaterEmergencyGovernanceMetadataItemResponse[];
  provisional_attention_labels: WaterEmergencyGovernanceMetadataItemResponse[];
  provisional_timing_labels: WaterEmergencyGovernanceMetadataItemResponse[];
  provisional_readiness_labels: WaterEmergencyGovernanceMetadataItemResponse[];
  owner_review_required_items: WaterEmergencyGovernanceMetadataItemResponse[];
  future_role_visibility_roles: string[];
};

export type WaterEmergencyResultWindowMetadataResponse = {
  total_count: number;
  visible_count: number;
  result_limit: number;
  has_more: boolean;
  sort_key: string;
  generated_at: string;
};

export type WaterEmergencyDashboardResponse = {
  generated_at: string;
  total_records: number;
  open_count: number;
  closed_count: number;
  status_counts: CountBucket[];
  stage_counts: CountBucket[];
  multi_visit_count: number;
  equipment_onsite_count: number;
  moisture_tracking_required_count: number;
  equipment_summary: WaterEmergencyEquipmentSummaryResponse;
  visit_chain_summary: WaterEmergencyVisitChainSummaryResponse;
  drying_stage_summary: WaterEmergencyDryingStageSummaryResponse;
  review_exception_summary: WaterEmergencyReviewExceptionSummaryResponse;
  next_step_summary: WaterEmergencyNextStepReadinessSummaryResponse;
  operator_queue_summary: WaterEmergencyOperatorQueueSummaryResponse;
  aging_followup_summary: WaterEmergencyAgingFollowUpSummaryResponse;
  view_state_summary: WaterEmergencyViewStateSummaryResponse;
  governance_metadata: WaterEmergencyGovernanceMetadataResponse;
  result_window_metadata: WaterEmergencyResultWindowMetadataResponse;
  related_job_count: number;
  related_work_order_count: number;
  related_visit_count: number;
  review_indicator_count: number;
  escalation_indicator_count: number;
  data_gap_counts: CountBucket[];
  audit_correlation_count: number;
  records: WaterEmergencyRecordSummaryResponse[];
  timeline_summary: OperationalEventTimelineSummaryResponse;
};

export type WaterEmergencyDetailResponse = {
  generated_at: string;
  record: WaterEmergencyRecordSummaryResponse;
  job: WaterEmergencyJobReferenceResponse | null;
  work_orders: WaterEmergencyWorkOrderReferenceResponse[];
  visits: WaterEmergencyVisitReferenceResponse[];
  review_indicators: WaterEmergencyReviewIndicatorResponse[];
  equipment_context: WaterEmergencyDetailEquipmentContextResponse;
  visit_chain: WaterEmergencyVisitChainResponse;
  drying_stage_context: WaterEmergencyDetailDryingStageContextResponse;
  review_exception_context: WaterEmergencyReviewExceptionContextResponse;
  next_step_readiness: WaterEmergencyNextStepReadinessResponse;
  data_gap_counts: CountBucket[];
  audit_correlation_ids: string[];
  timeline_summary: OperationalEventTimelineSummaryResponse;
};

export type ManualReviewDetailResponse = {
  generated_at: string;
  review_item: ManualReviewQueueItemResponse;
  reason_context: ManualReviewReasonEvidenceContextResponse;
  decision_readiness: ManualReviewDecisionReadinessResponse;
  action_preflight: ManualReviewActionPreflightResponse;
  future_action_preview: ManualReviewFutureActionPreviewResponse;
  command_contract: ManualReviewCommandContractResponse;
  audit_ledger_dry_run: ManualReviewAuditLedgerDryRunResponse;
  command_validation: ManualReviewCommandValidationResponse;
  permission_readiness: ManualReviewPermissionReadinessResponse;
  auth_boundary_readiness: ManualReviewAuthBoundaryReadinessResponse;
  linked_entity_context: ManualReviewDetailLinkedEntityContextResponse;
  data_gap_counts: CountBucket[];
  audit_correlation_ids: string[];
  taxonomy_metadata: ManualReviewTaxonomyMetadataResponse;
  timeline_summary: OperationalEventTimelineSummaryResponse;
};

export type DashboardOverviewResponse = {
  generated_at: string;
  operational_summary: OperationalDashboardSummaryResponse;
  lifecycle_summary: DispatchLifecycleSummaryResponse;
  manual_review_summary: ManualReviewSummaryResponse;
  dispatch_summary: DashboardDispatchSummaryResponse;
  timeline_summary: OperationalEventTimelineSummaryResponse;
};

export type AuthCutoverPrerequisiteResponse = {
  key: string;
  label: string;
  status: string;
  satisfied_now: boolean;
  owner_review_required: boolean;
  reason: string;
};

export type CurrentRouteAccessibilityAuditItemResponse = {
  method: string;
  route: string;
  currently_requires_auth: boolean;
  future_auth_required: boolean;
  future_permission: string;
  enforcement_enabled: boolean;
  authorization_header_can_grant_authority: boolean;
  reason: string;
};

export type AuthStatusResponse = {
  generated_at: string;
  phase0_auth_boundary_complete: boolean;
  auth_implemented: boolean;
  auth_enabled: boolean;
  auth_provider: string;
  auth_mode: string;
  token_verification_enabled: boolean;
  real_token_parsing_enabled: boolean;
  disabled_token_verifier_available: boolean;
  backend_auth_core_available: boolean;
  frontend_disabled_session_available: boolean;
  auth_status_bridge_available: boolean;
  auth_status_endpoint_available: boolean;
  rbac_enforcement_enabled: boolean;
  rbac_enforced: boolean;
  route_protection_enforced: boolean;
  route_guarding_enabled: boolean;
  current_routes_require_auth: boolean;
  authorization_header_required: boolean;
  authorization_header_parsed: boolean;
  authorization_header_can_grant_authority: boolean;
  frontend_authorization_headers_emitted: boolean;
  jwks_fetch_enabled: boolean;
  login_ui_available: boolean;
  user_management_available: boolean;
  manual_review_action_authority_granted: boolean;
  water_emergency_action_authority_granted: boolean;
  action_execution_available: boolean;
  mutation_endpoints_available: boolean;
  secret_hygiene_helper_available: boolean;
  committed_credentials_allowed: boolean;
  real_credentials_required_for_future_auth: boolean;
  future_auth_cutover_ready: boolean;
  future_auth_cutover_blocked_by: string[];
  future_auth_cutover_prerequisites: AuthCutoverPrerequisiteResponse[];
  current_route_accessibility_audit: CurrentRouteAccessibilityAuditItemResponse[];
  phase_allows_auth_enforcement: boolean;
  phase_allows_rbac_enforcement: boolean;
  phase_allows_route_guarding: boolean;
  reason: string;
};

export type DashboardSource = "api" | "mock";

export type DashboardFetchResult<T> = {
  data: T;
  source: DashboardSource;
  errorMessage?: string;
  requestedUrl?: string;
};
