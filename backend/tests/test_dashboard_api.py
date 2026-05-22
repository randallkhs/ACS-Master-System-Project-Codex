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
    ManualReviewSummary,
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
        dispatch_response = client.get("/api/v1/dashboard/dispatch")
        water_response = client.get("/api/v1/dashboard/water-emergency")
        water_detail_response = client.get(
            "/api/v1/dashboard/water-emergency/00000000-0000-0000-0000-000000000031",
        )
        water_detail_missing_response = client.get(
            "/api/v1/dashboard/water-emergency/00000000-0000-0000-0000-000000009999",
        )
        mutation_response = client.post("/api/v1/dashboard/overview")
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
    assert water_mutation_response.status_code == 405
    assert water_detail_mutation_response.status_code == 405
