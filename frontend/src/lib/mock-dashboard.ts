import type {
  DashboardOverviewResponse,
  WaterEmergencyDashboardResponse
} from "@/lib/dashboard-contracts";

export const mockDashboardOverview: DashboardOverviewResponse = {
  generated_at: "2026-05-16T09:30:00Z",
  operational_summary: {
    total_jobs: 18,
    total_work_orders: 14,
    total_visits: 22,
    total_route_assignments: 17,
    open_manual_reviews: 4,
    blocked_operations: 3,
    escalation_indicators: 2,
    open_water_emergencies: 1,
    audit_correlation_count: 11
  },
  lifecycle_summary: {
    intake_lifecycle_counts: [
      { label: "approved", count: 10 },
      { label: "review_required", count: 4 },
      { label: "blocked", count: 2 },
      { label: "water_emergency_separated", count: 1 }
    ],
    job_status_counts: [
      { label: "open", count: 9 },
      { label: "scheduled", count: 6 },
      { label: "blocked", count: 3 }
    ],
    work_order_status_counts: [
      { label: "generated", count: 8 },
      { label: "ready_for_visit", count: 4 },
      { label: "review_required", count: 2 }
    ],
    visit_status_counts: [
      { label: "dispatch_ready", count: 7 },
      { label: "scheduled", count: 9 },
      { label: "blocked", count: 3 },
      { label: "water_emergency", count: 1 }
    ],
    route_status_counts: [
      { label: "prepared", count: 9 },
      { label: "authorized", count: 5 },
      { label: "blocked", count: 3 }
    ],
    dispatch_execution_state_counts: [
      { label: "not_executed", count: 8 },
      { label: "executed", count: 6 },
      { label: "blocked", count: 3 }
    ],
    dispatch_ready_visits: 7,
    dispatched_route_assignments: 6,
    water_emergency_records: 1,
    water_emergency_separated_intake: 1,
    blocker_count: 3
  },
  manual_review_summary: {
    total_items: 9,
    open_items: 4,
    deferred_items: 1,
    resolved_items: 3,
    archived_items: 1,
    severity_counts: [
      { label: "high", count: 2 },
      { label: "medium", count: 4 },
      { label: "low", count: 3 }
    ],
    reason_counts: [
      { label: "uncertain_cancellation", count: 2 },
      { label: "water_emergency_review", count: 1 },
      { label: "address_validation", count: 3 },
      { label: "dispatch_blocker", count: 3 }
    ],
    escalation_indicators: 2,
    audit_correlation_count: 5
  },
  dispatch_summary: {
    route_assignments: {
      total_assignments: 17,
      status_counts: [
        { label: "prepared", count: 9 },
        { label: "authorized", count: 5 },
        { label: "blocked", count: 3 }
      ],
      region_counts: [
        { label: "miami", count: 7 },
        { label: "broward", count: 6 },
        { label: "palm_beach", count: 4 }
      ],
      time_window_counts: [
        { label: "morning", count: 7 },
        { label: "afternoon", count: 8 },
        { label: "after_hours", count: 2 }
      ],
      authorization_state_counts: [
        { label: "authorized", count: 5 },
        { label: "pending", count: 9 },
        { label: "blocked", count: 3 }
      ],
      dispatched_count: 6,
      awaiting_dispatch_execution_count: 8,
      blocked_count: 3
    },
    external_execution: {
      adapter_state_counts: [
        { label: "prepared", count: 7 },
        { label: "not_prepared", count: 8 },
        { label: "blocked", count: 2 }
      ],
      execution_state_counts: [
        { label: "not_executed", count: 9 },
        { label: "completed", count: 6 },
        { label: "failed", count: 2 }
      ],
      confirmation_state_counts: [
        { label: "confirmed", count: 5 },
        { label: "pending", count: 10 },
        { label: "failed", count: 2 }
      ],
      prepared_count: 7,
      execution_completed_count: 6,
      execution_failed_count: 2,
      confirmation_failed_count: 2,
      retry_prepared_count: 1,
      reconciliation_required_count: 2
    },
    reconciliation_recovery: {
      reconciliation_state_counts: [
        { label: "consistent", count: 9 },
        { label: "mismatch", count: 2 },
        { label: "not_checked", count: 6 }
      ],
      recovery_state_counts: [
        { label: "no_recovery_needed", count: 11 },
        { label: "replay_prepared", count: 1 },
        { label: "blocked", count: 1 }
      ],
      mismatch_count: 2,
      divergence_count: 1,
      replay_prepared_count: 1,
      rollback_prepared_count: 0,
      recovery_blocked_count: 1
    },
    governance_accountability: {
      governance_state_counts: [
        { label: "approved", count: 5 },
        { label: "pending", count: 9 },
        { label: "blocked", count: 3 }
      ],
      accountability_state_counts: [
        { label: "normal", count: 12 },
        { label: "escalation_required", count: 2 },
        { label: "blocked", count: 3 }
      ],
      operator_approved_count: 5,
      intervention_required_count: 2,
      escalation_required_count: 2,
      incident_prepared_count: 1,
      accountability_blocked_count: 3
    }
  },
  timeline_summary: {
    total_events: 6,
    returned_events: 6,
    mutable_event_count: 0,
    audit_correlation_ids: [
      "audit-dashboard-001",
      "audit-dashboard-002",
      "audit-dashboard-003"
    ],
    entries: [
      {
        occurred_at: "2026-05-16T09:20:00Z",
        event_type: "operational_accountability.escalation_required",
        event_state: "recorded",
        entity_type: "route_assignment",
        entity_id: "0d91f55b-9086-49b0-9d93-6f83b38fc571",
        route_assignment_id: "0d91f55b-9086-49b0-9d93-6f83b38fc571",
        visit_id: "6a97f5c6-3b67-41e5-bfb4-08b0fd07f006",
        work_order_id: "47e2f8d4-30a2-4eab-99fa-426946b6456d",
        job_id: "c87983c7-17e0-4e12-8092-25f9e93ec36f",
        technician_id: null,
        audit_correlation_id: "audit-dashboard-003",
        previous_state: "pending",
        new_state: "escalation_required",
        is_immutable: true
      },
      {
        occurred_at: "2026-05-16T09:05:00Z",
        event_type: "operational_replay.replay_prepared",
        event_state: "recorded",
        entity_type: "route_assignment",
        entity_id: "214b905a-1c91-467f-8bfa-a58fa6dbe815",
        route_assignment_id: "214b905a-1c91-467f-8bfa-a58fa6dbe815",
        visit_id: "c345832e-1c97-48af-90b3-03b6ef780920",
        work_order_id: "95a27d09-141c-40f7-9427-6401ddcf9821",
        job_id: "96f01858-917a-4f5e-9218-ced3deea404f",
        technician_id: null,
        audit_correlation_id: "audit-dashboard-002",
        previous_state: "mismatch",
        new_state: "replay_prepared",
        is_immutable: true
      },
      {
        occurred_at: "2026-05-16T08:50:00Z",
        event_type: "external_execution.confirmation_failed",
        event_state: "recorded",
        entity_type: "route_assignment",
        entity_id: "5ed3cf8e-7391-4abd-8944-3d0c041fd5ef",
        route_assignment_id: "5ed3cf8e-7391-4abd-8944-3d0c041fd5ef",
        visit_id: "bc393a4e-1b61-4daa-a9f9-bb615e944d9b",
        work_order_id: "87f35d07-7bb6-4d7d-81fc-787cb05dc4a4",
        job_id: "97e60c93-1615-4fc4-a663-0307567bf04d",
        technician_id: "844f52e6-94b7-46e4-9115-34ca2e908afb",
        audit_correlation_id: "audit-dashboard-001",
        previous_state: "pending",
        new_state: "failed",
        is_immutable: true
      },
      {
        occurred_at: "2026-05-16T08:30:00Z",
        event_type: "operational_dispatch.executed",
        event_state: "recorded",
        entity_type: "route_assignment",
        entity_id: "41652616-ec51-43d4-a580-80442f644c0b",
        route_assignment_id: "41652616-ec51-43d4-a580-80442f644c0b",
        visit_id: "dc26eb6b-1978-4fae-9340-cf5d969a0102",
        work_order_id: "c78df81c-5381-4e31-9a7d-3d78d78d7ac0",
        job_id: "f91a2eb5-c6a5-4829-930f-71305d1ab695",
        technician_id: "9e0dd663-3e4d-4722-a7e5-f652e20fd82f",
        audit_correlation_id: "audit-dashboard-001",
        previous_state: "authorized",
        new_state: "executed",
        is_immutable: true
      },
      {
        occurred_at: "2026-05-16T08:10:00Z",
        event_type: "manual_review.created",
        event_state: "recorded",
        entity_type: "review_item",
        entity_id: "74c29ad0-a8f0-4b9a-b596-285b35556717",
        route_assignment_id: null,
        visit_id: null,
        work_order_id: null,
        job_id: "6cd9a578-b22a-45cb-b492-43c09f5d9d2b",
        technician_id: null,
        audit_correlation_id: "audit-dashboard-002",
        previous_state: null,
        new_state: "open",
        is_immutable: true
      },
      {
        occurred_at: "2026-05-16T07:55:00Z",
        event_type: "operational_intake.water_emergency_separated",
        event_state: "recorded",
        entity_type: "water_emergency",
        entity_id: "e9acb112-409f-4d4f-b98f-4b61a437c4c7",
        route_assignment_id: null,
        visit_id: null,
        work_order_id: null,
        job_id: "72eba727-e804-4dd0-8628-bf7eb1212c60",
        technician_id: null,
        audit_correlation_id: "audit-dashboard-003",
        previous_state: "intake_received",
        new_state: "water_emergency_separated",
        is_immutable: true
      }
    ]
  }
};

export const mockWaterEmergencyDashboard: WaterEmergencyDashboardResponse = {
  generated_at: "2026-05-16T09:30:00Z",
  total_records: 2,
  open_count: 1,
  closed_count: 1,
  status_counts: [
    { label: "drying_in_progress", count: 1 },
    { label: "closed", count: 1 }
  ],
  stage_counts: [
    { label: "monitoring", count: 1 },
    { label: "closed_after_monitoring", count: 1 }
  ],
  multi_visit_count: 1,
  equipment_onsite_count: 1,
  moisture_tracking_required_count: 1,
  related_job_count: 2,
  related_work_order_count: 0,
  related_visit_count: 2,
  review_indicator_count: 1,
  escalation_indicator_count: 1,
  data_gap_counts: [{ label: "no_timeline_evidence", count: 1 }],
  audit_correlation_count: 2,
  records: [
    {
      water_emergency_id: "e9acb112-409f-4d4f-b98f-4b61a437c4c7",
      job_id: "72eba727-e804-4dd0-8628-bf7eb1212c60",
      status: "drying_in_progress",
      drying_stage: "monitoring",
      next_required_action: "Synthetic drying progress review",
      is_open: true,
      equipment_onsite: true,
      moisture_tracking_required: true,
      opened_at: "2026-05-16T06:30:00Z",
      closed_at: null,
      related_work_order_ids: [],
      related_visit_ids: ["bc393a4e-1b61-4daa-a9f9-bb615e944d9b"],
      open_review_count: 1,
      timeline_event_count: 1,
      audit_correlation_ids: ["audit-dashboard-003"]
    },
    {
      water_emergency_id: "19be3f77-7771-4aca-bb8e-9534b32a0831",
      job_id: "871ac83f-88bb-4f09-8ca3-c3718dce6a46",
      status: "closed",
      drying_stage: "closed_after_monitoring",
      next_required_action: "No action. Synthetic closed Water Emergency example.",
      is_open: false,
      equipment_onsite: false,
      moisture_tracking_required: false,
      opened_at: "2026-05-14T08:30:00Z",
      closed_at: "2026-05-15T08:30:00Z",
      related_work_order_ids: [],
      related_visit_ids: [],
      open_review_count: 0,
      timeline_event_count: 0,
      audit_correlation_ids: []
    }
  ],
  timeline_summary: {
    total_events: 1,
    returned_events: 1,
    mutable_event_count: 0,
    audit_correlation_ids: ["audit-dashboard-003"],
    entries: [
      {
        occurred_at: "2026-05-16T07:55:00Z",
        event_type: "operational_intake.water_emergency_separated",
        event_state: "recorded",
        entity_type: "water_emergency",
        entity_id: "e9acb112-409f-4d4f-b98f-4b61a437c4c7",
        route_assignment_id: null,
        visit_id: null,
        work_order_id: null,
        job_id: "72eba727-e804-4dd0-8628-bf7eb1212c60",
        technician_id: null,
        audit_correlation_id: "audit-dashboard-003",
        previous_state: "intake_received",
        new_state: "water_emergency_separated",
        is_immutable: true
      }
    ]
  }
};
