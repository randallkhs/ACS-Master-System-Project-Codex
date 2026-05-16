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
            WaterEmergency(job_id=water_job_id, status="DRYING_IN_PROGRESS"),
            WaterEmergency(
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
