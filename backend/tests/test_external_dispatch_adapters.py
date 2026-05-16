from datetime import UTC, date, datetime
from uuid import uuid4

from app.domain.external_dispatch_adapter import (
    ExternalAdapterFailureCode,
    ExternalAdapterLifecycleState,
)
from app.models.route_assignment import RouteAssignment
from app.models.technician import Technician
from app.models.visit import Visit
from app.services.external_dispatch_adapters.service import (
    ExternalDispatchAdapterPreparationService,
)


def dispatched_route_assignment() -> tuple[RouteAssignment, Visit, Technician]:
    route_assignment_id = uuid4()
    visit_id = uuid4()
    work_order_id = uuid4()
    job_id = uuid4()
    technician_id = uuid4()
    audit_correlation_id = "audit-module-15"
    dispatched_at = datetime(2026, 5, 15, 18, 0, tzinfo=UTC)

    technician = Technician(
        id=technician_id,
        full_name="Luis Technician",
        is_active=True,
        availability_status="available",
        skills=["carpet_cleaning"],
        service_areas=["DE"],
        vehicle_label="Truck 1",
        fastfield_user_id="ff-luis",
    )
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
            "dispatch_execution": "executed_internal_only",
            "dispatch_execution_state": "dispatched",
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
        dispatch_lifecycle_snapshot={
            "previous_state": "awaiting_dispatch_execution",
            "new_state": "dispatched",
            "transitioned_at": dispatched_at.isoformat(),
        },
        dispatched_at=dispatched_at,
    )
    return route_assignment, visit, technician


def test_adapter_preparation_success_creates_external_payload_boundary() -> None:
    route_assignment, visit, technician = dispatched_route_assignment()

    result = ExternalDispatchAdapterPreparationService(
        now=lambda: datetime(2026, 5, 15, 19, 0, tzinfo=UTC),
    ).prepare_adapters(route_assignment, visit=visit, technician=technician)

    assert result.succeeded is True
    assert result.state == ExternalAdapterLifecycleState.AWAITING_EXTERNAL_EXECUTION
    assert result.request.route_assignment_id == route_assignment.id
    assert result.request.visit_id == visit.id
    assert result.request.audit_correlation_id == route_assignment.audit_correlation_id
    assert route_assignment.external_adapter_state == "awaiting_external_execution"
    assert route_assignment.external_adapter_prepared_at == datetime(
        2026,
        5,
        15,
        19,
        0,
        tzinfo=UTC,
    )
    assert (
        route_assignment.external_adapter_payload_snapshot["fastfield"]["execution_mode"]
        == "prepare_only"
    )
    assert (
        route_assignment.external_adapter_payload_snapshot["fastfield"]["external_execution"]
        == "not_executed"
    )
    assert visit.lifecycle_metadata["external_adapter_state"] == "awaiting_external_execution"


def test_blocked_visit_cannot_prepare_external_adapters() -> None:
    route_assignment, visit, technician = dispatched_route_assignment()
    visit.status = "blocked"

    result = ExternalDispatchAdapterPreparationService().prepare_adapters(
        route_assignment,
        visit=visit,
        technician=technician,
    )

    assert result.succeeded is False
    assert result.state == ExternalAdapterLifecycleState.EXTERNAL_EXECUTION_BLOCKED
    assert ExternalAdapterFailureCode.BLOCKED_VISIT in result.failure_codes
    assert route_assignment.external_adapter_state is None


def test_review_required_lifecycle_blocks_adapter_preparation() -> None:
    route_assignment, visit, technician = dispatched_route_assignment()
    visit.status = "review_required"

    result = ExternalDispatchAdapterPreparationService().prepare_adapters(
        route_assignment,
        visit=visit,
        technician=technician,
    )

    assert result.succeeded is False
    assert ExternalAdapterFailureCode.REVIEW_REQUIRED in result.failure_codes


def test_water_emergency_visit_blocks_standard_external_adapter_path() -> None:
    route_assignment, visit, technician = dispatched_route_assignment()
    visit.visit_type = "water_emergency"

    result = ExternalDispatchAdapterPreparationService().prepare_adapters(
        route_assignment,
        visit=visit,
        technician=technician,
    )

    assert result.succeeded is False
    assert result.failure_codes[0] == ExternalAdapterFailureCode.WATER_EMERGENCY_VISIT


def test_duplicate_adapter_preparation_is_blocked() -> None:
    route_assignment, visit, technician = dispatched_route_assignment()
    service = ExternalDispatchAdapterPreparationService(
        now=lambda: datetime(2026, 5, 15, 19, 0, tzinfo=UTC),
    )
    service.prepare_adapters(route_assignment, visit=visit, technician=technician)

    result = service.prepare_adapters(route_assignment, visit=visit, technician=technician)

    assert result.succeeded is False
    assert ExternalAdapterFailureCode.DUPLICATE_ADAPTER_PREPARATION in result.failure_codes
    assert route_assignment.external_adapter_state == "awaiting_external_execution"


def test_unauthorized_route_assignment_blocks_adapter_preparation() -> None:
    route_assignment, visit, technician = dispatched_route_assignment()
    route_assignment.dispatch_authorization_snapshot["authorized_for_dispatch"] = False

    result = ExternalDispatchAdapterPreparationService().prepare_adapters(
        route_assignment,
        visit=visit,
        technician=technician,
    )

    assert result.succeeded is False
    assert ExternalAdapterFailureCode.UNAUTHORIZED_ROUTE_ASSIGNMENT in result.failure_codes


def test_payload_evidence_is_generated_without_live_external_execution() -> None:
    route_assignment, visit, technician = dispatched_route_assignment()

    result = ExternalDispatchAdapterPreparationService().prepare_adapters(
        route_assignment,
        visit=visit,
        technician=technician,
    )

    payloads = result.evidence.payloads
    assert set(payloads) == {
        "fastfield",
        "google_sheets",
        "google_calendar",
        "technician_mobile",
    }
    assert all(payload["execution_mode"] == "prepare_only" for payload in payloads.values())
    assert all(payload["external_execution"] == "not_executed" for payload in payloads.values())
    assert result.evidence.adapter_execution["external_api_calls"] == "not_executed"


def test_undispatched_visit_cannot_prepare_external_adapters() -> None:
    route_assignment, visit, technician = dispatched_route_assignment()
    visit.status = "awaiting_dispatch_execution"

    result = ExternalDispatchAdapterPreparationService().prepare_adapters(
        route_assignment,
        visit=visit,
        technician=technician,
    )

    assert result.succeeded is False
    assert ExternalAdapterFailureCode.VISIT_NOT_DISPATCHED in result.failure_codes
    assert ExternalAdapterFailureCode.INVALID_LIFECYCLE in result.failure_codes


def test_external_adapter_audit_log_preserves_traceability() -> None:
    route_assignment, visit, technician = dispatched_route_assignment()
    service = ExternalDispatchAdapterPreparationService(
        now=lambda: datetime(2026, 5, 15, 19, 0, tzinfo=UTC),
    )
    service.prepare_adapters(route_assignment, visit=visit, technician=technician)

    audit_log = service.build_adapter_prepared_audit_log(route_assignment)

    assert audit_log.action == "external_dispatch_adapter.prepared"
    assert audit_log.entity_type == "route_assignment"
    assert audit_log.entity_id == route_assignment.id
    assert audit_log.audit_correlation_id == "audit-module-15"
    assert audit_log.details["external_adapter_state"] == "awaiting_external_execution"
    assert audit_log.details["external_api_calls"] == "not_executed"
    assert audit_log.details["visit_id"] == str(visit.id)
