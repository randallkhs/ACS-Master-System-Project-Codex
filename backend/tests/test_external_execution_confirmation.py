from datetime import UTC, date, datetime
from uuid import uuid4

from app.domain.external_execution_confirmation import (
    ExternalConfirmationFailureCode,
    ExternalConfirmationLifecycleState,
    SimulatedExternalConfirmationState,
)
from app.models.route_assignment import RouteAssignment
from app.models.visit import Visit
from app.services.external_execution_confirmation.service import (
    ExternalExecutionConfirmationService,
)


def confirmation_ready_route_assignment() -> tuple[RouteAssignment, Visit]:
    route_assignment_id = uuid4()
    visit_id = uuid4()
    work_order_id = uuid4()
    job_id = uuid4()
    technician_id = uuid4()
    audit_correlation_id = "audit-module-16"

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
            "external_adapter_state": "awaiting_external_confirmation",
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
        external_adapter_state="awaiting_external_confirmation",
        external_adapter_prepared_at=datetime(2026, 5, 15, 19, 0, tzinfo=UTC),
        external_adapter_payload_snapshot={
            "fastfield": {
                "execution_mode": "prepare_only",
                "external_execution": "not_executed",
            },
            "google_sheets": {
                "execution_mode": "prepare_only",
                "external_execution": "not_executed",
            },
            "google_calendar": {
                "execution_mode": "prepare_only",
                "external_execution": "not_executed",
            },
            "technician_mobile": {
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


def test_external_confirmation_success_preserves_evidence() -> None:
    route_assignment, visit = confirmation_ready_route_assignment()

    result = ExternalExecutionConfirmationService(
        now=lambda: datetime(2026, 5, 15, 20, 0, tzinfo=UTC),
    ).process_confirmation(
        route_assignment,
        visit=visit,
        simulated_state=SimulatedExternalConfirmationState.CONFIRMED,
        adapter_name="fastfield",
        external_reference="sim-fastfield-123",
    )

    assert result.succeeded is True
    assert result.state == ExternalConfirmationLifecycleState.EXTERNALLY_CONFIRMED
    assert result.traceability.route_assignment_id == route_assignment.id
    assert route_assignment.external_confirmation_state == "externally_confirmed"
    assert route_assignment.external_confirmed_at == datetime(2026, 5, 15, 20, 0, tzinfo=UTC)
    assert route_assignment.external_confirmation_snapshot["simulated_external_state"] == (
        "confirmed"
    )
    assert route_assignment.external_confirmation_snapshot["external_reference"] == (
        "sim-fastfield-123"
    )
    assert route_assignment.external_confirmation_snapshot["external_api_calls"] == ("not_executed")
    assert route_assignment.external_confirmation_lifecycle_snapshot["previous_state"] == (
        "awaiting_external_confirmation"
    )
    assert route_assignment.external_confirmation_lifecycle_snapshot["next_state"] == (
        "externally_confirmed"
    )
    assert visit.lifecycle_metadata["external_confirmation_state"] == "externally_confirmed"


def test_duplicate_external_confirmation_is_blocked() -> None:
    route_assignment, visit = confirmation_ready_route_assignment()
    service = ExternalExecutionConfirmationService(
        now=lambda: datetime(2026, 5, 15, 20, 0, tzinfo=UTC),
    )
    service.process_confirmation(
        route_assignment,
        visit=visit,
        simulated_state=SimulatedExternalConfirmationState.CONFIRMED,
    )

    result = service.process_confirmation(
        route_assignment,
        visit=visit,
        simulated_state=SimulatedExternalConfirmationState.CONFIRMED,
    )

    assert result.succeeded is False
    assert ExternalConfirmationFailureCode.DUPLICATE_CONFIRMATION in result.failure_codes
    assert route_assignment.external_confirmation_state == "externally_confirmed"


def test_invalid_lifecycle_blocks_external_confirmation() -> None:
    route_assignment, visit = confirmation_ready_route_assignment()
    route_assignment.external_adapter_state = "awaiting_external_execution"

    result = ExternalExecutionConfirmationService().process_confirmation(
        route_assignment,
        visit=visit,
        simulated_state=SimulatedExternalConfirmationState.CONFIRMED,
    )

    assert result.succeeded is False
    assert ExternalConfirmationFailureCode.ADAPTER_NOT_READY_FOR_CONFIRMATION in (
        result.failure_codes
    )
    assert ExternalConfirmationFailureCode.INVALID_LIFECYCLE in result.failure_codes
    assert route_assignment.external_confirmation_state is None


def test_failed_confirmation_can_prepare_retry_without_executing_retry() -> None:
    route_assignment, visit = confirmation_ready_route_assignment()
    service = ExternalExecutionConfirmationService(
        now=lambda: datetime(2026, 5, 15, 20, 0, tzinfo=UTC),
    )

    failure_result = service.process_confirmation(
        route_assignment,
        visit=visit,
        simulated_state=SimulatedExternalConfirmationState.FAILED,
        adapter_name="fastfield",
        failure_message="Simulated FastField timeout",
    )
    retry_result = service.prepare_retry(
        route_assignment,
        visit=visit,
        retry_reason="retry after simulated timeout",
    )

    assert failure_result.succeeded is True
    assert failure_result.state == ExternalConfirmationLifecycleState.EXTERNAL_CONFIRMATION_FAILED
    assert route_assignment.external_confirmation_failed_at == datetime(
        2026,
        5,
        15,
        20,
        0,
        tzinfo=UTC,
    )
    assert route_assignment.external_failure_snapshot["failure_message"] == (
        "Simulated FastField timeout"
    )
    assert retry_result.succeeded is True
    assert retry_result.state == ExternalConfirmationLifecycleState.AWAITING_RETRY
    assert route_assignment.external_confirmation_state == "awaiting_retry"
    assert route_assignment.retry_preparation_snapshot["retry_execution"] == "not_executed"
    assert route_assignment.retry_prepared_at == datetime(2026, 5, 15, 20, 0, tzinfo=UTC)


def test_retry_preparation_blocks_invalid_lifecycle() -> None:
    route_assignment, visit = confirmation_ready_route_assignment()
    service = ExternalExecutionConfirmationService()
    service.process_confirmation(
        route_assignment,
        visit=visit,
        simulated_state=SimulatedExternalConfirmationState.FAILED,
    )
    visit.status = "archived"

    result = service.prepare_retry(
        route_assignment,
        visit=visit,
        retry_reason="retry should not prepare archived visit",
    )

    assert result.succeeded is False
    assert ExternalConfirmationFailureCode.ARCHIVED_VISIT in result.failure_codes
    assert ExternalConfirmationFailureCode.INVALID_LIFECYCLE in result.failure_codes
    assert route_assignment.external_confirmation_state == "external_confirmation_failed"
    assert route_assignment.retry_preparation_snapshot is None


def test_reconciliation_required_transition_preserves_reconciliation_evidence() -> None:
    route_assignment, visit = confirmation_ready_route_assignment()

    result = ExternalExecutionConfirmationService(
        now=lambda: datetime(2026, 5, 15, 20, 0, tzinfo=UTC),
    ).process_confirmation(
        route_assignment,
        visit=visit,
        simulated_state=SimulatedExternalConfirmationState.RECONCILIATION_REQUIRED,
        adapter_name="google_calendar",
        failure_message="Simulated vendor mismatch",
    )

    assert result.succeeded is True
    assert result.state == ExternalConfirmationLifecycleState.RECONCILIATION_REQUIRED
    assert route_assignment.external_confirmation_state == "reconciliation_required"
    assert route_assignment.reconciliation_snapshot["reconciliation_required"] is True
    assert route_assignment.reconciliation_snapshot["reconciliation_execution"] == "not_executed"
    assert route_assignment.reconciliation_required_at == datetime(
        2026,
        5,
        15,
        20,
        0,
        tzinfo=UTC,
    )


def test_water_emergency_blocks_standard_external_confirmation() -> None:
    route_assignment, visit = confirmation_ready_route_assignment()
    visit.visit_type = "water_emergency"

    result = ExternalExecutionConfirmationService().process_confirmation(
        route_assignment,
        visit=visit,
        simulated_state=SimulatedExternalConfirmationState.CONFIRMED,
    )

    assert result.succeeded is False
    assert result.failure_codes[0] == ExternalConfirmationFailureCode.WATER_EMERGENCY_VISIT


def test_blocked_or_review_required_lifecycle_cannot_confirm() -> None:
    route_assignment, visit = confirmation_ready_route_assignment()
    visit.status = "review_required"

    result = ExternalExecutionConfirmationService().process_confirmation(
        route_assignment,
        visit=visit,
        simulated_state=SimulatedExternalConfirmationState.CONFIRMED,
    )

    assert result.succeeded is False
    assert ExternalConfirmationFailureCode.REVIEW_REQUIRED in result.failure_codes
    assert ExternalConfirmationFailureCode.INVALID_LIFECYCLE in result.failure_codes


def test_unauthorized_route_assignment_cannot_confirm() -> None:
    route_assignment, visit = confirmation_ready_route_assignment()
    route_assignment.dispatch_authorization_snapshot["authorized_for_dispatch"] = False

    result = ExternalExecutionConfirmationService().process_confirmation(
        route_assignment,
        visit=visit,
        simulated_state=SimulatedExternalConfirmationState.CONFIRMED,
    )

    assert result.succeeded is False
    assert ExternalConfirmationFailureCode.UNAUTHORIZED_ROUTE_ASSIGNMENT in result.failure_codes


def test_external_confirmation_audit_log_preserves_traceability() -> None:
    route_assignment, visit = confirmation_ready_route_assignment()
    service = ExternalExecutionConfirmationService(
        now=lambda: datetime(2026, 5, 15, 20, 0, tzinfo=UTC),
    )
    service.process_confirmation(
        route_assignment,
        visit=visit,
        simulated_state=SimulatedExternalConfirmationState.CONFIRMED,
        adapter_name="fastfield",
        external_reference="sim-fastfield-123",
    )

    audit_log = service.build_external_confirmation_audit_log(route_assignment)

    assert audit_log.action == "external_execution.confirmed"
    assert audit_log.entity_type == "route_assignment"
    assert audit_log.entity_id == route_assignment.id
    assert audit_log.audit_correlation_id == "audit-module-16"
    assert audit_log.details["external_confirmation_state"] == "externally_confirmed"
    assert audit_log.details["external_api_calls"] == "not_executed"
    assert audit_log.details["visit_id"] == str(visit.id)
