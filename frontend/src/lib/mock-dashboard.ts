import type {
  DashboardOverviewResponse,
  ManualReviewDetailResponse,
  ManualReviewQueueResponse,
  WaterEmergencyDashboardResponse,
  WaterEmergencyDetailResponse
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

export const mockManualReviewQueue: ManualReviewQueueResponse = {
  generated_at: "2026-05-16T09:35:00Z",
  total_items: 5,
  open_items: 2,
  deferred_items: 1,
  resolved_items: 1,
  archived_items: 1,
  active_attention_count: 3,
  water_emergency_related_count: 1,
  dispatch_related_count: 3,
  blocked_count: 3,
  status_counts: [
    { label: "archived", count: 1 },
    { label: "deferred", count: 1 },
    { label: "open", count: 2 },
    { label: "resolved", count: 1 }
  ],
  reason_counts: [
    { label: "missing_customer_data", count: 1 },
    { label: "water_emergency_equipment_review", count: 1 },
    { label: "duplicate_route_conflict", count: 1 },
    { label: "cancellation_status_uncertainty", count: 1 },
    { label: "needs_operator_review", count: 1 }
  ],
  severity_counts: [
    { label: "critical", count: 1 },
    { label: "high", count: 2 },
    { label: "medium", count: 1 },
    { label: "low", count: 1 }
  ],
  group_counts: [
    { label: "open", count: 2 },
    { label: "deferred", count: 1 },
    { label: "resolved", count: 1 },
    { label: "archived", count: 1 },
    { label: "blocked", count: 3 },
    { label: "water_emergency_related", count: 1 },
    { label: "dispatch_related", count: 3 },
    { label: "missing_data", count: 1 },
    { label: "duplicate_or_conflict", count: 1 },
    { label: "cancellation_or_status_uncertainty", count: 1 },
    { label: "needs_operator_review", count: 1 }
  ],
  age_bucket_counts: [
    { label: "new", count: 1 },
    { label: "active", count: 1 },
    { label: "aging", count: 1 },
    { label: "resolved_or_archived", count: 2 }
  ],
  decision_readiness_counts: [
    { label: "blocked_by_missing_data", count: 1 },
    { label: "needs_water_emergency_review", count: 1 },
    { label: "resolved_or_archived", count: 2 },
    { label: "needs_operator_review", count: 1 }
  ],
  audit_correlation_count: 5,
  taxonomy_metadata: {
    randall_authorized_phase_0_baseline: true,
    source: "phase_0_visibility_heuristic",
    legal_or_insurance_policy: false,
    requires_alfonso_owner_review: false,
    baseline_note:
      "Manual Review queue groups are Randall-authorized Phase 0 visibility baselines only.",
    group_definitions: [
      {
        key: "water_emergency_related",
        label: "Water Emergency related",
        category: "manual_review_visibility",
        source: "phase_0_visibility_heuristic",
        randall_authorized_phase_0_baseline: true,
        legal_or_insurance_policy: false,
        requires_alfonso_owner_review: false,
        reason:
          "Separates Water Emergency review visibility from standard dispatch review context."
      },
      {
        key: "dispatch_related",
        label: "Dispatch related",
        category: "manual_review_visibility",
        source: "phase_0_visibility_heuristic",
        randall_authorized_phase_0_baseline: true,
        legal_or_insurance_policy: false,
        requires_alfonso_owner_review: false,
        reason:
          "Identifies review records tied to standard job, visit, work-order, or route evidence."
      }
    ]
  },
  available_filters: [
    {
      key: "all",
      label: "All reviews",
      count: 5,
      description: "Every persisted Manual Review item returned by this read-only queue."
    },
    {
      key: "open",
      label: "Open",
      count: 2,
      description: "Open Manual Review items requiring safety visibility."
    },
    {
      key: "deferred",
      label: "Deferred",
      count: 1,
      description: "Review items intentionally deferred for later operator follow-up."
    },
    {
      key: "resolved",
      label: "Resolved",
      count: 1,
      description: "Resolved review items kept separate from active review needs."
    },
    {
      key: "archived",
      label: "Archived",
      count: 1,
      description: "Archived review history separated from active review needs."
    },
    {
      key: "active_attention",
      label: "Active attention",
      count: 3,
      description: "Open or deferred review items still requiring operator attention."
    },
    {
      key: "water_emergency_related",
      label: "Water Emergency related",
      count: 1,
      description: "Review items specifically tied to Water Emergency records, jobs, or visits."
    },
    {
      key: "dispatch_related",
      label: "Dispatch related",
      count: 3,
      description: "Review items tied to standard job, work-order, visit, or route evidence."
    },
    {
      key: "missing_data",
      label: "Missing data",
      count: 1,
      description: "Review items whose reason indicates missing, invalid, incomplete, or unknown data."
    },
    {
      key: "duplicate_or_conflict",
      label: "Duplicate or conflict",
      count: 1,
      description: "Review items whose reason indicates duplicate or conflicting evidence."
    },
    {
      key: "cancellation_or_status_uncertainty",
      label: "Cancellation or status uncertainty",
      count: 1,
      description: "Review items whose reason indicates cancellation or status uncertainty."
    },
    {
      key: "needs_operator_review",
      label: "Needs operator review",
      count: 1,
      description: "Fallback visibility group when no more specific Phase 0 group is deterministic."
    }
  ],
  sort_options: [
    {
      key: "attention",
      label: "Attention priority",
      description: "Active, blocker, severity, status, and created-time ordering."
    },
    {
      key: "newest",
      label: "Newest first",
      description: "Most recently created Manual Review items first."
    },
    {
      key: "status",
      label: "Status and reason",
      description: "Status group, reason code, attention, and created-time ordering."
    }
  ],
  result_window_metadata: {
    total_count: 5,
    visible_count: 5,
    result_limit: 5,
    has_more: false,
    sort_key: "attention",
    generated_at: "2026-05-16T09:35:00Z"
  },
  items: [
    {
      review_item_id: "41000000-0000-4000-8000-000000000001",
      status: "open",
      severity: "high",
      reason_code: "missing_customer_data",
      visibility_groups: ["open", "blocked", "dispatch_related", "missing_data"],
      primary_group: "missing_data",
      entity_type: "job",
      entity_id: "42000000-0000-4000-8000-000000000001",
      job_id: "42000000-0000-4000-8000-000000000001",
      work_order_id: "43000000-0000-4000-8000-000000000001",
      visit_id: null,
      route_assignment_id: null,
      water_emergency_id: null,
      created_at: "2026-05-16T06:30:00Z",
      updated_at: "2026-05-16T06:30:00Z",
      reviewed_at: null,
      deferred_until: null,
      resolved_at: null,
      age_bucket: "new",
      age_hours: 3,
      blocker_indicator: true,
      attention_indicator: true,
      confidence_score: 64,
      recommended_action: "Review missing synthetic customer data.",
      audit_correlation_id: "audit-manual-review-mock-001",
      evidence_references: [
        "review:41000000-0000-4000-8000-000000000001",
        "job:42000000-0000-4000-8000-000000000001",
        "work_order:43000000-0000-4000-8000-000000000001",
        "audit:audit-manual-review-mock-001"
      ],
      decision_readiness: {
        label: "blocked_by_missing_data",
        summary:
          "Missing, invalid, incomplete, or unknown data is present. The review remains read-only and needs operator-safe information gathering before any future action.",
        reason_codes: [
          "missing_data_evidence",
          "active_manual_review",
          "blocker_indicator",
          "high_or_critical_severity"
        ],
        evidence_references: [
          "review:41000000-0000-4000-8000-000000000001",
          "job:42000000-0000-4000-8000-000000000001",
          "work_order:43000000-0000-4000-8000-000000000001",
          "audit:audit-manual-review-mock-001"
        ],
        is_active_decision_need: true,
        is_resolution_candidate: false
      }
    },
    {
      review_item_id: "41000000-0000-4000-8000-000000000002",
      status: "deferred",
      severity: "critical",
      reason_code: "water_emergency_equipment_review",
      visibility_groups: ["deferred", "blocked", "water_emergency_related"],
      primary_group: "water_emergency_related",
      entity_type: "water_emergency",
      entity_id: "e9acb112-409f-4d4f-b98f-4b61a437c4c7",
      job_id: "72eba727-8f18-45d5-a1d3-c4fa4bd21f2d",
      work_order_id: null,
      visit_id: "f862c2f6-4e1c-47ac-b3e9-9639a8f9c31b",
      route_assignment_id: null,
      water_emergency_id: "e9acb112-409f-4d4f-b98f-4b61a437c4c7",
      created_at: "2026-05-15T06:30:00Z",
      updated_at: "2026-05-16T07:30:00Z",
      reviewed_at: null,
      deferred_until: "2026-05-16T15:30:00Z",
      resolved_at: null,
      age_bucket: "active",
      age_hours: 27,
      blocker_indicator: true,
      attention_indicator: true,
      confidence_score: 72,
      recommended_action: "Review synthetic Water Emergency equipment context.",
      audit_correlation_id: "audit-manual-review-mock-002",
      evidence_references: [
        "review:41000000-0000-4000-8000-000000000002",
        "job:72eba727-8f18-45d5-a1d3-c4fa4bd21f2d",
        "visit:f862c2f6-4e1c-47ac-b3e9-9639a8f9c31b",
        "water_emergency:e9acb112-409f-4d4f-b98f-4b61a437c4c7",
        "audit:audit-manual-review-mock-002"
      ],
      decision_readiness: {
        label: "needs_water_emergency_review",
        summary:
          "This Manual Review item is specifically tied to Water Emergency evidence and remains separated from standard dispatch review context.",
        reason_codes: [
          "water_emergency_related",
          "active_manual_review",
          "blocker_indicator",
          "high_or_critical_severity"
        ],
        evidence_references: [
          "review:41000000-0000-4000-8000-000000000002",
          "job:72eba727-8f18-45d5-a1d3-c4fa4bd21f2d",
          "visit:f862c2f6-4e1c-47ac-b3e9-9639a8f9c31b",
          "water_emergency:e9acb112-409f-4d4f-b98f-4b61a437c4c7",
          "audit:audit-manual-review-mock-002"
        ],
        is_active_decision_need: true,
        is_resolution_candidate: false
      }
    },
    {
      review_item_id: "41000000-0000-4000-8000-000000000003",
      status: "resolved",
      severity: "medium",
      reason_code: "duplicate_route_conflict",
      visibility_groups: [
        "resolved",
        "dispatch_related",
        "duplicate_or_conflict"
      ],
      primary_group: "duplicate_or_conflict",
      entity_type: "route_assignment",
      entity_id: "44000000-0000-4000-8000-000000000003",
      job_id: "42000000-0000-4000-8000-000000000003",
      work_order_id: "43000000-0000-4000-8000-000000000003",
      visit_id: "45000000-0000-4000-8000-000000000003",
      route_assignment_id: "44000000-0000-4000-8000-000000000003",
      water_emergency_id: null,
      created_at: "2026-05-12T09:30:00Z",
      updated_at: "2026-05-15T09:30:00Z",
      reviewed_at: null,
      deferred_until: null,
      resolved_at: "2026-05-15T09:30:00Z",
      age_bucket: "resolved_or_archived",
      age_hours: 72,
      blocker_indicator: false,
      attention_indicator: false,
      confidence_score: 91,
      recommended_action: null,
      audit_correlation_id: "audit-manual-review-mock-003",
      evidence_references: [
        "review:41000000-0000-4000-8000-000000000003",
        "job:42000000-0000-4000-8000-000000000003",
        "work_order:43000000-0000-4000-8000-000000000003",
        "visit:45000000-0000-4000-8000-000000000003",
        "route_assignment:44000000-0000-4000-8000-000000000003"
      ],
      decision_readiness: {
        label: "resolved_or_archived",
        summary:
          "Resolved or archived Manual Review evidence is retained as read-only history; it is not an active decision need.",
        reason_codes: ["resolved_or_archived_status"],
        evidence_references: [
          "review:41000000-0000-4000-8000-000000000003",
          "job:42000000-0000-4000-8000-000000000003",
          "work_order:43000000-0000-4000-8000-000000000003",
          "visit:45000000-0000-4000-8000-000000000003",
          "route_assignment:44000000-0000-4000-8000-000000000003"
        ],
        is_active_decision_need: false,
        is_resolution_candidate: false
      }
    },
    {
      review_item_id: "41000000-0000-4000-8000-000000000004",
      status: "archived",
      severity: "low",
      reason_code: "cancellation_status_uncertainty",
      visibility_groups: [
        "archived",
        "dispatch_related",
        "cancellation_or_status_uncertainty"
      ],
      primary_group: "cancellation_or_status_uncertainty",
      entity_type: "job",
      entity_id: "42000000-0000-4000-8000-000000000004",
      job_id: "42000000-0000-4000-8000-000000000004",
      work_order_id: null,
      visit_id: null,
      route_assignment_id: null,
      water_emergency_id: null,
      created_at: "2026-05-11T09:30:00Z",
      updated_at: "2026-05-15T09:30:00Z",
      reviewed_at: null,
      deferred_until: null,
      resolved_at: null,
      age_bucket: "resolved_or_archived",
      age_hours: 96,
      blocker_indicator: false,
      attention_indicator: false,
      confidence_score: 98,
      recommended_action: null,
      audit_correlation_id: "audit-manual-review-mock-004",
      evidence_references: [
        "review:41000000-0000-4000-8000-000000000004",
        "job:42000000-0000-4000-8000-000000000004"
      ],
      decision_readiness: {
        label: "resolved_or_archived",
        summary:
          "Resolved or archived Manual Review evidence is retained as read-only history; it is not an active decision need.",
        reason_codes: ["resolved_or_archived_status"],
        evidence_references: [
          "review:41000000-0000-4000-8000-000000000004",
          "job:42000000-0000-4000-8000-000000000004"
        ],
        is_active_decision_need: false,
        is_resolution_candidate: false
      }
    },
    {
      review_item_id: "41000000-0000-4000-8000-000000000005",
      status: "open",
      severity: "high",
      reason_code: "needs_operator_review",
      visibility_groups: ["open", "blocked", "needs_operator_review"],
      primary_group: "blocked",
      entity_type: null,
      entity_id: null,
      job_id: null,
      work_order_id: null,
      visit_id: null,
      route_assignment_id: null,
      water_emergency_id: null,
      created_at: "2026-05-13T09:30:00Z",
      updated_at: "2026-05-13T09:30:00Z",
      reviewed_at: null,
      deferred_until: null,
      resolved_at: null,
      age_bucket: "aging",
      age_hours: 48,
      blocker_indicator: true,
      attention_indicator: true,
      confidence_score: 58,
      recommended_action: "Route to operator review.",
      audit_correlation_id: "audit-manual-review-mock-005",
      evidence_references: [
        "review:41000000-0000-4000-8000-000000000005",
        "audit:audit-manual-review-mock-005"
      ],
      decision_readiness: {
        label: "needs_operator_review",
        summary:
          "No more specific deterministic readiness label is available, so this item remains in Manual Review for operator-safe visibility.",
        reason_codes: [
          "operator_review_required",
          "active_manual_review",
          "blocker_indicator",
          "high_or_critical_severity"
        ],
        evidence_references: [
          "review:41000000-0000-4000-8000-000000000005",
          "audit:audit-manual-review-mock-005"
        ],
        is_active_decision_need: true,
        is_resolution_candidate: false
      }
    }
  ]
};

export const mockManualReviewDetail: ManualReviewDetailResponse = {
  generated_at: "2026-05-16T09:36:00Z",
  review_item: mockManualReviewQueue.items[0],
  reason_context: {
    reason_code: "missing_customer_data",
    status: "open",
    severity: "high",
    confidence_score: 64,
    recommended_action: "Review missing synthetic customer data.",
    review_reason_codes: ["missing_customer_data"],
    snapshot_keys: ["validation_snapshot"],
    blocker_indicator: true,
    attention_indicator: true,
    evidence_references: mockManualReviewQueue.items[0].evidence_references
  },
  decision_readiness: mockManualReviewQueue.items[0].decision_readiness,
  linked_entity_context: {
    entity_type: "job",
    entity_id: "42000000-0000-4000-8000-000000000001",
    job_id: "42000000-0000-4000-8000-000000000001",
    job_status: "awaiting_dispatch",
    job_type: "standard",
    work_order_id: "43000000-0000-4000-8000-000000000001",
    work_order_status: "generated",
    visit_id: null,
    visit_status: null,
    route_assignment_id: null,
    route_assignment_status: null,
    water_emergency_id: null,
    water_emergency_status: null,
    water_emergency_stage: null,
    is_water_emergency_related: false,
    is_dispatch_related: true,
    unknown_indicators: [],
    audit_correlation_ids: ["audit-manual-review-mock-001"]
  },
  data_gap_counts: [],
  audit_correlation_ids: ["audit-manual-review-mock-001"],
  taxonomy_metadata: mockManualReviewQueue.taxonomy_metadata,
  timeline_summary: {
    total_events: 1,
    returned_events: 1,
    mutable_event_count: 0,
    audit_correlation_ids: ["audit-manual-review-mock-001"],
    entries: [
      {
        occurred_at: "2026-05-16T09:00:00Z",
        event_type: "manual_review.evidence_attached",
        event_state: "recorded",
        entity_type: "review_item",
        entity_id: "41000000-0000-4000-8000-000000000001",
        route_assignment_id: null,
        visit_id: null,
        work_order_id: "43000000-0000-4000-8000-000000000001",
        job_id: "42000000-0000-4000-8000-000000000001",
        technician_id: null,
        audit_correlation_id: "audit-manual-review-mock-001",
        previous_state: "open",
        new_state: "evidence_attached",
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
  equipment_summary: {
    equipment_onsite_count: 1,
    moisture_tracking_required_count: 1,
    work_orders_with_equipment_notes_count: 1,
    records_missing_equipment_context_count: 0,
    inventory_entity_available: false,
    unknown_counts: [{ label: "equipment_inventory_not_modeled", count: 1 }]
  },
  visit_chain_summary: {
    total_visits: 2,
    multi_visit_record_count: 1,
    open_records_without_visits_count: 0,
    scheduled_visit_count: 1,
    completed_visit_count: 0,
    visit_status_counts: [
      { label: "review_required", count: 1 },
      { label: "scheduled", count: 1 }
    ]
  },
  drying_stage_summary: {
    stage_counts: [
      { label: "monitoring", count: 1 },
      { label: "closed_after_monitoring", count: 1 }
    ],
    active_stage_counts: [{ label: "monitoring", count: 1 }],
    missing_stage_count: 0,
    moisture_tracking_required_count: 1
  },
  review_exception_summary: {
    total_review_count: 3,
    open_review_count: 1,
    deferred_review_count: 1,
    resolved_review_count: 0,
    archived_review_count: 1,
    critical_unresolved_count: 1,
    escalation_indicator_count: 2,
    review_reason_counts: [
      { label: "water_detail_unknown_blocker", count: 1 },
      { label: "water_emergency_deferred_review", count: 1 },
      { label: "water_emergency_archived_exception", count: 1 }
    ],
    blocker_reason_counts: [
      { label: "water_detail_unknown_blocker", count: 1 },
      { label: "water_emergency_archived_exception", count: 1 }
    ],
    unknown_counts: [{ label: "open_record_without_scoped_review", count: 1 }],
    review_item_ids: [
      "74c29ad0-a8f0-4b9a-b596-285b35556717",
      "4b7cb8c9-b1d4-4e71-bbe5-5387f255e392",
      "48791671-859c-4e6c-a9ad-2dbd6324c11d"
    ],
    audit_correlation_ids: ["audit-dashboard-003", "audit-dashboard-review"]
  },
  next_step_summary: {
    total_records: 2,
    needs_attention_count: 1,
    closed_without_active_action_count: 1,
    label_counts: [
      { label: "needs_manual_review", count: 1 },
      { label: "needs_operator_decision", count: 1 },
      { label: "needs_equipment_review", count: 1 },
      { label: "closed_no_active_next_step", count: 1 }
    ],
    blocker_counts: [
      { label: "water_detail_unknown_blocker", count: 1 },
      { label: "equipment_inventory_not_modeled", count: 1 }
    ],
    records: [
      {
        water_emergency_id: "e9acb112-409f-4d4f-b98f-4b61a437c4c7",
        primary_label: "needs_manual_review",
        labels: [
          "needs_manual_review",
          "needs_operator_decision",
          "needs_equipment_review"
        ],
        summary:
          "Open Manual Review evidence exists; operator review remains required before any future Water Emergency workflow step.",
        reason_codes: [
          "water_detail_unknown_blocker",
          "equipment_inventory_not_modeled"
        ],
        evidence_references: [
          "job:72eba727-e804-4dd0-8628-bf7eb1212c60",
          "water_emergency:e9acb112-409f-4d4f-b98f-4b61a437c4c7",
          "review:74c29ad0-a8f0-4b9a-b596-285b35556717"
        ],
        current_status: "drying_in_progress",
        current_stage: "monitoring",
        open_review_count: 1,
        critical_alert_count: 1,
        blocker_count: 1,
        unknown_count: 1,
        requires_operator_attention: true,
        related_job_id: "72eba727-e804-4dd0-8628-bf7eb1212c60",
        related_work_order_ids: ["87f35d07-7bb6-4d7d-81fc-787cb05dc4a4"],
        related_visit_ids: [
          "bc393a4e-1b61-4daa-a9f9-bb615e944d9b",
          "94b62507-5b8d-4a9d-9578-5225492d81d1"
        ],
        audit_correlation_ids: ["audit-dashboard-003"]
      },
      {
        water_emergency_id: "19be3f77-7771-4aca-bb8e-9534b32a0831",
        primary_label: "closed_no_active_next_step",
        labels: ["closed_no_active_next_step"],
        summary:
          "Closed or resolved Water Emergency record; no active next-step action is implied.",
        reason_codes: ["water_emergency_closed_or_resolved"],
        evidence_references: [
          "job:871ac83f-88bb-4f09-8ca3-c3718dce6a46",
          "water_emergency:19be3f77-7771-4aca-bb8e-9534b32a0831"
        ],
        current_status: "closed",
        current_stage: "closed_after_monitoring",
        open_review_count: 0,
        critical_alert_count: 0,
        blocker_count: 0,
        unknown_count: 0,
        requires_operator_attention: false,
        related_job_id: "871ac83f-88bb-4f09-8ca3-c3718dce6a46",
        related_work_order_ids: [],
        related_visit_ids: [],
        audit_correlation_ids: []
      }
    ]
  },
  operator_queue_summary: {
    total_records: 2,
    active_attention_count: 1,
    closed_or_resolved_count: 1,
    critical_attention_count: 1,
    queue_group_counts: [
      { label: "active_attention", count: 1 },
      { label: "closed_or_resolved", count: 1 }
    ],
    attention_label_counts: [
      { label: "critical_attention", count: 1 },
      { label: "closed_or_resolved", count: 1 }
    ],
    items: [
      {
        water_emergency_id: "e9acb112-409f-4d4f-b98f-4b61a437c4c7",
        attention_label: "critical_attention",
        queue_group: "active_attention",
        attention_rank: 10,
        readiness_labels: [
          "needs_manual_review",
          "needs_operator_decision",
          "needs_equipment_review"
        ],
        summary:
          "Critical unresolved Water Emergency evidence exists; operator attention is needed before any future emergency workflow step.",
        reason_codes: [
          "water_detail_unknown_blocker",
          "equipment_inventory_not_modeled"
        ],
        evidence_references: [
          "job:72eba727-e804-4dd0-8628-bf7eb1212c60",
          "water_emergency:e9acb112-409f-4d4f-b98f-4b61a437c4c7",
          "review:74c29ad0-a8f0-4b9a-b596-285b35556717"
        ],
        current_status: "drying_in_progress",
        current_stage: "monitoring",
        open_review_count: 1,
        critical_alert_count: 1,
        blocker_count: 1,
        unknown_count: 1,
        related_job_id: "72eba727-e804-4dd0-8628-bf7eb1212c60",
        related_work_order_ids: ["87f35d07-7bb6-4d7d-81fc-787cb05dc4a4"],
        related_visit_ids: [
          "bc393a4e-1b61-4daa-a9f9-bb615e944d9b",
          "94b62507-5b8d-4a9d-9578-5225492d81d1"
        ],
        audit_correlation_ids: ["audit-dashboard-003"]
      },
      {
        water_emergency_id: "19be3f77-7771-4aca-bb8e-9534b32a0831",
        attention_label: "closed_or_resolved",
        queue_group: "closed_or_resolved",
        attention_rank: 90,
        readiness_labels: ["closed_no_active_next_step"],
        summary:
          "Closed or resolved Water Emergency record; it is separated from active attention items.",
        reason_codes: ["water_emergency_closed_or_resolved"],
        evidence_references: [
          "job:871ac83f-88bb-4f09-8ca3-c3718dce6a46",
          "water_emergency:19be3f77-7771-4aca-bb8e-9534b32a0831"
        ],
        current_status: "closed",
        current_stage: "closed_after_monitoring",
        open_review_count: 0,
        critical_alert_count: 0,
        blocker_count: 0,
        unknown_count: 0,
        related_job_id: "871ac83f-88bb-4f09-8ca3-c3718dce6a46",
        related_work_order_ids: [],
        related_visit_ids: [],
        audit_correlation_ids: []
      }
    ]
  },
  aging_followup_summary: {
    total_records: 2,
    active_timing_risk_count: 1,
    closed_or_resolved_count: 1,
    followup_due_count: 0,
    followup_overdue_count: 0,
    stale_evidence_count: 1,
    unknown_timing_count: 0,
    label_counts: [
      { label: "stale_evidence", count: 1 },
      { label: "closed_or_resolved", count: 1 }
    ],
    age_bucket_counts: [
      { label: "3_to_7_days", count: 1 },
      { label: "over_7_days", count: 1 }
    ],
    followup_bucket_counts: [
      { label: "followup_not_due", count: 1 },
      { label: "closed_or_resolved", count: 1 }
    ],
    items: [
      {
        water_emergency_id: "e9acb112-409f-4d4f-b98f-4b61a437c4c7",
        time_sensitivity_label: "stale_evidence",
        timing_group: "stale_or_unknown",
        timing_rank: 30,
        age_bucket: "3_to_7_days",
        followup_bucket: "followup_not_due",
        age_hours: 96,
        hours_since_last_visit: 76,
        hours_since_last_review: 30,
        hours_since_last_event: 76,
        opened_at: "2026-05-16T06:30:00Z",
        last_visit_at: "2026-05-17T10:00:00Z",
        last_review_at: "2026-05-19T08:30:00Z",
        last_event_at: "2026-05-17T10:00:00Z",
        closed_at: null,
        summary:
          "The latest related evidence is old enough to be flagged as stale for operator awareness.",
        reason_codes: ["stale_evidence", "water_detail_unknown_blocker"],
        missing_timestamp_indicators: [],
        stale_indicator_count: 1,
        requires_operator_attention: true,
        related_job_id: "72eba727-e804-4dd0-8628-bf7eb1212c60",
        related_work_order_ids: ["87f35d07-7bb6-4d7d-81fc-787cb05dc4a4"],
        related_visit_ids: [
          "bc393a4e-1b61-4daa-a9f9-bb615e944d9b",
          "94b62507-5b8d-4a9d-9578-5225492d81d1"
        ],
        audit_correlation_ids: ["audit-dashboard-003"],
        evidence_references: [
          "job:72eba727-e804-4dd0-8628-bf7eb1212c60",
          "water_emergency:e9acb112-409f-4d4f-b98f-4b61a437c4c7"
        ]
      },
      {
        water_emergency_id: "19be3f77-7771-4aca-bb8e-9534b32a0831",
        time_sensitivity_label: "closed_or_resolved",
        timing_group: "closed_or_resolved",
        timing_rank: 90,
        age_bucket: "over_7_days",
        followup_bucket: "closed_or_resolved",
        age_hours: 240,
        hours_since_last_visit: null,
        hours_since_last_review: null,
        hours_since_last_event: null,
        opened_at: "2026-05-10T08:00:00Z",
        last_visit_at: null,
        last_review_at: null,
        last_event_at: null,
        closed_at: "2026-05-14T17:00:00Z",
        summary:
          "Closed or resolved Water Emergency record; it is separated from active timing risks.",
        reason_codes: ["closed_or_resolved"],
        missing_timestamp_indicators: ["missing_last_evidence_at"],
        stale_indicator_count: 0,
        requires_operator_attention: false,
        related_job_id: "871ac83f-88bb-4f09-8ca3-c3718dce6a46",
        related_work_order_ids: [],
        related_visit_ids: [],
        audit_correlation_ids: [],
        evidence_references: [
          "job:871ac83f-88bb-4f09-8ca3-c3718dce6a46",
          "water_emergency:19be3f77-7771-4aca-bb8e-9534b32a0831"
        ]
      }
    ]
  },
  view_state_summary: {
    total_records: 2,
    active_record_count: 1,
    closed_or_resolved_count: 1,
    available_filters: [
      {
        key: "all",
        label: "All records",
        count: 2,
        description:
          "Every persisted Water Emergency record in this read-only dashboard response."
      },
      {
        key: "active",
        label: "Active records",
        count: 1,
        description:
          "Open Water Emergency records separated from closed or resolved records."
      },
      {
        key: "critical_attention",
        label: "Critical attention",
        count: 1,
        description: "Records with critical persisted review or alert evidence."
      },
      {
        key: "needs_manual_review",
        label: "Needs Manual Review",
        count: 1,
        description: "Records with Manual Review or operator-decision evidence."
      },
      {
        key: "blocked_missing_data",
        label: "Blocked or missing data",
        count: 1,
        description: "Records with blocker, unknown, or missing-data evidence."
      },
      {
        key: "followup_due",
        label: "Follow-up due",
        count: 0,
        description: "Records with conservative Phase 0 follow-up due visibility."
      },
      {
        key: "followup_overdue",
        label: "Follow-up overdue",
        count: 0,
        description: "Records with conservative Phase 0 follow-up overdue visibility."
      },
      {
        key: "stale_evidence",
        label: "Stale evidence",
        count: 1,
        description:
          "Records where related evidence is old enough to flag for operator awareness."
      },
      {
        key: "ready_for_close_review",
        label: "Ready for close review",
        count: 0,
        description: "Records with persisted close-review readiness evidence."
      },
      {
        key: "needs_followup",
        label: "Needs follow-up",
        count: 0,
        description: "Records with visit-chain follow-up visibility evidence."
      },
      {
        key: "equipment_review_needed",
        label: "Equipment review needed",
        count: 0,
        description: "Records with equipment context that needs operator review."
      },
      {
        key: "drying_stage_review_needed",
        label: "Drying-stage review needed",
        count: 0,
        description:
          "Records with drying-stage or moisture confirmation visibility."
      },
      {
        key: "needs_operator_review",
        label: "Needs operator review",
        count: 0,
        description:
          "Records with no safer deterministic group than operator review."
      },
      {
        key: "unknown_timing",
        label: "Unknown timing",
        count: 0,
        description: "Records missing enough timing evidence to avoid inferred SLA status."
      },
      {
        key: "closed_or_resolved",
        label: "Closed or resolved",
        count: 1,
        description: "Closed or resolved records separated from active attention groups."
      }
    ],
    sort_options: [
      {
        key: "attention",
        label: "Attention priority",
        description:
          "Critical, review, blocker, timing, close-review, monitoring, then closed."
      },
      {
        key: "last_activity",
        label: "Last activity",
        description:
          "Most recent persisted visit, review, event, opened, or closed timestamp."
      },
      {
        key: "status",
        label: "Status and stage",
        description: "Current status, drying stage, and deterministic attention rank."
      }
    ],
    group_counts: [
      { label: "critical_attention", count: 1 },
      { label: "closed_or_resolved", count: 1 }
    ],
    items: [
      {
        water_emergency_id: "e9acb112-409f-4d4f-b98f-4b61a437c4c7",
        filter_groups: [
          "all",
          "active",
          "critical_attention",
          "needs_manual_review",
          "blocked_missing_data",
          "stale_evidence"
        ],
        primary_filter_group: "critical_attention",
        sort_rank: 10,
        sort_label: "critical_attention",
        queue_group: "active_attention",
        attention_label: "critical_attention",
        time_sensitivity_label: "stale_evidence",
        readiness_label: "needs_manual_review",
        is_active: true,
        current_status: "drying_in_progress",
        current_stage: "monitoring",
        open_review_count: 1,
        critical_alert_count: 1,
        blocker_count: 1,
        unknown_count: 1,
        last_activity_at: "2026-05-19T08:30:00Z",
        summary:
          "Critical unresolved Water Emergency evidence exists; operator attention is needed before any future emergency workflow step.",
        reason_codes: ["water_detail_unknown_blocker", "stale_evidence"],
        related_job_id: "72eba727-e804-4dd0-8628-bf7eb1212c60",
        related_work_order_ids: ["87f35d07-7bb6-4d7d-81fc-787cb05dc4a4"],
        related_visit_ids: [
          "bc393a4e-1b61-4daa-a9f9-bb615e944d9b",
          "94b62507-5b8d-4a9d-9578-5225492d81d1"
        ],
        audit_correlation_ids: ["audit-dashboard-003"],
        evidence_references: [
          "job:72eba727-e804-4dd0-8628-bf7eb1212c60",
          "water_emergency:e9acb112-409f-4d4f-b98f-4b61a437c4c7",
          "review:74c29ad0-a8f0-4b9a-b596-285b35556717"
        ]
      },
      {
        water_emergency_id: "19be3f77-7771-4aca-bb8e-9534b32a0831",
        filter_groups: ["all", "closed_or_resolved"],
        primary_filter_group: "closed_or_resolved",
        sort_rank: 140,
        sort_label: "closed_or_resolved",
        queue_group: "closed_or_resolved",
        attention_label: "closed_or_resolved",
        time_sensitivity_label: "closed_or_resolved",
        readiness_label: "closed_no_active_next_step",
        is_active: false,
        current_status: "closed",
        current_stage: "closed_after_monitoring",
        open_review_count: 0,
        critical_alert_count: 0,
        blocker_count: 0,
        unknown_count: 0,
        last_activity_at: "2026-05-14T17:00:00Z",
        summary:
          "Closed or resolved Water Emergency record; it is separated from active attention items.",
        reason_codes: ["water_emergency_closed_or_resolved", "closed_or_resolved"],
        related_job_id: "871ac83f-88bb-4f09-8ca3-c3718dce6a46",
        related_work_order_ids: [],
        related_visit_ids: [],
        audit_correlation_ids: [],
        evidence_references: [
          "job:871ac83f-88bb-4f09-8ca3-c3718dce6a46",
          "water_emergency:19be3f77-7771-4aca-bb8e-9534b32a0831"
        ]
      }
    ]
  },
  governance_metadata: {
    randall_authorized_phase_0_baseline: true,
    source: "phase_0_visibility_heuristic",
    legal_or_insurance_policy: false,
    requires_alfonso_owner_review: false,
    baseline_note:
      "Randall-authorized Phase 0 visibility baseline for internal Water Emergency dashboard labels, filters, readiness groups, and view-state defaults.",
    timing_heuristic_note:
      "Water Emergency timing labels are conservative software visibility heuristics, not final SLA enforcement, insurance policy, drying certification language, or customer-facing promise.",
    provisional_filter_groups: [
      {
        key: "all",
        label: "All records",
        category: "filter_group",
        source: "phase_0_visibility_heuristic",
        randall_authorized_phase_0_baseline: true,
        legal_or_insurance_policy: false,
        requires_alfonso_owner_review: false,
        reason: "Internal read-only filter group for dashboard view state."
      },
      {
        key: "closed_or_resolved",
        label: "Closed or resolved",
        category: "filter_group",
        source: "phase_0_visibility_heuristic",
        randall_authorized_phase_0_baseline: true,
        legal_or_insurance_policy: false,
        requires_alfonso_owner_review: false,
        reason: "Internal read-only filter group for dashboard view state."
      }
    ],
    provisional_attention_labels: [
      {
        key: "critical_attention",
        label: "Critical attention",
        category: "attention_label",
        source: "phase_0_visibility_heuristic",
        randall_authorized_phase_0_baseline: true,
        legal_or_insurance_policy: false,
        requires_alfonso_owner_review: false,
        reason: "Internal read-only attention label for operator scanability."
      }
    ],
    provisional_timing_labels: [
      {
        key: "followup_due",
        label: "Follow-up due",
        category: "timing_label",
        source: "phase_0_visibility_heuristic",
        randall_authorized_phase_0_baseline: true,
        legal_or_insurance_policy: false,
        requires_alfonso_owner_review: false,
        reason:
          "Internal read-only timing label for Phase 0 follow-up visibility; not final SLA enforcement."
      }
    ],
    provisional_readiness_labels: [
      {
        key: "needs_manual_review",
        label: "Needs Manual Review",
        category: "readiness_label",
        source: "phase_0_visibility_heuristic",
        randall_authorized_phase_0_baseline: true,
        legal_or_insurance_policy: false,
        requires_alfonso_owner_review: false,
        reason: "Internal read-only readiness label for operator context."
      }
    ],
    owner_review_required_items: [
      {
        key: "formal_sla_or_insurance_policy",
        label: "Formal SLA or insurance policy",
        category: "owner_review_boundary",
        source: "owner_review_required",
        randall_authorized_phase_0_baseline: false,
        legal_or_insurance_policy: true,
        requires_alfonso_owner_review: true,
        reason:
          "Final SLA commitments, insurance documentation, drying certification, warranty language, or customer-facing policy can create company liability and require Alfonso owner review."
      }
    ],
    future_role_visibility_roles: [
      "office_admin",
      "operations_manager",
      "dispatcher",
      "reviewer",
      "technician",
      "owner"
    ]
  },
  result_window_metadata: {
    total_count: 2,
    visible_count: 2,
    result_limit: 2,
    has_more: false,
    sort_key: "attention",
    generated_at: "2026-05-22T12:00:00Z"
  },
  related_job_count: 2,
  related_work_order_count: 1,
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
      related_work_order_ids: ["87f35d07-7bb6-4d7d-81fc-787cb05dc4a4"],
      related_visit_ids: [
        "bc393a4e-1b61-4daa-a9f9-bb615e944d9b",
        "94b62507-5b8d-4a9d-9578-5225492d81d1"
      ],
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

export const mockWaterEmergencyDetail: WaterEmergencyDetailResponse = {
  generated_at: "2026-05-16T09:35:00Z",
  record: mockWaterEmergencyDashboard.records[0],
  job: {
    job_id: "72eba727-e804-4dd0-8628-bf7eb1212c60",
    job_type: "water_emergency",
    status: "active",
    review_status: null,
    priority: "urgent",
    requested_date: "2026-05-16",
    scheduled_date: "2026-05-16",
    source_system: "module32_mock",
    source_event_id: "module32-water-emergency-detail"
  },
  work_orders: [
    {
      work_order_id: "87f35d07-7bb6-4d7d-81fc-787cb05dc4a4",
      work_order_number: "WATER-DETAIL-001",
      status: "generated",
      dispatch_status: "not_dispatched",
      assigned_technician_id: null,
      audit_correlation_id: "audit-dashboard-003"
    }
  ],
  visits: [
    {
      visit_id: "bc393a4e-1b61-4daa-a9f9-bb615e944d9b",
      work_order_id: "87f35d07-7bb6-4d7d-81fc-787cb05dc4a4",
      technician_id: "844f52e6-94b7-46e4-9115-34ca2e908afb",
      visit_type: "water_emergency",
      status: "review_required",
      scheduled_start_at: "2026-05-16T13:00:00Z",
      scheduled_end_at: "2026-05-16T15:00:00Z",
      arrived_at: null,
      completed_at: null,
      audit_correlation_id: "audit-dashboard-003"
    },
    {
      visit_id: "94b62507-5b8d-4a9d-9578-5225492d81d1",
      work_order_id: "87f35d07-7bb6-4d7d-81fc-787cb05dc4a4",
      technician_id: "844f52e6-94b7-46e4-9115-34ca2e908afb",
      visit_type: "water_emergency",
      status: "scheduled",
      scheduled_start_at: "2026-05-17T13:00:00Z",
      scheduled_end_at: "2026-05-17T14:00:00Z",
      arrived_at: null,
      completed_at: null,
      audit_correlation_id: "audit-dashboard-003"
    }
  ],
  review_indicators: [
    {
      review_item_id: "74c29ad0-a8f0-4b9a-b596-285b35556717",
      status: "open",
      severity: "critical",
      reason_code: "water_detail_unknown_blocker",
      confidence_score: 70,
      entity_type: "water_emergency",
      entity_id: "e9acb112-409f-4d4f-b98f-4b61a437c4c7",
      job_id: "72eba727-e804-4dd0-8628-bf7eb1212c60",
      visit_id: "bc393a4e-1b61-4daa-a9f9-bb615e944d9b",
      audit_correlation_id: "audit-dashboard-003",
      recommended_action: "Review synthetic Water Emergency detail evidence."
    }
  ],
  equipment_context: {
    equipment_onsite: true,
    moisture_tracking_required: true,
    inventory_entity_available: false,
    required_equipment_notes: [
      {
        work_order_id: "87f35d07-7bb6-4d7d-81fc-787cb05dc4a4",
        required_equipment_notes:
          "Synthetic-only equipment context: air movers and dehumidifier placeholders."
      }
    ],
    unknown_indicators: ["equipment_inventory_not_modeled"]
  },
  visit_chain: {
    total_visits: 2,
    completed_visit_count: 0,
    open_visit_count: 2,
    first_visit_at: "2026-05-16T13:00:00Z",
    latest_visit_at: "2026-05-17T13:00:00Z",
    next_scheduled_visit_at: "2026-05-16T13:00:00Z",
    visit_status_counts: [
      { label: "review_required", count: 1 },
      { label: "scheduled", count: 1 }
    ]
  },
  drying_stage_context: {
    status: "drying_in_progress",
    current_stage: "monitoring",
    next_required_action: "Synthetic drying progress review",
    moisture_tracking_required: true,
    missing_indicators: []
  },
  review_exception_context: {
    total_review_count: 1,
    open_review_count: 1,
    deferred_review_count: 0,
    resolved_review_count: 0,
    archived_review_count: 0,
    critical_unresolved_count: 1,
    escalation_indicator_count: 1,
    review_reason_counts: [{ label: "water_detail_unknown_blocker", count: 1 }],
    blocker_reason_counts: [{ label: "water_detail_unknown_blocker", count: 1 }],
    unknown_indicators: [],
    review_item_ids: ["74c29ad0-a8f0-4b9a-b596-285b35556717"],
    audit_correlation_ids: ["audit-dashboard-003"]
  },
  next_step_readiness: mockWaterEmergencyDashboard.next_step_summary.records[0],
  data_gap_counts: [],
  audit_correlation_ids: ["audit-dashboard-003"],
  timeline_summary: {
    total_events: 1,
    returned_events: 1,
    mutable_event_count: 0,
    audit_correlation_ids: ["audit-dashboard-003"],
    entries: [
      {
        occurred_at: "2026-05-16T07:45:00Z",
        event_type: "water_emergency.extraction_started",
        event_state: "recorded",
        entity_type: "water_emergency",
        entity_id: "e9acb112-409f-4d4f-b98f-4b61a437c4c7",
        route_assignment_id: null,
        visit_id: "bc393a4e-1b61-4daa-a9f9-bb615e944d9b",
        work_order_id: "87f35d07-7bb6-4d7d-81fc-787cb05dc4a4",
        job_id: "72eba727-e804-4dd0-8628-bf7eb1212c60",
        technician_id: "844f52e6-94b7-46e4-9115-34ca2e908afb",
        audit_correlation_id: "audit-dashboard-003",
        previous_state: "new",
        new_state: "extraction_started",
        is_immutable: true
      }
    ]
  }
};
