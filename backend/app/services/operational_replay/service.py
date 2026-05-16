from collections.abc import Callable, Sequence
from datetime import UTC, datetime

from app.domain.operational_replay import (
    RecoveryCoordinationResult,
    ReplayEligibilityEvidence,
    ReplayPreparationResult,
    ReplayRecoveryBlocker,
    ReplayRecoveryEvidence,
    ReplayRecoveryFailureCode,
    ReplayRecoveryLifecycleState,
    ReplayRecoveryTraceability,
    RollbackPreparationEvidence,
)
from app.models.audit_log import AuditLog
from app.models.operational_event_record import OperationalEventRecord
from app.models.route_assignment import RouteAssignment
from app.models.visit import Visit

DISPATCHED_STATUS = "dispatched"
RECONCILIATION_CONTEXT_STATES = {
    "reconciliation_required",
    "divergence_detected",
    "awaiting_manual_resolution",
}
TERMINAL_REPLAY_STATES = {
    ReplayRecoveryLifecycleState.REPLAY_PREPARED.value,
    ReplayRecoveryLifecycleState.ROLLBACK_PREPARED.value,
    ReplayRecoveryLifecycleState.RECOVERY_REQUIRED.value,
    ReplayRecoveryLifecycleState.AWAITING_MANUAL_RECOVERY.value,
}


class OperationalReplayPreparationService:
    def __init__(self, *, now: Callable[[], datetime] | None = None) -> None:
        self.now = now or (lambda: datetime.now(UTC))

    def prepare_replay(
        self,
        route_assignment: RouteAssignment,
        *,
        visit: Visit,
        operational_events: Sequence[OperationalEventRecord] = (),
    ) -> ReplayPreparationResult:
        return self._prepare(
            route_assignment,
            visit=visit,
            operational_events=operational_events,
            target_state=ReplayRecoveryLifecycleState.REPLAY_PREPARED,
        )

    def prepare_rollback(
        self,
        route_assignment: RouteAssignment,
        *,
        visit: Visit,
        operational_events: Sequence[OperationalEventRecord] = (),
    ) -> ReplayPreparationResult:
        return self._prepare(
            route_assignment,
            visit=visit,
            operational_events=operational_events,
            target_state=ReplayRecoveryLifecycleState.ROLLBACK_PREPARED,
        )

    def _prepare(
        self,
        route_assignment: RouteAssignment,
        *,
        visit: Visit,
        operational_events: Sequence[OperationalEventRecord],
        target_state: ReplayRecoveryLifecycleState,
    ) -> ReplayPreparationResult:
        timestamp = self.now()
        traceability = replay_recovery_traceability(route_assignment, visit)
        eligibility = replay_eligibility(route_assignment, operational_events)
        rollback = rollback_preparation_evidence(
            route_assignment,
            operational_events,
            prepared=target_state == ReplayRecoveryLifecycleState.ROLLBACK_PREPARED,
        )
        recovery = recovery_coordination_result(route_assignment, operational_events)
        blockers = replay_recovery_blockers(route_assignment, visit, operational_events)
        if any(
            blocker.code == ReplayRecoveryFailureCode.DUPLICATE_REPLAY_PREPARATION
            for blocker in blockers
        ):
            return failed_replay_result(
                route_assignment,
                state=ReplayRecoveryLifecycleState.REPLAY_BLOCKED,
                traceability=traceability,
                eligibility=eligibility,
                rollback=rollback,
                recovery=recovery,
                blockers=blockers,
            )
        if blockers:
            apply_replay_blocked(
                route_assignment,
                eligibility,
                rollback,
                recovery,
                blockers,
                timestamp,
            )
            return failed_replay_result(
                route_assignment,
                state=ReplayRecoveryLifecycleState.REPLAY_BLOCKED,
                traceability=traceability,
                eligibility=eligibility,
                rollback=rollback,
                recovery=recovery,
                blockers=blockers,
            )

        apply_replay_prepared(
            route_assignment,
            eligibility,
            rollback,
            recovery,
            operational_events,
            target_state,
            timestamp,
        )
        return ReplayPreparationResult(
            succeeded=True,
            state=target_state,
            traceability=traceability,
            replay_eligibility=eligibility,
            rollback_preparation=rollback_preparation_evidence(
                route_assignment,
                operational_events,
                prepared=target_state == ReplayRecoveryLifecycleState.ROLLBACK_PREPARED,
            ),
            recovery_coordination=recovery,
            evidence=replay_recovery_evidence(route_assignment),
        )

    @staticmethod
    def build_replay_recovery_audit_log(route_assignment: RouteAssignment) -> AuditLog:
        audit_snapshot = route_assignment.replay_recovery_audit_snapshot or {}
        return AuditLog(
            action=audit_snapshot.get("action") or "operational_replay.recorded",
            entity_type="route_assignment",
            entity_id=route_assignment.id,
            audit_correlation_id=route_assignment.audit_correlation_id,
            details={
                "route_assignment_id": str(route_assignment.id),
                "visit_id": str(route_assignment.visit_id) if route_assignment.visit_id else None,
                "job_id": str(route_assignment.job_id) if route_assignment.job_id else None,
                "technician_id": str(route_assignment.technician_id)
                if route_assignment.technician_id
                else None,
                "replay_recovery_state": route_assignment.replay_recovery_state,
                "replay_execution": audit_snapshot.get("replay_execution"),
                "rollback_execution": audit_snapshot.get("rollback_execution"),
                "external_api_calls": audit_snapshot.get("external_api_calls"),
            },
        )


def replay_recovery_blockers(
    route_assignment: RouteAssignment,
    visit: Visit,
    operational_events: Sequence[OperationalEventRecord],
) -> tuple[ReplayRecoveryBlocker, ...]:
    blockers: list[ReplayRecoveryBlocker] = []
    if route_assignment.id is None or route_assignment.visit_id != visit.id:
        blockers.append(
            ReplayRecoveryBlocker(
                code=ReplayRecoveryFailureCode.MISSING_ROUTE_ASSIGNMENT_LINKAGE,
                message="Route assignment must be linked to the Visit being prepared.",
            ),
        )
    if not (route_assignment.audit_correlation_id or visit.audit_correlation_id):
        blockers.append(
            ReplayRecoveryBlocker(
                code=ReplayRecoveryFailureCode.MISSING_AUDIT_CORRELATION,
                message="Replay and recovery preparation requires audit correlation continuity.",
            ),
        )
    if visit.visit_type == "water_emergency":
        blockers.append(
            ReplayRecoveryBlocker(
                code=ReplayRecoveryFailureCode.WATER_EMERGENCY_VISIT,
                message="Water Emergency Visits require a separated replay/recovery path.",
            ),
        )
    if visit.status == "review_required":
        blockers.append(
            ReplayRecoveryBlocker(
                code=ReplayRecoveryFailureCode.REVIEW_REQUIRED,
                message="Manual Review remains authoritative before replay or recovery.",
            ),
        )
    if visit.status != DISPATCHED_STATUS or route_assignment.dispatch_execution_state != (
        DISPATCHED_STATUS
    ):
        blockers.append(
            ReplayRecoveryBlocker(
                code=ReplayRecoveryFailureCode.INVALID_LIFECYCLE,
                message="Replay preparation requires a dispatched internal lifecycle.",
                metadata={
                    "visit_status": visit.status,
                    "dispatch_execution_state": route_assignment.dispatch_execution_state,
                },
            ),
        )
    if not route_assignment_authorized(route_assignment):
        blockers.append(
            ReplayRecoveryBlocker(
                code=ReplayRecoveryFailureCode.UNAUTHORIZED_ROUTE_ASSIGNMENT,
                message="Only authorized Route Assignments can prepare replay or recovery.",
            ),
        )
    if route_assignment.replay_recovery_state in TERMINAL_REPLAY_STATES:
        blockers.append(
            ReplayRecoveryBlocker(
                code=ReplayRecoveryFailureCode.DUPLICATE_REPLAY_PREPARATION,
                message="Replay or recovery has already been prepared for this Route Assignment.",
                metadata={"replay_recovery_state": route_assignment.replay_recovery_state},
            ),
        )
    mutable_events = [
        str(event.id)
        for event in operational_events
        if not event.is_immutable or event.immutable_evidence_snapshot is None
    ]
    if mutable_events:
        blockers.append(
            ReplayRecoveryBlocker(
                code=ReplayRecoveryFailureCode.IMMUTABLE_HISTORY_VIOLATION,
                message="Operational event history must remain immutable during replay.",
                metadata={"mutable_event_ids": mutable_events},
            ),
        )
    if not has_recovery_context(route_assignment):
        blockers.append(
            ReplayRecoveryBlocker(
                code=ReplayRecoveryFailureCode.NO_RECOVERY_CONTEXT,
                message="Replay preparation requires reconciliation, retry, or failure context.",
            ),
        )
    return tuple(dedupe_blockers(blockers))


def apply_replay_prepared(
    route_assignment: RouteAssignment,
    eligibility: ReplayEligibilityEvidence,
    rollback: RollbackPreparationEvidence,
    recovery: RecoveryCoordinationResult,
    operational_events: Sequence[OperationalEventRecord],
    target_state: ReplayRecoveryLifecycleState,
    timestamp: datetime,
) -> None:
    route_assignment.replay_recovery_state = target_state.value
    route_assignment.replay_eligibility_snapshot = eligibility.evidence
    route_assignment.replay_preparation_snapshot = replay_preparation_snapshot(
        route_assignment,
        operational_events,
        target_state,
        timestamp,
    )
    route_assignment.rollback_preparation_snapshot = rollback.evidence
    route_assignment.replay_blocker_snapshot = {}
    route_assignment.recovery_coordination_snapshot = recovery.evidence
    route_assignment.replay_recovery_audit_snapshot = replay_recovery_audit_snapshot(
        route_assignment,
        target_state,
    )
    if target_state == ReplayRecoveryLifecycleState.ROLLBACK_PREPARED:
        route_assignment.rollback_prepared_at = timestamp
    else:
        route_assignment.replay_prepared_at = timestamp


def apply_replay_blocked(
    route_assignment: RouteAssignment,
    eligibility: ReplayEligibilityEvidence,
    rollback: RollbackPreparationEvidence,
    recovery: RecoveryCoordinationResult,
    blockers: tuple[ReplayRecoveryBlocker, ...],
    timestamp: datetime,
) -> None:
    state = ReplayRecoveryLifecycleState.REPLAY_BLOCKED
    route_assignment.replay_recovery_state = state.value
    route_assignment.replay_eligibility_snapshot = eligibility.evidence
    route_assignment.replay_preparation_snapshot = {
        "state": state.value,
        "replay_prepared": False,
        "replay_execution": "not_executed",
        "automatic_replay_execution": "not_executed",
        "external_api_calls": "not_executed",
        "immutable_history_mutated": False,
    }
    route_assignment.rollback_preparation_snapshot = rollback.evidence
    route_assignment.recovery_coordination_snapshot = recovery.evidence
    route_assignment.replay_blocker_snapshot = blocker_snapshot(blockers, timestamp)
    route_assignment.replay_recovery_audit_snapshot = replay_recovery_audit_snapshot(
        route_assignment,
        state,
    )
    route_assignment.replay_blocked_at = timestamp


def failed_replay_result(
    route_assignment: RouteAssignment,
    *,
    state: ReplayRecoveryLifecycleState,
    traceability: ReplayRecoveryTraceability,
    eligibility: ReplayEligibilityEvidence,
    rollback: RollbackPreparationEvidence,
    recovery: RecoveryCoordinationResult,
    blockers: tuple[ReplayRecoveryBlocker, ...],
) -> ReplayPreparationResult:
    return ReplayPreparationResult(
        succeeded=False,
        state=state,
        traceability=traceability,
        replay_eligibility=eligibility,
        rollback_preparation=rollback,
        recovery_coordination=recovery,
        failure_reasons=blockers,
        evidence=ReplayRecoveryEvidence(
            replay=route_assignment.replay_preparation_snapshot or {},
            rollback=route_assignment.rollback_preparation_snapshot or rollback.evidence,
            eligibility=route_assignment.replay_eligibility_snapshot or eligibility.evidence,
            blockers=route_assignment.replay_blocker_snapshot or {},
            recovery_coordination=route_assignment.recovery_coordination_snapshot
            or recovery.evidence,
            audit=route_assignment.replay_recovery_audit_snapshot
            or replay_recovery_audit_snapshot(route_assignment, state),
            failure_reasons=blockers,
        ),
    )


def replay_eligibility(
    route_assignment: RouteAssignment,
    operational_events: Sequence[OperationalEventRecord],
) -> ReplayEligibilityEvidence:
    has_reconciliation = has_reconciliation_context(route_assignment)
    has_retry = bool(route_assignment.retry_preparation_snapshot)
    has_failure = bool(
        route_assignment.external_execution_failure_snapshot
        or route_assignment.external_failure_snapshot
    )
    evidence = {
        "eligible_for_replay": has_reconciliation or has_retry or has_failure,
        "has_reconciliation_context": has_reconciliation,
        "has_retry_context": has_retry,
        "has_failure_context": has_failure,
        "dispatch_reconciliation_state": route_assignment.dispatch_reconciliation_state,
        "external_execution_state": route_assignment.external_execution_state,
        "external_confirmation_state": route_assignment.external_confirmation_state,
        "event_history_count": len(operational_events),
        "immutable_history_valid": all(
            event.is_immutable and event.immutable_evidence_snapshot is not None
            for event in operational_events
        ),
        "replay_execution": "not_executed",
        "rollback_execution": "not_executed",
        "external_api_calls": "not_executed",
        "ai_authority": "none",
    }
    return ReplayEligibilityEvidence(
        eligible_for_replay=bool(evidence["eligible_for_replay"]),
        has_reconciliation_context=has_reconciliation,
        has_retry_context=has_retry,
        has_failure_context=has_failure,
        immutable_event_count=len(operational_events),
        evidence=evidence,
    )


def rollback_preparation_evidence(
    route_assignment: RouteAssignment,
    operational_events: Sequence[OperationalEventRecord],
    *,
    prepared: bool,
) -> RollbackPreparationEvidence:
    evidence = {
        "rollback_prepared": prepared,
        "rollback_execution": "not_executed",
        "automatic_rollback_execution": "not_executed",
        "rollback_requires_manual_authorization": True,
        "source_reconciliation_state": route_assignment.dispatch_reconciliation_state,
        "event_history_count": len(operational_events),
        "immutable_history_mutated": False,
    }
    return RollbackPreparationEvidence(
        rollback_prepared=prepared,
        rollback_execution="not_executed",
        evidence=evidence,
    )


def recovery_coordination_result(
    route_assignment: RouteAssignment,
    operational_events: Sequence[OperationalEventRecord],
) -> RecoveryCoordinationResult:
    manual_recovery_required = bool(
        route_assignment.dispatch_divergence_snapshot
        or route_assignment.dispatch_mismatch_snapshot
        or route_assignment.retry_preparation_snapshot
    )
    evidence = {
        "recovery_required": has_recovery_context(route_assignment),
        "manual_recovery_required": manual_recovery_required,
        "coordination_state": ReplayRecoveryLifecycleState.RECOVERY_REQUIRED.value,
        "next_manual_state": ReplayRecoveryLifecycleState.AWAITING_MANUAL_RECOVERY.value,
        "replay_execution": "not_executed",
        "rollback_execution": "not_executed",
        "retry_execution": "not_executed",
        "reconciliation_replay_execution": "not_executed",
        "external_api_calls": "not_executed",
        "immutable_history_mutated": False,
        "event_history_count": len(operational_events),
        "audit_correlation_id": route_assignment.audit_correlation_id,
    }
    return RecoveryCoordinationResult(
        recovery_required=bool(evidence["recovery_required"]),
        manual_recovery_required=manual_recovery_required,
        recovery_state=ReplayRecoveryLifecycleState.RECOVERY_REQUIRED,
        evidence=evidence,
    )


def replay_preparation_snapshot(
    route_assignment: RouteAssignment,
    operational_events: Sequence[OperationalEventRecord],
    state: ReplayRecoveryLifecycleState,
    timestamp: datetime,
) -> dict[str, object]:
    return {
        "state": state.value,
        "replay_prepared": state == ReplayRecoveryLifecycleState.REPLAY_PREPARED,
        "replay_execution": "not_executed",
        "automatic_replay_execution": "not_executed",
        "external_api_calls": "not_executed",
        "retry_execution": "not_executed",
        "reconciliation_replay_execution": "not_executed",
        "immutable_history_mutated": False,
        "event_history_count": len(operational_events),
        "source_reconciliation_state": route_assignment.dispatch_reconciliation_state,
        "prepared_at": timestamp.isoformat(),
    }


def blocker_snapshot(
    blockers: tuple[ReplayRecoveryBlocker, ...],
    timestamp: datetime,
) -> dict[str, object]:
    return {
        "state": ReplayRecoveryLifecycleState.REPLAY_BLOCKED.value,
        "blocked_at": timestamp.isoformat(),
        "replay_execution": "not_executed",
        "rollback_execution": "not_executed",
        "external_api_calls": "not_executed",
        "immutable_history_mutated": False,
        "blockers": [
            {
                "code": blocker.code.value,
                "message": blocker.message,
                "metadata": blocker.metadata or {},
            }
            for blocker in blockers
        ],
    }


def replay_recovery_audit_snapshot(
    route_assignment: RouteAssignment,
    state: ReplayRecoveryLifecycleState,
) -> dict[str, object]:
    action_by_state = {
        ReplayRecoveryLifecycleState.REPLAY_PREPARED: "operational_replay.replay_prepared",
        ReplayRecoveryLifecycleState.ROLLBACK_PREPARED: "operational_replay.rollback_prepared",
        ReplayRecoveryLifecycleState.REPLAY_BLOCKED: "operational_replay.blocked",
    }
    return {
        "action": action_by_state.get(state, "operational_replay.recorded"),
        "state": state.value,
        "route_assignment_id": str(route_assignment.id) if route_assignment.id else None,
        "visit_id": str(route_assignment.visit_id) if route_assignment.visit_id else None,
        "job_id": str(route_assignment.job_id) if route_assignment.job_id else None,
        "audit_correlation_id": route_assignment.audit_correlation_id,
        "replay_execution": "not_executed",
        "rollback_execution": "not_executed",
        "external_api_calls": "not_executed",
        "immutable_history_mutated": False,
        "ai_authority": "none",
    }


def replay_recovery_evidence(route_assignment: RouteAssignment) -> ReplayRecoveryEvidence:
    return ReplayRecoveryEvidence(
        replay=route_assignment.replay_preparation_snapshot or {},
        rollback=route_assignment.rollback_preparation_snapshot or {},
        eligibility=route_assignment.replay_eligibility_snapshot or {},
        blockers=route_assignment.replay_blocker_snapshot or {},
        recovery_coordination=route_assignment.recovery_coordination_snapshot or {},
        audit=route_assignment.replay_recovery_audit_snapshot or {},
    )


def replay_recovery_traceability(
    route_assignment: RouteAssignment,
    visit: Visit,
) -> ReplayRecoveryTraceability:
    return ReplayRecoveryTraceability(
        route_assignment_id=route_assignment.id,
        visit_id=visit.id,
        work_order_id=visit.work_order_id,
        job_id=route_assignment.job_id or visit.job_id,
        technician_id=route_assignment.technician_id or visit.technician_id,
        audit_correlation_id=route_assignment.audit_correlation_id or visit.audit_correlation_id,
    )


def has_reconciliation_context(route_assignment: RouteAssignment) -> bool:
    return bool(
        route_assignment.dispatch_reconciliation_state in RECONCILIATION_CONTEXT_STATES
        or route_assignment.dispatch_divergence_snapshot
        or route_assignment.dispatch_mismatch_snapshot
    )


def has_recovery_context(route_assignment: RouteAssignment) -> bool:
    return bool(
        has_reconciliation_context(route_assignment)
        or route_assignment.retry_preparation_snapshot
        or route_assignment.external_execution_failure_snapshot
        or route_assignment.external_failure_snapshot
    )


def route_assignment_authorized(route_assignment: RouteAssignment) -> bool:
    authorization_snapshot = route_assignment.dispatch_authorization_snapshot or {}
    execution_boundary_snapshot = route_assignment.dispatch_execution_boundary_snapshot or {}
    return bool(
        authorization_snapshot.get("authorized_for_dispatch")
        and execution_boundary_snapshot.get("authorized_for_dispatch")
    )


def dedupe_blockers(
    blockers: list[ReplayRecoveryBlocker],
) -> tuple[ReplayRecoveryBlocker, ...]:
    deduped: list[ReplayRecoveryBlocker] = []
    seen: set[ReplayRecoveryFailureCode] = set()
    for blocker in blockers:
        if blocker.code in seen:
            continue
        deduped.append(blocker)
        seen.add(blocker.code)
    return tuple(deduped)
