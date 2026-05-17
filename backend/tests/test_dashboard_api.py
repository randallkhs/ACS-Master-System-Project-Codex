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
    ReconciliationRecoverySummary,
    RouteAssignmentSummary,
    WaterEmergencyDashboardReadModel,
    WaterEmergencyRecordSummary,
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
    app.dependency_overrides[get_db_session] = override_db_session

    with TestClient(app) as client:
        overview_response = client.get("/api/v1/dashboard/overview")
        lifecycle_response = client.get("/api/v1/dashboard/lifecycle")
        review_response = client.get("/api/v1/dashboard/review")
        dispatch_response = client.get("/api/v1/dashboard/dispatch")
        water_response = client.get("/api/v1/dashboard/water-emergency")
        mutation_response = client.post("/api/v1/dashboard/overview")
        water_mutation_response = client.post("/api/v1/dashboard/water-emergency")

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
    assert water_response.json()["records"][0]["related_visit_ids"] == [
        "00000000-0000-0000-0000-000000000033",
    ]
    assert mutation_response.status_code == 405
    assert water_mutation_response.status_code == 405
