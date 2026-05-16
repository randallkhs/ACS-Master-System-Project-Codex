from datetime import UTC, date, datetime
from uuid import uuid4

from app.domain.operational_accountability import (
    AccountabilityEscalationType,
    AccountabilityFailureCode,
    AccountabilityLifecycleState,
)
from app.models.operational_event_record import OperationalEventRecord
from app.models.route_assignment import RouteAssignment
from app.models.visit import Visit
from app.services.operational_accountability.service import OperationalAccountabilityService


def accountability_ready_route_assignment() -> tuple[RouteAssignment, Visit]:
    route_assignment_id = uuid4()
    visit_id = uuid4()
    work_order_id = uuid4()
    job_id = uuid4()
    technician_id = uuid4()
    audit_correlation_id = "audit-module-22"

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
            "governance_state": "operator_approved",
            "replay_recovery_state": "replay_prepared",
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
        dispatched_at=datetime(2026, 5, 15, 18, 0, tzinfo=UTC),
        dispatch_reconciliation_state="reconciliation_required",
        dispatch_reconciliation_prepared_at=datetime(2026, 5, 15, 21, 10, tzinfo=UTC),
        dispatch_divergence_snapshot={
            "manual_resolution_required": True,
            "critical_divergence": True,
        },
        dispatch_mismatch_snapshot={
            "mismatch_count": 1,
            "mismatches": [{"code": "external_confirmation_mismatch"}],
        },
        replay_recovery_state="replay_prepared",
        replay_preparation_snapshot={
            "replay_prepared": True,
            "replay_execution": "not_executed",
            "automatic_replay_execution": "not_executed",
        },
        replay_eligibility_snapshot={"eligible_for_replay": True},
        recovery_coordination_snapshot={"manual_recovery_required": True},
        replay_recovery_audit_snapshot={"audit_correlation_id": audit_correlation_id},
        replay_prepared_at=datetime(2026, 5, 15, 21, 20, tzinfo=UTC),
        governance_state="operator_approved",
        governance_approval_snapshot={
            "approved": True,
            "operation": "replay",
            "replay_execution": "not_executed",
        },
        replay_authorization_snapshot={
            "authorized_for_replay": True,
            "replay_execution": "not_executed",
        },
        governance_audit_snapshot={
            "operator_id": "operator-luis",
            "operator_role": "operations_manager",
            "immutable_history_mutated": False,
        },
        governance_approved_at=datetime(2026, 5, 15, 21, 30, tzinfo=UTC),
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
        occurred_at=datetime(2026, 5, 15, 21, 35, tzinfo=UTC),
        recorded_at=datetime(2026, 5, 15, 21, 35, tzinfo=UTC),
        event_type="operational_governance.operator_approved",
        event_state="operator_approved",
        entity_type="route_assignment",
        entity_id=route_assignment.id,
        route_assignment_id=route_assignment.id,
        visit_id=visit.id,
        work_order_id=visit.work_order_id,
        job_id=route_assignment.job_id,
        technician_id=route_assignment.technician_id,
        audit_correlation_id=route_assignment.audit_correlation_id,
        previous_state="replay_prepared",
        new_state="operator_approved",
        event_fingerprint=f"event:{route_assignment.id}:{is_immutable}",
        is_immutable=is_immutable,
        event_snapshot={"governance_state": "operator_approved"},
        transition_snapshot={"replay_execution": "not_executed"},
        immutable_evidence_snapshot={"immutable": is_immutable, "append_only": True},
        retry_recovery_snapshot=route_assignment.replay_preparation_snapshot,
        reconciliation_snapshot=route_assignment.dispatch_divergence_snapshot,
        audit_snapshot={"audit_correlation_id": route_assignment.audit_correlation_id},
    )


def test_escalation_preparation_success_preserves_governance_and_immutable_evidence() -> None:
    route_assignment, visit = accountability_ready_route_assignment()
    event = immutable_event_record(route_assignment, visit)

    result = OperationalAccountabilityService(
        now=lambda: datetime(2026, 5, 15, 21, 40, tzinfo=UTC),
    ).prepare_escalation(
        route_assignment,
        visit=visit,
        operator_id="operator-luis",
        operator_role="operations_manager",
        escalation_type=AccountabilityEscalationType.CRITICAL_DIVERGENCE,
        operational_events=(event,),
    )

    assert result.succeeded is True
    assert result.state == AccountabilityLifecycleState.ESCALATION_REQUIRED
    assert route_assignment.accountability_state == "escalation_required"
    assert route_assignment.escalation_preparation_snapshot["escalation_execution"] == (
        "not_executed"
    )
    assert route_assignment.accountability_evidence_snapshot["governance_state"] == (
        "operator_approved"
    )
    assert route_assignment.accountability_audit_snapshot["immutable_history_mutated"] is False
    assert route_assignment.escalation_required_at == datetime(
        2026,
        5,
        15,
        21,
        40,
        tzinfo=UTC,
    )
    assert event.is_immutable is True


def test_incident_preparation_success_records_incident_without_execution() -> None:
    route_assignment, visit = accountability_ready_route_assignment()

    result = OperationalAccountabilityService(
        now=lambda: datetime(2026, 5, 15, 21, 45, tzinfo=UTC),
    ).prepare_incident(
        route_assignment,
        visit=visit,
        operator_id="operator-luis",
        operator_role="operations_manager",
        incident_type="critical_operational_exception",
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    assert result.succeeded is True
    assert result.state == AccountabilityLifecycleState.INCIDENT_PREPARED
    assert route_assignment.accountability_state == "incident_prepared"
    assert route_assignment.operational_incident_snapshot["incident_execution"] == "not_executed"
    assert route_assignment.operational_incident_snapshot["incident_type"] == (
        "critical_operational_exception"
    )
    assert route_assignment.incident_prepared_at == datetime(
        2026,
        5,
        15,
        21,
        45,
        tzinfo=UTC,
    )


def test_duplicate_escalation_prevention_blocks_second_preparation() -> None:
    route_assignment, visit = accountability_ready_route_assignment()
    service = OperationalAccountabilityService()
    service.prepare_escalation(
        route_assignment,
        visit=visit,
        operator_id="operator-luis",
        operator_role="operations_manager",
        escalation_type=AccountabilityEscalationType.REPLAY_RECOVERY,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    result = service.prepare_escalation(
        route_assignment,
        visit=visit,
        operator_id="operator-luis",
        operator_role="operations_manager",
        escalation_type=AccountabilityEscalationType.REPLAY_RECOVERY,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    assert result.succeeded is False
    assert AccountabilityFailureCode.DUPLICATE_ESCALATION in result.failure_codes
    assert route_assignment.accountability_state == "escalation_required"


def test_invalid_lifecycle_blocks_escalation_preparation() -> None:
    route_assignment, visit = accountability_ready_route_assignment()
    visit.status = "archived"

    result = OperationalAccountabilityService().prepare_escalation(
        route_assignment,
        visit=visit,
        operator_id="operator-luis",
        operator_role="operations_manager",
        escalation_type=AccountabilityEscalationType.CRITICAL_DIVERGENCE,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    assert result.succeeded is False
    assert result.state == AccountabilityLifecycleState.ACCOUNTABILITY_BLOCKED
    assert AccountabilityFailureCode.INVALID_LIFECYCLE in result.failure_codes
    assert route_assignment.accountability_state == "accountability_blocked"


def test_unauthorized_intervention_escalation_blocking() -> None:
    route_assignment, visit = accountability_ready_route_assignment()

    result = OperationalAccountabilityService().prepare_escalation(
        route_assignment,
        visit=visit,
        operator_id="operator-readonly",
        operator_role="viewer",
        escalation_type=AccountabilityEscalationType.MANUAL_INTERVENTION,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    assert result.succeeded is False
    assert AccountabilityFailureCode.UNAUTHORIZED_INTERVENTION_ESCALATION in result.failure_codes
    assert route_assignment.accountability_state == "accountability_blocked"


def test_water_emergency_blocks_standard_accountability_flow() -> None:
    route_assignment, visit = accountability_ready_route_assignment()
    visit.visit_type = "water_emergency"

    result = OperationalAccountabilityService().prepare_escalation(
        route_assignment,
        visit=visit,
        operator_id="operator-luis",
        operator_role="operations_manager",
        escalation_type=AccountabilityEscalationType.CRITICAL_DIVERGENCE,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    assert result.succeeded is False
    assert result.failure_codes[0] == AccountabilityFailureCode.WATER_EMERGENCY_VISIT


def test_mutable_event_history_blocks_accountability_preparation() -> None:
    route_assignment, visit = accountability_ready_route_assignment()
    event = immutable_event_record(route_assignment, visit, is_immutable=False)

    result = OperationalAccountabilityService().prepare_incident(
        route_assignment,
        visit=visit,
        operator_id="operator-luis",
        operator_role="operations_manager",
        incident_type="critical_operational_exception",
        operational_events=(event,),
    )

    assert result.succeeded is False
    assert AccountabilityFailureCode.IMMUTABLE_HISTORY_VIOLATION in result.failure_codes
    assert event.is_immutable is False
    assert route_assignment.accountability_state == "accountability_blocked"


def test_accountability_requires_governance_approval_before_escalation() -> None:
    route_assignment, visit = accountability_ready_route_assignment()
    route_assignment.governance_state = "awaiting_operator_approval"
    route_assignment.governance_approval_snapshot = {"approved": False}

    result = OperationalAccountabilityService().prepare_escalation(
        route_assignment,
        visit=visit,
        operator_id="operator-luis",
        operator_role="operations_manager",
        escalation_type=AccountabilityEscalationType.REPLAY_RECOVERY,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    assert result.succeeded is False
    assert AccountabilityFailureCode.GOVERNANCE_REQUIRED in result.failure_codes


def test_accountability_audit_log_preserves_traceability() -> None:
    route_assignment, visit = accountability_ready_route_assignment()
    service = OperationalAccountabilityService(
        now=lambda: datetime(2026, 5, 15, 21, 40, tzinfo=UTC),
    )
    service.prepare_escalation(
        route_assignment,
        visit=visit,
        operator_id="operator-luis",
        operator_role="operations_manager",
        escalation_type=AccountabilityEscalationType.CRITICAL_DIVERGENCE,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    audit_log = service.build_accountability_audit_log(route_assignment)

    assert audit_log.action == "operational_accountability.escalation_required"
    assert audit_log.entity_type == "route_assignment"
    assert audit_log.entity_id == route_assignment.id
    assert audit_log.audit_correlation_id == "audit-module-22"
    assert audit_log.details["accountability_state"] == "escalation_required"
    assert audit_log.details["escalation_execution"] == "not_executed"
