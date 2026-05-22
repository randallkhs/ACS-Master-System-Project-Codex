from datetime import UTC, date, datetime
from uuid import uuid4

from app.models.intake_processing_record import IntakeProcessingRecord
from app.models.job import Job
from app.models.operational_event_record import OperationalEventRecord
from app.models.review_item import ReviewItem
from app.models.route_assignment import RouteAssignment
from app.models.visit import Visit
from app.models.water_emergency import WaterEmergency
from app.models.work_order import WorkOrder
from app.services.dashboard.service import DashboardReadModelService


def bucket_count(buckets: object, label: str) -> int:
    return {bucket.label: bucket.count for bucket in buckets}[label]


def dashboard_source_records() -> dict[str, list[object]]:
    standard_job_id = uuid4()
    water_job_id = uuid4()
    water_emergency_id = uuid4()
    closed_water_emergency_id = uuid4()
    work_order_id = uuid4()
    visit_id = uuid4()
    water_visit_id = uuid4()
    route_assignment_id = uuid4()
    blocked_route_assignment_id = uuid4()
    technician_id = uuid4()
    audit_correlation_id = "audit-dashboard-001"

    return {
        "intake_records": [
            IntakeProcessingRecord(
                source_system="google_calendar",
                source_id="event-approved",
                lifecycle_state="approved_for_dispatch",
                orchestration_state="eligible",
                audit_correlation_id=audit_correlation_id,
                dispatch_eligible=True,
            ),
            IntakeProcessingRecord(
                source_system="google_calendar",
                source_id="event-review",
                lifecycle_state="review_required",
                orchestration_state="review_required",
                audit_correlation_id="audit-dashboard-002",
                requires_review=True,
            ),
            IntakeProcessingRecord(
                source_system="google_calendar",
                source_id="event-blocked",
                lifecycle_state="blocked",
                orchestration_state="blocked",
                audit_correlation_id="audit-dashboard-003",
                blocked=True,
                unsafe=True,
            ),
            IntakeProcessingRecord(
                source_system="google_calendar",
                source_id="event-water",
                lifecycle_state="review_required",
                orchestration_state="water_emergency_separated",
                audit_correlation_id="audit-dashboard-004",
                requires_review=True,
                water_emergency_separated=True,
            ),
        ],
        "jobs": [
            Job(id=standard_job_id, job_type="standard", status="awaiting_dispatch"),
            Job(id=water_job_id, job_type="water_emergency", status="active"),
        ],
        "work_orders": [
            WorkOrder(
                id=work_order_id,
                job_id=standard_job_id,
                status="generated",
                dispatch_status="not_dispatched",
                audit_correlation_id=audit_correlation_id,
            ),
        ],
        "visits": [
            Visit(
                id=visit_id,
                job_id=standard_job_id,
                work_order_id=work_order_id,
                technician_id=technician_id,
                visit_type="standard",
                status="dispatch_ready",
                audit_correlation_id=audit_correlation_id,
            ),
            Visit(
                id=water_visit_id,
                job_id=water_job_id,
                visit_type="water_emergency",
                status="review_required",
                audit_correlation_id="audit-dashboard-water",
            ),
        ],
        "route_assignments": [
            RouteAssignment(
                id=route_assignment_id,
                route_date=date(2026, 5, 16),
                technician_id=technician_id,
                job_id=standard_job_id,
                visit_id=visit_id,
                route_order=1,
                region="DE",
                time_window="AM",
                status="dispatched",
                route_group_key="DE-AM-2026-05-16",
                audit_correlation_id=audit_correlation_id,
                dispatch_execution_state="dispatched",
                dispatched_at=datetime(2026, 5, 16, 9, 0, tzinfo=UTC),
                external_adapter_state="awaiting_external_execution",
                external_adapter_prepared_at=datetime(2026, 5, 16, 9, 5, tzinfo=UTC),
                external_execution_state="awaiting_external_confirmation",
                external_execution_completed_at=datetime(2026, 5, 16, 9, 10, tzinfo=UTC),
                external_confirmation_state="failed",
                external_failure_snapshot={"provider_state": "failed"},
                external_confirmation_failed_at=datetime(2026, 5, 16, 9, 15, tzinfo=UTC),
                retry_preparation_snapshot={"retry_execution": "not_executed"},
                retry_prepared_at=datetime(2026, 5, 16, 9, 20, tzinfo=UTC),
                dispatch_reconciliation_state="reconciliation_required",
                dispatch_divergence_snapshot={"critical_divergence": True},
                dispatch_mismatch_snapshot={
                    "mismatch_count": 2,
                    "mismatches": [{"code": "external_confirmation_mismatch"}],
                },
                replay_recovery_state="replay_prepared",
                replay_preparation_snapshot={"replay_execution": "not_executed"},
                replay_prepared_at=datetime(2026, 5, 16, 9, 25, tzinfo=UTC),
                governance_state="operator_approved",
                governance_approved_at=datetime(2026, 5, 16, 9, 30, tzinfo=UTC),
                accountability_state="escalation_required",
                escalation_required_at=datetime(2026, 5, 16, 9, 35, tzinfo=UTC),
            ),
            RouteAssignment(
                id=blocked_route_assignment_id,
                route_date=date(2026, 5, 16),
                job_id=standard_job_id,
                visit_id=visit_id,
                route_order=2,
                region="NJ",
                time_window="PM",
                status="blocked",
                audit_correlation_id="audit-dashboard-blocked",
                dispatch_execution_state="blocked",
                external_execution_state="failed",
                external_execution_failure_snapshot={"provider_state": "failed"},
                external_execution_failed_at=datetime(2026, 5, 16, 10, 0, tzinfo=UTC),
                dispatch_reconciliation_state="reconciliation_blocked",
                dispatch_reconciliation_blocker_snapshot={"blocked": True},
                replay_recovery_state="replay_blocked",
                replay_blocker_snapshot={"blocked": True},
                governance_state="governance_blocked",
                governance_blocker_snapshot={"blocked": True},
                accountability_state="accountability_blocked",
                escalation_blocker_snapshot={"blocked": True},
            ),
        ],
        "review_items": [
            ReviewItem(
                reason_code="cancellation_uncertain",
                status="open",
                severity="critical",
                confidence_score=61.0,
                audit_correlation_id=audit_correlation_id,
            ),
            ReviewItem(
                reason_code="water_emergency_review",
                status="deferred",
                severity="high",
                confidence_score=72.0,
                audit_correlation_id="audit-dashboard-water",
            ),
            ReviewItem(
                reason_code="operator_resolved",
                status="approved",
                severity="low",
                confidence_score=99.0,
                audit_correlation_id="audit-dashboard-resolved",
            ),
        ],
        "water_emergencies": [
            WaterEmergency(
                id=water_emergency_id,
                job_id=water_job_id,
                status="DRYING_IN_PROGRESS",
                drying_stage="monitoring",
                next_required_action="Schedule synthetic drying check.",
                equipment_onsite=True,
                moisture_tracking_required=True,
                opened_at=datetime(2026, 5, 16, 7, 30, tzinfo=UTC),
            ),
            WaterEmergency(
                id=closed_water_emergency_id,
                job_id=uuid4(),
                status="CLOSED",
                closed_at=datetime(2026, 5, 16, 11, 0, tzinfo=UTC),
            ),
        ],
        "operational_events": [
            OperationalEventRecord(
                id=uuid4(),
                occurred_at=datetime(2026, 5, 16, 9, 5, tzinfo=UTC),
                recorded_at=datetime(2026, 5, 16, 9, 5, tzinfo=UTC),
                event_type="external_adapter.prepared",
                event_state="awaiting_external_execution",
                entity_type="route_assignment",
                entity_id=route_assignment_id,
                route_assignment_id=route_assignment_id,
                visit_id=visit_id,
                work_order_id=work_order_id,
                job_id=standard_job_id,
                technician_id=technician_id,
                audit_correlation_id=audit_correlation_id,
                previous_state="dispatched",
                new_state="awaiting_external_execution",
                event_fingerprint="dashboard-event-2",
                is_immutable=True,
            ),
            OperationalEventRecord(
                id=uuid4(),
                occurred_at=datetime(2026, 5, 16, 9, 0, tzinfo=UTC),
                recorded_at=datetime(2026, 5, 16, 9, 0, tzinfo=UTC),
                event_type="dispatch_execution.dispatched",
                event_state="dispatched",
                entity_type="route_assignment",
                entity_id=route_assignment_id,
                route_assignment_id=route_assignment_id,
                visit_id=visit_id,
                work_order_id=work_order_id,
                job_id=standard_job_id,
                technician_id=technician_id,
                audit_correlation_id=audit_correlation_id,
                previous_state="authorized",
                new_state="dispatched",
                event_fingerprint="dashboard-event-1",
                is_immutable=True,
            ),
        ],
    }


def build_overview():
    records = dashboard_source_records()
    return DashboardReadModelService(
        now=lambda: datetime(2026, 5, 16, 12, 0, tzinfo=UTC),
    ).build_overview(
        intake_records=records["intake_records"],
        jobs=records["jobs"],
        work_orders=records["work_orders"],
        visits=records["visits"],
        route_assignments=records["route_assignments"],
        review_items=records["review_items"],
        water_emergencies=records["water_emergencies"],
        operational_events=records["operational_events"],
    )


def test_dashboard_summary_generation_aggregates_operational_state() -> None:
    overview = build_overview()

    assert overview.generated_at == datetime(2026, 5, 16, 12, 0, tzinfo=UTC)
    assert overview.operational_summary.total_jobs == 2
    assert overview.operational_summary.total_work_orders == 1
    assert overview.operational_summary.total_visits == 2
    assert overview.operational_summary.total_route_assignments == 2
    assert overview.operational_summary.open_manual_reviews == 2
    assert overview.operational_summary.open_water_emergencies == 1
    assert overview.operational_summary.audit_correlation_count == 7


def test_manual_review_summary_counts_blockers_and_escalation_indicators() -> None:
    review = build_overview().manual_review_summary

    assert review.total_items == 3
    assert review.open_items == 1
    assert review.deferred_items == 1
    assert review.resolved_items == 1
    assert review.archived_items == 0
    assert review.escalation_indicators == 2
    assert bucket_count(review.severity_counts, "critical") == 1
    assert bucket_count(review.reason_counts, "water_emergency_review") == 1


def test_dispatch_lifecycle_summary_counts_persisted_lifecycle_state() -> None:
    lifecycle = build_overview().lifecycle_summary

    assert bucket_count(lifecycle.intake_lifecycle_counts, "review_required") == 2
    assert bucket_count(lifecycle.job_status_counts, "awaiting_dispatch") == 1
    assert bucket_count(lifecycle.visit_status_counts, "dispatch_ready") == 1
    assert bucket_count(lifecycle.route_status_counts, "blocked") == 1
    assert bucket_count(lifecycle.dispatch_execution_state_counts, "dispatched") == 1
    assert lifecycle.dispatch_ready_visits == 1
    assert lifecycle.dispatched_route_assignments == 1
    assert lifecycle.water_emergency_records == 2
    assert lifecycle.water_emergency_separated_intake == 1
    assert lifecycle.blocker_count >= 1


def test_water_emergency_dispatch_ready_visits_stay_out_of_standard_dispatch_count() -> None:
    records = dashboard_source_records()
    water_emergency = records["water_emergencies"][0]
    assert isinstance(water_emergency, WaterEmergency)

    records["visits"].append(
        Visit(
            id=uuid4(),
            job_id=water_emergency.job_id,
            visit_type="water_emergency",
            status="dispatch_ready",
            audit_correlation_id="audit-dashboard-water-dispatch-ready",
        ),
    )

    lifecycle = DashboardReadModelService().build_lifecycle(
        intake_records=records["intake_records"],
        jobs=records["jobs"],
        work_orders=records["work_orders"],
        visits=records["visits"],
        route_assignments=records["route_assignments"],
        water_emergencies=records["water_emergencies"],
    )

    assert bucket_count(lifecycle.visit_status_counts, "dispatch_ready") == 2
    assert lifecycle.dispatch_ready_visits == 1


def test_water_emergency_dashboard_summary_stays_separate_and_read_only() -> None:
    records = dashboard_source_records()
    water_emergency = records["water_emergencies"][0]
    assert isinstance(water_emergency, WaterEmergency)
    water_job_id = water_emergency.job_id
    water_visit_id = next(
        visit.id for visit in records["visits"] if getattr(visit, "job_id", None) == water_job_id
    )
    extra_water_visit_id = uuid4()
    water_work_order_id = uuid4()
    water_timeline_id = uuid4()

    records["work_orders"].append(
        WorkOrder(
            id=water_work_order_id,
            job_id=water_job_id,
            work_order_number="WATER-VISIBILITY-001",
            status="generated",
            dispatch_status="not_dispatched",
            required_equipment_notes=(
                "Synthetic-only equipment context: air movers and dehumidifier placeholders."
            ),
            audit_correlation_id="audit-dashboard-water-extra",
        ),
    )
    records["visits"].append(
        Visit(
            id=extra_water_visit_id,
            job_id=water_job_id,
            work_order_id=water_work_order_id,
            visit_type="water_emergency",
            status="scheduled",
            audit_correlation_id="audit-dashboard-water-extra",
        ),
    )
    records["review_items"].append(
        ReviewItem(
            job_id=water_job_id,
            entity_type="water_emergency",
            entity_id=water_emergency.id,
            reason_code="water_emergency_missing_pickup",
            status="open",
            severity="critical",
            audit_correlation_id="audit-dashboard-water-extra",
        ),
    )
    records["review_items"].append(
        ReviewItem(
            job_id=water_job_id,
            entity_type="water_emergency",
            entity_id=water_emergency.id,
            reason_code="water_emergency_archived_exception",
            status="archived",
            severity="low",
            audit_correlation_id="audit-dashboard-water-archived",
        ),
    )
    records["operational_events"].append(
        OperationalEventRecord(
            id=water_timeline_id,
            occurred_at=datetime(2026, 5, 16, 8, 15, tzinfo=UTC),
            recorded_at=datetime(2026, 5, 16, 8, 15, tzinfo=UTC),
            event_type="water_emergency.monitoring_required",
            event_state="review_required",
            entity_type="water_emergency",
            entity_id=water_emergency.id,
            route_assignment_id=None,
            visit_id=extra_water_visit_id,
            work_order_id=None,
            job_id=water_job_id,
            technician_id=None,
            audit_correlation_id="audit-dashboard-water-extra",
            previous_state="dispatched",
            new_state="monitoring_required",
            event_fingerprint="dashboard-water-event-1",
            is_immutable=True,
        ),
    )

    summary = DashboardReadModelService().build_water_emergency(
        jobs=records["jobs"],
        work_orders=records["work_orders"],
        visits=records["visits"],
        review_items=records["review_items"],
        water_emergencies=records["water_emergencies"],
        operational_events=records["operational_events"],
    )

    assert summary.open_count == 1
    assert summary.closed_count == 1
    assert bucket_count(summary.status_counts, "drying_in_progress") == 1
    assert bucket_count(summary.stage_counts, "monitoring") == 1
    assert summary.multi_visit_count == 1
    assert summary.equipment_onsite_count == 1
    assert summary.moisture_tracking_required_count == 1
    assert summary.related_job_count == 1
    assert summary.related_work_order_count == 1
    assert summary.related_visit_count == 2
    assert summary.review_indicator_count == 2
    assert summary.escalation_indicator_count == 2
    assert summary.review_exception_summary.total_review_count == 3
    assert summary.review_exception_summary.open_review_count == 1
    assert summary.review_exception_summary.deferred_review_count == 1
    assert summary.review_exception_summary.resolved_review_count == 0
    assert summary.review_exception_summary.archived_review_count == 1
    assert summary.review_exception_summary.critical_unresolved_count == 1
    assert summary.review_exception_summary.escalation_indicator_count == 2
    assert summary.next_step_summary.total_records == 2
    assert summary.next_step_summary.needs_attention_count == 1
    assert summary.next_step_summary.closed_without_active_action_count == 1
    assert bucket_count(summary.next_step_summary.label_counts, "needs_manual_review") == 1
    assert bucket_count(summary.next_step_summary.label_counts, "needs_operator_decision") == 1
    assert bucket_count(summary.next_step_summary.label_counts, "closed_no_active_next_step") == 1
    assert (
        bucket_count(
            summary.review_exception_summary.review_reason_counts,
            "water_emergency_missing_pickup",
        )
        == 1
    )
    assert (
        bucket_count(
            summary.review_exception_summary.blocker_reason_counts,
            "water_emergency_missing_pickup",
        )
        == 1
    )
    assert summary.visit_chain_summary.total_visits == 2
    assert summary.visit_chain_summary.multi_visit_record_count == 1
    assert summary.visit_chain_summary.open_records_without_visits_count == 0
    assert bucket_count(summary.visit_chain_summary.visit_status_counts, "scheduled") == 1
    assert bucket_count(summary.visit_chain_summary.visit_status_counts, "review_required") == 1
    assert summary.equipment_summary.equipment_onsite_count == 1
    assert summary.equipment_summary.moisture_tracking_required_count == 1
    assert summary.equipment_summary.work_orders_with_equipment_notes_count == 1
    assert summary.equipment_summary.inventory_entity_available is False
    assert (
        bucket_count(summary.equipment_summary.unknown_counts, "equipment_inventory_not_modeled")
        == 1
    )
    assert summary.drying_stage_summary.missing_stage_count == 1
    assert summary.drying_stage_summary.moisture_tracking_required_count == 1
    assert bucket_count(summary.drying_stage_summary.active_stage_counts, "monitoring") == 1
    assert summary.timeline_summary.total_events == 1
    assert summary.timeline_summary.entries[0].entity_type == "water_emergency"
    assert summary.records[0].job_id == water_job_id
    assert set(summary.records[0].related_visit_ids) == {water_visit_id, extra_water_visit_id}


def test_water_emergency_record_reviews_are_scoped_to_each_record() -> None:
    records = dashboard_source_records()
    first_record = records["water_emergencies"][0]
    second_record = records["water_emergencies"][1]
    assert isinstance(first_record, WaterEmergency)
    assert isinstance(second_record, WaterEmergency)

    records["review_items"].extend(
        [
            ReviewItem(
                job_id=first_record.job_id,
                entity_type="water_emergency",
                entity_id=first_record.id,
                reason_code="first_water_emergency_review",
                status="open",
                severity="high",
                audit_correlation_id="audit-dashboard-water-first",
            ),
            ReviewItem(
                job_id=second_record.job_id,
                entity_type="water_emergency",
                entity_id=second_record.id,
                reason_code="second_water_emergency_review",
                status="open",
                severity="high",
                audit_correlation_id="audit-dashboard-water-second",
            ),
            ReviewItem(
                entity_type="water_emergency",
                reason_code="generic_water_emergency_review",
                status="open",
                severity="high",
                audit_correlation_id="audit-dashboard-water-generic",
            ),
        ],
    )

    summary = DashboardReadModelService().build_water_emergency(
        jobs=records["jobs"],
        work_orders=records["work_orders"],
        visits=records["visits"],
        review_items=records["review_items"],
        water_emergencies=records["water_emergencies"],
        operational_events=records["operational_events"],
    )

    record_summaries = {record.water_emergency_id: record for record in summary.records}

    assert record_summaries[first_record.id].open_review_count == 1
    assert record_summaries[second_record.id].open_review_count == 1
    assert summary.review_indicator_count == 4
    assert summary.review_exception_summary.open_review_count == 3
    assert summary.review_exception_summary.deferred_review_count == 1


def test_water_emergency_detail_read_model_includes_scoped_evidence() -> None:
    records = dashboard_source_records()
    water_emergency = records["water_emergencies"][0]
    closed_water_emergency = records["water_emergencies"][1]
    assert isinstance(water_emergency, WaterEmergency)
    assert isinstance(closed_water_emergency, WaterEmergency)
    water_job_id = water_emergency.job_id
    water_work_order_id = uuid4()
    first_timeline_id = uuid4()
    second_timeline_id = uuid4()

    records["work_orders"].append(
        WorkOrder(
            id=water_work_order_id,
            job_id=water_job_id,
            work_order_number="WATER-DETAIL-001",
            status="generated",
            dispatch_status="not_dispatched",
            required_equipment_notes=(
                "Synthetic-only detail equipment: air movers, dehumidifier, moisture meter."
            ),
            audit_correlation_id="audit-dashboard-water-detail",
        ),
    )
    records["visits"].append(
        Visit(
            id=uuid4(),
            job_id=water_job_id,
            work_order_id=water_work_order_id,
            visit_type="water_emergency",
            status="scheduled",
            scheduled_start_at=datetime(2026, 5, 16, 13, 0, tzinfo=UTC),
            audit_correlation_id="audit-dashboard-water-detail",
        ),
    )
    records["review_items"].extend(
        [
            ReviewItem(
                id=uuid4(),
                job_id=water_job_id,
                entity_type="water_emergency",
                entity_id=water_emergency.id,
                reason_code="water_detail_unknown_blocker",
                status="open",
                severity="critical",
                confidence_score=71.0,
                audit_correlation_id="audit-dashboard-water-detail",
                recommended_action="Review synthetic Water Emergency detail evidence.",
            ),
            ReviewItem(
                job_id=closed_water_emergency.job_id,
                entity_type="water_emergency",
                entity_id=closed_water_emergency.id,
                reason_code="closed_water_detail_review",
                status="open",
                severity="high",
                audit_correlation_id="audit-dashboard-water-closed",
            ),
            ReviewItem(
                entity_type="water_emergency",
                reason_code="generic_water_detail_review",
                status="open",
                severity="high",
                audit_correlation_id="audit-dashboard-water-generic",
            ),
        ],
    )
    records["operational_events"].extend(
        [
            OperationalEventRecord(
                id=second_timeline_id,
                occurred_at=datetime(2026, 5, 16, 10, 30, tzinfo=UTC),
                recorded_at=datetime(2026, 5, 16, 10, 30, tzinfo=UTC),
                event_type="water_emergency.monitoring_required",
                event_state="review_required",
                entity_type="water_emergency",
                entity_id=water_emergency.id,
                route_assignment_id=None,
                visit_id=None,
                work_order_id=water_work_order_id,
                job_id=water_job_id,
                technician_id=None,
                audit_correlation_id="audit-dashboard-water-detail",
                previous_state="dispatched",
                new_state="monitoring_required",
                event_fingerprint="dashboard-water-detail-event-2",
                is_immutable=True,
            ),
            OperationalEventRecord(
                id=first_timeline_id,
                occurred_at=datetime(2026, 5, 16, 9, 45, tzinfo=UTC),
                recorded_at=datetime(2026, 5, 16, 9, 45, tzinfo=UTC),
                event_type="water_emergency.extraction_started",
                event_state="recorded",
                entity_type="water_emergency",
                entity_id=water_emergency.id,
                route_assignment_id=None,
                visit_id=None,
                work_order_id=water_work_order_id,
                job_id=water_job_id,
                technician_id=None,
                audit_correlation_id="audit-dashboard-water-detail",
                previous_state="new",
                new_state="extraction_started",
                event_fingerprint="dashboard-water-detail-event-1",
                is_immutable=True,
            ),
        ],
    )

    detail = DashboardReadModelService().build_water_emergency_detail(
        water_emergency.id,
        jobs=records["jobs"],
        work_orders=records["work_orders"],
        visits=records["visits"],
        review_items=records["review_items"],
        water_emergencies=records["water_emergencies"],
        operational_events=records["operational_events"],
    )

    assert detail is not None
    assert detail.record.water_emergency_id == water_emergency.id
    assert detail.job is not None
    assert detail.job.job_id == water_job_id
    assert detail.work_orders[0].work_order_id == water_work_order_id
    assert detail.equipment_context.equipment_onsite is True
    assert detail.equipment_context.moisture_tracking_required is True
    assert detail.equipment_context.inventory_entity_available is False
    assert detail.equipment_context.required_equipment_notes[0].work_order_id == water_work_order_id
    assert "equipment_inventory_not_modeled" in detail.equipment_context.unknown_indicators
    assert detail.visit_chain.total_visits == 2
    assert detail.visit_chain.open_visit_count == 2
    assert bucket_count(detail.visit_chain.visit_status_counts, "scheduled") == 1
    assert detail.drying_stage_context.status == "drying_in_progress"
    assert detail.drying_stage_context.current_stage == "monitoring"
    assert detail.drying_stage_context.missing_indicators == ()
    assert len(detail.visits) == 2
    assert [review.reason_code for review in detail.review_indicators] == [
        "water_detail_unknown_blocker",
    ]
    assert detail.record.open_review_count == 1
    assert detail.review_exception_context.total_review_count == 1
    assert detail.review_exception_context.open_review_count == 1
    assert detail.review_exception_context.critical_unresolved_count == 1
    assert detail.next_step_readiness.primary_label == "needs_manual_review"
    assert "needs_operator_decision" in detail.next_step_readiness.labels
    assert detail.next_step_readiness.open_review_count == 1
    assert detail.next_step_readiness.critical_alert_count == 1
    assert detail.next_step_readiness.requires_operator_attention is True
    assert any(
        reference.startswith("review:")
        for reference in detail.next_step_readiness.evidence_references
    )
    assert (
        bucket_count(
            detail.review_exception_context.blocker_reason_counts,
            "water_detail_unknown_blocker",
        )
        == 1
    )
    assert "audit-dashboard-water-detail" in detail.review_exception_context.audit_correlation_ids
    assert [entry.event_type for entry in detail.timeline_summary.entries] == [
        "water_emergency.extraction_started",
        "water_emergency.monitoring_required",
    ]
    assert detail.data_gap_counts == ()


def test_water_emergency_detail_review_exception_context_reports_missing_scoped_review() -> None:
    records = dashboard_source_records()
    water_emergency = records["water_emergencies"][0]
    assert isinstance(water_emergency, WaterEmergency)

    detail = DashboardReadModelService().build_water_emergency_detail(
        water_emergency.id,
        jobs=records["jobs"],
        work_orders=records["work_orders"],
        visits=records["visits"],
        review_items=records["review_items"],
        water_emergencies=records["water_emergencies"],
        operational_events=records["operational_events"],
    )

    assert detail is not None
    assert detail.review_exception_context.total_review_count == 0
    assert "no_scoped_review_items" in detail.review_exception_context.unknown_indicators


def test_water_emergency_next_step_missing_data_blocks_readiness() -> None:
    records = dashboard_source_records()
    water_emergency = records["water_emergencies"][0]
    assert isinstance(water_emergency, WaterEmergency)
    water_emergency.drying_stage = None
    water_emergency.next_required_action = None
    water_emergency.moisture_tracking_required = True

    records["visits"] = [
        visit
        for visit in records["visits"]
        if getattr(visit, "job_id", None) != water_emergency.job_id
    ]
    records["review_items"] = []
    records["operational_events"] = []

    detail = DashboardReadModelService().build_water_emergency_detail(
        water_emergency.id,
        jobs=records["jobs"],
        work_orders=records["work_orders"],
        visits=records["visits"],
        review_items=records["review_items"],
        water_emergencies=records["water_emergencies"],
        operational_events=records["operational_events"],
    )

    assert detail is not None
    assert detail.next_step_readiness.primary_label == "blocked_by_missing_data"
    assert "awaiting_more_information" in detail.next_step_readiness.labels
    assert "needs_visit_followup" in detail.next_step_readiness.labels
    assert "needs_drying_stage_confirmation" in detail.next_step_readiness.labels
    assert detail.next_step_readiness.open_review_count == 0
    assert detail.next_step_readiness.unknown_count >= 3


def test_water_emergency_next_step_ready_for_close_review_is_visibility_only() -> None:
    job_id = uuid4()
    work_order_id = uuid4()
    visit_id = uuid4()
    water_emergency_id = uuid4()
    event_id = uuid4()
    technician_id = uuid4()
    occurred_at = datetime(2026, 1, 15, 16, tzinfo=UTC)
    water_emergency = WaterEmergency(
        id=water_emergency_id,
        job_id=job_id,
        status="READY_FOR_PICKUP",
        drying_stage="ready_for_pickup",
        next_required_action="Ready for close-review visibility only.",
        equipment_onsite=False,
        moisture_tracking_required=False,
        opened_at=occurred_at,
    )

    detail = DashboardReadModelService().build_water_emergency_detail(
        water_emergency_id,
        jobs=[Job(id=job_id, job_type="water_emergency", status="ready_for_close_review")],
        work_orders=[
            WorkOrder(
                id=work_order_id,
                job_id=job_id,
                status="completed",
                dispatch_status="water_emergency_separated",
                audit_correlation_id="audit-ready-close-review",
            ),
        ],
        visits=[
            Visit(
                id=visit_id,
                job_id=job_id,
                work_order_id=work_order_id,
                technician_id=technician_id,
                visit_type="water_emergency",
                status="completed",
                completed_at=occurred_at,
                audit_correlation_id="audit-ready-close-review",
            ),
        ],
        review_items=[],
        water_emergencies=[water_emergency],
        operational_events=[
            OperationalEventRecord(
                id=event_id,
                occurred_at=occurred_at,
                recorded_at=occurred_at,
                event_type="water_emergency.ready_for_close_review",
                event_state="ready_for_close_review",
                entity_type="water_emergency",
                entity_id=water_emergency_id,
                job_id=job_id,
                work_order_id=work_order_id,
                visit_id=visit_id,
                audit_correlation_id="audit-ready-close-review",
                event_fingerprint="ready-close-review-test",
            ),
        ],
    )

    assert detail is not None
    assert detail.next_step_readiness.primary_label == "ready_for_close_review"
    assert detail.next_step_readiness.labels == ("ready_for_close_review",)
    assert detail.next_step_readiness.requires_operator_attention is True
    assert detail.next_step_readiness.open_review_count == 0
    assert detail.next_step_readiness.blocker_count == 0
    assert detail.next_step_readiness.unknown_count == 0


def test_closed_water_emergency_next_step_does_not_imply_active_action() -> None:
    records = dashboard_source_records()
    closed_water_emergency = records["water_emergencies"][1]
    assert isinstance(closed_water_emergency, WaterEmergency)

    detail = DashboardReadModelService().build_water_emergency_detail(
        closed_water_emergency.id,
        jobs=records["jobs"],
        work_orders=records["work_orders"],
        visits=records["visits"],
        review_items=records["review_items"],
        water_emergencies=records["water_emergencies"],
        operational_events=records["operational_events"],
    )

    assert detail is not None
    assert detail.next_step_readiness.primary_label == "closed_no_active_next_step"
    assert detail.next_step_readiness.labels == ("closed_no_active_next_step",)
    assert detail.next_step_readiness.requires_operator_attention is False
    assert detail.next_step_readiness.open_review_count == 0


def test_water_emergency_detail_read_model_returns_none_for_missing_record() -> None:
    records = dashboard_source_records()

    detail = DashboardReadModelService().build_water_emergency_detail(
        uuid4(),
        jobs=records["jobs"],
        work_orders=records["work_orders"],
        visits=records["visits"],
        review_items=records["review_items"],
        water_emergencies=records["water_emergencies"],
        operational_events=records["operational_events"],
    )

    assert detail is None


def test_external_execution_summary_counts_adapter_and_confirmation_state() -> None:
    external = build_overview().dispatch_summary.external_execution

    assert bucket_count(external.adapter_state_counts, "awaiting_external_execution") == 1
    assert bucket_count(external.execution_state_counts, "failed") == 1
    assert bucket_count(external.confirmation_state_counts, "failed") == 1
    assert external.prepared_count == 1
    assert external.execution_completed_count == 1
    assert external.execution_failed_count == 1
    assert external.confirmation_failed_count == 1
    assert external.retry_prepared_count == 1
    assert external.reconciliation_required_count == 1


def test_reconciliation_recovery_and_accountability_counts_are_read_models() -> None:
    dispatch = build_overview().dispatch_summary

    assert (
        bucket_count(
            dispatch.reconciliation_recovery.reconciliation_state_counts,
            "reconciliation_required",
        )
        == 1
    )
    assert dispatch.reconciliation_recovery.mismatch_count == 2
    assert dispatch.reconciliation_recovery.divergence_count == 1
    assert dispatch.reconciliation_recovery.replay_prepared_count == 1
    assert dispatch.reconciliation_recovery.recovery_blocked_count == 1

    assert (
        bucket_count(
            dispatch.governance_accountability.governance_state_counts, "operator_approved"
        )
        == 1
    )
    assert dispatch.governance_accountability.operator_approved_count == 1
    assert dispatch.governance_accountability.escalation_required_count == 1
    assert dispatch.governance_accountability.accountability_blocked_count == 1


def test_operational_timeline_is_ordered_and_preserves_audit_correlation() -> None:
    timeline = build_overview().timeline_summary

    assert timeline.total_events == 2
    assert timeline.returned_events == 2
    assert timeline.mutable_event_count == 0
    assert timeline.audit_correlation_ids == ("audit-dashboard-001",)
    assert [entry.event_type for entry in timeline.entries] == [
        "dispatch_execution.dispatched",
        "external_adapter.prepared",
    ]
    assert timeline.entries[0].audit_correlation_id == "audit-dashboard-001"


def test_dashboard_read_models_do_not_mutate_orm_objects() -> None:
    records = dashboard_source_records()
    route_assignments = records["route_assignments"]
    before = [
        (
            route.status,
            route.external_execution_state,
            route.dispatch_reconciliation_state,
            route.replay_recovery_state,
            route.governance_state,
            route.accountability_state,
        )
        for route in route_assignments
    ]

    DashboardReadModelService().build_overview(
        intake_records=records["intake_records"],
        jobs=records["jobs"],
        work_orders=records["work_orders"],
        visits=records["visits"],
        route_assignments=route_assignments,
        review_items=records["review_items"],
        water_emergencies=records["water_emergencies"],
        operational_events=records["operational_events"],
    )

    after = [
        (
            route.status,
            route.external_execution_state,
            route.dispatch_reconciliation_state,
            route.replay_recovery_state,
            route.governance_state,
            route.accountability_state,
        )
        for route in route_assignments
    ]
    assert after == before
