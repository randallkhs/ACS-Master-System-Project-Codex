from datetime import UTC, date, datetime
from uuid import uuid4

from app.domain.operational_governance import (
    GovernanceFailureCode,
    GovernanceLifecycleState,
    GovernanceOperation,
)
from app.models.operational_event_record import OperationalEventRecord
from app.models.route_assignment import RouteAssignment
from app.models.visit import Visit
from app.services.operational_governance.service import OperationalGovernanceService


def governance_ready_route_assignment() -> tuple[RouteAssignment, Visit]:
    route_assignment_id = uuid4()
    visit_id = uuid4()
    work_order_id = uuid4()
    job_id = uuid4()
    technician_id = uuid4()
    audit_correlation_id = "audit-module-21"

    visit = Visit(
        id=visit_id,
        job_id=job_id,
        work_order_id=work_order_id,
        technician_id=technician_id,
        visit_type="standard",
        status="dispatched",
        audit_correlation_id=audit_correlation_id,
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
        dispatch_divergence_snapshot={"manual_resolution_required": True},
        dispatch_mismatch_snapshot={"mismatch_count": 1},
        replay_recovery_state="replay_prepared",
        replay_preparation_snapshot={
            "replay_prepared": True,
            "replay_execution": "not_executed",
            "automatic_replay_execution": "not_executed",
        },
        rollback_preparation_snapshot={
            "rollback_prepared": False,
            "rollback_execution": "not_executed",
            "automatic_rollback_execution": "not_executed",
        },
        replay_eligibility_snapshot={"eligible_for_replay": True},
        recovery_coordination_snapshot={"manual_recovery_required": True},
        replay_recovery_audit_snapshot={"audit_correlation_id": audit_correlation_id},
        replay_prepared_at=datetime(2026, 5, 15, 21, 20, tzinfo=UTC),
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
        occurred_at=datetime(2026, 5, 15, 21, 25, tzinfo=UTC),
        recorded_at=datetime(2026, 5, 15, 21, 25, tzinfo=UTC),
        event_type="operational_replay.replay_prepared",
        event_state="replay_prepared",
        entity_type="route_assignment",
        entity_id=route_assignment.id,
        route_assignment_id=route_assignment.id,
        visit_id=visit.id,
        work_order_id=visit.work_order_id,
        job_id=route_assignment.job_id,
        technician_id=route_assignment.technician_id,
        audit_correlation_id=route_assignment.audit_correlation_id,
        previous_state="reconciliation_required",
        new_state="replay_prepared",
        event_fingerprint=f"event:{route_assignment.id}:{is_immutable}",
        is_immutable=is_immutable,
        event_snapshot={"replay_recovery_state": "replay_prepared"},
        transition_snapshot={"replay_execution": "not_executed"},
        immutable_evidence_snapshot={"immutable": is_immutable, "append_only": True},
        retry_recovery_snapshot=route_assignment.replay_preparation_snapshot,
        reconciliation_snapshot=route_assignment.dispatch_divergence_snapshot,
        audit_snapshot={"audit_correlation_id": route_assignment.audit_correlation_id},
    )


def test_governance_approval_success_authorizes_replay_without_execution() -> None:
    route_assignment, visit = governance_ready_route_assignment()
    event = immutable_event_record(route_assignment, visit)

    result = OperationalGovernanceService(
        now=lambda: datetime(2026, 5, 15, 21, 30, tzinfo=UTC),
    ).approve_operation(
        route_assignment,
        visit=visit,
        operator_id="operator-luis",
        operator_role="operations_manager",
        operation=GovernanceOperation.REPLAY,
        operational_events=(event,),
    )

    assert result.succeeded is True
    assert result.state == GovernanceLifecycleState.OPERATOR_APPROVED
    assert route_assignment.governance_state == "operator_approved"
    assert route_assignment.governance_approval_snapshot["approved"] is True
    assert route_assignment.replay_authorization_snapshot["authorized_for_replay"] is True
    assert route_assignment.replay_authorization_snapshot["replay_execution"] == "not_executed"
    assert route_assignment.governance_audit_snapshot["operator_id"] == "operator-luis"
    assert route_assignment.governance_audit_snapshot["immutable_history_mutated"] is False
    assert event.is_immutable is True


def test_duplicate_approval_prevention_blocks_second_approval() -> None:
    route_assignment, visit = governance_ready_route_assignment()
    service = OperationalGovernanceService()
    service.approve_operation(
        route_assignment,
        visit=visit,
        operator_id="operator-luis",
        operator_role="operations_manager",
        operation=GovernanceOperation.REPLAY,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    result = service.approve_operation(
        route_assignment,
        visit=visit,
        operator_id="operator-luis",
        operator_role="operations_manager",
        operation=GovernanceOperation.REPLAY,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    assert result.succeeded is False
    assert GovernanceFailureCode.DUPLICATE_APPROVAL in result.failure_codes
    assert route_assignment.governance_state == "operator_approved"


def test_invalid_lifecycle_blocks_governance_approval() -> None:
    route_assignment, visit = governance_ready_route_assignment()
    visit.status = "archived"

    result = OperationalGovernanceService().approve_operation(
        route_assignment,
        visit=visit,
        operator_id="operator-luis",
        operator_role="operations_manager",
        operation=GovernanceOperation.REPLAY,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    assert result.succeeded is False
    assert result.state == GovernanceLifecycleState.GOVERNANCE_BLOCKED
    assert GovernanceFailureCode.INVALID_LIFECYCLE in result.failure_codes
    assert route_assignment.governance_state == "governance_blocked"


def test_unauthorized_intervention_blocks_governance() -> None:
    route_assignment, visit = governance_ready_route_assignment()

    result = OperationalGovernanceService().authorize_intervention(
        route_assignment,
        visit=visit,
        operator_id="operator-readonly",
        operator_role="viewer",
        intervention_reason="Investigate reconciliation mismatch.",
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    assert result.succeeded is False
    assert GovernanceFailureCode.UNAUTHORIZED_OPERATOR_ACTION in result.failure_codes
    assert route_assignment.governance_state == "governance_blocked"


def test_replay_authorization_requires_replay_preparation() -> None:
    route_assignment, visit = governance_ready_route_assignment()
    route_assignment.replay_recovery_state = "replay_blocked"
    route_assignment.replay_preparation_snapshot = {"replay_prepared": False}

    result = OperationalGovernanceService().approve_operation(
        route_assignment,
        visit=visit,
        operator_id="operator-luis",
        operator_role="operations_manager",
        operation=GovernanceOperation.REPLAY,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    assert result.succeeded is False
    assert GovernanceFailureCode.REPLAY_NOT_PREPARED in result.failure_codes


def test_rollback_authorization_requires_rollback_preparation() -> None:
    route_assignment, visit = governance_ready_route_assignment()

    result = OperationalGovernanceService().approve_operation(
        route_assignment,
        visit=visit,
        operator_id="operator-luis",
        operator_role="operations_manager",
        operation=GovernanceOperation.ROLLBACK,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    assert result.succeeded is False
    assert GovernanceFailureCode.ROLLBACK_NOT_PREPARED in result.failure_codes
    assert route_assignment.governance_state == "governance_blocked"


def test_water_emergency_blocks_standard_governance_flow() -> None:
    route_assignment, visit = governance_ready_route_assignment()
    visit.visit_type = "water_emergency"

    result = OperationalGovernanceService().approve_operation(
        route_assignment,
        visit=visit,
        operator_id="operator-luis",
        operator_role="operations_manager",
        operation=GovernanceOperation.REPLAY,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    assert result.succeeded is False
    assert result.failure_codes[0] == GovernanceFailureCode.WATER_EMERGENCY_VISIT


def test_mutable_event_history_blocks_governance_approval() -> None:
    route_assignment, visit = governance_ready_route_assignment()
    event = immutable_event_record(route_assignment, visit, is_immutable=False)

    result = OperationalGovernanceService().approve_operation(
        route_assignment,
        visit=visit,
        operator_id="operator-luis",
        operator_role="operations_manager",
        operation=GovernanceOperation.REPLAY,
        operational_events=(event,),
    )

    assert result.succeeded is False
    assert GovernanceFailureCode.IMMUTABLE_HISTORY_VIOLATION in result.failure_codes
    assert event.is_immutable is False
    assert route_assignment.governance_state == "governance_blocked"


def test_governance_audit_log_preserves_traceability() -> None:
    route_assignment, visit = governance_ready_route_assignment()
    service = OperationalGovernanceService(
        now=lambda: datetime(2026, 5, 15, 21, 30, tzinfo=UTC),
    )
    service.approve_operation(
        route_assignment,
        visit=visit,
        operator_id="operator-luis",
        operator_role="operations_manager",
        operation=GovernanceOperation.REPLAY,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    audit_log = service.build_governance_audit_log(route_assignment)

    assert audit_log.action == "operational_governance.operator_approved"
    assert audit_log.entity_type == "route_assignment"
    assert audit_log.entity_id == route_assignment.id
    assert audit_log.audit_correlation_id == "audit-module-21"
    assert audit_log.details["governance_state"] == "operator_approved"
    assert audit_log.details["operator_id"] == "operator-luis"
