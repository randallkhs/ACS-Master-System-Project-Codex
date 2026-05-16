from collections.abc import Callable
from datetime import UTC, datetime

from app.domain.dispatch_execution import (
    DispatchExecutionBlockerCode,
    DispatchExecutionEvidence,
    DispatchExecutionFailureReason,
    DispatchExecutionResult,
    DispatchExecutionState,
    DispatchExecutionTraceability,
    DispatchLifecycleTransition,
)
from app.models.audit_log import AuditLog
from app.models.route_assignment import RouteAssignment
from app.models.technician import Technician
from app.models.visit import Visit

AUTHORIZED_ROUTE_ASSIGNMENT_STATUS = "awaiting_dispatch_execution"
DISPATCHED_STATUS = "dispatched"


class DispatchExecutionService:
    def __init__(self, *, now: Callable[[], datetime] | None = None) -> None:
        self.now = now or (lambda: datetime.now(UTC))

    def execute_dispatch(
        self,
        route_assignment: RouteAssignment,
        *,
        visit: Visit,
        technician: Technician | None = None,
    ) -> DispatchExecutionResult:
        timestamp = self.now()
        previous_state = route_assignment.status
        failure_reasons = dispatch_failure_reasons(route_assignment, visit, technician)
        if failure_reasons:
            return failed_dispatch_result(
                route_assignment,
                visit,
                failure_reasons,
                timestamp,
            )

        transition = DispatchLifecycleTransition(
            previous_state=previous_state,
            new_state=DispatchExecutionState.DISPATCHED,
            transitioned_at=timestamp,
        )
        apply_dispatch_execution(route_assignment, visit, transition)
        return DispatchExecutionResult(
            succeeded=True,
            state=DispatchExecutionState.DISPATCHED,
            traceability=dispatch_traceability(route_assignment, visit),
            lifecycle_transition=transition,
            evidence=dispatch_execution_evidence(route_assignment),
        )

    @staticmethod
    def build_dispatch_executed_audit_log(route_assignment: RouteAssignment) -> AuditLog:
        execution_snapshot = route_assignment.dispatch_execution_snapshot or {}
        return AuditLog(
            action="operational_dispatch.executed",
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
                "dispatch_execution_state": route_assignment.dispatch_execution_state,
                "external_integrations": execution_snapshot.get("external_integrations"),
                "dispatch_executed_at": route_assignment.dispatched_at.isoformat()
                if route_assignment.dispatched_at
                else None,
            },
        )


def dispatch_failure_reasons(
    route_assignment: RouteAssignment,
    visit: Visit,
    technician: Technician | None,
) -> tuple[DispatchExecutionFailureReason, ...]:
    reasons: list[DispatchExecutionFailureReason] = []
    if route_assignment.id is None or route_assignment.visit_id != visit.id:
        reasons.append(
            DispatchExecutionFailureReason(
                code=DispatchExecutionBlockerCode.MISSING_ROUTE_ASSIGNMENT_LINKAGE,
                message="Route assignment must be linked to the Visit being dispatched.",
                metadata={
                    "route_assignment_visit_id": str(route_assignment.visit_id)
                    if route_assignment.visit_id
                    else None,
                    "visit_id": str(visit.id) if visit.id else None,
                },
            ),
        )
    if route_assignment.status == DISPATCHED_STATUS or route_assignment.dispatched_at is not None:
        reasons.append(
            DispatchExecutionFailureReason(
                code=DispatchExecutionBlockerCode.DUPLICATE_DISPATCH,
                message="Route assignment has already been dispatched.",
            ),
        )
    if visit.visit_type == "water_emergency":
        reasons.append(
            DispatchExecutionFailureReason(
                code=DispatchExecutionBlockerCode.WATER_EMERGENCY_VISIT,
                message="Water Emergency Visits require a separated dispatch execution path.",
            ),
        )
    if visit.status == "blocked":
        reasons.append(
            DispatchExecutionFailureReason(
                code=DispatchExecutionBlockerCode.BLOCKED_VISIT,
                message="Blocked Visits cannot dispatch.",
            ),
        )
    if visit.status == "review_required":
        reasons.append(
            DispatchExecutionFailureReason(
                code=DispatchExecutionBlockerCode.REVIEW_REQUIRED,
                message="Review-required Visits cannot dispatch.",
            ),
        )
    if visit.status == "archived":
        reasons.append(
            DispatchExecutionFailureReason(
                code=DispatchExecutionBlockerCode.ARCHIVED_VISIT,
                message="Archived Visits cannot dispatch.",
            ),
        )
    if visit.technician_id is None:
        reasons.append(
            DispatchExecutionFailureReason(
                code=DispatchExecutionBlockerCode.UNASSIGNED_VISIT,
                message="Unassigned Visits cannot dispatch.",
            ),
        )
    if visit.scheduled_start_at is None:
        reasons.append(
            DispatchExecutionFailureReason(
                code=DispatchExecutionBlockerCode.UNSCHEDULED_VISIT,
                message="Unscheduled Visits cannot dispatch.",
            ),
        )
    if technician is not None and not technician.is_active:
        reasons.append(
            DispatchExecutionFailureReason(
                code=DispatchExecutionBlockerCode.INACTIVE_TECHNICIAN,
                message="Inactive technicians block dispatch execution.",
            ),
        )
    if not route_assignment_authorized(route_assignment):
        reasons.append(
            DispatchExecutionFailureReason(
                code=DispatchExecutionBlockerCode.UNAUTHORIZED_ROUTE_ASSIGNMENT,
                message="Only dispatch-authorized Route Assignments may dispatch.",
            ),
        )
    if route_assignment.status != AUTHORIZED_ROUTE_ASSIGNMENT_STATUS:
        reasons.append(
            DispatchExecutionFailureReason(
                code=DispatchExecutionBlockerCode.INVALID_EXECUTION_STATE,
                message="Route assignment must be awaiting dispatch execution.",
                metadata={"route_assignment_status": route_assignment.status},
            ),
        )
    return tuple(dedupe_failure_reasons(reasons))


def failed_dispatch_result(
    route_assignment: RouteAssignment,
    visit: Visit,
    failure_reasons: tuple[DispatchExecutionFailureReason, ...],
    timestamp: datetime,
) -> DispatchExecutionResult:
    state = DispatchExecutionState.DISPATCH_BLOCKED
    transition = DispatchLifecycleTransition(
        previous_state=route_assignment.status,
        new_state=state,
        transitioned_at=timestamp,
    )
    return DispatchExecutionResult(
        succeeded=False,
        state=state,
        traceability=dispatch_traceability(route_assignment, visit),
        lifecycle_transition=transition,
        failure_reasons=failure_reasons,
        evidence=DispatchExecutionEvidence(
            execution={
                "state": state.value,
                "dispatch_execution": "not_executed",
                "external_integrations": "not_executed",
            },
            lifecycle=lifecycle_transition_snapshot(transition),
            route_assignment=route_assignment_snapshot(route_assignment),
            audit=audit_evidence_snapshot(route_assignment, state),
            failure_reasons=failure_reasons,
        ),
    )


def apply_dispatch_execution(
    route_assignment: RouteAssignment,
    visit: Visit,
    transition: DispatchLifecycleTransition,
) -> None:
    route_assignment.status = DISPATCHED_STATUS
    route_assignment.dispatch_execution_state = DispatchExecutionState.DISPATCHED.value
    route_assignment.dispatch_execution_snapshot = dispatch_execution_snapshot(
        route_assignment,
        transition,
    )
    route_assignment.dispatch_lifecycle_snapshot = lifecycle_transition_snapshot(transition)
    route_assignment.dispatch_audit_snapshot = audit_evidence_snapshot(
        route_assignment,
        DispatchExecutionState.DISPATCHED,
    )
    route_assignment.dispatched_at = transition.transitioned_at

    visit.status = DISPATCHED_STATUS
    metadata = dict(visit.lifecycle_metadata or {})
    metadata["dispatch_execution"] = "executed_internal_only"
    metadata["dispatch_execution_state"] = DispatchExecutionState.DISPATCHED.value
    metadata["dispatch_executed_at"] = transition.transitioned_at.isoformat()
    metadata["external_integrations"] = "not_executed"
    metadata["route_assignment_id"] = str(route_assignment.id)
    metadata["audit_correlation_id"] = route_assignment.audit_correlation_id
    visit.lifecycle_metadata = metadata


def route_assignment_authorized(route_assignment: RouteAssignment) -> bool:
    authorization_snapshot = route_assignment.dispatch_authorization_snapshot or {}
    execution_boundary_snapshot = route_assignment.dispatch_execution_boundary_snapshot or {}
    return bool(
        authorization_snapshot.get("authorized_for_dispatch")
        and execution_boundary_snapshot.get("authorized_for_dispatch")
    )


def dispatch_execution_snapshot(
    route_assignment: RouteAssignment,
    transition: DispatchLifecycleTransition,
) -> dict[str, object]:
    return {
        "state": DispatchExecutionState.DISPATCHED.value,
        "route_assignment_id": str(route_assignment.id),
        "visit_id": str(route_assignment.visit_id) if route_assignment.visit_id else None,
        "job_id": str(route_assignment.job_id) if route_assignment.job_id else None,
        "technician_id": str(route_assignment.technician_id)
        if route_assignment.technician_id
        else None,
        "dispatched_at": transition.transitioned_at.isoformat(),
        "dispatch_execution": "executed_internal_only",
        "external_integrations": "not_executed",
        "fastfield_execution": "not_executed",
        "google_calendar_sync": "not_executed",
        "google_sheets_export": "not_executed",
        "technician_mobile_workflow": "not_executed",
        "background_workers": "not_executed",
        "ai_authority": "not_used",
    }


def lifecycle_transition_snapshot(transition: DispatchLifecycleTransition) -> dict[str, object]:
    return {
        "previous_state": transition.previous_state,
        "new_state": transition.new_state.value,
        "next_state": transition.new_state.value,
        "transitioned_at": transition.transitioned_at.isoformat(),
        "external_integrations": transition.external_integrations,
    }


def audit_evidence_snapshot(
    route_assignment: RouteAssignment,
    state: DispatchExecutionState,
) -> dict[str, object]:
    action = (
        "operational_dispatch.executed"
        if state == DispatchExecutionState.DISPATCHED
        else "operational_dispatch.blocked"
    )
    return {
        "action": action,
        "state": state.value,
        "route_assignment_id": str(route_assignment.id) if route_assignment.id else None,
        "visit_id": str(route_assignment.visit_id) if route_assignment.visit_id else None,
        "job_id": str(route_assignment.job_id) if route_assignment.job_id else None,
        "audit_correlation_id": route_assignment.audit_correlation_id,
    }


def route_assignment_snapshot(route_assignment: RouteAssignment) -> dict[str, object]:
    return {
        "id": str(route_assignment.id) if route_assignment.id else None,
        "status": route_assignment.status,
        "route_date": route_assignment.route_date.isoformat()
        if route_assignment.route_date
        else None,
        "visit_id": str(route_assignment.visit_id) if route_assignment.visit_id else None,
        "job_id": str(route_assignment.job_id) if route_assignment.job_id else None,
        "technician_id": str(route_assignment.technician_id)
        if route_assignment.technician_id
        else None,
        "audit_correlation_id": route_assignment.audit_correlation_id,
    }


def dispatch_execution_evidence(route_assignment: RouteAssignment) -> DispatchExecutionEvidence:
    transition = route_assignment.dispatch_lifecycle_snapshot or {}
    return DispatchExecutionEvidence(
        execution=route_assignment.dispatch_execution_snapshot or {},
        lifecycle=transition,
        route_assignment=route_assignment_snapshot(route_assignment),
        audit=route_assignment.dispatch_audit_snapshot or {},
    )


def dispatch_traceability(
    route_assignment: RouteAssignment,
    visit: Visit,
) -> DispatchExecutionTraceability:
    return DispatchExecutionTraceability(
        route_assignment_id=route_assignment.id,
        visit_id=visit.id,
        work_order_id=visit.work_order_id,
        job_id=route_assignment.job_id or visit.job_id,
        technician_id=route_assignment.technician_id or visit.technician_id,
        audit_correlation_id=route_assignment.audit_correlation_id or visit.audit_correlation_id,
    )


def dedupe_failure_reasons(
    reasons: list[DispatchExecutionFailureReason],
) -> tuple[DispatchExecutionFailureReason, ...]:
    deduped: list[DispatchExecutionFailureReason] = []
    seen: set[DispatchExecutionBlockerCode] = set()
    for reason in reasons:
        if reason.code in seen:
            continue
        deduped.append(reason)
        seen.add(reason.code)
    return tuple(deduped)
