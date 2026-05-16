from collections.abc import Callable
from datetime import UTC, datetime

from app.domain.external_execution_confirmation import (
    ExternalConfirmationEvidence,
    ExternalConfirmationFailureCode,
    ExternalConfirmationFailureReason,
    ExternalConfirmationLifecycleState,
    ExternalConfirmationResult,
    ExternalConfirmationTraceability,
    SimulatedExternalConfirmationState,
)
from app.models.audit_log import AuditLog
from app.models.route_assignment import RouteAssignment
from app.models.visit import Visit

DISPATCHED_STATUS = "dispatched"


class ExternalExecutionConfirmationService:
    def __init__(self, *, now: Callable[[], datetime] | None = None) -> None:
        self.now = now or (lambda: datetime.now(UTC))

    def process_confirmation(
        self,
        route_assignment: RouteAssignment,
        *,
        visit: Visit,
        simulated_state: SimulatedExternalConfirmationState,
        adapter_name: str = "external_adapter",
        external_reference: str | None = None,
        failure_message: str | None = None,
    ) -> ExternalConfirmationResult:
        timestamp = self.now()
        failure_reasons = confirmation_failure_reasons(route_assignment, visit)
        if failure_reasons:
            return failed_confirmation_result(route_assignment, visit, failure_reasons)

        if simulated_state == SimulatedExternalConfirmationState.CONFIRMED:
            state = ExternalConfirmationLifecycleState.EXTERNALLY_CONFIRMED
            apply_confirmation_success(
                route_assignment,
                visit,
                adapter_name=adapter_name,
                external_reference=external_reference,
                timestamp=timestamp,
            )
        elif simulated_state == SimulatedExternalConfirmationState.FAILED:
            state = ExternalConfirmationLifecycleState.EXTERNAL_CONFIRMATION_FAILED
            apply_confirmation_failure(
                route_assignment,
                visit,
                adapter_name=adapter_name,
                failure_message=failure_message,
                timestamp=timestamp,
            )
        else:
            state = ExternalConfirmationLifecycleState.RECONCILIATION_REQUIRED
            apply_reconciliation_required(
                route_assignment,
                visit,
                adapter_name=adapter_name,
                failure_message=failure_message,
                timestamp=timestamp,
            )

        return ExternalConfirmationResult(
            succeeded=True,
            state=state,
            traceability=external_confirmation_traceability(route_assignment, visit),
            evidence=external_confirmation_evidence(route_assignment),
        )

    def prepare_retry(
        self,
        route_assignment: RouteAssignment,
        *,
        visit: Visit,
        retry_reason: str,
    ) -> ExternalConfirmationResult:
        timestamp = self.now()
        failure_reasons = retry_failure_reasons(route_assignment, visit)
        if failure_reasons:
            return failed_confirmation_result(route_assignment, visit, failure_reasons)

        previous_state = route_assignment.external_confirmation_state
        state = ExternalConfirmationLifecycleState.AWAITING_RETRY
        route_assignment.external_confirmation_state = state.value
        route_assignment.retry_preparation_snapshot = {
            "retry_eligible": True,
            "retry_reason": retry_reason,
            "retry_execution": "not_executed",
            "automatic_retry": "not_executed",
            "prepared_at": timestamp.isoformat(),
            "external_api_calls": "not_executed",
        }
        route_assignment.external_confirmation_lifecycle_snapshot = confirmation_lifecycle_snapshot(
            previous_state=previous_state,
            next_state=state,
            transitioned_at=timestamp,
        )
        route_assignment.external_confirmation_audit_snapshot = confirmation_audit_snapshot(
            route_assignment,
            state,
        )
        route_assignment.retry_prepared_at = timestamp
        update_visit_confirmation_metadata(visit, state, timestamp)

        return ExternalConfirmationResult(
            succeeded=True,
            state=state,
            traceability=external_confirmation_traceability(route_assignment, visit),
            evidence=external_confirmation_evidence(route_assignment),
        )

    @staticmethod
    def build_external_confirmation_audit_log(route_assignment: RouteAssignment) -> AuditLog:
        audit_snapshot = route_assignment.external_confirmation_audit_snapshot or {}
        return AuditLog(
            action=audit_snapshot.get("action") or "external_execution.confirmation_recorded",
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
                "external_confirmation_state": route_assignment.external_confirmation_state,
                "external_api_calls": audit_snapshot.get("external_api_calls"),
                "confirmed_at": route_assignment.external_confirmed_at.isoformat()
                if route_assignment.external_confirmed_at
                else None,
            },
        )


def confirmation_failure_reasons(
    route_assignment: RouteAssignment,
    visit: Visit,
) -> tuple[ExternalConfirmationFailureReason, ...]:
    reasons: list[ExternalConfirmationFailureReason] = []
    if route_assignment.id is None or route_assignment.visit_id != visit.id:
        reasons.append(
            ExternalConfirmationFailureReason(
                code=ExternalConfirmationFailureCode.MISSING_ROUTE_ASSIGNMENT_LINKAGE,
                message="Route assignment must be linked to the Visit being confirmed.",
            ),
        )
    if visit.visit_type == "water_emergency":
        reasons.append(
            ExternalConfirmationFailureReason(
                code=ExternalConfirmationFailureCode.WATER_EMERGENCY_VISIT,
                message="Water Emergency Visits require a separated confirmation path.",
            ),
        )
    if (
        route_assignment.external_confirmation_state
        == (ExternalConfirmationLifecycleState.EXTERNALLY_CONFIRMED.value)
        or route_assignment.external_confirmed_at is not None
    ):
        reasons.append(
            ExternalConfirmationFailureReason(
                code=ExternalConfirmationFailureCode.DUPLICATE_CONFIRMATION,
                message="External execution has already been confirmed.",
            ),
        )
    if visit.status == "blocked":
        reasons.append(
            ExternalConfirmationFailureReason(
                code=ExternalConfirmationFailureCode.BLOCKED_VISIT,
                message="Blocked Visits cannot confirm external execution.",
            ),
        )
    if visit.status == "review_required":
        reasons.append(
            ExternalConfirmationFailureReason(
                code=ExternalConfirmationFailureCode.REVIEW_REQUIRED,
                message="Review-required Visits cannot confirm external execution.",
            ),
        )
    if visit.status == "archived":
        reasons.append(
            ExternalConfirmationFailureReason(
                code=ExternalConfirmationFailureCode.ARCHIVED_VISIT,
                message="Archived Visits cannot confirm external execution.",
            ),
        )
    if visit.status != DISPATCHED_STATUS:
        reasons.append(
            ExternalConfirmationFailureReason(
                code=ExternalConfirmationFailureCode.INVALID_LIFECYCLE,
                message="Visit lifecycle must remain dispatched for external confirmation.",
                metadata={"visit_status": visit.status},
            ),
        )
    if route_assignment.external_adapter_state != (
        ExternalConfirmationLifecycleState.AWAITING_EXTERNAL_CONFIRMATION.value
    ):
        reasons.append(
            ExternalConfirmationFailureReason(
                code=ExternalConfirmationFailureCode.ADAPTER_NOT_READY_FOR_CONFIRMATION,
                message="Route assignment must be awaiting external confirmation.",
                metadata={"external_adapter_state": route_assignment.external_adapter_state},
            ),
        )
        reasons.append(
            ExternalConfirmationFailureReason(
                code=ExternalConfirmationFailureCode.INVALID_LIFECYCLE,
                message="External adapter lifecycle is not ready for confirmation.",
                metadata={"external_adapter_state": route_assignment.external_adapter_state},
            ),
        )
    if not route_assignment_authorized(route_assignment):
        reasons.append(
            ExternalConfirmationFailureReason(
                code=ExternalConfirmationFailureCode.UNAUTHORIZED_ROUTE_ASSIGNMENT,
                message="Only authorized Route Assignments can confirm external execution.",
            ),
        )
    return tuple(dedupe_failure_reasons(reasons))


def retry_failure_reasons(
    route_assignment: RouteAssignment,
    visit: Visit,
) -> tuple[ExternalConfirmationFailureReason, ...]:
    reasons = list(confirmation_base_safety_reasons(route_assignment, visit))
    if route_assignment.external_confirmation_state != (
        ExternalConfirmationLifecycleState.EXTERNAL_CONFIRMATION_FAILED.value
    ):
        reasons.append(
            ExternalConfirmationFailureReason(
                code=ExternalConfirmationFailureCode.INVALID_RETRY_STATE,
                message="Retry preparation requires a failed confirmation state.",
                metadata={
                    "external_confirmation_state": route_assignment.external_confirmation_state,
                },
            ),
        )
    return tuple(dedupe_failure_reasons(reasons))


def confirmation_base_safety_reasons(
    route_assignment: RouteAssignment,
    visit: Visit,
) -> tuple[ExternalConfirmationFailureReason, ...]:
    reasons: list[ExternalConfirmationFailureReason] = []
    if route_assignment.id is None or route_assignment.visit_id != visit.id:
        reasons.append(
            ExternalConfirmationFailureReason(
                code=ExternalConfirmationFailureCode.MISSING_ROUTE_ASSIGNMENT_LINKAGE,
                message="Route assignment must be linked to the Visit.",
            ),
        )
    if visit.visit_type == "water_emergency":
        reasons.append(
            ExternalConfirmationFailureReason(
                code=ExternalConfirmationFailureCode.WATER_EMERGENCY_VISIT,
                message="Water Emergency Visits require a separated recovery path.",
            ),
        )
    if visit.status == "blocked":
        reasons.append(
            ExternalConfirmationFailureReason(
                code=ExternalConfirmationFailureCode.BLOCKED_VISIT,
                message="Blocked Visits cannot prepare external recovery.",
            ),
        )
    if visit.status == "review_required":
        reasons.append(
            ExternalConfirmationFailureReason(
                code=ExternalConfirmationFailureCode.REVIEW_REQUIRED,
                message="Review-required Visits cannot prepare external recovery.",
            ),
        )
    if visit.status == "archived":
        reasons.append(
            ExternalConfirmationFailureReason(
                code=ExternalConfirmationFailureCode.ARCHIVED_VISIT,
                message="Archived Visits cannot prepare external recovery.",
            ),
        )
    if visit.status != DISPATCHED_STATUS:
        reasons.append(
            ExternalConfirmationFailureReason(
                code=ExternalConfirmationFailureCode.INVALID_LIFECYCLE,
                message="Visit lifecycle must remain dispatched for external recovery.",
                metadata={"visit_status": visit.status},
            ),
        )
    if not route_assignment_authorized(route_assignment):
        reasons.append(
            ExternalConfirmationFailureReason(
                code=ExternalConfirmationFailureCode.UNAUTHORIZED_ROUTE_ASSIGNMENT,
                message="Only authorized Route Assignments can prepare external recovery.",
            ),
        )
    return tuple(reasons)


def failed_confirmation_result(
    route_assignment: RouteAssignment,
    visit: Visit,
    failure_reasons: tuple[ExternalConfirmationFailureReason, ...],
) -> ExternalConfirmationResult:
    state = ExternalConfirmationLifecycleState.EXTERNAL_CONFIRMATION_FAILED
    return ExternalConfirmationResult(
        succeeded=False,
        state=state,
        traceability=external_confirmation_traceability(route_assignment, visit),
        failure_reasons=failure_reasons,
        evidence=ExternalConfirmationEvidence(
            confirmation={},
            lifecycle=route_assignment.external_confirmation_lifecycle_snapshot or {},
            failure=route_assignment.external_failure_snapshot or {},
            retry=route_assignment.retry_preparation_snapshot or {},
            reconciliation=route_assignment.reconciliation_snapshot or {},
            audit=confirmation_audit_snapshot(route_assignment, state),
            failure_reasons=failure_reasons,
        ),
    )


def apply_confirmation_success(
    route_assignment: RouteAssignment,
    visit: Visit,
    *,
    adapter_name: str,
    external_reference: str | None,
    timestamp: datetime,
) -> None:
    state = ExternalConfirmationLifecycleState.EXTERNALLY_CONFIRMED
    previous_state = route_assignment.external_adapter_state
    route_assignment.external_confirmation_state = state.value
    route_assignment.external_confirmation_snapshot = {
        "simulated_external_state": SimulatedExternalConfirmationState.CONFIRMED.value,
        "adapter_name": adapter_name,
        "external_reference": external_reference,
        "confirmed_at": timestamp.isoformat(),
        "external_api_calls": "not_executed",
        "reconciliation_required": False,
    }
    route_assignment.external_confirmation_lifecycle_snapshot = confirmation_lifecycle_snapshot(
        previous_state=previous_state,
        next_state=state,
        transitioned_at=timestamp,
    )
    route_assignment.external_confirmation_audit_snapshot = confirmation_audit_snapshot(
        route_assignment,
        state,
    )
    route_assignment.external_confirmed_at = timestamp
    update_visit_confirmation_metadata(visit, state, timestamp)


def apply_confirmation_failure(
    route_assignment: RouteAssignment,
    visit: Visit,
    *,
    adapter_name: str,
    failure_message: str | None,
    timestamp: datetime,
) -> None:
    state = ExternalConfirmationLifecycleState.EXTERNAL_CONFIRMATION_FAILED
    previous_state = route_assignment.external_adapter_state
    route_assignment.external_confirmation_state = state.value
    route_assignment.external_failure_snapshot = {
        "simulated_external_state": SimulatedExternalConfirmationState.FAILED.value,
        "adapter_name": adapter_name,
        "failure_message": failure_message,
        "failed_at": timestamp.isoformat(),
        "retry_eligible": True,
        "automatic_retry": "not_executed",
        "external_api_calls": "not_executed",
    }
    route_assignment.external_confirmation_lifecycle_snapshot = confirmation_lifecycle_snapshot(
        previous_state=previous_state,
        next_state=state,
        transitioned_at=timestamp,
    )
    route_assignment.external_confirmation_audit_snapshot = confirmation_audit_snapshot(
        route_assignment,
        state,
    )
    route_assignment.external_confirmation_failed_at = timestamp
    update_visit_confirmation_metadata(visit, state, timestamp)


def apply_reconciliation_required(
    route_assignment: RouteAssignment,
    visit: Visit,
    *,
    adapter_name: str,
    failure_message: str | None,
    timestamp: datetime,
) -> None:
    state = ExternalConfirmationLifecycleState.RECONCILIATION_REQUIRED
    previous_state = route_assignment.external_adapter_state
    route_assignment.external_confirmation_state = state.value
    simulated_state = SimulatedExternalConfirmationState.RECONCILIATION_REQUIRED.value
    route_assignment.reconciliation_snapshot = {
        "simulated_external_state": simulated_state,
        "adapter_name": adapter_name,
        "reconciliation_reason": failure_message,
        "reconciliation_required": True,
        "reconciliation_execution": "not_executed",
        "external_api_calls": "not_executed",
        "prepared_at": timestamp.isoformat(),
    }
    route_assignment.external_confirmation_lifecycle_snapshot = confirmation_lifecycle_snapshot(
        previous_state=previous_state,
        next_state=state,
        transitioned_at=timestamp,
    )
    route_assignment.external_confirmation_audit_snapshot = confirmation_audit_snapshot(
        route_assignment,
        state,
    )
    route_assignment.reconciliation_required_at = timestamp
    update_visit_confirmation_metadata(visit, state, timestamp)


def confirmation_lifecycle_snapshot(
    *,
    previous_state: str | None,
    next_state: ExternalConfirmationLifecycleState,
    transitioned_at: datetime,
) -> dict[str, object]:
    return {
        "previous_state": previous_state,
        "next_state": next_state.value,
        "transitioned_at": transitioned_at.isoformat(),
        "external_api_calls": "not_executed",
        "automatic_retry": "not_executed",
        "automatic_reconciliation": "not_executed",
    }


def confirmation_audit_snapshot(
    route_assignment: RouteAssignment,
    state: ExternalConfirmationLifecycleState,
) -> dict[str, object]:
    action_by_state = {
        ExternalConfirmationLifecycleState.EXTERNALLY_CONFIRMED: "external_execution.confirmed",
        ExternalConfirmationLifecycleState.EXTERNAL_CONFIRMATION_FAILED: (
            "external_execution.confirmation_failed"
        ),
        ExternalConfirmationLifecycleState.AWAITING_RETRY: "external_execution.retry_prepared",
        ExternalConfirmationLifecycleState.RECONCILIATION_REQUIRED: (
            "external_execution.reconciliation_required"
        ),
    }
    return {
        "action": action_by_state.get(state, "external_execution.confirmation_blocked"),
        "state": state.value,
        "route_assignment_id": str(route_assignment.id) if route_assignment.id else None,
        "visit_id": str(route_assignment.visit_id) if route_assignment.visit_id else None,
        "job_id": str(route_assignment.job_id) if route_assignment.job_id else None,
        "audit_correlation_id": route_assignment.audit_correlation_id,
        "external_api_calls": "not_executed",
    }


def update_visit_confirmation_metadata(
    visit: Visit,
    state: ExternalConfirmationLifecycleState,
    timestamp: datetime,
) -> None:
    metadata = dict(visit.lifecycle_metadata or {})
    metadata["external_confirmation_state"] = state.value
    metadata["external_confirmation_updated_at"] = timestamp.isoformat()
    metadata["external_api_calls"] = "not_executed"
    visit.lifecycle_metadata = metadata


def route_assignment_authorized(route_assignment: RouteAssignment) -> bool:
    authorization_snapshot = route_assignment.dispatch_authorization_snapshot or {}
    execution_boundary_snapshot = route_assignment.dispatch_execution_boundary_snapshot or {}
    return bool(
        authorization_snapshot.get("authorized_for_dispatch")
        and execution_boundary_snapshot.get("authorized_for_dispatch")
    )


def external_confirmation_traceability(
    route_assignment: RouteAssignment,
    visit: Visit,
) -> ExternalConfirmationTraceability:
    return ExternalConfirmationTraceability(
        route_assignment_id=route_assignment.id,
        visit_id=visit.id,
        work_order_id=visit.work_order_id,
        job_id=route_assignment.job_id or visit.job_id,
        technician_id=route_assignment.technician_id or visit.technician_id,
        audit_correlation_id=route_assignment.audit_correlation_id or visit.audit_correlation_id,
    )


def external_confirmation_evidence(
    route_assignment: RouteAssignment,
) -> ExternalConfirmationEvidence:
    return ExternalConfirmationEvidence(
        confirmation=route_assignment.external_confirmation_snapshot or {},
        lifecycle=route_assignment.external_confirmation_lifecycle_snapshot or {},
        failure=route_assignment.external_failure_snapshot or {},
        retry=route_assignment.retry_preparation_snapshot or {},
        reconciliation=route_assignment.reconciliation_snapshot or {},
        audit=route_assignment.external_confirmation_audit_snapshot or {},
    )


def dedupe_failure_reasons(
    reasons: list[ExternalConfirmationFailureReason],
) -> tuple[ExternalConfirmationFailureReason, ...]:
    deduped: list[ExternalConfirmationFailureReason] = []
    seen: set[ExternalConfirmationFailureCode] = set()
    for reason in reasons:
        if reason.code in seen:
            continue
        deduped.append(reason)
        seen.add(reason.code)
    return tuple(deduped)
