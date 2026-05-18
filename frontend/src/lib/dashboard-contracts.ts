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
  data_gap_counts: CountBucket[];
  audit_correlation_ids: string[];
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
