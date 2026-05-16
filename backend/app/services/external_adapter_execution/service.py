from collections.abc import Callable, Mapping
from datetime import UTC, datetime

from app.domain.external_adapter_execution import (
    ExecutionProviderResult,
    ExternalExecutionEvidence,
    ExternalExecutionFailureCode,
    ExternalExecutionFailureReason,
    ExternalExecutionLifecycleState,
    ExternalExecutionRequest,
    ExternalExecutionResult,
    ProviderExecutionState,
)
from app.models.audit_log import AuditLog
from app.models.route_assignment import RouteAssignment
from app.models.visit import Visit

DISPATCHED_STATUS = "dispatched"
ADAPTER_READY_STATE = "awaiting_external_execution"
DEFAULT_EXTERNAL_EXECUTION_PROVIDERS = (
    "fastfield",
    "google_sheets",
    "google_calendar",
    "technician_mobile",
)


class ExternalAdapterExecutionService:
    def __init__(self, *, now: Callable[[], datetime] | None = None) -> None:
        self.now = now or (lambda: datetime.now(UTC))

    def execute_prepared_adapters(
        self,
        route_assignment: RouteAssignment,
        *,
        visit: Visit,
        provider_outcomes: Mapping[str, ProviderExecutionState] | None = None,
    ) -> ExternalExecutionResult:
        timestamp = self.now()
        request = external_execution_request(route_assignment, visit, timestamp)
        failure_reasons = external_execution_failure_reasons(route_assignment, visit)
        if failure_reasons:
            return failed_external_execution_result(
                route_assignment,
                request,
                failure_reasons,
            )

        outcomes = dict(provider_outcomes or {})
        provider_results = provider_execution_results(
            route_assignment,
            request,
            outcomes,
            timestamp,
        )
        if any(
            result.state == ProviderExecutionState.FAILED for result in provider_results.values()
        ):
            apply_external_execution_failure(
                route_assignment,
                visit,
                request,
                provider_results,
                timestamp,
            )
            return ExternalExecutionResult(
                succeeded=False,
                state=ExternalExecutionLifecycleState.EXTERNAL_EXECUTION_FAILED,
                request=request,
                provider_results=provider_results,
                evidence=external_execution_evidence(route_assignment),
            )

        if any(
            result.state == ProviderExecutionState.RECONCILIATION_REQUIRED
            for result in provider_results.values()
        ):
            apply_external_execution_reconciliation_required(
                route_assignment,
                visit,
                request,
                provider_results,
                timestamp,
            )
            return ExternalExecutionResult(
                succeeded=False,
                state=ExternalExecutionLifecycleState.RECONCILIATION_REQUIRED,
                request=request,
                provider_results=provider_results,
                evidence=external_execution_evidence(route_assignment),
            )

        apply_external_execution_success(
            route_assignment,
            visit,
            request,
            provider_results,
            timestamp,
        )
        return ExternalExecutionResult(
            succeeded=True,
            state=ExternalExecutionLifecycleState.AWAITING_EXTERNAL_CONFIRMATION,
            request=request,
            provider_results=provider_results,
            evidence=external_execution_evidence(route_assignment),
        )

    @staticmethod
    def build_external_execution_audit_log(route_assignment: RouteAssignment) -> AuditLog:
        audit_snapshot = route_assignment.external_execution_audit_snapshot or {}
        return AuditLog(
            action=audit_snapshot.get("action") or "external_adapter_execution.recorded",
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
                "external_execution_state": route_assignment.external_execution_state,
                "external_api_calls": audit_snapshot.get("external_api_calls"),
                "completed_at": route_assignment.external_execution_completed_at.isoformat()
                if route_assignment.external_execution_completed_at
                else None,
            },
        )


def external_execution_failure_reasons(
    route_assignment: RouteAssignment,
    visit: Visit,
) -> tuple[ExternalExecutionFailureReason, ...]:
    reasons: list[ExternalExecutionFailureReason] = []
    if route_assignment.id is None or route_assignment.visit_id != visit.id:
        reasons.append(
            ExternalExecutionFailureReason(
                code=ExternalExecutionFailureCode.MISSING_ROUTE_ASSIGNMENT_LINKAGE,
                message="Route assignment must be linked to the Visit being executed.",
            ),
        )
    if visit.visit_type == "water_emergency":
        reasons.append(
            ExternalExecutionFailureReason(
                code=ExternalExecutionFailureCode.WATER_EMERGENCY_VISIT,
                message="Water Emergency Visits require a separated external execution path.",
            ),
        )
    if (
        route_assignment.external_execution_started_at is not None
        or route_assignment.external_execution_state
        in {
            ExternalExecutionLifecycleState.AWAITING_EXTERNAL_CONFIRMATION.value,
            ExternalExecutionLifecycleState.EXTERNAL_EXECUTION_FAILED.value,
            ExternalExecutionLifecycleState.RECONCILIATION_REQUIRED.value,
        }
        or route_assignment.external_adapter_state
        in {
            ExternalExecutionLifecycleState.AWAITING_EXTERNAL_CONFIRMATION.value,
            ExternalExecutionLifecycleState.EXTERNAL_EXECUTION_FAILED.value,
            ExternalExecutionLifecycleState.RECONCILIATION_REQUIRED.value,
        }
    ):
        reasons.append(
            ExternalExecutionFailureReason(
                code=ExternalExecutionFailureCode.DUPLICATE_EXTERNAL_EXECUTION,
                message="External adapter execution has already been attempted.",
            ),
        )
    if visit.status == "blocked":
        reasons.append(
            ExternalExecutionFailureReason(
                code=ExternalExecutionFailureCode.BLOCKED_VISIT,
                message="Blocked Visits cannot execute external adapters.",
            ),
        )
    if visit.status == "review_required":
        reasons.append(
            ExternalExecutionFailureReason(
                code=ExternalExecutionFailureCode.REVIEW_REQUIRED,
                message="Review-required Visits cannot execute external adapters.",
            ),
        )
    if visit.status == "archived":
        reasons.append(
            ExternalExecutionFailureReason(
                code=ExternalExecutionFailureCode.ARCHIVED_VISIT,
                message="Archived Visits cannot execute external adapters.",
            ),
        )
    if visit.status != DISPATCHED_STATUS:
        reasons.append(
            ExternalExecutionFailureReason(
                code=ExternalExecutionFailureCode.INVALID_LIFECYCLE,
                message="Visit lifecycle must remain dispatched for external execution.",
                metadata={"visit_status": visit.status},
            ),
        )
    if route_assignment.external_adapter_state != ADAPTER_READY_STATE:
        reasons.append(
            ExternalExecutionFailureReason(
                code=ExternalExecutionFailureCode.ADAPTER_NOT_PREPARED,
                message="Route assignment must be awaiting external execution.",
                metadata={"external_adapter_state": route_assignment.external_adapter_state},
            ),
        )
        reasons.append(
            ExternalExecutionFailureReason(
                code=ExternalExecutionFailureCode.INVALID_LIFECYCLE,
                message="External adapter lifecycle is not ready for controlled execution.",
                metadata={"external_adapter_state": route_assignment.external_adapter_state},
            ),
        )
    payloads = route_assignment.external_adapter_payload_snapshot or {}
    missing_payloads = [
        provider for provider in DEFAULT_EXTERNAL_EXECUTION_PROVIDERS if provider not in payloads
    ]
    if missing_payloads:
        reasons.append(
            ExternalExecutionFailureReason(
                code=ExternalExecutionFailureCode.MISSING_PROVIDER_PAYLOAD,
                message="Prepared adapter payloads are required before external execution.",
                metadata={"missing_providers": missing_payloads},
            ),
        )
    if not route_assignment_authorized(route_assignment):
        reasons.append(
            ExternalExecutionFailureReason(
                code=ExternalExecutionFailureCode.UNAUTHORIZED_EXECUTION,
                message="Only authorized Route Assignments can execute external adapters.",
            ),
        )
    return tuple(dedupe_failure_reasons(reasons))


def failed_external_execution_result(
    route_assignment: RouteAssignment,
    request: ExternalExecutionRequest,
    failure_reasons: tuple[ExternalExecutionFailureReason, ...],
) -> ExternalExecutionResult:
    state = ExternalExecutionLifecycleState.EXTERNAL_EXECUTION_FAILED
    return ExternalExecutionResult(
        succeeded=False,
        state=state,
        request=request,
        provider_results={},
        failure_reasons=failure_reasons,
        evidence=ExternalExecutionEvidence(
            execution=route_assignment.external_execution_evidence_snapshot or {},
            lifecycle=route_assignment.external_execution_lifecycle_snapshot or {},
            providers=route_assignment.external_execution_provider_snapshot or {},
            failure=route_assignment.external_execution_failure_snapshot or {},
            adapter=route_assignment.external_adapter_evidence_snapshot or {},
            audit=external_execution_audit_snapshot(route_assignment, state),
            failure_reasons=failure_reasons,
        ),
    )


def apply_external_execution_success(
    route_assignment: RouteAssignment,
    visit: Visit,
    request: ExternalExecutionRequest,
    provider_results: dict[str, ExecutionProviderResult],
    timestamp: datetime,
) -> None:
    state = ExternalExecutionLifecycleState.AWAITING_EXTERNAL_CONFIRMATION
    previous_state = route_assignment.external_adapter_state
    route_assignment.external_execution_state = state.value
    route_assignment.external_adapter_state = state.value
    route_assignment.external_execution_request_snapshot = external_execution_request_snapshot(
        request,
    )
    route_assignment.external_execution_provider_snapshot = provider_results_snapshot(
        provider_results,
    )
    route_assignment.external_execution_evidence_snapshot = {
        "execution_boundary": "simulated_controlled_execution",
        "state": state.value,
        "provider_count": len(provider_results),
        "external_api_calls": "not_executed",
        "real_vendor_execution": "not_executed",
        "awaiting_external_confirmation": True,
        "provider_results": {
            provider: result.state.value for provider, result in provider_results.items()
        },
    }
    route_assignment.external_execution_lifecycle_snapshot = external_execution_lifecycle_snapshot(
        previous_state=previous_state,
        next_state=state,
        transitioned_at=timestamp,
    )
    route_assignment.external_execution_audit_snapshot = external_execution_audit_snapshot(
        route_assignment,
        state,
    )
    route_assignment.external_execution_started_at = timestamp
    route_assignment.external_execution_completed_at = timestamp
    update_visit_execution_metadata(visit, state, timestamp)


def apply_external_execution_failure(
    route_assignment: RouteAssignment,
    visit: Visit,
    request: ExternalExecutionRequest,
    provider_results: dict[str, ExecutionProviderResult],
    timestamp: datetime,
) -> None:
    state = ExternalExecutionLifecycleState.EXTERNAL_EXECUTION_FAILED
    previous_state = route_assignment.external_adapter_state
    route_assignment.external_execution_state = state.value
    route_assignment.external_adapter_state = state.value
    route_assignment.external_execution_request_snapshot = external_execution_request_snapshot(
        request,
    )
    route_assignment.external_execution_provider_snapshot = provider_results_snapshot(
        provider_results,
    )
    route_assignment.external_execution_evidence_snapshot = {
        "execution_boundary": "simulated_controlled_execution",
        "state": state.value,
        "provider_count": len(provider_results),
        "external_api_calls": "not_executed",
        "real_vendor_execution": "not_executed",
        "automatic_retry": "not_executed",
        "provider_results": {
            provider: result.state.value for provider, result in provider_results.items()
        },
    }
    route_assignment.external_execution_failure_snapshot = {
        "state": state.value,
        "failed_providers": [
            provider
            for provider, result in provider_results.items()
            if result.state == ProviderExecutionState.FAILED
        ],
        "automatic_retry": "not_executed",
        "external_api_calls": "not_executed",
        "real_vendor_execution": "not_executed",
        "failed_at": timestamp.isoformat(),
    }
    route_assignment.external_execution_lifecycle_snapshot = external_execution_lifecycle_snapshot(
        previous_state=previous_state,
        next_state=state,
        transitioned_at=timestamp,
    )
    route_assignment.external_execution_audit_snapshot = external_execution_audit_snapshot(
        route_assignment,
        state,
    )
    route_assignment.external_execution_started_at = timestamp
    route_assignment.external_execution_failed_at = timestamp
    route_assignment.external_adapter_failed_at = timestamp
    update_visit_execution_metadata(visit, state, timestamp)


def apply_external_execution_reconciliation_required(
    route_assignment: RouteAssignment,
    visit: Visit,
    request: ExternalExecutionRequest,
    provider_results: dict[str, ExecutionProviderResult],
    timestamp: datetime,
) -> None:
    state = ExternalExecutionLifecycleState.RECONCILIATION_REQUIRED
    previous_state = route_assignment.external_adapter_state
    route_assignment.external_execution_state = state.value
    route_assignment.external_adapter_state = state.value
    route_assignment.external_execution_request_snapshot = external_execution_request_snapshot(
        request,
    )
    route_assignment.external_execution_provider_snapshot = provider_results_snapshot(
        provider_results,
    )
    route_assignment.external_execution_evidence_snapshot = {
        "execution_boundary": "simulated_controlled_execution",
        "state": state.value,
        "provider_count": len(provider_results),
        "external_api_calls": "not_executed",
        "real_vendor_execution": "not_executed",
        "automatic_reconciliation": "not_executed",
        "provider_results": {
            provider: result.state.value for provider, result in provider_results.items()
        },
    }
    route_assignment.external_execution_failure_snapshot = {
        "state": state.value,
        "reconciliation_required": True,
        "reconciliation_execution": "not_executed",
        "external_api_calls": "not_executed",
        "real_vendor_execution": "not_executed",
        "prepared_at": timestamp.isoformat(),
    }
    route_assignment.external_execution_lifecycle_snapshot = external_execution_lifecycle_snapshot(
        previous_state=previous_state,
        next_state=state,
        transitioned_at=timestamp,
    )
    route_assignment.external_execution_audit_snapshot = external_execution_audit_snapshot(
        route_assignment,
        state,
    )
    route_assignment.external_execution_started_at = timestamp
    update_visit_execution_metadata(visit, state, timestamp)


def provider_execution_results(
    route_assignment: RouteAssignment,
    request: ExternalExecutionRequest,
    provider_outcomes: Mapping[str, ProviderExecutionState],
    timestamp: datetime,
) -> dict[str, ExecutionProviderResult]:
    payloads = route_assignment.external_adapter_payload_snapshot or {}
    results: dict[str, ExecutionProviderResult] = {}
    for provider in request.providers:
        state = provider_outcomes.get(provider, ProviderExecutionState.COMPLETED)
        correlation_id = provider_correlation_id(request, provider, timestamp)
        results[provider] = ExecutionProviderResult(
            provider=provider,
            state=state,
            correlation_id=correlation_id,
            evidence={
                "provider": provider,
                "state": state.value,
                "correlation_id": correlation_id,
                "audit_correlation_id": request.audit_correlation_id,
                "route_assignment_id": str(request.route_assignment_id)
                if request.route_assignment_id
                else None,
                "visit_id": str(request.visit_id) if request.visit_id else None,
                "payload_snapshot": payloads.get(provider, {}),
                "external_api_calls": "not_executed",
                "real_vendor_execution": "not_executed",
                "executed_at": timestamp.isoformat(),
            },
        )
    return results


def external_execution_request(
    route_assignment: RouteAssignment,
    visit: Visit,
    timestamp: datetime,
) -> ExternalExecutionRequest:
    payloads = route_assignment.external_adapter_payload_snapshot or {}
    providers = tuple(
        provider for provider in DEFAULT_EXTERNAL_EXECUTION_PROVIDERS if provider in payloads
    )
    if not providers:
        providers = DEFAULT_EXTERNAL_EXECUTION_PROVIDERS
    return ExternalExecutionRequest(
        route_assignment_id=route_assignment.id,
        visit_id=visit.id,
        work_order_id=visit.work_order_id,
        job_id=route_assignment.job_id or visit.job_id,
        technician_id=route_assignment.technician_id or visit.technician_id,
        audit_correlation_id=route_assignment.audit_correlation_id or visit.audit_correlation_id,
        providers=providers,
        requested_at=timestamp,
    )


def external_execution_request_snapshot(request: ExternalExecutionRequest) -> dict[str, object]:
    return {
        "route_assignment_id": str(request.route_assignment_id)
        if request.route_assignment_id
        else None,
        "visit_id": str(request.visit_id) if request.visit_id else None,
        "work_order_id": str(request.work_order_id) if request.work_order_id else None,
        "job_id": str(request.job_id) if request.job_id else None,
        "technician_id": str(request.technician_id) if request.technician_id else None,
        "audit_correlation_id": request.audit_correlation_id,
        "providers": list(request.providers),
        "requested_at": request.requested_at.isoformat(),
        "execution_mode": request.execution_mode,
        "external_api_calls": "not_executed",
    }


def provider_results_snapshot(
    provider_results: dict[str, ExecutionProviderResult],
) -> dict[str, dict[str, object]]:
    return {
        provider: {
            "provider": result.provider,
            "state": result.state.value,
            "correlation_id": result.correlation_id,
            "audit_correlation_id": result.evidence.get("audit_correlation_id"),
            "route_assignment_id": result.evidence.get("route_assignment_id"),
            "visit_id": result.evidence.get("visit_id"),
            "payload_snapshot": result.evidence.get("payload_snapshot"),
            "external_api_calls": "not_executed",
            "real_vendor_execution": "not_executed",
        }
        for provider, result in provider_results.items()
    }


def external_execution_lifecycle_snapshot(
    *,
    previous_state: str | None,
    next_state: ExternalExecutionLifecycleState,
    transitioned_at: datetime,
) -> dict[str, object]:
    return {
        "previous_state": previous_state,
        "started_state": ExternalExecutionLifecycleState.EXTERNAL_EXECUTION_STARTED.value,
        "completed_state": ExternalExecutionLifecycleState.EXTERNAL_EXECUTION_COMPLETED.value,
        "next_state": next_state.value,
        "transitioned_at": transitioned_at.isoformat(),
        "external_api_calls": "not_executed",
        "automatic_retry": "not_executed",
        "immutable_audit_continuity": "preserved",
    }


def external_execution_audit_snapshot(
    route_assignment: RouteAssignment,
    state: ExternalExecutionLifecycleState,
) -> dict[str, object]:
    action_by_state = {
        ExternalExecutionLifecycleState.AWAITING_EXTERNAL_CONFIRMATION: (
            "external_adapter_execution.completed"
        ),
        ExternalExecutionLifecycleState.EXTERNAL_EXECUTION_FAILED: (
            "external_adapter_execution.failed"
        ),
        ExternalExecutionLifecycleState.RECONCILIATION_REQUIRED: (
            "external_adapter_execution.reconciliation_required"
        ),
    }
    return {
        "action": action_by_state.get(state, "external_adapter_execution.blocked"),
        "state": state.value,
        "route_assignment_id": str(route_assignment.id) if route_assignment.id else None,
        "visit_id": str(route_assignment.visit_id) if route_assignment.visit_id else None,
        "job_id": str(route_assignment.job_id) if route_assignment.job_id else None,
        "audit_correlation_id": route_assignment.audit_correlation_id,
        "external_api_calls": "not_executed",
        "immutable_audit_continuity": "preserved",
    }


def update_visit_execution_metadata(
    visit: Visit,
    state: ExternalExecutionLifecycleState,
    timestamp: datetime,
) -> None:
    metadata = dict(visit.lifecycle_metadata or {})
    metadata["external_execution_state"] = state.value
    metadata["external_execution_updated_at"] = timestamp.isoformat()
    metadata["external_api_calls"] = "not_executed"
    visit.lifecycle_metadata = metadata


def external_execution_evidence(route_assignment: RouteAssignment) -> ExternalExecutionEvidence:
    return ExternalExecutionEvidence(
        execution=route_assignment.external_execution_evidence_snapshot or {},
        lifecycle=route_assignment.external_execution_lifecycle_snapshot or {},
        providers=route_assignment.external_execution_provider_snapshot or {},
        failure=route_assignment.external_execution_failure_snapshot or {},
        adapter=route_assignment.external_adapter_evidence_snapshot or {},
        audit=route_assignment.external_execution_audit_snapshot or {},
    )


def route_assignment_authorized(route_assignment: RouteAssignment) -> bool:
    authorization_snapshot = route_assignment.dispatch_authorization_snapshot or {}
    execution_boundary_snapshot = route_assignment.dispatch_execution_boundary_snapshot or {}
    return bool(
        authorization_snapshot.get("authorized_for_dispatch")
        and execution_boundary_snapshot.get("authorized_for_dispatch")
    )


def provider_correlation_id(
    request: ExternalExecutionRequest,
    provider: str,
    timestamp: datetime,
) -> str:
    return f"{request.audit_correlation_id}:{provider}:{timestamp.isoformat()}"


def dedupe_failure_reasons(
    reasons: list[ExternalExecutionFailureReason],
) -> tuple[ExternalExecutionFailureReason, ...]:
    deduped: list[ExternalExecutionFailureReason] = []
    seen: set[ExternalExecutionFailureCode] = set()
    for reason in reasons:
        if reason.code in seen:
            continue
        deduped.append(reason)
        seen.add(reason.code)
    return tuple(deduped)
