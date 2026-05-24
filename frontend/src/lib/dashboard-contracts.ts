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

export type DashboardSource = "api" | "mock";

export type DashboardFetchResult<T> = {
  data: T;
  source: DashboardSource;
  errorMessage?: string;
  requestedUrl?: string;
};
