from datetime import UTC, date, datetime
from uuid import uuid4

from app.domain.external_adapter_execution import (
    ExternalExecutionFailureCode,
    ExternalExecutionLifecycleState,
    ProviderExecutionState,
)
from app.models.route_assignment import RouteAssignment
from app.models.visit import Visit
from app.services.external_adapter_execution.service import ExternalAdapterExecutionService


def adapter_prepared_route_assignment() -> tuple[RouteAssignment, Visit]:
    route_assignment_id = uuid4()
    visit_id = uuid4()
    work_order_id = uuid4()
    job_id = uuid4()
    technician_id = uuid4()
    audit_correlation_id = "audit-module-18"

    visit = Visit(
        id=visit_id,
        job_id=job_id,
        work_order_id=work_order_id,
        technician_id=technician_id,
        visit_type="standard",
        status="dispatched",
        audit_correlation_id=audit_correlation_id,
        scheduled_start_at=datetime(2026, 5, 16, 9, 0, tzinfo=UTC),
        scheduled_end_at=datetime(2026, 5, 16, 11, 0, tzinfo=UTC),
        lifecycle_metadata={
            "dispatch_execution_state": "dispatched",
            "external_adapter_state": "awaiting_external_execution",
        },
    )
    route_assignment = RouteAssignment(
        id=route_assignment_id,
        route_date=date(2026, 5, 16),
        technician_id=technician_id,
        job_id=job_id,
        visit_id=visit_id,
        route_order=1,
        region="DE",
        time_window="AM",
        status="dispatched",
        route_group_key="DE-AM-2026-05-16",
        audit_correlation_id=audit_correlation_id,
        dispatch_authorization_snapshot={"authorized_for_dispatch": True},
        dispatch_execution_boundary_snapshot={"authorized_for_dispatch": True},
        dispatch_execution_state="dispatched",
        dispatch_execution_snapshot={
            "state": "dispatched",
            "dispatch_execution": "executed_internal_only",
            "external_integrations": "not_executed",
        },
        dispatched_at=datetime(2026, 5, 15, 18, 0, tzinfo=UTC),
        external_adapter_state="awaiting_external_execution",
        external_adapter_prepared_at=datetime(2026, 5, 15, 19, 0, tzinfo=UTC),
        external_adapter_request_snapshot={
            "route_assignment_id": str(route_assignment_id),
            "visit_id": str(visit_id),
            "audit_correlation_id": audit_correlation_id,
            "target_adapters": [
                "fastfield",
                "google_sheets",
                "google_calendar",
                "technician_mobile",
            ],
            "execution_mode": "prepare_only",
        },
        external_adapter_payload_snapshot={
            "fastfield": {
                "adapter": "fastfield",
                "execution_mode": "prepare_only",
                "external_execution": "not_executed",
            },
            "google_sheets": {
                "adapter": "google_sheets",
                "execution_mode": "prepare_only",
                "external_execution": "not_executed",
            },
            "google_calendar": {
                "adapter": "google_calendar",
                "execution_mode": "prepare_only",
                "external_execution": "not_executed",
            },
            "technician_mobile": {
                "adapter": "technician_mobile",
                "execution_mode": "prepare_only",
                "external_execution": "not_executed",
            },
        },
        external_adapter_evidence_snapshot={
            "adapter_preparation": "prepared",
            "external_api_calls": "not_executed",
        },
    )
    return route_assignment, visit


def test_successful_external_execution_transitions_to_confirmation_ready_state() -> None:
    route_assignment, visit = adapter_prepared_route_assignment()

    result = ExternalAdapterExecutionService(
        now=lambda: datetime(2026, 5, 15, 20, 0, tzinfo=UTC),
    ).execute_prepared_adapters(route_assignment, visit=visit)

    assert result.succeeded is True
    assert result.state == ExternalExecutionLifecycleState.AWAITING_EXTERNAL_CONFIRMATION
    assert route_assignment.external_execution_state == "awaiting_external_confirmation"
    assert route_assignment.external_adapter_state == "awaiting_external_confirmation"
    assert route_assignment.external_execution_completed_at == datetime(
        2026,
        5,
        15,
        20,
        0,
        tzinfo=UTC,
    )
    assert route_assignment.external_execution_evidence_snapshot["external_api_calls"] == (
        "not_executed"
    )
    assert visit.lifecycle_metadata["external_execution_state"] == "awaiting_external_confirmation"


def test_duplicate_external_execution_is_blocked() -> None:
    route_assignment, visit = adapter_prepared_route_assignment()
    service = ExternalAdapterExecutionService(
        now=lambda: datetime(2026, 5, 15, 20, 0, tzinfo=UTC),
    )
    service.execute_prepared_adapters(route_assignment, visit=visit)

    result = service.execute_prepared_adapters(route_assignment, visit=visit)

    assert result.succeeded is False
    assert ExternalExecutionFailureCode.DUPLICATE_EXTERNAL_EXECUTION in result.failure_codes
    assert route_assignment.external_execution_state == "awaiting_external_confirmation"


def test_blocked_visit_cannot_execute_external_adapters() -> None:
    route_assignment, visit = adapter_prepared_route_assignment()
    visit.status = "blocked"

    result = ExternalAdapterExecutionService().execute_prepared_adapters(
        route_assignment,
        visit=visit,
    )

    assert result.succeeded is False
    assert ExternalExecutionFailureCode.BLOCKED_VISIT in result.failure_codes
    assert route_assignment.external_execution_state is None


def test_review_required_lifecycle_blocks_external_execution() -> None:
    route_assignment, visit = adapter_prepared_route_assignment()
    visit.status = "review_required"

    result = ExternalAdapterExecutionService().execute_prepared_adapters(
        route_assignment,
        visit=visit,
    )

    assert result.succeeded is False
    assert ExternalExecutionFailureCode.REVIEW_REQUIRED in result.failure_codes


def test_water_emergency_blocks_standard_external_execution_path() -> None:
    route_assignment, visit = adapter_prepared_route_assignment()
    visit.visit_type = "water_emergency"

    result = ExternalAdapterExecutionService().execute_prepared_adapters(
        route_assignment,
        visit=visit,
    )

    assert result.succeeded is False
    assert result.failure_codes[0] == ExternalExecutionFailureCode.WATER_EMERGENCY_VISIT


def test_invalid_adapter_lifecycle_blocks_external_execution() -> None:
    route_assignment, visit = adapter_prepared_route_assignment()
    route_assignment.external_adapter_state = "internal_dispatch_complete"

    result = ExternalAdapterExecutionService().execute_prepared_adapters(
        route_assignment,
        visit=visit,
    )

    assert result.succeeded is False
    assert ExternalExecutionFailureCode.ADAPTER_NOT_PREPARED in result.failure_codes
    assert ExternalExecutionFailureCode.INVALID_LIFECYCLE in result.failure_codes


def test_unauthorized_route_assignment_blocks_external_execution() -> None:
    route_assignment, visit = adapter_prepared_route_assignment()
    route_assignment.dispatch_authorization_snapshot["authorized_for_dispatch"] = False

    result = ExternalAdapterExecutionService().execute_prepared_adapters(
        route_assignment,
        visit=visit,
    )

    assert result.succeeded is False
    assert ExternalExecutionFailureCode.UNAUTHORIZED_EXECUTION in result.failure_codes


def test_provider_execution_failure_preserves_failure_evidence_without_retry() -> None:
    route_assignment, visit = adapter_prepared_route_assignment()

    result = ExternalAdapterExecutionService(
        now=lambda: datetime(2026, 5, 15, 20, 0, tzinfo=UTC),
    ).execute_prepared_adapters(
        route_assignment,
        visit=visit,
        provider_outcomes={"fastfield": ProviderExecutionState.FAILED},
    )

    assert result.succeeded is False
    assert result.state == ExternalExecutionLifecycleState.EXTERNAL_EXECUTION_FAILED
    assert route_assignment.external_execution_state == "external_execution_failed"
    assert route_assignment.external_execution_failed_at == datetime(
        2026,
        5,
        15,
        20,
        0,
        tzinfo=UTC,
    )
    assert route_assignment.external_execution_failure_snapshot["automatic_retry"] == (
        "not_executed"
    )
    assert route_assignment.external_execution_failure_snapshot["external_api_calls"] == (
        "not_executed"
    )


def test_failed_external_execution_attempt_cannot_be_replayed_silently() -> None:
    route_assignment, visit = adapter_prepared_route_assignment()
    service = ExternalAdapterExecutionService()
    service.execute_prepared_adapters(
        route_assignment,
        visit=visit,
        provider_outcomes={"fastfield": ProviderExecutionState.FAILED},
    )

    result = service.execute_prepared_adapters(route_assignment, visit=visit)

    assert result.succeeded is False
    assert ExternalExecutionFailureCode.DUPLICATE_EXTERNAL_EXECUTION in result.failure_codes
    assert route_assignment.external_execution_state == "external_execution_failed"


def test_provider_execution_traceability_and_audit_continuity() -> None:
    route_assignment, visit = adapter_prepared_route_assignment()
    service = ExternalAdapterExecutionService(
        now=lambda: datetime(2026, 5, 15, 20, 0, tzinfo=UTC),
    )

    result = service.execute_prepared_adapters(route_assignment, visit=visit)
    audit_log = service.build_external_execution_audit_log(route_assignment)

    fastfield_result = result.provider_results["fastfield"]
    assert fastfield_result.provider == "fastfield"
    assert fastfield_result.state == ProviderExecutionState.COMPLETED
    assert fastfield_result.correlation_id.startswith("audit-module-18:fastfield:")
    assert fastfield_result.evidence["real_vendor_execution"] == "not_executed"
    assert (
        route_assignment.external_execution_provider_snapshot["fastfield"]["audit_correlation_id"]
        == "audit-module-18"
    )
    assert audit_log.action == "external_adapter_execution.completed"
    assert audit_log.entity_type == "route_assignment"
    assert audit_log.audit_correlation_id == "audit-module-18"
