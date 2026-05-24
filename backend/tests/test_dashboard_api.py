from datetime import UTC, datetime
from uuid import UUID

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.db.session import get_db_session
from app.domain.dashboard import (
    CountBucket,
    DashboardDispatchSummary,
    DashboardOverviewReadModel,
    DispatchLifecycleSummary,
    ExternalExecutionSummary,
    GovernanceAccountabilitySummary,
    ManualReviewActionPreflight,
    ManualReviewAuditLedgerDryRun,
    ManualReviewCommandContract,
    ManualReviewCommandValidation,
    ManualReviewDecisionReadiness,
    ManualReviewDetailLinkedEntityContext,
    ManualReviewDetailReadModel,
    ManualReviewFilterOption,
    ManualReviewFutureActionPreview,
    ManualReviewPermissionReadiness,
    ManualReviewQueueItem,
    ManualReviewQueueReadModel,
    ManualReviewReasonEvidenceContext,
    ManualReviewResultWindowMetadata,
    ManualReviewSafetyGate,
    ManualReviewSortOption,
    ManualReviewSummary,
    ManualReviewTaxonomyMetadata,
    ManualReviewTaxonomyMetadataItem,
    OperationalDashboardSummary,
    OperationalEventTimelineSummary,
    OperationalTimelineEntry,
    ReconciliationRecoverySummary,
    RouteAssignmentSummary,
    WaterEmergencyAgingFollowUpItem,
    WaterEmergencyAgingFollowUpSummary,
    WaterEmergencyDashboardReadModel,
    WaterEmergencyDetailDryingStageContext,
    WaterEmergencyDetailEquipmentContext,
    WaterEmergencyDetailReadModel,
    WaterEmergencyDryingStageSummary,
    WaterEmergencyEquipmentNote,
    WaterEmergencyEquipmentSummary,
    WaterEmergencyFilterOption,
    WaterEmergencyGovernanceMetadata,
    WaterEmergencyGovernanceMetadataItem,
    WaterEmergencyJobReference,
    WaterEmergencyNextStepReadiness,
    WaterEmergencyNextStepReadinessSummary,
    WaterEmergencyOperatorQueueSummary,
    WaterEmergencyQueueItem,
    WaterEmergencyRecordSummary,
    WaterEmergencyResultWindowMetadata,
    WaterEmergencyReviewExceptionContext,
    WaterEmergencyReviewExceptionSummary,
    WaterEmergencyReviewIndicator,
    WaterEmergencySortOption,
    WaterEmergencyViewStateItem,
    WaterEmergencyViewStateSummary,
    WaterEmergencyVisitChain,
    WaterEmergencyVisitChainSummary,
    WaterEmergencyVisitReference,
    WaterEmergencyWorkOrderReference,
)
from app.main import create_app
from app.services.dashboard.service import DashboardReadModelService


def dashboard_overview_contract() -> DashboardOverviewReadModel:
    empty_buckets: tuple[CountBucket, ...] = ()
    lifecycle = DispatchLifecycleSummary(
        intake_lifecycle_counts=(CountBucket(label="approved_for_dispatch", count=1),),
        job_status_counts=(CountBucket(label="awaiting_dispatch", count=1),),
        work_order_status_counts=empty_buckets,
        visit_status_counts=empty_buckets,
        route_status_counts=empty_buckets,
        dispatch_execution_state_counts=empty_buckets,
        dispatch_ready_visits=0,
        dispatched_route_assignments=0,
        water_emergency_records=0,
        water_emergency_separated_intake=0,
        blocker_count=0,
    )
    review = ManualReviewSummary(
        total_items=0,
        open_items=0,
        deferred_items=0,
        resolved_items=0,
        archived_items=0,
        severity_counts=empty_buckets,
        reason_counts=empty_buckets,
        escalation_indicators=0,
        audit_correlation_count=0,
    )
    dispatch = DashboardDispatchSummary(
        route_assignments=RouteAssignmentSummary(
            total_assignments=0,
            status_counts=empty_buckets,
            region_counts=empty_buckets,
            time_window_counts=empty_buckets,
            authorization_state_counts=empty_buckets,
            dispatched_count=0,
            awaiting_dispatch_execution_count=0,
            blocked_count=0,
        ),
        external_execution=ExternalExecutionSummary(
            adapter_state_counts=empty_buckets,
            execution_state_counts=empty_buckets,
            confirmation_state_counts=empty_buckets,
            prepared_count=0,
            execution_completed_count=0,
            execution_failed_count=0,
            confirmation_failed_count=0,
            retry_prepared_count=0,
            reconciliation_required_count=0,
        ),
        reconciliation_recovery=ReconciliationRecoverySummary(
            reconciliation_state_counts=empty_buckets,
            recovery_state_counts=empty_buckets,
            mismatch_count=0,
            divergence_count=0,
            replay_prepared_count=0,
            rollback_prepared_count=0,
            recovery_blocked_count=0,
        ),
        governance_accountability=GovernanceAccountabilitySummary(
            governance_state_counts=empty_buckets,
            accountability_state_counts=empty_buckets,
            operator_approved_count=0,
            intervention_required_count=0,
            escalation_required_count=0,
            incident_prepared_count=0,
            accountability_blocked_count=0,
        ),
    )
    return DashboardOverviewReadModel(
        generated_at=datetime(2026, 5, 16, 12, 30, tzinfo=UTC),
        operational_summary=OperationalDashboardSummary(
            total_jobs=1,
            total_work_orders=0,
            total_visits=0,
            total_route_assignments=0,
            open_manual_reviews=0,
            blocked_operations=0,
            escalation_indicators=0,
            open_water_emergencies=0,
            audit_correlation_count=0,
        ),
        lifecycle_summary=lifecycle,
        manual_review_summary=review,
        dispatch_summary=dispatch,
        timeline_summary=OperationalEventTimelineSummary(
            total_events=0,
            returned_events=0,
            mutable_event_count=0,
            audit_correlation_ids=(),
            entries=(),
        ),
    )


def water_emergency_contract() -> WaterEmergencyDashboardReadModel:
    return WaterEmergencyDashboardReadModel(
        generated_at=datetime(2026, 5, 16, 12, 45, tzinfo=UTC),
        total_records=1,
        open_count=1,
        closed_count=0,
        status_counts=(CountBucket(label="drying_in_progress", count=1),),
        stage_counts=(CountBucket(label="monitoring", count=1),),
        multi_visit_count=1,
        equipment_onsite_count=1,
        moisture_tracking_required_count=1,
        equipment_summary=WaterEmergencyEquipmentSummary(
            equipment_onsite_count=1,
            moisture_tracking_required_count=1,
            work_orders_with_equipment_notes_count=1,
            records_missing_equipment_context_count=0,
            inventory_entity_available=False,
            unknown_counts=(CountBucket(label="equipment_inventory_not_modeled", count=1),),
        ),
        visit_chain_summary=WaterEmergencyVisitChainSummary(
            total_visits=2,
            multi_visit_record_count=1,
            open_records_without_visits_count=0,
            scheduled_visit_count=1,
            completed_visit_count=0,
            visit_status_counts=(CountBucket(label="scheduled", count=1),),
        ),
        drying_stage_summary=WaterEmergencyDryingStageSummary(
            stage_counts=(CountBucket(label="monitoring", count=1),),
            active_stage_counts=(CountBucket(label="monitoring", count=1),),
            missing_stage_count=0,
            moisture_tracking_required_count=1,
        ),
        review_exception_summary=WaterEmergencyReviewExceptionSummary(
            total_review_count=1,
            open_review_count=1,
            deferred_review_count=0,
            resolved_review_count=0,
            archived_review_count=0,
            critical_unresolved_count=1,
            escalation_indicator_count=1,
            review_reason_counts=(CountBucket(label="water_detail_review", count=1),),
            blocker_reason_counts=(CountBucket(label="water_detail_review", count=1),),
            unknown_counts=(),
            review_item_ids=(UUID("00000000-0000-0000-0000-000000000035"),),
            audit_correlation_ids=("audit-water-001",),
        ),
        next_step_summary=WaterEmergencyNextStepReadinessSummary(
            total_records=1,
            needs_attention_count=1,
            closed_without_active_action_count=0,
            label_counts=(
                CountBucket(label="needs_manual_review", count=1),
                CountBucket(label="needs_operator_decision", count=1),
            ),
            blocker_counts=(CountBucket(label="water_detail_review", count=1),),
            records=(
                WaterEmergencyNextStepReadiness(
                    water_emergency_id=UUID("00000000-0000-0000-0000-000000000031"),
                    primary_label="needs_manual_review",
                    labels=("needs_manual_review", "needs_operator_decision"),
                    summary=(
                        "Open Manual Review evidence exists; operator review remains required "
                        "before any future Water Emergency workflow step."
                    ),
                    reason_codes=("water_detail_review",),
                    evidence_references=(
                        "job:00000000-0000-0000-0000-000000000032",
                        "water_emergency:00000000-0000-0000-0000-000000000031",
                    ),
                    current_status="drying_in_progress",
                    current_stage="monitoring",
                    open_review_count=1,
                    critical_alert_count=0,
                    blocker_count=1,
                    unknown_count=0,
                    requires_operator_attention=True,
                    related_job_id=UUID("00000000-0000-0000-0000-000000000032"),
                    related_work_order_ids=(),
                    related_visit_ids=(UUID("00000000-0000-0000-0000-000000000033"),),
                    audit_correlation_ids=("audit-water-001",),
                ),
            ),
        ),
        operator_queue_summary=WaterEmergencyOperatorQueueSummary(
            total_records=1,
            active_attention_count=1,
            closed_or_resolved_count=0,
            critical_attention_count=1,
            queue_group_counts=(CountBucket(label="active_attention", count=1),),
            attention_label_counts=(CountBucket(label="critical_attention", count=1),),
            items=(
                WaterEmergencyQueueItem(
                    water_emergency_id=UUID("00000000-0000-0000-0000-000000000031"),
                    attention_label="critical_attention",
                    queue_group="active_attention",
                    attention_rank=10,
                    readiness_labels=("needs_manual_review", "needs_operator_decision"),
                    summary=("Critical Water Emergency review evidence needs operator attention."),
                    reason_codes=("water_detail_review",),
                    evidence_references=(
                        "job:00000000-0000-0000-0000-000000000032",
                        "water_emergency:00000000-0000-0000-0000-000000000031",
                    ),
                    current_status="drying_in_progress",
                    current_stage="monitoring",
                    open_review_count=1,
                    critical_alert_count=1,
                    blocker_count=1,
                    unknown_count=0,
                    related_job_id=UUID("00000000-0000-0000-0000-000000000032"),
                    related_work_order_ids=(),
                    related_visit_ids=(UUID("00000000-0000-0000-0000-000000000033"),),
                    audit_correlation_ids=("audit-water-001",),
                ),
            ),
        ),
        aging_followup_summary=WaterEmergencyAgingFollowUpSummary(
            total_records=1,
            active_timing_risk_count=1,
            closed_or_resolved_count=0,
            followup_due_count=0,
            followup_overdue_count=0,
            stale_evidence_count=0,
            unknown_timing_count=0,
            label_counts=(CountBucket(label="waiting_for_review", count=1),),
            age_bucket_counts=(CountBucket(label="under_24h", count=1),),
            followup_bucket_counts=(CountBucket(label="followup_not_due", count=1),),
            items=(
                WaterEmergencyAgingFollowUpItem(
                    water_emergency_id=UUID("00000000-0000-0000-0000-000000000031"),
                    time_sensitivity_label="waiting_for_review",
                    timing_group="manual_review",
                    timing_rank=20,
                    age_bucket="under_24h",
                    followup_bucket="followup_not_due",
                    age_hours=4,
                    hours_since_last_visit=2,
                    hours_since_last_review=1,
                    hours_since_last_event=1,
                    opened_at=datetime(2026, 5, 16, 8, 0, tzinfo=UTC),
                    last_visit_at=datetime(2026, 5, 16, 10, 0, tzinfo=UTC),
                    last_review_at=datetime(2026, 5, 16, 11, 0, tzinfo=UTC),
                    last_event_at=datetime(2026, 5, 16, 11, 0, tzinfo=UTC),
                    closed_at=None,
                    summary=(
                        "Open Manual Review evidence exists; Manual Review remains authoritative."
                    ),
                    reason_codes=("waiting_for_review", "water_detail_review"),
                    missing_timestamp_indicators=(),
                    stale_indicator_count=0,
                    requires_operator_attention=True,
                    related_job_id=UUID("00000000-0000-0000-0000-000000000032"),
                    related_work_order_ids=(),
                    related_visit_ids=(UUID("00000000-0000-0000-0000-000000000033"),),
                    audit_correlation_ids=("audit-water-001",),
                    evidence_references=(
                        "job:00000000-0000-0000-0000-000000000032",
                        "water_emergency:00000000-0000-0000-0000-000000000031",
                    ),
                ),
            ),
        ),
        view_state_summary=WaterEmergencyViewStateSummary(
            total_records=1,
            active_record_count=1,
            closed_or_resolved_count=0,
            available_filters=(
                WaterEmergencyFilterOption(
                    key="all",
                    label="All records",
                    count=1,
                    description="Every persisted Water Emergency record.",
                ),
                WaterEmergencyFilterOption(
                    key="active",
                    label="Active records",
                    count=1,
                    description="Open Water Emergency records.",
                ),
                WaterEmergencyFilterOption(
                    key="needs_manual_review",
                    label="Needs Manual Review",
                    count=1,
                    description="Records with Manual Review evidence.",
                ),
            ),
            sort_options=(
                WaterEmergencySortOption(
                    key="attention",
                    label="Attention priority",
                    description="Critical, review, blocker, timing, and closed ordering.",
                ),
            ),
            group_counts=(CountBucket(label="needs_manual_review", count=1),),
            items=(
                WaterEmergencyViewStateItem(
                    water_emergency_id=UUID("00000000-0000-0000-0000-000000000031"),
                    filter_groups=("all", "active", "needs_manual_review"),
                    primary_filter_group="needs_manual_review",
                    sort_rank=20,
                    sort_label="needs_manual_review",
                    queue_group="active_attention",
                    attention_label="critical_attention",
                    time_sensitivity_label="waiting_for_review",
                    readiness_label="needs_manual_review",
                    is_active=True,
                    current_status="drying_in_progress",
                    current_stage="monitoring",
                    open_review_count=1,
                    critical_alert_count=1,
                    blocker_count=1,
                    unknown_count=0,
                    last_activity_at=datetime(2026, 5, 16, 11, 0, tzinfo=UTC),
                    summary="Critical Water Emergency review evidence needs operator attention.",
                    reason_codes=("waiting_for_review", "water_detail_review"),
                    related_job_id=UUID("00000000-0000-0000-0000-000000000032"),
                    related_work_order_ids=(),
                    related_visit_ids=(UUID("00000000-0000-0000-0000-000000000033"),),
                    audit_correlation_ids=("audit-water-001",),
                    evidence_references=(
                        "job:00000000-0000-0000-0000-000000000032",
                        "water_emergency:00000000-0000-0000-0000-000000000031",
                    ),
                ),
            ),
        ),
        governance_metadata=WaterEmergencyGovernanceMetadata(
            randall_authorized_phase_0_baseline=True,
            source="phase_0_visibility_heuristic",
            legal_or_insurance_policy=False,
            requires_alfonso_owner_review=False,
            baseline_note=(
                "Randall-authorized Phase 0 visibility baseline for internal software labels."
            ),
            timing_heuristic_note=(
                "Timing labels are conservative software visibility heuristics, "
                "not final SLA enforcement."
            ),
            provisional_filter_groups=(
                WaterEmergencyGovernanceMetadataItem(
                    key="needs_manual_review",
                    label="Needs Manual Review",
                    category="filter_group",
                    source="phase_0_visibility_heuristic",
                    randall_authorized_phase_0_baseline=True,
                    legal_or_insurance_policy=False,
                    requires_alfonso_owner_review=False,
                    reason="Internal read-only filter label.",
                ),
            ),
            provisional_attention_labels=(
                WaterEmergencyGovernanceMetadataItem(
                    key="critical_attention",
                    label="Critical attention",
                    category="attention_label",
                    source="phase_0_visibility_heuristic",
                    randall_authorized_phase_0_baseline=True,
                    legal_or_insurance_policy=False,
                    requires_alfonso_owner_review=False,
                    reason="Internal read-only attention label.",
                ),
            ),
            provisional_timing_labels=(
                WaterEmergencyGovernanceMetadataItem(
                    key="waiting_for_review",
                    label="Waiting for review",
                    category="timing_label",
                    source="phase_0_visibility_heuristic",
                    randall_authorized_phase_0_baseline=True,
                    legal_or_insurance_policy=False,
                    requires_alfonso_owner_review=False,
                    reason="Internal read-only timing label.",
                ),
            ),
            provisional_readiness_labels=(
                WaterEmergencyGovernanceMetadataItem(
                    key="needs_manual_review",
                    label="Needs Manual Review",
                    category="readiness_label",
                    source="phase_0_visibility_heuristic",
                    randall_authorized_phase_0_baseline=True,
                    legal_or_insurance_policy=False,
                    requires_alfonso_owner_review=False,
                    reason="Internal read-only readiness label.",
                ),
            ),
            owner_review_required_items=(
                WaterEmergencyGovernanceMetadataItem(
                    key="formal_sla_or_insurance_policy",
                    label="Formal SLA or insurance policy",
                    category="owner_review_boundary",
                    source="owner_review_required",
                    randall_authorized_phase_0_baseline=False,
                    legal_or_insurance_policy=True,
                    requires_alfonso_owner_review=True,
                    reason=(
                        "Final SLA, drying certification, insurance, warranty, "
                        "or customer-facing policy can create company liability."
                    ),
                ),
            ),
            future_role_visibility_roles=(
                "office_admin",
                "operations_manager",
                "dispatcher",
                "reviewer",
                "technician",
                "owner",
            ),
        ),
        result_window_metadata=WaterEmergencyResultWindowMetadata(
            total_count=1,
            visible_count=1,
            result_limit=1,
            has_more=False,
            sort_key="attention",
            generated_at=datetime(2026, 5, 16, 12, 45, tzinfo=UTC),
        ),
        related_job_count=1,
        related_work_order_count=0,
        related_visit_count=2,
        review_indicator_count=1,
        escalation_indicator_count=1,
        data_gap_counts=(),
        audit_correlation_count=1,
        records=(
            WaterEmergencyRecordSummary(
                water_emergency_id=UUID("00000000-0000-0000-0000-000000000031"),
                job_id=UUID("00000000-0000-0000-0000-000000000032"),
                status="drying_in_progress",
                drying_stage="monitoring",
                next_required_action="Schedule drying check.",
                is_open=True,
                equipment_onsite=True,
                moisture_tracking_required=True,
                opened_at=datetime(2026, 5, 16, 8, 0, tzinfo=UTC),
                closed_at=None,
                related_work_order_ids=(),
                related_visit_ids=(UUID("00000000-0000-0000-0000-000000000033"),),
                open_review_count=1,
                timeline_event_count=1,
                audit_correlation_ids=("audit-water-001",),
            ),
        ),
        timeline_summary=OperationalEventTimelineSummary(
            total_events=0,
            returned_events=0,
            mutable_event_count=0,
            audit_correlation_ids=(),
            entries=(),
        ),
    )


def water_emergency_detail_contract() -> WaterEmergencyDetailReadModel:
    record = water_emergency_contract().records[0]
    return WaterEmergencyDetailReadModel(
        generated_at=datetime(2026, 5, 16, 12, 50, tzinfo=UTC),
        record=record,
        job=WaterEmergencyJobReference(
            job_id=record.job_id,
            job_type="water_emergency",
            status="active",
            review_status=None,
            priority="urgent",
            requested_date=None,
            scheduled_date=None,
            source_system="module32_test",
            source_event_id="module32-water-detail",
        ),
        work_orders=(
            WaterEmergencyWorkOrderReference(
                work_order_id=UUID("00000000-0000-0000-0000-000000000034"),
                work_order_number="WATER-DETAIL-001",
                status="generated",
                dispatch_status="not_dispatched",
                assigned_technician_id=None,
                audit_correlation_id="audit-water-001",
            ),
        ),
        visits=(
            WaterEmergencyVisitReference(
                visit_id=UUID("00000000-0000-0000-0000-000000000033"),
                work_order_id=UUID("00000000-0000-0000-0000-000000000034"),
                technician_id=None,
                visit_type="water_emergency",
                status="scheduled",
                scheduled_start_at=datetime(2026, 5, 16, 13, 0, tzinfo=UTC),
                scheduled_end_at=None,
                arrived_at=None,
                completed_at=None,
                audit_correlation_id="audit-water-001",
            ),
        ),
        review_indicators=(
            WaterEmergencyReviewIndicator(
                review_item_id=UUID("00000000-0000-0000-0000-000000000035"),
                status="open",
                severity="high",
                reason_code="water_detail_review",
                confidence_score=70.0,
                entity_type="water_emergency",
                entity_id=record.water_emergency_id,
                job_id=record.job_id,
                visit_id=UUID("00000000-0000-0000-0000-000000000033"),
                audit_correlation_id="audit-water-001",
                recommended_action="Review synthetic detail evidence.",
            ),
        ),
        equipment_context=WaterEmergencyDetailEquipmentContext(
            equipment_onsite=True,
            moisture_tracking_required=True,
            inventory_entity_available=False,
            required_equipment_notes=(
                WaterEmergencyEquipmentNote(
                    work_order_id=UUID("00000000-0000-0000-0000-000000000034"),
                    required_equipment_notes=(
                        "Synthetic-only detail equipment notes for read-model testing."
                    ),
                ),
            ),
            unknown_indicators=("equipment_inventory_not_modeled",),
        ),
        visit_chain=WaterEmergencyVisitChain(
            total_visits=1,
            completed_visit_count=0,
            open_visit_count=1,
            first_visit_at=datetime(2026, 5, 16, 13, 0, tzinfo=UTC),
            latest_visit_at=datetime(2026, 5, 16, 13, 0, tzinfo=UTC),
            next_scheduled_visit_at=datetime(2026, 5, 16, 13, 0, tzinfo=UTC),
            visit_status_counts=(CountBucket(label="scheduled", count=1),),
        ),
        drying_stage_context=WaterEmergencyDetailDryingStageContext(
            status="drying_in_progress",
            current_stage="monitoring",
            next_required_action="Schedule drying check.",
            moisture_tracking_required=True,
            missing_indicators=(),
        ),
        review_exception_context=WaterEmergencyReviewExceptionContext(
            total_review_count=1,
            open_review_count=1,
            deferred_review_count=0,
            resolved_review_count=0,
            archived_review_count=0,
            critical_unresolved_count=0,
            escalation_indicator_count=1,
            review_reason_counts=(CountBucket(label="water_detail_review", count=1),),
            blocker_reason_counts=(CountBucket(label="water_detail_review", count=1),),
            unknown_indicators=(),
            review_item_ids=(UUID("00000000-0000-0000-0000-000000000035"),),
            audit_correlation_ids=("audit-water-001",),
        ),
        next_step_readiness=WaterEmergencyNextStepReadiness(
            water_emergency_id=record.water_emergency_id,
            primary_label="needs_manual_review",
            labels=("needs_manual_review", "needs_operator_decision"),
            summary=(
                "Open Manual Review evidence exists; operator review remains required before "
                "any future Water Emergency workflow step."
            ),
            reason_codes=("water_detail_review",),
            evidence_references=(
                f"job:{record.job_id}",
                f"water_emergency:{record.water_emergency_id}",
                "visit:00000000-0000-0000-0000-000000000033",
                "review:00000000-0000-0000-0000-000000000035",
            ),
            current_status="drying_in_progress",
            current_stage="monitoring",
            open_review_count=1,
            critical_alert_count=0,
            blocker_count=1,
            unknown_count=0,
            requires_operator_attention=True,
            related_job_id=record.job_id,
            related_work_order_ids=(UUID("00000000-0000-0000-0000-000000000034"),),
            related_visit_ids=(UUID("00000000-0000-0000-0000-000000000033"),),
            audit_correlation_ids=("audit-water-001",),
        ),
        data_gap_counts=(),
        audit_correlation_ids=("audit-water-001",),
        timeline_summary=OperationalEventTimelineSummary(
            total_events=1,
            returned_events=1,
            mutable_event_count=0,
            audit_correlation_ids=("audit-water-001",),
            entries=(
                OperationalTimelineEntry(
                    occurred_at=datetime(2026, 5, 16, 9, 45, tzinfo=UTC),
                    event_type="water_emergency.extraction_started",
                    event_state="recorded",
                    entity_type="water_emergency",
                    entity_id=record.water_emergency_id,
                    route_assignment_id=None,
                    visit_id=UUID("00000000-0000-0000-0000-000000000033"),
                    work_order_id=UUID("00000000-0000-0000-0000-000000000034"),
                    job_id=record.job_id,
                    technician_id=None,
                    audit_correlation_id="audit-water-001",
                    previous_state="new",
                    new_state="extraction_started",
                    is_immutable=True,
                ),
            ),
        ),
    )


def manual_review_command_validation_contract(
    *,
    label: str,
    candidate_future_command_type: str,
    audit_correlation_reference: str,
    evidence_references: tuple[str, ...],
    validation_status: str = "future_requirements_visible",
    validation_blockers: tuple[str, ...] = ("validation_read_only_phase",),
    validation_warnings: tuple[str, ...] = ("validation_warning_requires_review",),
    entity_context_present: bool = True,
    status_allows_future_action: bool = True,
    water_emergency_scope_checked: bool = True,
    water_emergency_scope_required: bool = False,
    no_conflict_blocker: bool = True,
    missing_data_reviewed: bool = True,
    missing_data_required: bool = False,
    requires_water_emergency_scope_check: bool = False,
) -> ManualReviewCommandValidation:
    return ManualReviewCommandValidation(
        label=label,
        summary=(
            "Manual Review command validation is visible as read-only Phase 0 "
            "preparation and cannot execute commands."
        ),
        candidate_future_command_type=candidate_future_command_type,
        validation_status=validation_status,
        validation_blockers=validation_blockers,
        validation_warnings=validation_warnings,
        safety_gates=(
            ManualReviewSafetyGate(
                key="entity_context_present",
                label="Entity context present",
                passed=entity_context_present,
                required=True,
                reason="A future command must be tied to deterministic entity context.",
            ),
            ManualReviewSafetyGate(
                key="status_allows_future_action",
                label="Status allows future action",
                passed=status_allows_future_action,
                required=True,
                reason="Resolved or archived reviews cannot be active command targets.",
            ),
            ManualReviewSafetyGate(
                key="review_not_resolved_or_archived",
                label="Review not resolved or archived",
                passed=status_allows_future_action,
                required=True,
                reason="Historical reviews stay separated from active command readiness.",
            ),
            ManualReviewSafetyGate(
                key="water_emergency_scope_checked",
                label="Water Emergency scope checked",
                passed=water_emergency_scope_checked,
                required=water_emergency_scope_required,
                reason="Water Emergency reviews require separated future scope checks.",
            ),
            ManualReviewSafetyGate(
                key="no_conflict_blocker",
                label="No conflict blocker",
                passed=no_conflict_blocker,
                required=True,
                reason="Conflict evidence must remain blocked for future review.",
            ),
            ManualReviewSafetyGate(
                key="missing_data_reviewed",
                label="Missing data reviewed",
                passed=missing_data_reviewed,
                required=missing_data_required,
                reason="Missing data requires operator-safe evidence review.",
            ),
            ManualReviewSafetyGate(
                key="operator_identity_required",
                label="Operator identity required",
                passed=True,
                required=True,
                reason="Future commands must declare operator identity capture.",
            ),
            ManualReviewSafetyGate(
                key="role_authorization_required",
                label="Role authorization required",
                passed=True,
                required=True,
                reason="Future commands must declare role authorization.",
            ),
            ManualReviewSafetyGate(
                key="audit_reason_required",
                label="Audit reason required",
                passed=True,
                required=True,
                reason="Future commands must declare audit reason capture.",
            ),
            ManualReviewSafetyGate(
                key="idempotency_key_required",
                label="Idempotency key required",
                passed=True,
                required=True,
                reason="Future commands must declare an idempotency key.",
            ),
            ManualReviewSafetyGate(
                key="immutable_event_required",
                label="Immutable event required",
                passed=True,
                required=True,
                reason="Future commands must declare immutable event recording.",
            ),
            ManualReviewSafetyGate(
                key="post_action_consistency_check_required",
                label="Post-action consistency check required",
                passed=True,
                required=True,
                reason="Future commands must declare post-action consistency checks.",
            ),
            ManualReviewSafetyGate(
                key="phase_allows_execution",
                label="Phase allows execution",
                passed=False,
                required=True,
                reason=(
                    "Phase 0 exposes validation visibility only; Manual Review command "
                    "execution is disabled."
                ),
            ),
        ),
        audit_correlation_references=(audit_correlation_reference,),
        evidence_references=evidence_references,
        is_currently_executable=False,
        phase_allows_execution=False,
        execution_unavailable_reason=(
            "Manual Review command validation is visibility only; execution is not "
            "available in Phase 0."
        ),
        requires_audit_reason=True,
        requires_operator_identity=True,
        requires_role_authorization=True,
        requires_idempotency_key=True,
        requires_immutable_event_recording=True,
        requires_post_action_consistency_check=True,
        requires_water_emergency_scope_check=requires_water_emergency_scope_check,
        requires_linked_entity_context=True,
    )


def manual_review_permission_readiness_contract(
    *,
    label: str,
    candidate_future_command_type: str = "request_information",
    future_required_roles: tuple[str, ...] = ("reviewer", "operations_manager", "dispatcher"),
    future_required_permissions: tuple[str, ...] = (
        "manual_review.future_command.view",
        "manual_review.future_command.prepare",
        "manual_review.audit_actor.capture",
        "manual_review.audit_reason.capture",
        "manual_review.idempotency.require",
        "manual_review.immutable_event.require",
        "manual_review.consistency_check.require",
        "manual_review.dispatch_review.prepare",
    ),
    extra_required_labels: tuple[str, ...] = (),
    audit_correlation_reference: str = "audit:audit-manual-review-api-001",
    evidence_references: tuple[str, ...] = (),
    requires_water_emergency_scope_check: bool = False,
) -> ManualReviewPermissionReadiness:
    return ManualReviewPermissionReadiness(
        label=label,
        summary=(
            "Manual Review permission readiness is read-only Phase 0 visibility for "
            "future auth and role authorization."
        ),
        candidate_future_command_type=candidate_future_command_type,
        future_required_roles=future_required_roles,
        future_forbidden_roles=("system_service", "technician", "unknown_operator"),
        future_required_permissions=future_required_permissions,
        required_permission_labels=(
            "permission_read_only_phase",
            "requires_future_auth",
            "requires_operator_identity",
            "requires_role_authorization",
            "requires_audit_reason",
            "requires_idempotency_key",
            "requires_immutable_event_recording",
            "requires_post_action_consistency_check",
            "service_account_not_allowed",
            "technician_action_not_allowed",
            "command_not_executable_phase_0",
            *extra_required_labels,
        ),
        identity_requirement_labels=(
            "requires_future_auth",
            "requires_operator_identity",
            "permission_blocked_unknown_operator",
            "service_account_not_allowed",
            "technician_action_not_allowed",
        ),
        audit_correlation_references=(audit_correlation_reference,),
        evidence_references=evidence_references,
        is_currently_executable=False,
        phase_allows_execution=False,
        execution_unavailable_reason=(
            "Manual Review permission readiness is visibility only; auth, RBAC, and "
            "action execution are not available in Phase 0."
        ),
        identity_unavailable_reason=(
            "Phase 0 does not implement login, sessions, token handling, operator identity, "
            "or RBAC; future Manual Review commands remain non-executable."
        ),
        future_operator_identity_required=True,
        future_operator_id_required=True,
        future_operator_display_name_required=True,
        future_operator_email_required=True,
        future_authentication_provider_boundary=(
            "Future ACS-FSM auth provider boundary is not implemented in Phase 0; "
            "Manual Review commands must not rely on service accounts or fake roles."
        ),
        future_role_authorization_required=True,
        future_permission_set_required=True,
        future_audit_actor_required=True,
        future_audit_reason_required=True,
        future_idempotency_key_required=True,
        future_immutable_event_required=True,
        future_post_action_consistency_check_required=True,
        impersonation_allowed=False,
        service_account_allowed=False,
        technician_action_allowed=False,
        requires_water_emergency_scope_check=requires_water_emergency_scope_check,
    )


def manual_review_queue_contract() -> ManualReviewQueueReadModel:
    return ManualReviewQueueReadModel(
        generated_at=datetime(2026, 5, 16, 12, 50, tzinfo=UTC),
        total_items=2,
        open_items=1,
        deferred_items=0,
        resolved_items=1,
        archived_items=0,
        active_attention_count=1,
        water_emergency_related_count=1,
        dispatch_related_count=1,
        blocked_count=1,
        status_counts=(
            CountBucket(label="open", count=1),
            CountBucket(label="resolved", count=1),
        ),
        reason_counts=(
            CountBucket(label="missing_customer_data", count=1),
            CountBucket(label="water_emergency_review", count=1),
        ),
        severity_counts=(
            CountBucket(label="critical", count=1),
            CountBucket(label="low", count=1),
        ),
        group_counts=(
            CountBucket(label="open", count=1),
            CountBucket(label="resolved", count=1),
            CountBucket(label="water_emergency_related", count=1),
            CountBucket(label="dispatch_related", count=1),
        ),
        decision_readiness_counts=(
            CountBucket(label="blocked_by_missing_data", count=1),
            CountBucket(label="resolved_or_archived", count=1),
        ),
        action_preflight_counts=(
            CountBucket(label="blocked_by_missing_data", count=1),
            CountBucket(label="blocked_by_resolved_or_archived_status", count=1),
        ),
        future_action_preview_counts=(
            CountBucket(label="future_request_information_preview", count=1),
            CountBucket(label="no_action_available_resolved_or_archived", count=1),
        ),
        command_contract_counts=(
            CountBucket(label="requires_preflight_pass", count=1),
            CountBucket(label="command_not_executable_phase_0", count=1),
        ),
        audit_ledger_dry_run_counts=(
            CountBucket(label="dry_run_only_phase_0", count=1),
            CountBucket(label="command_execution_blocked_resolved_or_archived", count=1),
        ),
        command_validation_counts=(
            CountBucket(label="validation_warning_requires_review", count=1),
            CountBucket(label="validation_blocked_resolved_or_archived", count=1),
        ),
        permission_readiness_counts=(
            CountBucket(label="permission_ready_for_future_auth_phase", count=1),
            CountBucket(label="permission_blocked_resolved_or_archived", count=1),
        ),
        age_bucket_counts=(
            CountBucket(label="new", count=1),
            CountBucket(label="resolved_or_archived", count=1),
        ),
        audit_correlation_count=2,
        taxonomy_metadata=ManualReviewTaxonomyMetadata(
            randall_authorized_phase_0_baseline=True,
            source="phase_0_visibility_heuristic",
            legal_or_insurance_policy=False,
            requires_alfonso_owner_review=False,
            baseline_note=(
                "Manual Review queue labels are Randall-authorized Phase 0 "
                "visibility baselines only."
            ),
            group_definitions=(
                ManualReviewTaxonomyMetadataItem(
                    key="water_emergency_related",
                    label="Water Emergency related",
                    category="manual_review_visibility",
                    source="phase_0_visibility_heuristic",
                    randall_authorized_phase_0_baseline=True,
                    legal_or_insurance_policy=False,
                    requires_alfonso_owner_review=False,
                    reason="Separates Water Emergency review visibility from standard dispatch.",
                ),
            ),
        ),
        available_filters=(
            ManualReviewFilterOption(
                key="all",
                label="All reviews",
                count=2,
                description="Every persisted Manual Review item returned by this read-only queue.",
            ),
            ManualReviewFilterOption(
                key="active_attention",
                label="Active attention",
                count=1,
                description="Open or deferred review items still requiring operator attention.",
            ),
            ManualReviewFilterOption(
                key="water_emergency_related",
                label="Water Emergency related",
                count=1,
                description="Review items specifically tied to Water Emergency records.",
            ),
        ),
        sort_options=(
            ManualReviewSortOption(
                key="attention",
                label="Attention priority",
                description="Active, blocker, severity, status, and created-time ordering.",
            ),
            ManualReviewSortOption(
                key="newest",
                label="Newest first",
                description="Most recently created Manual Review items first.",
            ),
        ),
        result_window_metadata=ManualReviewResultWindowMetadata(
            total_count=2,
            visible_count=2,
            result_limit=2,
            has_more=False,
            sort_key="attention",
            generated_at=datetime(2026, 5, 16, 12, 50, tzinfo=UTC),
        ),
        items=(
            ManualReviewQueueItem(
                review_item_id=UUID("00000000-0000-0000-0000-000000000040"),
                status="open",
                severity="critical",
                reason_code="missing_customer_data",
                visibility_groups=("open", "missing_data", "dispatch_related"),
                primary_group="missing_data",
                entity_type="job",
                entity_id=UUID("00000000-0000-0000-0000-000000000041"),
                job_id=UUID("00000000-0000-0000-0000-000000000041"),
                work_order_id=UUID("00000000-0000-0000-0000-000000000042"),
                visit_id=None,
                route_assignment_id=None,
                water_emergency_id=None,
                created_at=datetime(2026, 5, 16, 11, 0, tzinfo=UTC),
                updated_at=datetime(2026, 5, 16, 11, 0, tzinfo=UTC),
                reviewed_at=None,
                deferred_until=None,
                resolved_at=None,
                age_bucket="new",
                age_hours=1,
                blocker_indicator=True,
                attention_indicator=True,
                confidence_score=66.0,
                recommended_action="Review missing synthetic data.",
                audit_correlation_id="audit-manual-review-api-001",
                decision_readiness=ManualReviewDecisionReadiness(
                    label="blocked_by_missing_data",
                    summary="Missing data evidence needs operator-safe review.",
                    reason_codes=("missing_data_evidence", "active_manual_review"),
                    evidence_references=(
                        "review:00000000-0000-0000-0000-000000000040",
                        "job:00000000-0000-0000-0000-000000000041",
                        "work_order:00000000-0000-0000-0000-000000000042",
                        "audit:audit-manual-review-api-001",
                    ),
                    is_active_decision_need=True,
                    is_resolution_candidate=False,
                ),
                action_preflight=ManualReviewActionPreflight(
                    label="blocked_by_missing_data",
                    summary=(
                        "Future Manual Review action is blocked until missing-data "
                        "context is addressed. This Phase 0 label is read-only."
                    ),
                    blocker_codes=("missing_data_context_required",),
                    required_future_controls=(
                        "action_not_available_read_only_phase",
                        "requires_future_auth",
                        "requires_operator_identity",
                        "requires_audit_reason",
                    ),
                    evidence_references=(
                        "review:00000000-0000-0000-0000-000000000040",
                        "job:00000000-0000-0000-0000-000000000041",
                        "work_order:00000000-0000-0000-0000-000000000042",
                        "audit:audit-manual-review-api-001",
                    ),
                    is_currently_executable=False,
                    requires_operator_identity=True,
                    requires_audit_reason=True,
                ),
                future_action_preview=ManualReviewFutureActionPreview(
                    label="future_request_information_preview",
                    description=(
                        "A future authenticated workflow may request missing information, "
                        "but this Phase 0 preview is not executable."
                    ),
                    expected_outcome_summary=(
                        "Expected outcome preview: operator gathers missing information before "
                        "any resolution action is designed."
                    ),
                    impacted_entity_summary=(
                        "Impacted entities: review:00000000-0000-0000-0000-000000000040, "
                        "job:00000000-0000-0000-0000-000000000041, "
                        "work_order:00000000-0000-0000-0000-000000000042"
                    ),
                    impacted_entity_references=(
                        "review:00000000-0000-0000-0000-000000000040",
                        "job:00000000-0000-0000-0000-000000000041",
                        "work_order:00000000-0000-0000-0000-000000000042",
                    ),
                    blocker_codes=("missing_data_context_required",),
                    required_future_controls=(
                        "preview_not_executable_read_only_phase",
                        "requires_future_auth",
                        "requires_operator_identity",
                        "requires_audit_reason",
                    ),
                    evidence_references=(
                        "review:00000000-0000-0000-0000-000000000040",
                        "job:00000000-0000-0000-0000-000000000041",
                        "work_order:00000000-0000-0000-0000-000000000042",
                        "audit:audit-manual-review-api-001",
                    ),
                    is_currently_executable=False,
                    requires_operator_identity=True,
                    requires_audit_reason=True,
                ),
                command_contract=ManualReviewCommandContract(
                    label="requires_preflight_pass",
                    summary=(
                        "Future Manual Review commands require missing-data context and "
                        "the future audit envelope before execution can be implemented."
                    ),
                    future_command_candidates=("request_information",),
                    required_contract_labels=(
                        "command_contract_read_only_phase",
                        "requires_future_auth",
                        "requires_operator_identity",
                        "requires_role_authorization",
                        "requires_audit_reason",
                        "requires_idempotency_key",
                        "requires_preflight_pass",
                        "requires_immutable_event_recording",
                        "requires_post_action_consistency_check",
                        "command_not_executable_phase_0",
                    ),
                    impacted_entity_summary=(
                        "Impacted entities: review:00000000-0000-0000-0000-000000000040, "
                        "job:00000000-0000-0000-0000-000000000041, "
                        "work_order:00000000-0000-0000-0000-000000000042"
                    ),
                    impacted_entity_references=(
                        "review:00000000-0000-0000-0000-000000000040",
                        "job:00000000-0000-0000-0000-000000000041",
                        "work_order:00000000-0000-0000-0000-000000000042",
                    ),
                    blocker_codes=("missing_data_context_required",),
                    evidence_references=(
                        "review:00000000-0000-0000-0000-000000000040",
                        "job:00000000-0000-0000-0000-000000000041",
                        "work_order:00000000-0000-0000-0000-000000000042",
                        "audit:audit-manual-review-api-001",
                    ),
                    is_currently_executable=False,
                    not_executable_reason=("Manual Review commands are not executable in Phase 0."),
                    requires_operator_identity=True,
                    requires_role_authorization=True,
                    requires_audit_reason=True,
                    requires_idempotency_key=True,
                    requires_immutable_event_recording=True,
                    requires_post_action_consistency_check=True,
                ),
                audit_ledger_dry_run=ManualReviewAuditLedgerDryRun(
                    label="dry_run_only_phase_0",
                    summary=(
                        "Future Manual Review command dry-run is visible for audit-ledger "
                        "preparation only and cannot execute in Phase 0."
                    ),
                    future_command_type_candidates=("request_information",),
                    required_labels=(
                        "dry_run_only_phase_0",
                        "audit_envelope_required",
                        "operator_identity_required",
                        "role_authorization_required",
                        "idempotency_key_required",
                        "immutable_event_required",
                        "consistency_check_required",
                        "command_execution_blocked_read_only_phase",
                    ),
                    proposed_future_event_type=("manual_review.future_command.request_information"),
                    proposed_future_event_state="proposed_not_recorded",
                    proposed_future_audit_envelope_fields=(
                        "review_item_id",
                        "future_command_type",
                        "operator_identity_id",
                        "role_authorization",
                        "audit_reason",
                        "idempotency_key",
                        "preflight_label",
                        "command_contract_label",
                        "impacted_entity_references",
                        "audit_correlation_id",
                        "occurred_at",
                        "immutable_event_fingerprint",
                        "post_action_consistency_check",
                    ),
                    proposed_future_idempotency_scope=(
                        "manual_review:00000000-0000-0000-0000-000000000040:request_information"
                    ),
                    proposed_future_consistency_check_summary=(
                        "Future command execution would re-read the review item, linked "
                        "entities, immutable event fingerprint, and post-action state before "
                        "presenting any outcome."
                    ),
                    audit_correlation_references=("audit:audit-manual-review-api-001",),
                    evidence_references=(
                        "review:00000000-0000-0000-0000-000000000040",
                        "job:00000000-0000-0000-0000-000000000041",
                        "work_order:00000000-0000-0000-0000-000000000042",
                        "audit:audit-manual-review-api-001",
                    ),
                    is_currently_executable=False,
                    phase_allows_execution=False,
                    execution_unavailable_reason=(
                        "Manual Review command dry-runs are visibility only; execution "
                        "is not available in Phase 0."
                    ),
                    requires_operator_identity=True,
                    requires_role_authorization=True,
                    requires_audit_reason=True,
                    requires_idempotency_key=True,
                    requires_immutable_event_recording=True,
                    requires_post_action_consistency_check=True,
                ),
                command_validation=manual_review_command_validation_contract(
                    label="validation_warning_requires_review",
                    candidate_future_command_type="request_information",
                    validation_status="warning_missing_data_review_required",
                    validation_warnings=(
                        "validation_warning_requires_review",
                        "missing_data_review_required",
                    ),
                    missing_data_reviewed=False,
                    missing_data_required=True,
                    audit_correlation_reference="audit:audit-manual-review-api-001",
                    evidence_references=(
                        "review:00000000-0000-0000-0000-000000000040",
                        "job:00000000-0000-0000-0000-000000000041",
                        "work_order:00000000-0000-0000-0000-000000000042",
                        "audit:audit-manual-review-api-001",
                    ),
                ),
                permission_readiness=manual_review_permission_readiness_contract(
                    label="permission_ready_for_future_auth_phase",
                    candidate_future_command_type="request_information",
                    extra_required_labels=(
                        "permission_ready_for_future_auth_phase",
                        "requires_reviewer_role",
                        "requires_dispatcher_role",
                        "requires_operations_manager_role",
                    ),
                    audit_correlation_reference="audit:audit-manual-review-api-001",
                    evidence_references=(
                        "review:00000000-0000-0000-0000-000000000040",
                        "job:00000000-0000-0000-0000-000000000041",
                        "work_order:00000000-0000-0000-0000-000000000042",
                        "audit:audit-manual-review-api-001",
                    ),
                ),
                evidence_references=(
                    "review:00000000-0000-0000-0000-000000000040",
                    "job:00000000-0000-0000-0000-000000000041",
                    "work_order:00000000-0000-0000-0000-000000000042",
                    "audit:audit-manual-review-api-001",
                ),
            ),
            ManualReviewQueueItem(
                review_item_id=UUID("00000000-0000-0000-0000-000000000043"),
                status="resolved",
                severity="low",
                reason_code="water_emergency_review",
                visibility_groups=("resolved", "water_emergency_related"),
                primary_group="water_emergency_related",
                entity_type="water_emergency",
                entity_id=UUID("00000000-0000-0000-0000-000000000031"),
                job_id=UUID("00000000-0000-0000-0000-000000000032"),
                work_order_id=None,
                visit_id=None,
                route_assignment_id=None,
                water_emergency_id=UUID("00000000-0000-0000-0000-000000000031"),
                created_at=datetime(2026, 5, 15, 11, 0, tzinfo=UTC),
                updated_at=datetime(2026, 5, 16, 10, 0, tzinfo=UTC),
                reviewed_at=None,
                deferred_until=None,
                resolved_at=datetime(2026, 5, 16, 10, 0, tzinfo=UTC),
                age_bucket="resolved_or_archived",
                age_hours=25,
                blocker_indicator=False,
                attention_indicator=False,
                confidence_score=94.0,
                recommended_action=None,
                audit_correlation_id="audit-manual-review-api-002",
                decision_readiness=ManualReviewDecisionReadiness(
                    label="resolved_or_archived",
                    summary="Resolved review evidence is retained as read-only history.",
                    reason_codes=("resolved_or_archived_status",),
                    evidence_references=(
                        "review:00000000-0000-0000-0000-000000000043",
                        "job:00000000-0000-0000-0000-000000000032",
                        "water_emergency:00000000-0000-0000-0000-000000000031",
                        "audit:audit-manual-review-api-002",
                    ),
                    is_active_decision_need=False,
                    is_resolution_candidate=False,
                ),
                action_preflight=ManualReviewActionPreflight(
                    label="blocked_by_resolved_or_archived_status",
                    summary=(
                        "Resolved or archived Manual Review items are historical "
                        "visibility and are not eligible for active future actions."
                    ),
                    blocker_codes=("resolved_or_archived_status",),
                    required_future_controls=(
                        "action_not_available_read_only_phase",
                        "requires_future_auth",
                        "requires_operator_identity",
                        "requires_audit_reason",
                    ),
                    evidence_references=(
                        "review:00000000-0000-0000-0000-000000000043",
                        "job:00000000-0000-0000-0000-000000000032",
                        "water_emergency:00000000-0000-0000-0000-000000000031",
                        "audit:audit-manual-review-api-002",
                    ),
                    is_currently_executable=False,
                    requires_operator_identity=True,
                    requires_audit_reason=True,
                ),
                future_action_preview=ManualReviewFutureActionPreview(
                    label="no_action_available_resolved_or_archived",
                    description=(
                        "Resolved or archived review history has no active future action preview."
                    ),
                    expected_outcome_summary=(
                        "Expected outcome preview: retain historical visibility without "
                        "opening an active action."
                    ),
                    impacted_entity_summary=(
                        "Impacted entities: review:00000000-0000-0000-0000-000000000043, "
                        "water_emergency:00000000-0000-0000-0000-000000000031"
                    ),
                    impacted_entity_references=(
                        "review:00000000-0000-0000-0000-000000000043",
                        "job:00000000-0000-0000-0000-000000000032",
                        "water_emergency:00000000-0000-0000-0000-000000000031",
                    ),
                    blocker_codes=("resolved_or_archived_status",),
                    required_future_controls=(
                        "preview_not_executable_read_only_phase",
                        "requires_future_auth",
                        "requires_operator_identity",
                        "requires_audit_reason",
                    ),
                    evidence_references=(
                        "review:00000000-0000-0000-0000-000000000043",
                        "job:00000000-0000-0000-0000-000000000032",
                        "water_emergency:00000000-0000-0000-0000-000000000031",
                        "audit:audit-manual-review-api-002",
                    ),
                    is_currently_executable=False,
                    requires_operator_identity=True,
                    requires_audit_reason=True,
                ),
                command_contract=ManualReviewCommandContract(
                    label="command_not_executable_phase_0",
                    summary=(
                        "Resolved or archived Manual Review records are retained as "
                        "read-only history and do not expose active future command eligibility."
                    ),
                    future_command_candidates=(),
                    required_contract_labels=(
                        "command_contract_read_only_phase",
                        "requires_future_auth",
                        "requires_operator_identity",
                        "requires_role_authorization",
                        "requires_audit_reason",
                        "requires_idempotency_key",
                        "requires_preflight_pass",
                        "requires_immutable_event_recording",
                        "requires_post_action_consistency_check",
                        "command_not_executable_phase_0",
                    ),
                    impacted_entity_summary=(
                        "Impacted entities: review:00000000-0000-0000-0000-000000000043, "
                        "water_emergency:00000000-0000-0000-0000-000000000031"
                    ),
                    impacted_entity_references=(
                        "review:00000000-0000-0000-0000-000000000043",
                        "job:00000000-0000-0000-0000-000000000032",
                        "water_emergency:00000000-0000-0000-0000-000000000031",
                    ),
                    blocker_codes=("resolved_or_archived_status",),
                    evidence_references=(
                        "review:00000000-0000-0000-0000-000000000043",
                        "job:00000000-0000-0000-0000-000000000032",
                        "water_emergency:00000000-0000-0000-0000-000000000031",
                        "audit:audit-manual-review-api-002",
                    ),
                    is_currently_executable=False,
                    not_executable_reason=("Manual Review commands are not executable in Phase 0."),
                    requires_operator_identity=True,
                    requires_role_authorization=True,
                    requires_audit_reason=True,
                    requires_idempotency_key=True,
                    requires_immutable_event_recording=True,
                    requires_post_action_consistency_check=True,
                ),
                audit_ledger_dry_run=ManualReviewAuditLedgerDryRun(
                    label="command_execution_blocked_resolved_or_archived",
                    summary=(
                        "Resolved or archived Manual Review records retain audit-ledger "
                        "visibility without active command dry-run execution."
                    ),
                    future_command_type_candidates=(),
                    required_labels=(
                        "dry_run_only_phase_0",
                        "audit_envelope_required",
                        "operator_identity_required",
                        "role_authorization_required",
                        "idempotency_key_required",
                        "immutable_event_required",
                        "consistency_check_required",
                        "command_execution_blocked_read_only_phase",
                        "command_execution_blocked_resolved_or_archived",
                    ),
                    proposed_future_event_type="manual_review.future_command.blocked",
                    proposed_future_event_state="proposed_not_recorded",
                    proposed_future_audit_envelope_fields=(
                        "review_item_id",
                        "future_command_type",
                        "operator_identity_id",
                        "role_authorization",
                        "audit_reason",
                        "idempotency_key",
                        "preflight_label",
                        "command_contract_label",
                        "impacted_entity_references",
                        "audit_correlation_id",
                        "occurred_at",
                        "immutable_event_fingerprint",
                        "post_action_consistency_check",
                    ),
                    proposed_future_idempotency_scope=(
                        "manual_review:00000000-0000-0000-0000-000000000043:blocked"
                    ),
                    proposed_future_consistency_check_summary=(
                        "Future command execution would re-read the review item, linked "
                        "entities, immutable event fingerprint, and post-action state before "
                        "presenting any outcome."
                    ),
                    audit_correlation_references=("audit:audit-manual-review-api-002",),
                    evidence_references=(
                        "review:00000000-0000-0000-0000-000000000043",
                        "job:00000000-0000-0000-0000-000000000032",
                        "water_emergency:00000000-0000-0000-0000-000000000031",
                        "audit:audit-manual-review-api-002",
                    ),
                    is_currently_executable=False,
                    phase_allows_execution=False,
                    execution_unavailable_reason=(
                        "Manual Review command dry-runs are visibility only; execution "
                        "is not available in Phase 0."
                    ),
                    requires_operator_identity=True,
                    requires_role_authorization=True,
                    requires_audit_reason=True,
                    requires_idempotency_key=True,
                    requires_immutable_event_recording=True,
                    requires_post_action_consistency_check=True,
                ),
                command_validation=manual_review_command_validation_contract(
                    label="validation_blocked_resolved_or_archived",
                    candidate_future_command_type="blocked",
                    validation_status="blocked_resolved_or_archived",
                    validation_blockers=(
                        "validation_blocked_resolved_or_archived",
                        "validation_read_only_phase",
                    ),
                    status_allows_future_action=False,
                    water_emergency_scope_checked=False,
                    water_emergency_scope_required=True,
                    requires_water_emergency_scope_check=True,
                    audit_correlation_reference="audit:audit-manual-review-api-002",
                    evidence_references=(
                        "review:00000000-0000-0000-0000-000000000043",
                        "job:00000000-0000-0000-0000-000000000032",
                        "water_emergency:00000000-0000-0000-0000-000000000031",
                        "audit:audit-manual-review-api-002",
                    ),
                ),
                permission_readiness=manual_review_permission_readiness_contract(
                    label="permission_blocked_resolved_or_archived",
                    candidate_future_command_type="blocked",
                    future_required_roles=(),
                    future_required_permissions=(),
                    extra_required_labels=("permission_blocked_resolved_or_archived",),
                    audit_correlation_reference="audit:audit-manual-review-api-002",
                    evidence_references=(
                        "review:00000000-0000-0000-0000-000000000043",
                        "job:00000000-0000-0000-0000-000000000032",
                        "water_emergency:00000000-0000-0000-0000-000000000031",
                        "audit:audit-manual-review-api-002",
                    ),
                    requires_water_emergency_scope_check=True,
                ),
                evidence_references=(
                    "review:00000000-0000-0000-0000-000000000043",
                    "job:00000000-0000-0000-0000-000000000032",
                    "water_emergency:00000000-0000-0000-0000-000000000031",
                    "audit:audit-manual-review-api-002",
                ),
            ),
        ),
    )


def manual_review_detail_contract() -> ManualReviewDetailReadModel:
    review_item = manual_review_queue_contract().items[0]

    return ManualReviewDetailReadModel(
        generated_at=datetime(2026, 5, 16, 12, 55, tzinfo=UTC),
        review_item=review_item,
        reason_context=ManualReviewReasonEvidenceContext(
            reason_code="missing_customer_data",
            status="open",
            severity="critical",
            confidence_score=66.0,
            recommended_action="Review missing synthetic data.",
            review_reason_codes=("missing_customer_data",),
            snapshot_keys=("validation_snapshot",),
            blocker_indicator=True,
            attention_indicator=True,
            evidence_references=review_item.evidence_references,
        ),
        decision_readiness=review_item.decision_readiness,
        action_preflight=review_item.action_preflight,
        future_action_preview=review_item.future_action_preview,
        command_contract=review_item.command_contract,
        audit_ledger_dry_run=review_item.audit_ledger_dry_run,
        command_validation=review_item.command_validation,
        permission_readiness=review_item.permission_readiness,
        linked_entity_context=ManualReviewDetailLinkedEntityContext(
            entity_type="job",
            entity_id=UUID("00000000-0000-0000-0000-000000000041"),
            job_id=UUID("00000000-0000-0000-0000-000000000041"),
            job_status="awaiting_dispatch",
            job_type="standard",
            work_order_id=UUID("00000000-0000-0000-0000-000000000042"),
            work_order_status="generated",
            visit_id=None,
            visit_status=None,
            route_assignment_id=None,
            route_assignment_status=None,
            water_emergency_id=None,
            water_emergency_status=None,
            water_emergency_stage=None,
            is_water_emergency_related=False,
            is_dispatch_related=True,
            unknown_indicators=(),
            audit_correlation_ids=("audit-manual-review-api-001",),
        ),
        data_gap_counts=(),
        audit_correlation_ids=("audit-manual-review-api-001",),
        taxonomy_metadata=manual_review_queue_contract().taxonomy_metadata,
        timeline_summary=OperationalEventTimelineSummary(
            total_events=1,
            returned_events=1,
            mutable_event_count=0,
            audit_correlation_ids=("audit-manual-review-api-001",),
            entries=(
                OperationalTimelineEntry(
                    occurred_at=datetime(2026, 5, 16, 12, 10, tzinfo=UTC),
                    event_type="manual_review.evidence_attached",
                    event_state="recorded",
                    entity_type="review_item",
                    entity_id=review_item.review_item_id,
                    route_assignment_id=None,
                    visit_id=None,
                    work_order_id=review_item.work_order_id,
                    job_id=review_item.job_id,
                    technician_id=None,
                    audit_correlation_id="audit-manual-review-api-001",
                    previous_state="open",
                    new_state="evidence_attached",
                    is_immutable=True,
                ),
            ),
        ),
    )


def test_dashboard_api_routes_return_read_only_contracts(
    monkeypatch,
) -> None:
    settings = Settings(
        environment="testing",
        database_url="postgresql+psycopg://acs_user:acs_pass@db.internal:5432/acs_fsm_test",
    )
    app = create_app(settings)
    overview = dashboard_overview_contract()
    water_emergency = water_emergency_contract()
    water_emergency_detail = water_emergency_detail_contract()
    manual_review_queue = manual_review_queue_contract()
    manual_review_detail = manual_review_detail_contract()

    def override_db_session():
        yield object()

    monkeypatch.setattr(
        DashboardReadModelService,
        "build_overview_from_session",
        lambda self, session: overview,
    )
    monkeypatch.setattr(
        DashboardReadModelService,
        "build_lifecycle_from_session",
        lambda self, session: overview.lifecycle_summary,
    )
    monkeypatch.setattr(
        DashboardReadModelService,
        "build_review_from_session",
        lambda self, session: overview.manual_review_summary,
    )
    monkeypatch.setattr(
        DashboardReadModelService,
        "build_manual_review_queue_from_session",
        lambda self, session: manual_review_queue,
    )

    def build_manual_review_detail_from_session(self, session, review_item_id):
        if review_item_id == manual_review_detail.review_item.review_item_id:
            return manual_review_detail
        return None

    monkeypatch.setattr(
        DashboardReadModelService,
        "build_manual_review_detail_from_session",
        build_manual_review_detail_from_session,
    )
    monkeypatch.setattr(
        DashboardReadModelService,
        "build_dispatch_from_session",
        lambda self, session: overview.dispatch_summary,
    )
    monkeypatch.setattr(
        DashboardReadModelService,
        "build_water_emergency_from_session",
        lambda self, session: water_emergency,
    )

    def build_water_emergency_detail_from_session(self, session, water_emergency_id):
        if water_emergency_id == water_emergency_detail.record.water_emergency_id:
            return water_emergency_detail
        return None

    monkeypatch.setattr(
        DashboardReadModelService,
        "build_water_emergency_detail_from_session",
        build_water_emergency_detail_from_session,
    )
    app.dependency_overrides[get_db_session] = override_db_session

    with TestClient(app) as client:
        overview_response = client.get("/api/v1/dashboard/overview")
        lifecycle_response = client.get("/api/v1/dashboard/lifecycle")
        review_response = client.get("/api/v1/dashboard/review")
        manual_review_queue_response = client.get("/api/v1/dashboard/manual-review/queue")
        manual_review_detail_response = client.get(
            "/api/v1/dashboard/manual-review/queue/00000000-0000-0000-0000-000000000040",
        )
        manual_review_detail_missing_response = client.get(
            "/api/v1/dashboard/manual-review/queue/00000000-0000-0000-0000-000000009999",
        )
        dispatch_response = client.get("/api/v1/dashboard/dispatch")
        water_response = client.get("/api/v1/dashboard/water-emergency")
        water_detail_response = client.get(
            "/api/v1/dashboard/water-emergency/00000000-0000-0000-0000-000000000031",
        )
        water_detail_missing_response = client.get(
            "/api/v1/dashboard/water-emergency/00000000-0000-0000-0000-000000009999",
        )
        mutation_response = client.post("/api/v1/dashboard/overview")
        review_queue_mutation_response = client.post("/api/v1/dashboard/manual-review/queue")
        review_detail_mutation_response = client.post(
            "/api/v1/dashboard/manual-review/queue/00000000-0000-0000-0000-000000000040",
        )
        water_mutation_response = client.post("/api/v1/dashboard/water-emergency")
        water_detail_mutation_response = client.post(
            "/api/v1/dashboard/water-emergency/00000000-0000-0000-0000-000000000031",
        )

    assert overview_response.status_code == 200
    assert overview_response.json()["operational_summary"]["total_jobs"] == 1
    assert overview_response.json()["timeline_summary"]["entries"] == []
    assert lifecycle_response.status_code == 200
    assert lifecycle_response.json()["intake_lifecycle_counts"] == [
        {"label": "approved_for_dispatch", "count": 1},
    ]
    assert review_response.status_code == 200
    assert review_response.json()["open_items"] == 0
    assert manual_review_queue_response.status_code == 200
    assert manual_review_queue_response.json()["total_items"] == 2
    assert manual_review_queue_response.json()["active_attention_count"] == 1
    assert manual_review_queue_response.json()["water_emergency_related_count"] == 1
    assert manual_review_queue_response.json()["dispatch_related_count"] == 1
    assert manual_review_queue_response.json()["result_window_metadata"] == {
        "total_count": 2,
        "visible_count": 2,
        "result_limit": 2,
        "has_more": False,
        "sort_key": "attention",
        "generated_at": "2026-05-16T12:50:00Z",
    }
    assert manual_review_queue_response.json()["available_filters"][1]["key"] == (
        "active_attention"
    )
    assert manual_review_queue_response.json()["available_filters"][1]["count"] == 1
    assert manual_review_queue_response.json()["sort_options"][0]["key"] == "attention"
    assert manual_review_queue_response.json()["decision_readiness_counts"] == [
        {"label": "blocked_by_missing_data", "count": 1},
        {"label": "resolved_or_archived", "count": 1},
    ]
    assert manual_review_queue_response.json()["action_preflight_counts"] == [
        {"label": "blocked_by_missing_data", "count": 1},
        {"label": "blocked_by_resolved_or_archived_status", "count": 1},
    ]
    assert manual_review_queue_response.json()["future_action_preview_counts"] == [
        {"label": "future_request_information_preview", "count": 1},
        {"label": "no_action_available_resolved_or_archived", "count": 1},
    ]
    assert manual_review_queue_response.json()["command_contract_counts"] == [
        {"label": "requires_preflight_pass", "count": 1},
        {"label": "command_not_executable_phase_0", "count": 1},
    ]
    assert manual_review_queue_response.json()["audit_ledger_dry_run_counts"] == [
        {"label": "dry_run_only_phase_0", "count": 1},
        {"label": "command_execution_blocked_resolved_or_archived", "count": 1},
    ]
    assert manual_review_queue_response.json()["command_validation_counts"] == [
        {"label": "validation_warning_requires_review", "count": 1},
        {"label": "validation_blocked_resolved_or_archived", "count": 1},
    ]
    assert manual_review_queue_response.json()["permission_readiness_counts"] == [
        {"label": "permission_ready_for_future_auth_phase", "count": 1},
        {"label": "permission_blocked_resolved_or_archived", "count": 1},
    ]
    assert (
        manual_review_queue_response.json()["taxonomy_metadata"][
            "randall_authorized_phase_0_baseline"
        ]
        is True
    )
    assert (
        manual_review_queue_response.json()["taxonomy_metadata"]["legal_or_insurance_policy"]
        is False
    )
    assert manual_review_queue_response.json()["items"][0]["reason_code"] == (
        "missing_customer_data"
    )
    assert manual_review_queue_response.json()["items"][0]["decision_readiness"]["label"] == (
        "blocked_by_missing_data"
    )
    assert manual_review_queue_response.json()["items"][0]["action_preflight"]["label"] == (
        "blocked_by_missing_data"
    )
    assert manual_review_queue_response.json()["items"][0]["future_action_preview"]["label"] == (
        "future_request_information_preview"
    )
    assert manual_review_queue_response.json()["items"][0]["command_contract"]["label"] == (
        "requires_preflight_pass"
    )
    assert (
        manual_review_queue_response.json()["items"][0]["action_preflight"][
            "is_currently_executable"
        ]
        is False
    )
    assert (
        manual_review_queue_response.json()["items"][0]["future_action_preview"][
            "is_currently_executable"
        ]
        is False
    )
    assert (
        manual_review_queue_response.json()["items"][0]["future_action_preview"][
            "requires_operator_identity"
        ]
        is True
    )
    assert (
        manual_review_queue_response.json()["items"][0]["future_action_preview"][
            "requires_audit_reason"
        ]
        is True
    )
    assert (
        manual_review_queue_response.json()["items"][0]["command_contract"][
            "is_currently_executable"
        ]
        is False
    )
    assert (
        manual_review_queue_response.json()["items"][0]["command_contract"][
            "requires_role_authorization"
        ]
        is True
    )
    assert (
        "requires_idempotency_key"
        in manual_review_queue_response.json()["items"][0]["command_contract"][
            "required_contract_labels"
        ]
    )
    assert (
        manual_review_queue_response.json()["items"][0]["audit_ledger_dry_run"]["label"]
        == "dry_run_only_phase_0"
    )
    assert (
        manual_review_queue_response.json()["items"][0]["audit_ledger_dry_run"][
            "is_currently_executable"
        ]
        is False
    )
    assert (
        manual_review_queue_response.json()["items"][0]["audit_ledger_dry_run"][
            "phase_allows_execution"
        ]
        is False
    )
    assert manual_review_queue_response.json()["items"][0]["audit_ledger_dry_run"][
        "future_command_type_candidates"
    ] == ["request_information"]
    assert (
        manual_review_queue_response.json()["items"][0]["audit_ledger_dry_run"][
            "proposed_future_event_type"
        ]
        == "manual_review.future_command.request_information"
    )
    assert (
        manual_review_queue_response.json()["items"][0]["audit_ledger_dry_run"][
            "proposed_future_event_state"
        ]
        == "proposed_not_recorded"
    )
    assert (
        "idempotency_key_required"
        in manual_review_queue_response.json()["items"][0]["audit_ledger_dry_run"][
            "required_labels"
        ]
    )
    assert (
        "immutable_event_fingerprint"
        in manual_review_queue_response.json()["items"][0]["audit_ledger_dry_run"][
            "proposed_future_audit_envelope_fields"
        ]
    )
    assert (
        manual_review_queue_response.json()["items"][0]["audit_ledger_dry_run"][
            "requires_immutable_event_recording"
        ]
        is True
    )
    assert manual_review_queue_response.json()["items"][0]["command_validation"]["label"] == (
        "validation_warning_requires_review"
    )
    assert manual_review_queue_response.json()["items"][0]["permission_readiness"]["label"] == (
        "permission_ready_for_future_auth_phase"
    )
    assert (
        manual_review_queue_response.json()["items"][0]["permission_readiness"][
            "is_currently_executable"
        ]
        is False
    )
    assert (
        manual_review_queue_response.json()["items"][0]["permission_readiness"][
            "phase_allows_execution"
        ]
        is False
    )
    assert (
        manual_review_queue_response.json()["items"][0]["permission_readiness"][
            "future_operator_identity_required"
        ]
        is True
    )
    assert (
        manual_review_queue_response.json()["items"][0]["permission_readiness"][
            "future_role_authorization_required"
        ]
        is True
    )
    assert (
        manual_review_queue_response.json()["items"][0]["permission_readiness"][
            "service_account_allowed"
        ]
        is False
    )
    assert (
        manual_review_queue_response.json()["items"][0]["permission_readiness"][
            "technician_action_allowed"
        ]
        is False
    )
    assert (
        "dispatcher"
        in manual_review_queue_response.json()["items"][0]["permission_readiness"][
            "future_required_roles"
        ]
    )
    assert (
        "manual_review.dispatch_review.prepare"
        in manual_review_queue_response.json()["items"][0]["permission_readiness"][
            "future_required_permissions"
        ]
    )
    assert (
        manual_review_queue_response.json()["items"][0]["command_validation"][
            "is_currently_executable"
        ]
        is False
    )
    assert (
        manual_review_queue_response.json()["items"][0]["command_validation"][
            "phase_allows_execution"
        ]
        is False
    )
    assert (
        manual_review_queue_response.json()["items"][0]["command_validation"][
            "candidate_future_command_type"
        ]
        == "request_information"
    )
    assert (
        manual_review_queue_response.json()["items"][0]["command_validation"][
            "requires_idempotency_key"
        ]
        is True
    )
    assert manual_review_queue_response.json()["items"][0]["command_validation"]["safety_gates"][
        -1
    ] == {
        "key": "phase_allows_execution",
        "label": "Phase allows execution",
        "passed": False,
        "required": True,
        "reason": (
            "Phase 0 exposes validation visibility only; Manual Review command "
            "execution is disabled."
        ),
    }
    assert (
        "requires_future_auth"
        in (
            manual_review_queue_response.json()["items"][0]["action_preflight"][
                "required_future_controls"
            ]
        )
    )
    assert (
        manual_review_queue_response.json()["items"][0]["decision_readiness"][
            "is_active_decision_need"
        ]
        is True
    )
    assert manual_review_queue_response.json()["items"][1]["water_emergency_id"] == (
        "00000000-0000-0000-0000-000000000031"
    )
    assert manual_review_queue_response.json()["items"][1]["decision_readiness"]["label"] == (
        "resolved_or_archived"
    )
    assert manual_review_queue_response.json()["items"][1]["action_preflight"]["label"] == (
        "blocked_by_resolved_or_archived_status"
    )
    assert manual_review_queue_response.json()["items"][1]["future_action_preview"]["label"] == (
        "no_action_available_resolved_or_archived"
    )
    assert manual_review_queue_response.json()["items"][1]["command_contract"]["label"] == (
        "command_not_executable_phase_0"
    )
    assert (
        manual_review_queue_response.json()["items"][1]["audit_ledger_dry_run"]["label"]
        == "command_execution_blocked_resolved_or_archived"
    )
    assert manual_review_queue_response.json()["items"][1]["command_validation"]["label"] == (
        "validation_blocked_resolved_or_archived"
    )
    assert manual_review_queue_response.json()["items"][1]["permission_readiness"]["label"] == (
        "permission_blocked_resolved_or_archived"
    )
    assert (
        manual_review_queue_response.json()["items"][1]["command_validation"][
            "is_currently_executable"
        ]
        is False
    )
    assert manual_review_detail_response.status_code == 200
    assert manual_review_detail_response.json()["review_item"]["review_item_id"] == (
        "00000000-0000-0000-0000-000000000040"
    )
    assert manual_review_detail_response.json()["reason_context"]["reason_code"] == (
        "missing_customer_data"
    )
    assert manual_review_detail_response.json()["decision_readiness"]["label"] == (
        "blocked_by_missing_data"
    )
    assert manual_review_detail_response.json()["action_preflight"]["label"] == (
        "blocked_by_missing_data"
    )
    assert manual_review_detail_response.json()["future_action_preview"]["label"] == (
        "future_request_information_preview"
    )
    assert manual_review_detail_response.json()["command_contract"]["label"] == (
        "requires_preflight_pass"
    )
    assert (
        manual_review_detail_response.json()["command_contract"]["is_currently_executable"] is False
    )
    assert manual_review_detail_response.json()["audit_ledger_dry_run"]["label"] == (
        "dry_run_only_phase_0"
    )
    assert (
        manual_review_detail_response.json()["audit_ledger_dry_run"]["is_currently_executable"]
        is False
    )
    assert (
        manual_review_detail_response.json()["audit_ledger_dry_run"]["requires_idempotency_key"]
        is True
    )
    assert manual_review_detail_response.json()["command_validation"]["label"] == (
        "validation_warning_requires_review"
    )
    assert manual_review_detail_response.json()["permission_readiness"]["label"] == (
        "permission_ready_for_future_auth_phase"
    )
    assert (
        manual_review_detail_response.json()["permission_readiness"]["phase_allows_execution"]
        is False
    )
    assert (
        manual_review_detail_response.json()["command_validation"]["phase_allows_execution"]
        is False
    )
    assert (
        manual_review_detail_response.json()["command_validation"]["safety_gates"][-1]["key"]
        == "phase_allows_execution"
    )
    assert (
        manual_review_detail_response.json()["linked_entity_context"]["is_dispatch_related"] is True
    )
    assert (
        manual_review_detail_response.json()["timeline_summary"]["entries"][0]["event_type"]
        == "manual_review.evidence_attached"
    )
    assert manual_review_detail_missing_response.status_code == 404
    assert dispatch_response.status_code == 200
    assert dispatch_response.json()["external_execution"]["execution_failed_count"] == 0
    assert water_response.status_code == 200
    assert water_response.json()["open_count"] == 1
    assert water_response.json()["equipment_summary"]["inventory_entity_available"] is False
    assert water_response.json()["visit_chain_summary"]["total_visits"] == 2
    assert water_response.json()["drying_stage_summary"]["active_stage_counts"] == [
        {"label": "monitoring", "count": 1},
    ]
    assert water_response.json()["next_step_summary"]["label_counts"] == [
        {"label": "needs_manual_review", "count": 1},
        {"label": "needs_operator_decision", "count": 1},
    ]
    assert water_response.json()["operator_queue_summary"]["attention_label_counts"] == [
        {"label": "critical_attention", "count": 1},
    ]
    assert water_response.json()["operator_queue_summary"]["items"][0]["queue_group"] == (
        "active_attention"
    )
    assert water_response.json()["aging_followup_summary"]["label_counts"] == [
        {"label": "waiting_for_review", "count": 1},
    ]
    assert (
        water_response.json()["aging_followup_summary"]["items"][0]["time_sensitivity_label"]
        == "waiting_for_review"
    )
    assert water_response.json()["view_state_summary"]["available_filters"][0] == {
        "key": "all",
        "label": "All records",
        "count": 1,
        "description": "Every persisted Water Emergency record.",
    }
    assert water_response.json()["view_state_summary"]["items"][0]["filter_groups"] == [
        "all",
        "active",
        "needs_manual_review",
    ]
    assert (
        water_response.json()["governance_metadata"]["randall_authorized_phase_0_baseline"] is True
    )
    assert water_response.json()["governance_metadata"]["source"] == (
        "phase_0_visibility_heuristic"
    )
    assert water_response.json()["governance_metadata"]["legal_or_insurance_policy"] is False
    assert water_response.json()["governance_metadata"]["requires_alfonso_owner_review"] is False
    assert (
        water_response.json()["governance_metadata"]["owner_review_required_items"][0][
            "requires_alfonso_owner_review"
        ]
        is True
    )
    assert water_response.json()["result_window_metadata"] == {
        "total_count": 1,
        "visible_count": 1,
        "result_limit": 1,
        "has_more": False,
        "sort_key": "attention",
        "generated_at": "2026-05-16T12:45:00Z",
    }
    assert water_response.json()["records"][0]["related_visit_ids"] == [
        "00000000-0000-0000-0000-000000000033",
    ]
    assert water_detail_response.status_code == 200
    assert water_detail_response.json()["record"]["water_emergency_id"] == (
        "00000000-0000-0000-0000-000000000031"
    )
    assert water_detail_response.json()["review_indicators"][0]["reason_code"] == (
        "water_detail_review"
    )
    assert water_detail_response.json()["equipment_context"]["unknown_indicators"] == [
        "equipment_inventory_not_modeled",
    ]
    assert water_detail_response.json()["visit_chain"]["total_visits"] == 1
    assert water_detail_response.json()["drying_stage_context"]["current_stage"] == "monitoring"
    assert water_detail_response.json()["next_step_readiness"]["primary_label"] == (
        "needs_manual_review"
    )
    assert (
        "needs_operator_decision" in water_detail_response.json()["next_step_readiness"]["labels"]
    )
    assert water_detail_response.json()["timeline_summary"]["entries"][0]["event_type"] == (
        "water_emergency.extraction_started"
    )
    assert water_detail_missing_response.status_code == 404
    assert mutation_response.status_code == 405
    assert review_queue_mutation_response.status_code == 405
    assert review_detail_mutation_response.status_code == 405
    assert water_mutation_response.status_code == 405
    assert water_detail_mutation_response.status_code == 405
