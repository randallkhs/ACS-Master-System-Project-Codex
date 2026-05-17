from __future__ import annotations

import pytest

from app.core.config import Settings
from app.models.intake_processing_record import IntakeProcessingRecord
from app.models.job import Job
from app.models.operational_event_record import OperationalEventRecord
from app.models.review_item import ReviewItem
from app.models.route_assignment import RouteAssignment
from app.models.visit import Visit
from app.models.water_emergency import WaterEmergency
from app.models.work_order import WorkOrder
from app.services.dashboard.service import DashboardReadModelService
from scripts.check_local_database import _read_alembic_revision, validate_local_database_settings
from scripts.seed_dashboard_dev_data import (
    SEED_SOURCE_SYSTEM,
    build_dashboard_dev_seed_records,
    validate_seed_settings,
)
from scripts.verify_dashboard_endpoints import DASHBOARD_ENDPOINTS, verify_endpoint


def bucket_count(buckets: object, label: str) -> int:
    return {bucket.label: bucket.count for bucket in buckets}[label]


def seed_records_of_type(seed_records, model: type[object]) -> tuple[object, ...]:
    return tuple(record for record in seed_records.records if isinstance(record, model))


def test_dashboard_dev_seed_refuses_production() -> None:
    settings = Settings(
        environment="production",
        database_url="postgresql+psycopg://acs_user:secure-pass@db.internal:5432/acs_fsm",
    )

    with pytest.raises(RuntimeError, match="production"):
        validate_seed_settings(settings)


def test_dashboard_dev_seed_requires_local_database_host() -> None:
    settings = Settings(
        environment="development",
        database_url="postgresql+psycopg://acs_user:secure-pass@db.internal:5432/acs_fsm_dev",
    )

    with pytest.raises(RuntimeError, match="local PostgreSQL host"):
        validate_seed_settings(settings)


def test_dashboard_dev_seed_refuses_placeholder_credentials() -> None:
    settings = Settings(
        environment="development",
        database_url="postgresql+psycopg://acs_user:change-me@127.0.0.1:5432/acs_fsm_dev",
    )

    with pytest.raises(RuntimeError, match="placeholder database credentials"):
        validate_seed_settings(settings)


def test_dashboard_dev_seed_accepts_local_development_database_url() -> None:
    settings = Settings(
        environment="development",
        database_url="postgresql+psycopg://acs_fsm_dev:acs_fsm_dev@127.0.0.1:5432/acs_fsm_dev",
    )

    validate_seed_settings(settings)


def test_local_database_check_uses_same_local_safety_boundary() -> None:
    settings = Settings(
        environment="development",
        database_url="postgresql+psycopg://acs_fsm_dev:acs_fsm_dev@127.0.0.1:5432/acs_fsm_dev",
    )

    validate_local_database_settings(settings)

    unsafe_settings = Settings(
        environment="development",
        database_url="postgresql+psycopg://acs_user:secure-pass@db.internal:5432/acs_fsm_dev",
    )

    with pytest.raises(RuntimeError, match="local PostgreSQL host"):
        validate_local_database_settings(unsafe_settings)


def test_local_database_check_reports_unmigrated_database_as_connected() -> None:
    class FakeScalarResult:
        def __init__(self, value: str | None) -> None:
            self.value = value

        def scalar_one_or_none(self) -> str | None:
            return self.value

    class FakeConnection:
        def __init__(self) -> None:
            self.queries: list[str] = []

        def execute(self, statement):
            query = str(statement)
            self.queries.append(query)
            if "to_regclass" in query:
                return FakeScalarResult(None)
            msg = "version table must not be queried before migrations exist"
            raise AssertionError(msg)

    connection = FakeConnection()

    assert _read_alembic_revision(connection) is None
    assert connection.queries == ["select to_regclass('public.alembic_version')"]


def test_dashboard_dev_seed_records_are_synthetic_and_read_only() -> None:
    seed_records = build_dashboard_dev_seed_records()
    source_systems = {
        record.__dict__["source_system"]
        for record in seed_records.records
        if "source_system" in record.__dict__
    }
    event_fingerprints = {
        record.__dict__["event_fingerprint"]
        for record in seed_records.records
        if "event_fingerprint" in record.__dict__
    }

    assert seed_records.record_count == 47
    assert seed_records.scenario_labels == (
        "standard_dispatch_ready",
        "manual_review_blocked",
        "external_confirmation_failed",
        "external_confirmation_succeeded",
        "reconciliation_recovery_required",
        "governance_accountability_required",
        "water_emergency_separated",
        "water_emergency_closed",
    )
    assert source_systems == {SEED_SOURCE_SYSTEM}
    assert "module27-dashboard-demo-dispatched" in event_fingerprints
    assert "module27-dashboard-demo-adapter-prepared" in event_fingerprints
    assert "module29-dashboard-demo-external-confirmed" in event_fingerprints
    assert "module29-dashboard-demo-incident-prepared" in event_fingerprints

    route_assignment = next(
        record
        for record in seed_records.records
        if getattr(record, "external_failure_snapshot", None)
    )
    assert route_assignment.external_failure_snapshot["provider_execution"] == "not_executed"
    assert route_assignment.retry_preparation_snapshot["retry_execution"] == "not_executed"


def test_dashboard_dev_seed_scenarios_cover_realistic_read_model_states() -> None:
    seed_records = build_dashboard_dev_seed_records()
    overview = DashboardReadModelService().build_overview(
        intake_records=seed_records_of_type(seed_records, IntakeProcessingRecord),
        jobs=seed_records_of_type(seed_records, Job),
        work_orders=seed_records_of_type(seed_records, WorkOrder),
        visits=seed_records_of_type(seed_records, Visit),
        route_assignments=seed_records_of_type(seed_records, RouteAssignment),
        review_items=seed_records_of_type(seed_records, ReviewItem),
        water_emergencies=seed_records_of_type(seed_records, WaterEmergency),
        operational_events=seed_records_of_type(seed_records, OperationalEventRecord),
    )

    assert overview.operational_summary.total_jobs == 6
    assert overview.operational_summary.total_route_assignments == 5
    assert overview.operational_summary.open_manual_reviews == 3
    assert overview.operational_summary.open_water_emergencies == 1

    lifecycle = overview.lifecycle_summary
    assert bucket_count(lifecycle.intake_lifecycle_counts, "approved_for_dispatch") == 2
    assert bucket_count(lifecycle.intake_lifecycle_counts, "deferred") == 1
    assert bucket_count(lifecycle.intake_lifecycle_counts, "job_created") == 1
    assert lifecycle.dispatch_ready_visits == 2
    assert lifecycle.dispatched_route_assignments == 2
    assert lifecycle.water_emergency_records == 2
    assert lifecycle.water_emergency_separated_intake == 1

    review = overview.manual_review_summary
    assert review.open_items == 2
    assert review.deferred_items == 1
    assert review.resolved_items == 1
    assert review.archived_items == 1
    assert review.escalation_indicators == 3

    dispatch = overview.dispatch_summary
    assert dispatch.route_assignments.awaiting_dispatch_execution_count == 1
    assert dispatch.route_assignments.blocked_count == 2
    assert dispatch.external_execution.prepared_count == 3
    assert dispatch.external_execution.execution_failed_count == 1
    assert dispatch.external_execution.confirmation_failed_count == 1
    assert dispatch.external_execution.reconciliation_required_count == 2
    assert dispatch.reconciliation_recovery.mismatch_count == 3
    assert dispatch.reconciliation_recovery.divergence_count == 2
    assert dispatch.reconciliation_recovery.rollback_prepared_count == 1
    assert dispatch.governance_accountability.intervention_required_count == 1
    assert dispatch.governance_accountability.incident_prepared_count == 1

    timeline = overview.timeline_summary
    assert timeline.total_events == 8
    assert timeline.mutable_event_count == 0
    assert [entry.occurred_at for entry in timeline.entries] == sorted(
        entry.occurred_at for entry in timeline.entries
    )


def test_dashboard_endpoint_verifier_uses_get_only(monkeypatch) -> None:
    captured_methods: list[str] = []

    class FakeResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self) -> bytes:
            return b'{"status":"ok"}'

    def fake_urlopen(request, *, timeout):
        captured_methods.append(request.get_method())
        assert timeout == 2.0
        return FakeResponse()

    monkeypatch.setattr("scripts.verify_dashboard_endpoints.urlopen", fake_urlopen)

    result = verify_endpoint("http://127.0.0.1:8000", "/api/v1/health", timeout=2.0)

    assert result.ok
    assert result.status_code == 200
    assert result.response_keys == ("status",)
    assert captured_methods == ["GET"]


def test_dashboard_endpoint_verifier_includes_water_emergency_contract() -> None:
    assert "/api/v1/dashboard/water-emergency" in DASHBOARD_ENDPOINTS
