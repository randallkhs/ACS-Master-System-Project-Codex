from datetime import UTC, date, datetime
from uuid import uuid4

from app.domain.operational_replay import (
    ReplayRecoveryFailureCode,
    ReplayRecoveryLifecycleState,
)
from app.models.operational_event_record import OperationalEventRecord
from app.models.route_assignment import RouteAssignment
from app.models.visit import Visit
from app.services.operational_replay.service import OperationalReplayPreparationService


def replay_ready_route_assignment() -> tuple[RouteAssignment, Visit]:
    route_assignment_id = uuid4()
    visit_id = uuid4()
    work_order_id = uuid4()
    job_id = uuid4()
    technician_id = uuid4()
    audit_correlation_id = "audit-module-20"

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
            "dispatch_reconciliation_state": "reconciliation_required",
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
        external_execution_state="awaiting_external_confirmation",
        external_confirmation_state="external_confirmation_failed",
        retry_preparation_snapshot={"retry_eligible": True, "retry_execution": "not_executed"},
        dispatch_reconciliation_state="reconciliation_required",
        dispatch_consistency_snapshot={
            "is_consistent": False,
            "divergence_detected": True,
            "event_history_count": 1,
            "immutable_history_mutated": False,
        },
        dispatch_divergence_snapshot={
            "manual_resolution_required": True,
            "reconciliation_execution": "not_executed",
            "mismatch_codes": ["external_confirmation_mismatch"],
        },
        dispatch_mismatch_snapshot={
            "mismatch_count": 1,
            "mismatches": [{"code": "external_confirmation_mismatch"}],
        },
        dispatch_reconciliation_audit_snapshot={
            "audit_correlation_id": audit_correlation_id,
            "external_api_calls": "not_executed",
            "reconciliation_execution": "not_executed",
        },
        dispatch_reconciliation_prepared_at=datetime(2026, 5, 15, 21, 10, tzinfo=UTC),
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
        occurred_at=datetime(2026, 5, 15, 21, 15, tzinfo=UTC),
        recorded_at=datetime(2026, 5, 15, 21, 15, tzinfo=UTC),
        event_type="dispatch_reconciliation.reconciliation_required",
        event_state="reconciliation_required",
        entity_type="route_assignment",
        entity_id=route_assignment.id,
        route_assignment_id=route_assignment.id,
        visit_id=visit.id,
        work_order_id=visit.work_order_id,
        job_id=route_assignment.job_id,
        technician_id=route_assignment.technician_id,
        audit_correlation_id=route_assignment.audit_correlation_id,
        previous_state="externally_confirmed",
        new_state="reconciliation_required",
        event_fingerprint=f"event:{route_assignment.id}:{is_immutable}",
        is_immutable=is_immutable,
        event_snapshot={"dispatch_reconciliation_state": "reconciliation_required"},
        transition_snapshot={"reconciliation_execution": "not_executed"},
        immutable_evidence_snapshot={"immutable": is_immutable, "append_only": True},
        retry_recovery_snapshot=route_assignment.retry_preparation_snapshot,
        reconciliation_snapshot=route_assignment.dispatch_divergence_snapshot,
        audit_snapshot={"audit_correlation_id": route_assignment.audit_correlation_id},
    )


def test_replay_preparation_success_preserves_immutable_recovery_evidence() -> None:
    route_assignment, visit = replay_ready_route_assignment()
    event = immutable_event_record(route_assignment, visit)

    result = OperationalReplayPreparationService(
        now=lambda: datetime(2026, 5, 15, 21, 20, tzinfo=UTC),
    ).prepare_replay(
        route_assignment,
        visit=visit,
        operational_events=(event,),
    )

    assert result.succeeded is True
    assert result.state == ReplayRecoveryLifecycleState.REPLAY_PREPARED
    assert route_assignment.replay_recovery_state == "replay_prepared"
    assert route_assignment.replay_preparation_snapshot["replay_execution"] == "not_executed"
    assert route_assignment.replay_eligibility_snapshot["eligible_for_replay"] is True
    assert route_assignment.recovery_coordination_snapshot["manual_recovery_required"] is True
    assert route_assignment.replay_recovery_audit_snapshot["immutable_history_mutated"] is False
    assert event.is_immutable is True


def test_rollback_preparation_records_snapshot_without_executing_rollback() -> None:
    route_assignment, visit = replay_ready_route_assignment()

    result = OperationalReplayPreparationService().prepare_rollback(
        route_assignment,
        visit=visit,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    assert result.succeeded is True
    assert result.state == ReplayRecoveryLifecycleState.ROLLBACK_PREPARED
    assert route_assignment.replay_recovery_state == "rollback_prepared"
    assert route_assignment.rollback_preparation_snapshot["rollback_execution"] == "not_executed"
    assert route_assignment.rollback_preparation_snapshot["rollback_prepared"] is True
    assert route_assignment.replay_preparation_snapshot["replay_execution"] == "not_executed"


def test_missing_recovery_context_blocks_replay_preparation() -> None:
    route_assignment, visit = replay_ready_route_assignment()
    route_assignment.dispatch_reconciliation_state = "consistency_verified"
    route_assignment.dispatch_divergence_snapshot = {}
    route_assignment.dispatch_mismatch_snapshot = {}
    route_assignment.retry_preparation_snapshot = {}

    result = OperationalReplayPreparationService().prepare_replay(
        route_assignment,
        visit=visit,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    assert result.succeeded is False
    assert result.state == ReplayRecoveryLifecycleState.REPLAY_BLOCKED
    assert ReplayRecoveryFailureCode.NO_RECOVERY_CONTEXT in result.failure_codes
    assert route_assignment.replay_recovery_state == "replay_blocked"


def test_invalid_lifecycle_blocks_replay_preparation() -> None:
    route_assignment, visit = replay_ready_route_assignment()
    visit.status = "archived"

    result = OperationalReplayPreparationService().prepare_replay(
        route_assignment,
        visit=visit,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    assert result.succeeded is False
    assert ReplayRecoveryFailureCode.INVALID_LIFECYCLE in result.failure_codes
    assert route_assignment.replay_recovery_state == "replay_blocked"


def test_duplicate_replay_preparation_blocks_second_preparation() -> None:
    route_assignment, visit = replay_ready_route_assignment()
    service = OperationalReplayPreparationService()
    service.prepare_replay(
        route_assignment,
        visit=visit,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    result = service.prepare_replay(
        route_assignment,
        visit=visit,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    assert result.succeeded is False
    assert ReplayRecoveryFailureCode.DUPLICATE_REPLAY_PREPARATION in result.failure_codes
    assert route_assignment.replay_recovery_state == "replay_prepared"


def test_mutable_event_history_blocks_replay_preparation() -> None:
    route_assignment, visit = replay_ready_route_assignment()
    event = immutable_event_record(route_assignment, visit, is_immutable=False)

    result = OperationalReplayPreparationService().prepare_replay(
        route_assignment,
        visit=visit,
        operational_events=(event,),
    )

    assert result.succeeded is False
    assert ReplayRecoveryFailureCode.IMMUTABLE_HISTORY_VIOLATION in result.failure_codes
    assert event.is_immutable is False
    assert route_assignment.replay_recovery_state == "replay_blocked"


def test_water_emergency_blocks_standard_replay_path() -> None:
    route_assignment, visit = replay_ready_route_assignment()
    visit.visit_type = "water_emergency"

    result = OperationalReplayPreparationService().prepare_replay(
        route_assignment,
        visit=visit,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    assert result.succeeded is False
    assert result.failure_codes[0] == ReplayRecoveryFailureCode.WATER_EMERGENCY_VISIT


def test_unauthorized_route_assignment_blocks_replay_preparation() -> None:
    route_assignment, visit = replay_ready_route_assignment()
    route_assignment.dispatch_authorization_snapshot = {"authorized_for_dispatch": False}

    result = OperationalReplayPreparationService().prepare_replay(
        route_assignment,
        visit=visit,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    assert result.succeeded is False
    assert ReplayRecoveryFailureCode.UNAUTHORIZED_ROUTE_ASSIGNMENT in result.failure_codes


def test_replay_recovery_audit_log_preserves_traceability() -> None:
    route_assignment, visit = replay_ready_route_assignment()
    service = OperationalReplayPreparationService(
        now=lambda: datetime(2026, 5, 15, 21, 20, tzinfo=UTC),
    )
    service.prepare_replay(
        route_assignment,
        visit=visit,
        operational_events=(immutable_event_record(route_assignment, visit),),
    )

    audit_log = service.build_replay_recovery_audit_log(route_assignment)

    assert audit_log.action == "operational_replay.replay_prepared"
    assert audit_log.entity_type == "route_assignment"
    assert audit_log.entity_id == route_assignment.id
    assert audit_log.audit_correlation_id == "audit-module-20"
    assert audit_log.details["replay_recovery_state"] == "replay_prepared"
    assert audit_log.details["replay_execution"] == "not_executed"
