from collections.abc import Callable, Sequence
from datetime import UTC, datetime

from app.domain.dispatch_reconciliation import (
    ConsistencyVerificationResult,
    DivergenceEvidence,
    MismatchEvidence,
    ReconciliationBlocker,
    ReconciliationEvidence,
    ReconciliationFailureCode,
    ReconciliationLifecycleState,
    ReconciliationMismatchCode,
    ReconciliationResult,
    ReconciliationTraceability,
)
from app.models.audit_log import AuditLog
from app.models.operational_event_record import OperationalEventRecord
from app.models.route_assignment import RouteAssignment
from app.models.visit import Visit

DISPATCHED_STATUS = "dispatched"
CONFIRMATION_READY_STATE = "awaiting_external_confirmation"
CONFIRMED_STATE = "externally_confirmed"
TERMINAL_RECONCILIATION_STATES = {
    ReconciliationLifecycleState.CONSISTENCY_VERIFIED.value,
    ReconciliationLifecycleState.RECONCILIATION_REQUIRED.value,
    ReconciliationLifecycleState.AWAITING_MANUAL_RESOLUTION.value,
}


class DispatchReconciliationService:
    def __init__(self, *, now: Callable[[], datetime] | None = None) -> None:
        self.now = now or (lambda: datetime.now(UTC))

    def prepare_reconciliation(
        self,
        route_assignment: RouteAssignment,
        *,
        visit: Visit,
        operational_events: Sequence[OperationalEventRecord] = (),
    ) -> ReconciliationResult:
        timestamp = self.now()
        consistency = verify_consistency(route_assignment, visit)
        traceability = reconciliation_traceability(route_assignment, visit)
        blockers = reconciliation_blockers(route_assignment, visit, operational_events)
        if any(
            blocker.code == ReconciliationFailureCode.DUPLICATE_RECONCILIATION
            for blocker in blockers
        ):
            return failed_reconciliation_result(
                route_assignment,
                state=ReconciliationLifecycleState.RECONCILIATION_BLOCKED,
                consistency=consistency,
                traceability=traceability,
                blockers=blockers,
            )
        if blockers:
            apply_reconciliation_blocked(
                route_assignment,
                consistency,
                blockers,
                operational_events,
                timestamp,
            )
            return failed_reconciliation_result(
                route_assignment,
                state=ReconciliationLifecycleState.RECONCILIATION_BLOCKED,
                consistency=consistency,
                traceability=traceability,
                blockers=blockers,
            )

        if consistency.is_consistent:
            apply_consistency_verified(
                route_assignment,
                consistency,
                operational_events,
                timestamp,
            )
            state = ReconciliationLifecycleState.CONSISTENCY_VERIFIED
            return ReconciliationResult(
                succeeded=True,
                state=state,
                consistency=consistency,
                traceability=traceability,
                evidence=reconciliation_evidence(route_assignment),
            )

        divergence = divergence_evidence(consistency, route_assignment, operational_events)
        apply_reconciliation_required(
            route_assignment,
            consistency,
            divergence,
            operational_events,
            timestamp,
        )
        state = ReconciliationLifecycleState.RECONCILIATION_REQUIRED
        return ReconciliationResult(
            succeeded=True,
            state=state,
            consistency=consistency,
            traceability=traceability,
            divergence=divergence,
            evidence=reconciliation_evidence(route_assignment),
        )

    @staticmethod
    def build_reconciliation_audit_log(route_assignment: RouteAssignment) -> AuditLog:
        audit_snapshot = route_assignment.dispatch_reconciliation_audit_snapshot or {}
        return AuditLog(
            action=audit_snapshot.get("action") or "dispatch_reconciliation.recorded",
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
                "dispatch_reconciliation_state": route_assignment.dispatch_reconciliation_state,
                "external_api_calls": audit_snapshot.get("external_api_calls"),
            },
        )


def reconciliation_blockers(
    route_assignment: RouteAssignment,
    visit: Visit,
    operational_events: Sequence[OperationalEventRecord],
) -> tuple[ReconciliationBlocker, ...]:
    blockers: list[ReconciliationBlocker] = []
    if route_assignment.id is None or route_assignment.visit_id != visit.id:
        blockers.append(
            ReconciliationBlocker(
                code=ReconciliationFailureCode.MISSING_ROUTE_ASSIGNMENT_LINKAGE,
                message="Route assignment must be linked to the Visit being reconciled.",
            ),
        )
    if not (route_assignment.audit_correlation_id or visit.audit_correlation_id):
        blockers.append(
            ReconciliationBlocker(
                code=ReconciliationFailureCode.MISSING_AUDIT_CORRELATION,
                message="Reconciliation requires audit correlation continuity.",
            ),
        )
    if visit.visit_type == "water_emergency":
        blockers.append(
            ReconciliationBlocker(
                code=ReconciliationFailureCode.WATER_EMERGENCY_VISIT,
                message="Water Emergency Visits require a separated reconciliation path.",
            ),
        )
    if visit.status == "review_required":
        blockers.append(
            ReconciliationBlocker(
                code=ReconciliationFailureCode.REVIEW_REQUIRED,
                message="Manual Review remains authoritative before reconciliation.",
            ),
        )
    if visit.status != DISPATCHED_STATUS or route_assignment.dispatch_execution_state != (
        DISPATCHED_STATUS
    ):
        blockers.append(
            ReconciliationBlocker(
                code=ReconciliationFailureCode.INVALID_LIFECYCLE,
                message="Reconciliation preparation requires a dispatched internal lifecycle.",
                metadata={
                    "visit_status": visit.status,
                    "dispatch_execution_state": route_assignment.dispatch_execution_state,
                },
            ),
        )
    if not route_assignment_authorized(route_assignment):
        blockers.append(
            ReconciliationBlocker(
                code=ReconciliationFailureCode.UNAUTHORIZED_ROUTE_ASSIGNMENT,
                message="Only authorized Route Assignments can prepare reconciliation.",
            ),
        )
    if route_assignment.dispatch_reconciliation_state in TERMINAL_RECONCILIATION_STATES:
        blockers.append(
            ReconciliationBlocker(
                code=ReconciliationFailureCode.DUPLICATE_RECONCILIATION,
                message="Reconciliation has already been prepared for this Route Assignment.",
                metadata={
                    "dispatch_reconciliation_state": (
                        route_assignment.dispatch_reconciliation_state
                    ),
                },
            ),
        )
    mutable_events = [
        str(event.id)
        for event in operational_events
        if not event.is_immutable or event.immutable_evidence_snapshot is None
    ]
    if mutable_events:
        blockers.append(
            ReconciliationBlocker(
                code=ReconciliationFailureCode.IMMUTABLE_HISTORY_VIOLATION,
                message="Operational event history must remain immutable during reconciliation.",
                metadata={"mutable_event_ids": mutable_events},
            ),
        )
    return tuple(dedupe_blockers(blockers))


def verify_consistency(
    route_assignment: RouteAssignment,
    visit: Visit,
) -> ConsistencyVerificationResult:
    mismatches: list[MismatchEvidence] = []
    internal_state = route_assignment.dispatch_execution_state
    if internal_state != DISPATCHED_STATUS or visit.status != DISPATCHED_STATUS:
        mismatches.append(
            MismatchEvidence(
                code=ReconciliationMismatchCode.INTERNAL_LIFECYCLE_MISMATCH,
                message="Internal Visit and Route Assignment lifecycle are not both dispatched.",
                expected=DISPATCHED_STATUS,
                actual=f"visit={visit.status};route_assignment={internal_state}",
            ),
        )
    external_execution_state = route_assignment.external_execution_state
    if external_execution_state != CONFIRMATION_READY_STATE:
        mismatches.append(
            MismatchEvidence(
                code=ReconciliationMismatchCode.EXTERNAL_EXECUTION_MISMATCH,
                message="External execution has not reached confirmation readiness.",
                expected=CONFIRMATION_READY_STATE,
                actual=external_execution_state,
                metadata={
                    "external_execution_failure_snapshot": (
                        route_assignment.external_execution_failure_snapshot or {}
                    ),
                },
            ),
        )
    external_confirmation_state = route_assignment.external_confirmation_state
    if (
        external_confirmation_state != CONFIRMED_STATE
        or route_assignment.external_confirmed_at is None
    ):
        mismatches.append(
            MismatchEvidence(
                code=ReconciliationMismatchCode.EXTERNAL_CONFIRMATION_MISMATCH,
                message="External confirmation is not consistent with internal dispatch.",
                expected=CONFIRMED_STATE,
                actual=external_confirmation_state,
                metadata={
                    "external_confirmed_at": route_assignment.external_confirmed_at.isoformat()
                    if route_assignment.external_confirmed_at
                    else None,
                },
            ),
        )
    if (
        route_assignment.retry_preparation_snapshot
        or external_confirmation_state == "awaiting_retry"
    ):
        mismatches.append(
            MismatchEvidence(
                code=ReconciliationMismatchCode.RETRY_RECOVERY_MISMATCH,
                message="Retry or recovery preparation exists and requires reconciliation review.",
                expected="no_retry_recovery_pending",
                actual="retry_recovery_pending",
            ),
        )
    return ConsistencyVerificationResult(
        is_consistent=not mismatches,
        divergence_detected=bool(mismatches),
        internal_lifecycle_state=internal_state,
        external_execution_state=external_execution_state,
        external_confirmation_state=external_confirmation_state,
        mismatch_evidence=tuple(dedupe_mismatches(mismatches)),
    )


def apply_consistency_verified(
    route_assignment: RouteAssignment,
    consistency: ConsistencyVerificationResult,
    operational_events: Sequence[OperationalEventRecord],
    timestamp: datetime,
) -> None:
    state = ReconciliationLifecycleState.CONSISTENCY_VERIFIED
    route_assignment.dispatch_reconciliation_state = state.value
    route_assignment.dispatch_consistency_snapshot = consistency_snapshot(
        consistency,
        operational_events,
        timestamp,
    )
    route_assignment.dispatch_divergence_snapshot = {}
    route_assignment.dispatch_mismatch_snapshot = mismatch_snapshot(consistency)
    route_assignment.dispatch_reconciliation_blocker_snapshot = {}
    route_assignment.dispatch_reconciliation_audit_snapshot = reconciliation_audit_snapshot(
        route_assignment,
        state,
    )
    route_assignment.dispatch_consistency_verified_at = timestamp


def apply_reconciliation_required(
    route_assignment: RouteAssignment,
    consistency: ConsistencyVerificationResult,
    divergence: DivergenceEvidence,
    operational_events: Sequence[OperationalEventRecord],
    timestamp: datetime,
) -> None:
    state = ReconciliationLifecycleState.RECONCILIATION_REQUIRED
    route_assignment.dispatch_reconciliation_state = state.value
    route_assignment.dispatch_consistency_snapshot = consistency_snapshot(
        consistency,
        operational_events,
        timestamp,
    )
    route_assignment.dispatch_divergence_snapshot = divergence.evidence
    route_assignment.dispatch_mismatch_snapshot = mismatch_snapshot(consistency)
    route_assignment.dispatch_reconciliation_blocker_snapshot = {}
    route_assignment.dispatch_reconciliation_audit_snapshot = reconciliation_audit_snapshot(
        route_assignment,
        state,
    )
    route_assignment.dispatch_reconciliation_prepared_at = timestamp


def apply_reconciliation_blocked(
    route_assignment: RouteAssignment,
    consistency: ConsistencyVerificationResult,
    blockers: tuple[ReconciliationBlocker, ...],
    operational_events: Sequence[OperationalEventRecord],
    timestamp: datetime,
) -> None:
    state = ReconciliationLifecycleState.RECONCILIATION_BLOCKED
    route_assignment.dispatch_reconciliation_state = state.value
    route_assignment.dispatch_consistency_snapshot = consistency_snapshot(
        consistency,
        operational_events,
        timestamp,
    )
    route_assignment.dispatch_mismatch_snapshot = mismatch_snapshot(consistency)
    route_assignment.dispatch_reconciliation_blocker_snapshot = blocker_snapshot(
        blockers,
        timestamp,
    )
    route_assignment.dispatch_reconciliation_audit_snapshot = reconciliation_audit_snapshot(
        route_assignment,
        state,
    )
    route_assignment.dispatch_reconciliation_blocked_at = timestamp


def failed_reconciliation_result(
    route_assignment: RouteAssignment,
    *,
    state: ReconciliationLifecycleState,
    consistency: ConsistencyVerificationResult,
    traceability: ReconciliationTraceability,
    blockers: tuple[ReconciliationBlocker, ...],
) -> ReconciliationResult:
    return ReconciliationResult(
        succeeded=False,
        state=state,
        consistency=consistency,
        traceability=traceability,
        failure_reasons=blockers,
        evidence=ReconciliationEvidence(
            consistency=route_assignment.dispatch_consistency_snapshot or {},
            divergence=route_assignment.dispatch_divergence_snapshot or {},
            mismatch=route_assignment.dispatch_mismatch_snapshot or {},
            blockers=route_assignment.dispatch_reconciliation_blocker_snapshot or {},
            audit=route_assignment.dispatch_reconciliation_audit_snapshot
            or reconciliation_audit_snapshot(route_assignment, state),
            failure_reasons=blockers,
        ),
    )


def consistency_snapshot(
    consistency: ConsistencyVerificationResult,
    operational_events: Sequence[OperationalEventRecord],
    timestamp: datetime,
) -> dict[str, object]:
    return {
        "is_consistent": consistency.is_consistent,
        "divergence_detected": consistency.divergence_detected,
        "internal_lifecycle_state": consistency.internal_lifecycle_state,
        "external_execution_state": consistency.external_execution_state,
        "external_confirmation_state": consistency.external_confirmation_state,
        "mismatch_codes": [mismatch.code.value for mismatch in consistency.mismatch_evidence],
        "event_history_count": len(operational_events),
        "immutable_history_mutated": False,
        "verified_at": timestamp.isoformat(),
        "external_api_calls": "not_executed",
        "reconciliation_execution": "not_executed",
    }


def mismatch_snapshot(consistency: ConsistencyVerificationResult) -> dict[str, object]:
    return {
        "mismatch_count": len(consistency.mismatch_evidence),
        "mismatches": [
            {
                "code": mismatch.code.value,
                "message": mismatch.message,
                "expected": mismatch.expected,
                "actual": mismatch.actual,
                "metadata": mismatch.metadata or {},
            }
            for mismatch in consistency.mismatch_evidence
        ],
    }


def divergence_evidence(
    consistency: ConsistencyVerificationResult,
    route_assignment: RouteAssignment,
    operational_events: Sequence[OperationalEventRecord],
) -> DivergenceEvidence:
    evidence = {
        "state": ReconciliationLifecycleState.DIVERGENCE_DETECTED.value,
        "next_state": ReconciliationLifecycleState.RECONCILIATION_REQUIRED.value,
        "manual_resolution_state": ReconciliationLifecycleState.AWAITING_MANUAL_RESOLUTION.value,
        "divergence_detected": True,
        "manual_resolution_required": True,
        "reconciliation_execution": "not_executed",
        "external_api_calls": "not_executed",
        "immutable_history_mutated": False,
        "audit_correlation_id": route_assignment.audit_correlation_id,
        "event_history_count": len(operational_events),
        "mismatch_codes": [mismatch.code.value for mismatch in consistency.mismatch_evidence],
    }
    return DivergenceEvidence(
        divergence_detected=True,
        mismatch_count=len(consistency.mismatch_evidence),
        mismatch_codes=tuple(mismatch.code for mismatch in consistency.mismatch_evidence),
        manual_resolution_required=True,
        evidence=evidence,
    )


def blocker_snapshot(
    blockers: tuple[ReconciliationBlocker, ...],
    timestamp: datetime,
) -> dict[str, object]:
    return {
        "state": ReconciliationLifecycleState.RECONCILIATION_BLOCKED.value,
        "blocked_at": timestamp.isoformat(),
        "external_api_calls": "not_executed",
        "reconciliation_execution": "not_executed",
        "blockers": [
            {
                "code": blocker.code.value,
                "message": blocker.message,
                "metadata": blocker.metadata or {},
            }
            for blocker in blockers
        ],
    }


def reconciliation_audit_snapshot(
    route_assignment: RouteAssignment,
    state: ReconciliationLifecycleState,
) -> dict[str, object]:
    action_by_state = {
        ReconciliationLifecycleState.CONSISTENCY_VERIFIED: (
            "dispatch_reconciliation.consistency_verified"
        ),
        ReconciliationLifecycleState.RECONCILIATION_REQUIRED: (
            "dispatch_reconciliation.reconciliation_required"
        ),
        ReconciliationLifecycleState.RECONCILIATION_BLOCKED: ("dispatch_reconciliation.blocked"),
    }
    return {
        "action": action_by_state.get(state, "dispatch_reconciliation.recorded"),
        "state": state.value,
        "route_assignment_id": str(route_assignment.id) if route_assignment.id else None,
        "visit_id": str(route_assignment.visit_id) if route_assignment.visit_id else None,
        "job_id": str(route_assignment.job_id) if route_assignment.job_id else None,
        "audit_correlation_id": route_assignment.audit_correlation_id,
        "external_api_calls": "not_executed",
        "reconciliation_execution": "not_executed",
        "immutable_history_mutated": False,
    }


def reconciliation_evidence(route_assignment: RouteAssignment) -> ReconciliationEvidence:
    return ReconciliationEvidence(
        consistency=route_assignment.dispatch_consistency_snapshot or {},
        divergence=route_assignment.dispatch_divergence_snapshot or {},
        mismatch=route_assignment.dispatch_mismatch_snapshot or {},
        blockers=route_assignment.dispatch_reconciliation_blocker_snapshot or {},
        audit=route_assignment.dispatch_reconciliation_audit_snapshot or {},
    )


def reconciliation_traceability(
    route_assignment: RouteAssignment,
    visit: Visit,
) -> ReconciliationTraceability:
    return ReconciliationTraceability(
        route_assignment_id=route_assignment.id,
        visit_id=visit.id,
        work_order_id=visit.work_order_id,
        job_id=route_assignment.job_id or visit.job_id,
        technician_id=route_assignment.technician_id or visit.technician_id,
        audit_correlation_id=route_assignment.audit_correlation_id or visit.audit_correlation_id,
    )


def route_assignment_authorized(route_assignment: RouteAssignment) -> bool:
    authorization_snapshot = route_assignment.dispatch_authorization_snapshot or {}
    execution_boundary_snapshot = route_assignment.dispatch_execution_boundary_snapshot or {}
    return bool(
        authorization_snapshot.get("authorized_for_dispatch")
        and execution_boundary_snapshot.get("authorized_for_dispatch")
    )


def dedupe_blockers(
    blockers: list[ReconciliationBlocker],
) -> tuple[ReconciliationBlocker, ...]:
    deduped: list[ReconciliationBlocker] = []
    seen: set[ReconciliationFailureCode] = set()
    for blocker in blockers:
        if blocker.code in seen:
            continue
        deduped.append(blocker)
        seen.add(blocker.code)
    return tuple(deduped)


def dedupe_mismatches(
    mismatches: list[MismatchEvidence],
) -> tuple[MismatchEvidence, ...]:
    deduped: list[MismatchEvidence] = []
    seen: set[ReconciliationMismatchCode] = set()
    for mismatch in mismatches:
        if mismatch.code in seen:
            continue
        deduped.append(mismatch)
        seen.add(mismatch.code)
    return tuple(deduped)
