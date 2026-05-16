from collections.abc import Callable, Sequence
from datetime import UTC, datetime

from app.domain.operational_governance import (
    GovernanceApprovalResult,
    GovernanceAuditEvidence,
    GovernanceBlocker,
    GovernanceEvidence,
    GovernanceFailureCode,
    GovernanceLifecycleState,
    GovernanceOperation,
    GovernanceTraceability,
    InterventionAuthorizationResult,
    ReconciliationApprovalEvidence,
    ReplayAuthorizationEvidence,
    RollbackAuthorizationEvidence,
)
from app.models.audit_log import AuditLog
from app.models.operational_event_record import OperationalEventRecord
from app.models.route_assignment import RouteAssignment
from app.models.visit import Visit

DISPATCHED_STATUS = "dispatched"
APPROVAL_ROLES = {"admin", "operations_manager", "dispatcher_supervisor"}
INTERVENTION_ROLES = {"admin", "operations_manager"}
TERMINAL_GOVERNANCE_STATES = {
    GovernanceLifecycleState.OPERATOR_APPROVED.value,
    GovernanceLifecycleState.OPERATOR_REJECTED.value,
}


class OperationalGovernanceService:
    def __init__(self, *, now: Callable[[], datetime] | None = None) -> None:
        self.now = now or (lambda: datetime.now(UTC))

    def approve_operation(
        self,
        route_assignment: RouteAssignment,
        *,
        visit: Visit,
        operator_id: str | None,
        operator_role: str | None,
        operation: GovernanceOperation,
        operational_events: Sequence[OperationalEventRecord] = (),
    ) -> GovernanceApprovalResult:
        return self._evaluate_governance(
            route_assignment,
            visit=visit,
            operator_id=operator_id,
            operator_role=operator_role,
            operation=operation,
            operational_events=operational_events,
            intervention_reason=None,
            target_state=GovernanceLifecycleState.OPERATOR_APPROVED,
        )

    def authorize_intervention(
        self,
        route_assignment: RouteAssignment,
        *,
        visit: Visit,
        operator_id: str | None,
        operator_role: str | None,
        intervention_reason: str,
        operational_events: Sequence[OperationalEventRecord] = (),
    ) -> GovernanceApprovalResult:
        return self._evaluate_governance(
            route_assignment,
            visit=visit,
            operator_id=operator_id,
            operator_role=operator_role,
            operation=GovernanceOperation.MANUAL_INTERVENTION,
            operational_events=operational_events,
            intervention_reason=intervention_reason,
            target_state=GovernanceLifecycleState.INTERVENTION_REQUIRED,
        )

    def _evaluate_governance(
        self,
        route_assignment: RouteAssignment,
        *,
        visit: Visit,
        operator_id: str | None,
        operator_role: str | None,
        operation: GovernanceOperation,
        operational_events: Sequence[OperationalEventRecord],
        intervention_reason: str | None,
        target_state: GovernanceLifecycleState,
    ) -> GovernanceApprovalResult:
        timestamp = self.now()
        traceability = governance_traceability(route_assignment, visit, operator_id)
        replay = replay_authorization_evidence(route_assignment, operation)
        rollback = rollback_authorization_evidence(route_assignment, operation)
        reconciliation = reconciliation_approval_evidence(route_assignment, operation)
        intervention = intervention_authorization_result(
            route_assignment,
            operation=operation,
            intervention_reason=intervention_reason,
            authorized=operator_role in INTERVENTION_ROLES,
        )
        audit = governance_audit_evidence(
            route_assignment,
            state=target_state,
            operation=operation,
            operator_id=operator_id,
            operator_role=operator_role,
        )
        blockers = governance_blockers(
            route_assignment,
            visit,
            operator_id=operator_id,
            operator_role=operator_role,
            operation=operation,
            operational_events=operational_events,
            target_state=target_state,
        )
        if any(blocker.code == GovernanceFailureCode.DUPLICATE_APPROVAL for blocker in blockers):
            return failed_governance_result(
                route_assignment,
                state=GovernanceLifecycleState.GOVERNANCE_BLOCKED,
                operation=operation,
                traceability=traceability,
                replay=replay,
                rollback=rollback,
                reconciliation=reconciliation,
                intervention=intervention,
                audit=audit,
                blockers=blockers,
            )
        if blockers:
            apply_governance_blocked(
                route_assignment,
                operation,
                replay,
                rollback,
                reconciliation,
                intervention,
                audit,
                blockers,
                timestamp,
            )
            return failed_governance_result(
                route_assignment,
                state=GovernanceLifecycleState.GOVERNANCE_BLOCKED,
                operation=operation,
                traceability=traceability,
                replay=replay,
                rollback=rollback,
                reconciliation=reconciliation,
                intervention=intervention,
                audit=audit,
                blockers=blockers,
            )

        apply_governance_approved(
            route_assignment,
            operation,
            replay,
            rollback,
            reconciliation,
            intervention,
            audit,
            target_state,
            timestamp,
        )
        return GovernanceApprovalResult(
            succeeded=True,
            state=target_state,
            operation=operation,
            traceability=traceability,
            replay_authorization=replay,
            rollback_authorization=rollback,
            reconciliation_approval=reconciliation,
            intervention_authorization=intervention,
            audit=audit,
            evidence=governance_evidence(route_assignment),
        )

    @staticmethod
    def build_governance_audit_log(route_assignment: RouteAssignment) -> AuditLog:
        audit_snapshot = route_assignment.governance_audit_snapshot or {}
        return AuditLog(
            action=audit_snapshot.get("action") or "operational_governance.recorded",
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
                "governance_state": route_assignment.governance_state,
                "operator_id": audit_snapshot.get("operator_id"),
                "operation": audit_snapshot.get("operation"),
                "external_api_calls": audit_snapshot.get("external_api_calls"),
            },
        )


def governance_blockers(
    route_assignment: RouteAssignment,
    visit: Visit,
    *,
    operator_id: str | None,
    operator_role: str | None,
    operation: GovernanceOperation,
    operational_events: Sequence[OperationalEventRecord],
    target_state: GovernanceLifecycleState,
) -> tuple[GovernanceBlocker, ...]:
    blockers: list[GovernanceBlocker] = []
    if route_assignment.id is None or route_assignment.visit_id != visit.id:
        blockers.append(
            GovernanceBlocker(
                code=GovernanceFailureCode.MISSING_ROUTE_ASSIGNMENT_LINKAGE,
                message="Route assignment must be linked to the Visit under governance.",
            ),
        )
    if not (route_assignment.audit_correlation_id or visit.audit_correlation_id):
        blockers.append(
            GovernanceBlocker(
                code=GovernanceFailureCode.MISSING_AUDIT_CORRELATION,
                message="Operational governance requires audit correlation continuity.",
            ),
        )
    if not operator_id:
        blockers.append(
            GovernanceBlocker(
                code=GovernanceFailureCode.MISSING_OPERATOR_ID,
                message="Operational governance requires an explicit operator identity.",
            ),
        )
    if visit.visit_type == "water_emergency":
        blockers.append(
            GovernanceBlocker(
                code=GovernanceFailureCode.WATER_EMERGENCY_VISIT,
                message="Water Emergency work requires a separated governance path.",
            ),
        )
    if visit.status == "review_required":
        blockers.append(
            GovernanceBlocker(
                code=GovernanceFailureCode.REVIEW_REQUIRED,
                message="Manual Review remains authoritative before governance approval.",
            ),
        )
    if visit.status != DISPATCHED_STATUS or route_assignment.dispatch_execution_state != (
        DISPATCHED_STATUS
    ):
        blockers.append(
            GovernanceBlocker(
                code=GovernanceFailureCode.INVALID_LIFECYCLE,
                message="Governance approval requires a dispatched operational lifecycle.",
                metadata={
                    "visit_status": visit.status,
                    "dispatch_execution_state": route_assignment.dispatch_execution_state,
                },
            ),
        )
    if target_state == GovernanceLifecycleState.INTERVENTION_REQUIRED:
        if operator_role not in INTERVENTION_ROLES:
            blockers.append(unauthorized_operator_blocker(operator_role, operation))
    elif operator_role not in APPROVAL_ROLES:
        blockers.append(unauthorized_operator_blocker(operator_role, operation))
    if route_assignment.governance_state in TERMINAL_GOVERNANCE_STATES:
        blockers.append(
            GovernanceBlocker(
                code=GovernanceFailureCode.DUPLICATE_APPROVAL,
                message="Governance approval has already been recorded.",
                metadata={"governance_state": route_assignment.governance_state},
            ),
        )
    mutable_events = [
        str(event.id)
        for event in operational_events
        if not event.is_immutable or event.immutable_evidence_snapshot is None
    ]
    if mutable_events:
        blockers.append(
            GovernanceBlocker(
                code=GovernanceFailureCode.IMMUTABLE_HISTORY_VIOLATION,
                message="Operational event history must remain immutable during governance.",
                metadata={"mutable_event_ids": mutable_events},
            ),
        )
    blockers.extend(operation_specific_blockers(route_assignment, operation))
    return tuple(dedupe_blockers(blockers))


def operation_specific_blockers(
    route_assignment: RouteAssignment,
    operation: GovernanceOperation,
) -> list[GovernanceBlocker]:
    blockers: list[GovernanceBlocker] = []
    if operation == GovernanceOperation.REPLAY and not replay_prepared(route_assignment):
        blockers.append(
            GovernanceBlocker(
                code=GovernanceFailureCode.REPLAY_NOT_PREPARED,
                message="Replay must be prepared before governance can authorize it.",
                metadata={"replay_recovery_state": route_assignment.replay_recovery_state},
            ),
        )
    if operation == GovernanceOperation.ROLLBACK and not rollback_prepared(route_assignment):
        blockers.append(
            GovernanceBlocker(
                code=GovernanceFailureCode.ROLLBACK_NOT_PREPARED,
                message="Rollback must be prepared before governance can authorize it.",
                metadata={"replay_recovery_state": route_assignment.replay_recovery_state},
            ),
        )
    if operation == GovernanceOperation.RECONCILIATION and not reconciliation_prepared(
        route_assignment
    ):
        blockers.append(
            GovernanceBlocker(
                code=GovernanceFailureCode.RECONCILIATION_NOT_PREPARED,
                message="Reconciliation must be prepared before governance can approve it.",
                metadata={
                    "dispatch_reconciliation_state": (
                        route_assignment.dispatch_reconciliation_state
                    ),
                },
            ),
        )
    return blockers


def apply_governance_approved(
    route_assignment: RouteAssignment,
    operation: GovernanceOperation,
    replay: ReplayAuthorizationEvidence,
    rollback: RollbackAuthorizationEvidence,
    reconciliation: ReconciliationApprovalEvidence,
    intervention: InterventionAuthorizationResult,
    audit: GovernanceAuditEvidence,
    state: GovernanceLifecycleState,
    timestamp: datetime,
) -> None:
    route_assignment.governance_state = state.value
    route_assignment.governance_approval_snapshot = governance_approval_snapshot(
        operation,
        state,
        approved=state == GovernanceLifecycleState.OPERATOR_APPROVED,
        timestamp=timestamp,
    )
    route_assignment.intervention_authorization_snapshot = intervention.evidence
    route_assignment.replay_authorization_snapshot = replay.evidence
    route_assignment.rollback_authorization_snapshot = rollback.evidence
    route_assignment.reconciliation_approval_snapshot = reconciliation.evidence
    route_assignment.governance_blocker_snapshot = {}
    route_assignment.governance_audit_snapshot = audit.evidence
    if state == GovernanceLifecycleState.INTERVENTION_REQUIRED:
        route_assignment.intervention_required_at = timestamp
    else:
        route_assignment.governance_approved_at = timestamp


def apply_governance_blocked(
    route_assignment: RouteAssignment,
    operation: GovernanceOperation,
    replay: ReplayAuthorizationEvidence,
    rollback: RollbackAuthorizationEvidence,
    reconciliation: ReconciliationApprovalEvidence,
    intervention: InterventionAuthorizationResult,
    audit: GovernanceAuditEvidence,
    blockers: tuple[GovernanceBlocker, ...],
    timestamp: datetime,
) -> None:
    state = GovernanceLifecycleState.GOVERNANCE_BLOCKED
    route_assignment.governance_state = state.value
    route_assignment.governance_approval_snapshot = governance_approval_snapshot(
        operation,
        state,
        approved=False,
        timestamp=timestamp,
    )
    route_assignment.intervention_authorization_snapshot = intervention.evidence
    route_assignment.replay_authorization_snapshot = replay.evidence
    route_assignment.rollback_authorization_snapshot = rollback.evidence
    route_assignment.reconciliation_approval_snapshot = reconciliation.evidence
    route_assignment.governance_blocker_snapshot = blocker_snapshot(blockers, timestamp)
    route_assignment.governance_audit_snapshot = audit.evidence | {
        "state": state.value,
        "action": "operational_governance.blocked",
    }
    route_assignment.governance_blocked_at = timestamp


def failed_governance_result(
    route_assignment: RouteAssignment,
    *,
    state: GovernanceLifecycleState,
    operation: GovernanceOperation,
    traceability: GovernanceTraceability,
    replay: ReplayAuthorizationEvidence,
    rollback: RollbackAuthorizationEvidence,
    reconciliation: ReconciliationApprovalEvidence,
    intervention: InterventionAuthorizationResult,
    audit: GovernanceAuditEvidence,
    blockers: tuple[GovernanceBlocker, ...],
) -> GovernanceApprovalResult:
    return GovernanceApprovalResult(
        succeeded=False,
        state=state,
        operation=operation,
        traceability=traceability,
        replay_authorization=replay,
        rollback_authorization=rollback,
        reconciliation_approval=reconciliation,
        intervention_authorization=intervention,
        audit=audit,
        failure_reasons=blockers,
        evidence=GovernanceEvidence(
            approval=route_assignment.governance_approval_snapshot or {},
            intervention=route_assignment.intervention_authorization_snapshot
            or intervention.evidence,
            replay_authorization=route_assignment.replay_authorization_snapshot or replay.evidence,
            rollback_authorization=route_assignment.rollback_authorization_snapshot
            or rollback.evidence,
            reconciliation_approval=route_assignment.reconciliation_approval_snapshot
            or reconciliation.evidence,
            blockers=route_assignment.governance_blocker_snapshot or {},
            audit=route_assignment.governance_audit_snapshot or audit.evidence,
            failure_reasons=blockers,
        ),
    )


def replay_authorization_evidence(
    route_assignment: RouteAssignment,
    operation: GovernanceOperation,
) -> ReplayAuthorizationEvidence:
    authorized = operation == GovernanceOperation.REPLAY and replay_prepared(route_assignment)
    evidence = {
        "operation": operation.value,
        "authorized_for_replay": authorized,
        "replay_prepared": replay_prepared(route_assignment),
        "replay_recovery_state": route_assignment.replay_recovery_state,
        "replay_execution": "not_executed",
        "automatic_approval": "not_executed",
        "external_api_calls": "not_executed",
        "ai_authority": "none",
    }
    return ReplayAuthorizationEvidence(
        authorized_for_replay=authorized,
        replay_execution="not_executed",
        evidence=evidence,
    )


def rollback_authorization_evidence(
    route_assignment: RouteAssignment,
    operation: GovernanceOperation,
) -> RollbackAuthorizationEvidence:
    authorized = operation == GovernanceOperation.ROLLBACK and rollback_prepared(
        route_assignment,
    )
    evidence = {
        "operation": operation.value,
        "authorized_for_rollback": authorized,
        "rollback_prepared": rollback_prepared(route_assignment),
        "replay_recovery_state": route_assignment.replay_recovery_state,
        "rollback_execution": "not_executed",
        "automatic_rollback_execution": "not_executed",
        "external_api_calls": "not_executed",
        "ai_authority": "none",
    }
    return RollbackAuthorizationEvidence(
        authorized_for_rollback=authorized,
        rollback_execution="not_executed",
        evidence=evidence,
    )


def reconciliation_approval_evidence(
    route_assignment: RouteAssignment,
    operation: GovernanceOperation,
) -> ReconciliationApprovalEvidence:
    approved = operation == GovernanceOperation.RECONCILIATION and reconciliation_prepared(
        route_assignment,
    )
    evidence = {
        "operation": operation.value,
        "approved_for_reconciliation": approved,
        "reconciliation_prepared": reconciliation_prepared(route_assignment),
        "dispatch_reconciliation_state": route_assignment.dispatch_reconciliation_state,
        "reconciliation_execution": "not_executed",
        "manual_review_bypassed": False,
        "external_api_calls": "not_executed",
        "ai_authority": "none",
    }
    return ReconciliationApprovalEvidence(
        approved_for_reconciliation=approved,
        reconciliation_execution="not_executed",
        evidence=evidence,
    )


def intervention_authorization_result(
    route_assignment: RouteAssignment,
    *,
    operation: GovernanceOperation,
    intervention_reason: str | None,
    authorized: bool,
) -> InterventionAuthorizationResult:
    evidence = {
        "operation": operation.value,
        "intervention_required": operation == GovernanceOperation.MANUAL_INTERVENTION,
        "authorized_for_intervention": (
            operation == GovernanceOperation.MANUAL_INTERVENTION and authorized
        ),
        "intervention_reason": intervention_reason,
        "source_replay_recovery_state": route_assignment.replay_recovery_state,
        "source_reconciliation_state": route_assignment.dispatch_reconciliation_state,
        "intervention_execution": "not_executed",
        "workflow_engine": "not_executed",
        "external_api_calls": "not_executed",
        "ai_authority": "none",
    }
    return InterventionAuthorizationResult(
        intervention_required=bool(evidence["intervention_required"]),
        authorized_for_intervention=bool(evidence["authorized_for_intervention"]),
        intervention_execution="not_executed",
        evidence=evidence,
    )


def governance_audit_evidence(
    route_assignment: RouteAssignment,
    *,
    state: GovernanceLifecycleState,
    operation: GovernanceOperation,
    operator_id: str | None,
    operator_role: str | None,
) -> GovernanceAuditEvidence:
    action_by_state = {
        GovernanceLifecycleState.OPERATOR_APPROVED: "operational_governance.operator_approved",
        GovernanceLifecycleState.INTERVENTION_REQUIRED: (
            "operational_governance.intervention_required"
        ),
        GovernanceLifecycleState.GOVERNANCE_BLOCKED: "operational_governance.blocked",
    }
    action = action_by_state.get(state, "operational_governance.recorded")
    evidence = {
        "action": action,
        "state": state.value,
        "operation": operation.value,
        "route_assignment_id": str(route_assignment.id) if route_assignment.id else None,
        "visit_id": str(route_assignment.visit_id) if route_assignment.visit_id else None,
        "job_id": str(route_assignment.job_id) if route_assignment.job_id else None,
        "audit_correlation_id": route_assignment.audit_correlation_id,
        "operator_id": operator_id,
        "operator_role": operator_role,
        "replay_execution": "not_executed",
        "rollback_execution": "not_executed",
        "reconciliation_execution": "not_executed",
        "intervention_execution": "not_executed",
        "external_api_calls": "not_executed",
        "immutable_history_mutated": False,
        "ai_authority": "none",
    }
    return GovernanceAuditEvidence(
        action=action,
        operator_id=operator_id,
        operator_role=operator_role,
        evidence=evidence,
    )


def governance_approval_snapshot(
    operation: GovernanceOperation,
    state: GovernanceLifecycleState,
    *,
    approved: bool,
    timestamp: datetime,
) -> dict[str, object]:
    return {
        "operation": operation.value,
        "state": state.value,
        "approved": approved,
        "approval_recorded_at": timestamp.isoformat(),
        "automatic_approval": "not_executed",
        "hidden_lifecycle_transition": False,
        "manual_review_bypassed": False,
        "replay_execution": "not_executed",
        "rollback_execution": "not_executed",
        "reconciliation_execution": "not_executed",
        "external_api_calls": "not_executed",
    }


def blocker_snapshot(
    blockers: tuple[GovernanceBlocker, ...],
    timestamp: datetime,
) -> dict[str, object]:
    return {
        "state": GovernanceLifecycleState.GOVERNANCE_BLOCKED.value,
        "blocked_at": timestamp.isoformat(),
        "automatic_approval": "not_executed",
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


def governance_evidence(route_assignment: RouteAssignment) -> GovernanceEvidence:
    return GovernanceEvidence(
        approval=route_assignment.governance_approval_snapshot or {},
        intervention=route_assignment.intervention_authorization_snapshot or {},
        replay_authorization=route_assignment.replay_authorization_snapshot or {},
        rollback_authorization=route_assignment.rollback_authorization_snapshot or {},
        reconciliation_approval=route_assignment.reconciliation_approval_snapshot or {},
        blockers=route_assignment.governance_blocker_snapshot or {},
        audit=route_assignment.governance_audit_snapshot or {},
    )


def governance_traceability(
    route_assignment: RouteAssignment,
    visit: Visit,
    operator_id: str | None,
) -> GovernanceTraceability:
    return GovernanceTraceability(
        route_assignment_id=route_assignment.id,
        visit_id=visit.id,
        work_order_id=visit.work_order_id,
        job_id=route_assignment.job_id or visit.job_id,
        technician_id=route_assignment.technician_id or visit.technician_id,
        audit_correlation_id=route_assignment.audit_correlation_id or visit.audit_correlation_id,
        operator_id=operator_id,
    )


def replay_prepared(route_assignment: RouteAssignment) -> bool:
    replay_snapshot = route_assignment.replay_preparation_snapshot or {}
    return bool(
        route_assignment.replay_recovery_state == "replay_prepared"
        and replay_snapshot.get("replay_prepared")
        and replay_snapshot.get("replay_execution") == "not_executed"
    )


def rollback_prepared(route_assignment: RouteAssignment) -> bool:
    rollback_snapshot = route_assignment.rollback_preparation_snapshot or {}
    return bool(
        route_assignment.replay_recovery_state == "rollback_prepared"
        and rollback_snapshot.get("rollback_prepared")
        and rollback_snapshot.get("rollback_execution") == "not_executed"
    )


def reconciliation_prepared(route_assignment: RouteAssignment) -> bool:
    return route_assignment.dispatch_reconciliation_state in {
        "reconciliation_required",
        "awaiting_manual_resolution",
    }


def unauthorized_operator_blocker(
    operator_role: str | None,
    operation: GovernanceOperation,
) -> GovernanceBlocker:
    return GovernanceBlocker(
        code=GovernanceFailureCode.UNAUTHORIZED_OPERATOR_ACTION,
        message="Operator role is not authorized for this governance action.",
        metadata={"operator_role": operator_role, "operation": operation.value},
    )


def dedupe_blockers(blockers: list[GovernanceBlocker]) -> tuple[GovernanceBlocker, ...]:
    deduped: list[GovernanceBlocker] = []
    seen: set[GovernanceFailureCode] = set()
    for blocker in blockers:
        if blocker.code in seen:
            continue
        deduped.append(blocker)
        seen.add(blocker.code)
    return tuple(deduped)
