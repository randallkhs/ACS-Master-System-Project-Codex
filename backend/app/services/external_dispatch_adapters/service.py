from collections.abc import Callable
from datetime import UTC, datetime

from app.domain.external_dispatch_adapter import (
    AdapterExecutionEvidence,
    AdapterExecutionRequest,
    AdapterExecutionResult,
    AdapterFailureReason,
    ExternalAdapterFailureCode,
    ExternalAdapterLifecycleState,
)
from app.models.audit_log import AuditLog
from app.models.route_assignment import RouteAssignment
from app.models.technician import Technician
from app.models.visit import Visit

DISPATCHED_STATUS = "dispatched"
EXTERNAL_ADAPTER_TARGETS = (
    "fastfield",
    "google_sheets",
    "google_calendar",
    "technician_mobile",
)


class ExternalDispatchAdapterPreparationService:
    def __init__(self, *, now: Callable[[], datetime] | None = None) -> None:
        self.now = now or (lambda: datetime.now(UTC))

    def prepare_adapters(
        self,
        route_assignment: RouteAssignment,
        *,
        visit: Visit,
        technician: Technician | None = None,
    ) -> AdapterExecutionResult:
        timestamp = self.now()
        request = adapter_execution_request(route_assignment, visit, timestamp)
        failure_reasons = adapter_failure_reasons(route_assignment, visit)
        if failure_reasons:
            return failed_adapter_result(route_assignment, request, failure_reasons, timestamp)

        payloads = external_payload_snapshot(route_assignment, visit, technician, timestamp)
        apply_adapter_preparation(route_assignment, visit, request, payloads, timestamp)
        return AdapterExecutionResult(
            succeeded=True,
            state=ExternalAdapterLifecycleState.AWAITING_EXTERNAL_EXECUTION,
            request=request,
            evidence=adapter_execution_evidence(route_assignment),
        )

    @staticmethod
    def build_adapter_prepared_audit_log(route_assignment: RouteAssignment) -> AuditLog:
        audit_snapshot = route_assignment.external_adapter_audit_snapshot or {}
        return AuditLog(
            action="external_dispatch_adapter.prepared",
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
                "external_adapter_state": route_assignment.external_adapter_state,
                "external_api_calls": audit_snapshot.get("external_api_calls"),
                "prepared_at": route_assignment.external_adapter_prepared_at.isoformat()
                if route_assignment.external_adapter_prepared_at
                else None,
            },
        )


def adapter_failure_reasons(
    route_assignment: RouteAssignment,
    visit: Visit,
) -> tuple[AdapterFailureReason, ...]:
    reasons: list[AdapterFailureReason] = []
    if route_assignment.id is None or route_assignment.visit_id != visit.id:
        reasons.append(
            AdapterFailureReason(
                code=ExternalAdapterFailureCode.MISSING_ROUTE_ASSIGNMENT_LINKAGE,
                message="Route assignment must be linked to the Visit being prepared.",
                metadata={
                    "route_assignment_visit_id": str(route_assignment.visit_id)
                    if route_assignment.visit_id
                    else None,
                    "visit_id": str(visit.id) if visit.id else None,
                },
            ),
        )
    if visit.visit_type == "water_emergency":
        reasons.append(
            AdapterFailureReason(
                code=ExternalAdapterFailureCode.WATER_EMERGENCY_VISIT,
                message="Water Emergency Visits require a separated external adapter path.",
            ),
        )
    already_prepared = route_assignment.external_adapter_state in {
        ExternalAdapterLifecycleState.ADAPTER_PREPARED.value,
        ExternalAdapterLifecycleState.AWAITING_EXTERNAL_EXECUTION.value,
        ExternalAdapterLifecycleState.AWAITING_EXTERNAL_CONFIRMATION.value,
    }
    if route_assignment.external_adapter_prepared_at is not None or already_prepared:
        reasons.append(
            AdapterFailureReason(
                code=ExternalAdapterFailureCode.DUPLICATE_ADAPTER_PREPARATION,
                message="External adapter payloads have already been prepared.",
            ),
        )
    if visit.status == "blocked":
        reasons.append(
            AdapterFailureReason(
                code=ExternalAdapterFailureCode.BLOCKED_VISIT,
                message="Blocked Visits cannot prepare external adapter payloads.",
            ),
        )
    if visit.status == "review_required":
        reasons.append(
            AdapterFailureReason(
                code=ExternalAdapterFailureCode.REVIEW_REQUIRED,
                message="Review-required Visits cannot prepare external adapter payloads.",
            ),
        )
    if visit.status == "archived":
        reasons.append(
            AdapterFailureReason(
                code=ExternalAdapterFailureCode.ARCHIVED_VISIT,
                message="Archived Visits cannot prepare external adapter payloads.",
            ),
        )
    if visit.status != DISPATCHED_STATUS:
        reasons.append(
            AdapterFailureReason(
                code=ExternalAdapterFailureCode.VISIT_NOT_DISPATCHED,
                message="Only dispatched Visits can prepare external adapter payloads.",
                metadata={"visit_status": visit.status},
            ),
        )
        reasons.append(
            AdapterFailureReason(
                code=ExternalAdapterFailureCode.INVALID_LIFECYCLE,
                message="Visit lifecycle must be dispatched before external adapter preparation.",
                metadata={"visit_status": visit.status},
            ),
        )
    if route_assignment.dispatch_execution_state != DISPATCHED_STATUS or (
        route_assignment.dispatched_at is None
    ):
        reasons.append(
            AdapterFailureReason(
                code=ExternalAdapterFailureCode.INTERNAL_DISPATCH_NOT_COMPLETE,
                message="Internal dispatch execution must complete before adapter preparation.",
                metadata={
                    "dispatch_execution_state": route_assignment.dispatch_execution_state,
                    "dispatched_at": route_assignment.dispatched_at.isoformat()
                    if route_assignment.dispatched_at
                    else None,
                },
            ),
        )
    if not route_assignment_authorized(route_assignment):
        reasons.append(
            AdapterFailureReason(
                code=ExternalAdapterFailureCode.UNAUTHORIZED_ROUTE_ASSIGNMENT,
                message="Only authorized Route Assignments can prepare external adapter payloads.",
            ),
        )
    return tuple(dedupe_failure_reasons(reasons))


def failed_adapter_result(
    route_assignment: RouteAssignment,
    request: AdapterExecutionRequest,
    failure_reasons: tuple[AdapterFailureReason, ...],
    timestamp: datetime,
) -> AdapterExecutionResult:
    state = ExternalAdapterLifecycleState.EXTERNAL_EXECUTION_BLOCKED
    return AdapterExecutionResult(
        succeeded=False,
        state=state,
        request=request,
        failure_reasons=failure_reasons,
        evidence=AdapterExecutionEvidence(
            adapter_execution={
                "state": state.value,
                "adapter_preparation": "blocked",
                "external_api_calls": "not_executed",
                "blocked_at": timestamp.isoformat(),
            },
            lifecycle=adapter_lifecycle_snapshot(
                previous_state=route_assignment.external_adapter_state
                or ExternalAdapterLifecycleState.INTERNAL_DISPATCH_COMPLETE.value,
                next_state=state,
                transitioned_at=timestamp,
            ),
            payloads={},
            dispatch_execution=route_assignment.dispatch_execution_snapshot or {},
            audit=adapter_audit_snapshot(route_assignment, state),
            failure_reasons=failure_reasons,
        ),
    )


def apply_adapter_preparation(
    route_assignment: RouteAssignment,
    visit: Visit,
    request: AdapterExecutionRequest,
    payloads: dict[str, dict[str, object]],
    timestamp: datetime,
) -> None:
    state = ExternalAdapterLifecycleState.AWAITING_EXTERNAL_EXECUTION
    previous_state = (
        route_assignment.external_adapter_state
        or ExternalAdapterLifecycleState.INTERNAL_DISPATCH_COMPLETE.value
    )
    route_assignment.external_adapter_state = state.value
    route_assignment.external_adapter_request_snapshot = adapter_request_snapshot(request)
    route_assignment.external_adapter_payload_snapshot = payloads
    route_assignment.external_adapter_lifecycle_snapshot = adapter_lifecycle_snapshot(
        previous_state=previous_state,
        next_state=state,
        transitioned_at=timestamp,
    )
    route_assignment.external_adapter_evidence_snapshot = {
        "adapter_preparation": "prepared",
        "external_api_calls": "not_executed",
        "target_adapters": list(EXTERNAL_ADAPTER_TARGETS),
        "dispatch_execution_state": route_assignment.dispatch_execution_state,
    }
    route_assignment.external_adapter_audit_snapshot = adapter_audit_snapshot(
        route_assignment,
        state,
    )
    route_assignment.external_adapter_prepared_at = timestamp

    metadata = dict(visit.lifecycle_metadata or {})
    metadata["external_adapter_state"] = state.value
    metadata["external_adapter_prepared_at"] = timestamp.isoformat()
    metadata["external_api_calls"] = "not_executed"
    visit.lifecycle_metadata = metadata


def route_assignment_authorized(route_assignment: RouteAssignment) -> bool:
    authorization_snapshot = route_assignment.dispatch_authorization_snapshot or {}
    execution_boundary_snapshot = route_assignment.dispatch_execution_boundary_snapshot or {}
    return bool(
        authorization_snapshot.get("authorized_for_dispatch")
        and execution_boundary_snapshot.get("authorized_for_dispatch")
    )


def adapter_execution_request(
    route_assignment: RouteAssignment,
    visit: Visit,
    timestamp: datetime,
) -> AdapterExecutionRequest:
    return AdapterExecutionRequest(
        route_assignment_id=route_assignment.id,
        visit_id=visit.id,
        work_order_id=visit.work_order_id,
        job_id=route_assignment.job_id or visit.job_id,
        technician_id=route_assignment.technician_id or visit.technician_id,
        audit_correlation_id=route_assignment.audit_correlation_id or visit.audit_correlation_id,
        target_adapters=EXTERNAL_ADAPTER_TARGETS,
        requested_at=timestamp,
    )


def adapter_request_snapshot(request: AdapterExecutionRequest) -> dict[str, object]:
    return {
        "route_assignment_id": str(request.route_assignment_id)
        if request.route_assignment_id
        else None,
        "visit_id": str(request.visit_id) if request.visit_id else None,
        "work_order_id": str(request.work_order_id) if request.work_order_id else None,
        "job_id": str(request.job_id) if request.job_id else None,
        "technician_id": str(request.technician_id) if request.technician_id else None,
        "audit_correlation_id": request.audit_correlation_id,
        "target_adapters": list(request.target_adapters),
        "requested_at": request.requested_at.isoformat(),
        "execution_mode": request.execution_mode,
    }


def external_payload_snapshot(
    route_assignment: RouteAssignment,
    visit: Visit,
    technician: Technician | None,
    timestamp: datetime,
) -> dict[str, dict[str, object]]:
    base_payload = base_payload_snapshot(route_assignment, visit, technician, timestamp)
    return {
        "fastfield": {
            **base_payload,
            "adapter": "fastfield",
            "payload_type": "future_fastfield_dispatch",
            "fastfield_user_id": technician.fastfield_user_id if technician else None,
        },
        "google_sheets": {
            **base_payload,
            "adapter": "google_sheets",
            "payload_type": "future_dispatch_sheet_row",
            "sheet_section": "standard_jobs",
        },
        "google_calendar": {
            **base_payload,
            "adapter": "google_calendar",
            "payload_type": "future_calendar_sync",
            "calendar_action": "sync_dispatch_status",
        },
        "technician_mobile": {
            **base_payload,
            "adapter": "technician_mobile",
            "payload_type": "future_mobile_visit_sync",
            "mobile_workflow": "standard_visit",
        },
    }


def base_payload_snapshot(
    route_assignment: RouteAssignment,
    visit: Visit,
    technician: Technician | None,
    timestamp: datetime,
) -> dict[str, object]:
    return {
        "execution_mode": "prepare_only",
        "external_execution": "not_executed",
        "prepared_at": timestamp.isoformat(),
        "route_assignment_id": str(route_assignment.id) if route_assignment.id else None,
        "visit_id": str(visit.id) if visit.id else None,
        "work_order_id": str(visit.work_order_id) if visit.work_order_id else None,
        "job_id": str(route_assignment.job_id or visit.job_id),
        "technician_id": str(route_assignment.technician_id or visit.technician_id)
        if route_assignment.technician_id or visit.technician_id
        else None,
        "technician_name": technician.full_name if technician else None,
        "audit_correlation_id": route_assignment.audit_correlation_id or visit.audit_correlation_id,
        "route_date": route_assignment.route_date.isoformat()
        if route_assignment.route_date
        else None,
        "route_group_key": route_assignment.route_group_key,
        "route_order": route_assignment.route_order,
        "region": route_assignment.region,
        "time_window": route_assignment.time_window,
        "scheduled_start_at": visit.scheduled_start_at.isoformat()
        if visit.scheduled_start_at
        else None,
        "scheduled_end_at": visit.scheduled_end_at.isoformat() if visit.scheduled_end_at else None,
    }


def adapter_lifecycle_snapshot(
    *,
    previous_state: str | None,
    next_state: ExternalAdapterLifecycleState,
    transitioned_at: datetime,
) -> dict[str, object]:
    return {
        "previous_state": previous_state,
        "adapter_prepared_state": ExternalAdapterLifecycleState.ADAPTER_PREPARED.value,
        "next_state": next_state.value,
        "transitioned_at": transitioned_at.isoformat(),
        "external_api_calls": "not_executed",
    }


def adapter_audit_snapshot(
    route_assignment: RouteAssignment,
    state: ExternalAdapterLifecycleState,
) -> dict[str, object]:
    action = (
        "external_dispatch_adapter.prepared"
        if state == ExternalAdapterLifecycleState.AWAITING_EXTERNAL_EXECUTION
        else "external_dispatch_adapter.blocked"
    )
    return {
        "action": action,
        "state": state.value,
        "route_assignment_id": str(route_assignment.id) if route_assignment.id else None,
        "visit_id": str(route_assignment.visit_id) if route_assignment.visit_id else None,
        "job_id": str(route_assignment.job_id) if route_assignment.job_id else None,
        "audit_correlation_id": route_assignment.audit_correlation_id,
        "external_api_calls": "not_executed",
    }


def adapter_execution_evidence(route_assignment: RouteAssignment) -> AdapterExecutionEvidence:
    return AdapterExecutionEvidence(
        adapter_execution=route_assignment.external_adapter_evidence_snapshot or {},
        lifecycle=route_assignment.external_adapter_lifecycle_snapshot or {},
        payloads=route_assignment.external_adapter_payload_snapshot or {},
        dispatch_execution=route_assignment.dispatch_execution_snapshot or {},
        audit=route_assignment.external_adapter_audit_snapshot or {},
    )


def dedupe_failure_reasons(
    reasons: list[AdapterFailureReason],
) -> tuple[AdapterFailureReason, ...]:
    deduped: list[AdapterFailureReason] = []
    seen: set[ExternalAdapterFailureCode] = set()
    for reason in reasons:
        if reason.code in seen:
            continue
        deduped.append(reason)
        seen.add(reason.code)
    return tuple(deduped)
