from datetime import UTC, date, datetime
from uuid import uuid4

from app.domain.dispatch_reconciliation import (
    ReconciliationFailureCode,
    ReconciliationLifecycleState,
    ReconciliationMismatchCode,
)
from app.models.operational_event_record import OperationalEventRecord
from app.models.route_assignment import RouteAssignment
from app.models.visit import Visit
from app.services.dispatch_reconciliation.service import DispatchReconciliationService


def reconciled_route_assignment() -> tuple[RouteAssignment, Visit]:
    route_assignment_id = uuid4()
    visit_id = uuid4()
    work_order_id = uuid4()
    job_id = uuid4()
    technician_id = uuid4()
    audit_correlation_id = "audit-module-19"
    confirmed_at = datetime(2026, 5, 15, 21, 0, tzinfo=UTC)

    visit = Visit(
        id=visit_id,
        job_id=job_id,
        work_order_id=work_order_id,
        technician_id=technician_id,
        visit_type="standard",
        status="dispatched",
        audit_correlation_id=audit_correlation_id,
        lifecycle_metadata={
            "dispatch_execution_state": "dispatched",
            "external_execution_state": "awaiting_external_confirmation",
            "external_confirmation_state": "externally_confirmed",
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
        },
        dispatched_at=datetime(2026, 5, 15, 18, 0, tzinfo=UTC),
        external_adapter_state="awaiting_external_confirmation",
        external_execution_state="awaiting_external_confirmation",
        external_execution_evidence_snapshot={
            "state": "awaiting_external_confirmation",
            "external_api_calls": "not_executed",
            "real_vendor_execution": "not_executed",
        },
        external_execution_completed_at=datetime(2026, 5, 15, 20, 0, tzinfo=UTC),
        external_confirmation_state="externally_confirmed",
        external_confirmation_snapshot={
            "simulated_external_state": "confirmed",
            "external_api_calls": "not_executed",
        },
        external_confirmed_at=confirmed_at,
    )
    return route_assignment, visit


def immutable_event_record(
    route_assignment: RouteAssignment,
    visit: Visit,
    *,
    is_immutable: bool = True,
) -> OperationalEventRecord:
    return OperationalEventRecord(
        id=uuid4(),
        occurred_at=datetime(2026, 5, 15, 21, 5, tzinfo=UTC),
        recorded_at=datetime(2026, 5, 15, 21, 5, tzinfo=UTC),
        event_type="external_execution.confirmed",
        event_state="externally_confirmed",
        entity_type="route_assignment",
        entity_id=route_assignment.id,
        route_assignment_id=route_assignment.id,
        visit_id=visit.id,
        work_order_id=visit.work_order_id,
        job_id=route_assignment.job_id,
        technician_id=route_assignment.technician_id,
        audit_correlation_id=route_assignment.audit_correlation_id,
        previous_state="awaiting_external_confirmation",
        new_state="externally_confirmed",
        event_fingerprint=f"event:{route_assignment.id}:{is_immutable}",
        is_immutable=is_immutable,
        event_snapshot={"external_confirmation_state": "externally_confirmed"},
        transition_snapshot={"external_api_calls": "not_executed"},
        immutable_evidence_snapshot={"immutable": is_immutable, "append_only": True},
        retry_recovery_snapshot={},
        reconciliation_snapshot={},
        audit_snapshot={"audit_correlation_id": route_assignment.audit_correlation_id},
    )


def test_consistency_verification_success_preserves_audit_evidence() -> None:
    route_assignment, visit = reconciled_route_assignment()
    event = immutable_event_record(route_assignment, visit)

    result = DispatchReconciliationService(
        now=lambda: datetime(2026, 5, 15, 21, 10, tzinfo=UTC),
    ).prepare_reconciliation(
        route_assignment,
        visit=visit,
        operational_events=(event,),
    )

    assert result.succeeded is True
    assert result.state == ReconciliationLifecycleState.CONSISTENCY_VERIFIED
    assert result.consistency.is_consistent is True
    assert route_assignment.dispatch_reconciliation_state == "consistency_verified"
    assert route_assignment.dispatch_consistency_snapshot["external_confirmation_state"] == (
        "externally_confirmed"
    )
    assert route_assignment.dispatch_reconciliation_audit_snapshot["external_api_calls"] == (
        "not_executed"
    )
    assert event.is_immutable is True


def test_divergence_detection_classifies_external_confirmation_mismatch() -> None:
    route_assignment, visit = reconciled_route_assignment()
    route_assignment.external_confirmation_state = "external_confirmation_failed"
    route_assignment.external_confirmed_at = None

    result = DispatchReconciliationService().prepare_reconciliation(
        route_assignment,
        visit=visit,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    assert result.succeeded is True
    assert result.state == ReconciliationLifecycleState.RECONCILIATION_REQUIRED
    assert result.consistency.is_consistent is False
    assert result.consistency.divergence_detected is True
    assert ReconciliationMismatchCode.EXTERNAL_CONFIRMATION_MISMATCH in result.mismatch_codes
    assert route_assignment.dispatch_reconciliation_state == "reconciliation_required"
    assert route_assignment.dispatch_divergence_snapshot["manual_resolution_required"] is True


def test_reconciliation_required_transition_records_provider_failure_divergence() -> None:
    route_assignment, visit = reconciled_route_assignment()
    route_assignment.external_execution_state = "external_execution_failed"
    route_assignment.external_confirmation_state = None
    route_assignment.external_execution_failure_snapshot = {
        "state": "external_execution_failed",
        "failed_providers": ["fastfield"],
    }

    result = DispatchReconciliationService().prepare_reconciliation(
        route_assignment,
        visit=visit,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    assert result.succeeded is True
    assert result.state == ReconciliationLifecycleState.RECONCILIATION_REQUIRED
    assert ReconciliationMismatchCode.EXTERNAL_EXECUTION_MISMATCH in result.mismatch_codes
    assert route_assignment.dispatch_mismatch_snapshot["mismatch_count"] >= 1
    assert route_assignment.dispatch_divergence_snapshot["reconciliation_execution"] == (
        "not_executed"
    )


def test_duplicate_reconciliation_prevention_blocks_second_preparation() -> None:
    route_assignment, visit = reconciled_route_assignment()
    route_assignment.external_confirmation_state = "external_confirmation_failed"
    service = DispatchReconciliationService()
    service.prepare_reconciliation(
        route_assignment,
        visit=visit,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    result = service.prepare_reconciliation(
        route_assignment,
        visit=visit,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    assert result.succeeded is False
    assert result.state == ReconciliationLifecycleState.RECONCILIATION_BLOCKED
    assert ReconciliationFailureCode.DUPLICATE_RECONCILIATION in result.failure_codes
    assert route_assignment.dispatch_reconciliation_state == "reconciliation_required"


def test_invalid_lifecycle_blocks_reconciliation_preparation() -> None:
    route_assignment, visit = reconciled_route_assignment()
    visit.status = "archived"

    result = DispatchReconciliationService().prepare_reconciliation(
        route_assignment,
        visit=visit,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    assert result.succeeded is False
    assert result.state == ReconciliationLifecycleState.RECONCILIATION_BLOCKED
    assert ReconciliationFailureCode.INVALID_LIFECYCLE in result.failure_codes
    assert route_assignment.dispatch_reconciliation_state == "reconciliation_blocked"


def test_water_emergency_blocks_standard_reconciliation_path() -> None:
    route_assignment, visit = reconciled_route_assignment()
    visit.visit_type = "water_emergency"

    result = DispatchReconciliationService().prepare_reconciliation(
        route_assignment,
        visit=visit,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    assert result.succeeded is False
    assert result.failure_codes[0] == ReconciliationFailureCode.WATER_EMERGENCY_VISIT


def test_mutable_event_history_blocks_reconciliation_preparation() -> None:
    route_assignment, visit = reconciled_route_assignment()
    event = immutable_event_record(route_assignment, visit, is_immutable=False)

    result = DispatchReconciliationService().prepare_reconciliation(
        route_assignment,
        visit=visit,
        operational_events=(event,),
    )

    assert result.succeeded is False
    assert ReconciliationFailureCode.IMMUTABLE_HISTORY_VIOLATION in result.failure_codes
    assert event.is_immutable is False
    assert route_assignment.dispatch_reconciliation_state == "reconciliation_blocked"


def test_reconciliation_audit_log_preserves_traceability() -> None:
    route_assignment, visit = reconciled_route_assignment()
    service = DispatchReconciliationService(
        now=lambda: datetime(2026, 5, 15, 21, 10, tzinfo=UTC),
    )
    service.prepare_reconciliation(
        route_assignment,
        visit=visit,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    audit_log = service.build_reconciliation_audit_log(route_assignment)

    assert audit_log.action == "dispatch_reconciliation.consistency_verified"
    assert audit_log.entity_type == "route_assignment"
    assert audit_log.entity_id == route_assignment.id
    assert audit_log.audit_correlation_id == "audit-module-19"
    assert audit_log.details["dispatch_reconciliation_state"] == "consistency_verified"
    assert audit_log.details["external_api_calls"] == "not_executed"
