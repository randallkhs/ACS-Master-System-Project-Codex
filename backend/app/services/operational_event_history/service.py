from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.operational_event_history import (
    EventTimelineEntry,
    OperationalEventEvidence,
    OperationalEventFailureCode,
    OperationalEventFailureReason,
    OperationalEventResult,
    OperationalEventState,
    OperationalEventTraceability,
)
from app.models.operational_event_record import OperationalEventRecord
from app.models.route_assignment import RouteAssignment
from app.models.visit import Visit
from app.repositories.operational_event_records import OperationalEventRecordRepository


class OperationalEventHistoryService:
    def __init__(
        self,
        repository: OperationalEventRecordRepository,
        *,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self.repository = repository
        self.now = now or (lambda: datetime.now(UTC))

    def record_lifecycle_transition(
        self,
        *,
        event_type: str,
        entity_type: str,
        entity_id: UUID | None,
        previous_state: str | None,
        new_state: str | None,
        event_state: OperationalEventState,
        audit_correlation_id: str | None,
        route_assignment_id: UUID | None = None,
        visit_id: UUID | None = None,
        work_order_id: UUID | None = None,
        job_id: UUID | None = None,
        technician_id: UUID | None = None,
        event_snapshot: dict[str, object] | None = None,
        transition_evidence: dict[str, object] | None = None,
        retry_recovery_snapshot: dict[str, object] | None = None,
        reconciliation_snapshot: dict[str, object] | None = None,
        audit_snapshot: dict[str, object] | None = None,
    ) -> OperationalEventResult:
        timestamp = self.now()
        traceability = OperationalEventTraceability(
            entity_type=entity_type,
            entity_id=entity_id,
            route_assignment_id=route_assignment_id,
            visit_id=visit_id,
            work_order_id=work_order_id,
            job_id=job_id,
            technician_id=technician_id,
            audit_correlation_id=audit_correlation_id,
        )
        failure_reasons = event_failure_reasons(
            entity_type=entity_type,
            entity_id=entity_id,
            previous_state=previous_state,
            new_state=new_state,
            audit_correlation_id=audit_correlation_id,
        )
        if failure_reasons:
            return failed_event_result(
                state=OperationalEventState.BLOCKED,
                traceability=traceability,
                failure_reasons=failure_reasons,
            )

        event_fingerprint = build_event_fingerprint(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            previous_state=previous_state,
            new_state=new_state,
            audit_correlation_id=audit_correlation_id,
        )
        existing = self.repository.get_by_event_fingerprint(event_fingerprint)
        if existing is not None:
            reason = OperationalEventFailureReason(
                code=OperationalEventFailureCode.DUPLICATE_EVENT,
                message="An immutable operational event already exists for this transition.",
                metadata={"event_record_id": str(existing.id)},
            )
            return failed_event_result(
                state=OperationalEventState.BLOCKED,
                traceability=traceability,
                failure_reasons=(reason,),
            )

        transition_snapshot = transition_snapshot_for_event(
            event_type=event_type,
            event_state=event_state,
            previous_state=previous_state,
            new_state=new_state,
            occurred_at=timestamp,
            transition_evidence=transition_evidence,
        )
        record = OperationalEventRecord(
            id=uuid4(),
            occurred_at=timestamp,
            recorded_at=timestamp,
            event_type=event_type,
            event_state=event_state.value,
            entity_type=entity_type,
            entity_id=entity_id,
            route_assignment_id=route_assignment_id,
            visit_id=visit_id,
            work_order_id=work_order_id,
            job_id=job_id,
            technician_id=technician_id,
            audit_correlation_id=audit_correlation_id,
            previous_state=previous_state,
            new_state=new_state,
            event_fingerprint=event_fingerprint,
            is_immutable=True,
            event_snapshot=event_snapshot or {},
            transition_snapshot=transition_snapshot,
            immutable_evidence_snapshot=immutable_evidence_snapshot(
                audit_correlation_id=audit_correlation_id,
                occurred_at=timestamp,
            ),
            retry_recovery_snapshot=retry_recovery_snapshot or {},
            reconciliation_snapshot=reconciliation_snapshot or {},
            audit_snapshot=audit_snapshot or {},
        )
        self.repository.add(record)
        return OperationalEventResult(
            succeeded=True,
            state=event_state,
            event_record=record,
            traceability=traceability,
            evidence=event_evidence(record),
        )

    def record_dispatch_execution(
        self,
        route_assignment: RouteAssignment,
        *,
        visit: Visit,
    ) -> OperationalEventResult:
        lifecycle = route_assignment.dispatch_lifecycle_snapshot or {}
        return self.record_lifecycle_transition(
            event_type="operational_dispatch.executed",
            entity_type="route_assignment",
            entity_id=route_assignment.id,
            route_assignment_id=route_assignment.id,
            visit_id=visit.id,
            work_order_id=visit.work_order_id,
            job_id=route_assignment.job_id or visit.job_id,
            technician_id=route_assignment.technician_id or visit.technician_id,
            previous_state=string_value(lifecycle.get("previous_state")),
            new_state=string_value(lifecycle.get("new_state") or lifecycle.get("next_state")),
            event_state=OperationalEventState.DISPATCHED,
            audit_correlation_id=route_assignment.audit_correlation_id
            or visit.audit_correlation_id,
            event_snapshot=route_assignment.dispatch_execution_snapshot,
            transition_evidence=lifecycle,
            audit_snapshot=route_assignment.dispatch_audit_snapshot,
        )

    def record_adapter_preparation(
        self,
        route_assignment: RouteAssignment,
        *,
        visit: Visit,
    ) -> OperationalEventResult:
        lifecycle = route_assignment.external_adapter_lifecycle_snapshot or {}
        return self.record_lifecycle_transition(
            event_type="external_dispatch_adapter.prepared",
            entity_type="route_assignment",
            entity_id=route_assignment.id,
            route_assignment_id=route_assignment.id,
            visit_id=visit.id,
            work_order_id=visit.work_order_id,
            job_id=route_assignment.job_id or visit.job_id,
            technician_id=route_assignment.technician_id or visit.technician_id,
            previous_state=string_value(lifecycle.get("previous_state")),
            new_state=string_value(
                lifecycle.get("new_state")
                or lifecycle.get("next_state")
                or route_assignment.external_adapter_state,
            ),
            event_state=OperationalEventState.TRANSITIONED,
            audit_correlation_id=route_assignment.audit_correlation_id
            or visit.audit_correlation_id,
            event_snapshot=route_assignment.external_adapter_evidence_snapshot,
            transition_evidence=lifecycle,
            audit_snapshot=route_assignment.external_adapter_audit_snapshot,
        )

    def record_confirmation_recovery(
        self,
        route_assignment: RouteAssignment,
        *,
        visit: Visit,
    ) -> OperationalEventResult:
        confirmation_state = route_assignment.external_confirmation_state
        event_state = confirmation_event_state(confirmation_state)
        traceability = OperationalEventTraceability(
            entity_type="route_assignment",
            entity_id=route_assignment.id,
            route_assignment_id=route_assignment.id,
            visit_id=visit.id,
            work_order_id=visit.work_order_id,
            job_id=route_assignment.job_id or visit.job_id,
            technician_id=route_assignment.technician_id or visit.technician_id,
            audit_correlation_id=route_assignment.audit_correlation_id
            or visit.audit_correlation_id,
        )
        if event_state is None:
            reason = OperationalEventFailureReason(
                code=OperationalEventFailureCode.UNSUPPORTED_CONFIRMATION_STATE,
                message="External confirmation state is not supported by event history.",
                metadata={"external_confirmation_state": confirmation_state},
            )
            return failed_event_result(
                state=OperationalEventState.BLOCKED,
                traceability=traceability,
                failure_reasons=(reason,),
            )

        lifecycle = route_assignment.external_confirmation_lifecycle_snapshot or {}
        return self.record_lifecycle_transition(
            event_type=confirmation_event_type(event_state),
            entity_type="route_assignment",
            entity_id=route_assignment.id,
            route_assignment_id=route_assignment.id,
            visit_id=visit.id,
            work_order_id=visit.work_order_id,
            job_id=route_assignment.job_id or visit.job_id,
            technician_id=route_assignment.technician_id or visit.technician_id,
            previous_state=string_value(lifecycle.get("previous_state"))
            or confirmation_previous_state(event_state),
            new_state=confirmation_state,
            event_state=event_state,
            audit_correlation_id=traceability.audit_correlation_id,
            event_snapshot=confirmation_event_snapshot(route_assignment, event_state),
            transition_evidence=lifecycle,
            retry_recovery_snapshot=route_assignment.retry_preparation_snapshot,
            reconciliation_snapshot=route_assignment.reconciliation_snapshot,
            audit_snapshot=route_assignment.external_confirmation_audit_snapshot,
        )

    def route_assignment_timeline(
        self,
        route_assignment_id: UUID,
    ) -> tuple[EventTimelineEntry, ...]:
        return build_timeline_entries(
            self.repository.list_for_route_assignment(route_assignment_id),
        )

    def visit_timeline(self, visit_id: UUID) -> tuple[EventTimelineEntry, ...]:
        return build_timeline_entries(self.repository.list_for_visit(visit_id))


def event_failure_reasons(
    *,
    entity_type: str,
    entity_id: UUID | None,
    previous_state: str | None,
    new_state: str | None,
    audit_correlation_id: str | None,
) -> tuple[OperationalEventFailureReason, ...]:
    reasons: list[OperationalEventFailureReason] = []
    if not entity_type or entity_id is None:
        reasons.append(
            OperationalEventFailureReason(
                code=OperationalEventFailureCode.MISSING_ENTITY_LINKAGE,
                message="Operational event history requires a durable entity linkage.",
            ),
        )
    if not audit_correlation_id:
        reasons.append(
            OperationalEventFailureReason(
                code=OperationalEventFailureCode.MISSING_AUDIT_CORRELATION,
                message="Operational event history requires audit correlation continuity.",
            ),
        )
    if not previous_state or not new_state:
        reasons.append(
            OperationalEventFailureReason(
                code=OperationalEventFailureCode.MISSING_TRANSITION_STATE,
                message="Operational event history requires previous and new lifecycle states.",
            ),
        )
    if previous_state and new_state and previous_state == new_state:
        reasons.append(
            OperationalEventFailureReason(
                code=OperationalEventFailureCode.INVALID_TRANSITION,
                message="Operational event history does not record hidden no-op transitions.",
                metadata={"state": previous_state},
            ),
        )
    return tuple(dedupe_failure_reasons(reasons))


def failed_event_result(
    *,
    state: OperationalEventState,
    traceability: OperationalEventTraceability,
    failure_reasons: tuple[OperationalEventFailureReason, ...],
) -> OperationalEventResult:
    return OperationalEventResult(
        succeeded=False,
        state=state,
        traceability=traceability,
        failure_reasons=failure_reasons,
        evidence=OperationalEventEvidence(
            event={},
            transition={},
            immutable={},
            retry_recovery={},
            reconciliation={},
            audit={},
            failure_reasons=failure_reasons,
        ),
    )


def build_event_fingerprint(
    *,
    event_type: str,
    entity_type: str,
    entity_id: UUID | None,
    previous_state: str | None,
    new_state: str | None,
    audit_correlation_id: str | None,
) -> str:
    return "|".join(
        (
            event_type,
            entity_type,
            str(entity_id),
            str(previous_state),
            str(new_state),
            str(audit_correlation_id),
        ),
    )


def transition_snapshot_for_event(
    *,
    event_type: str,
    event_state: OperationalEventState,
    previous_state: str | None,
    new_state: str | None,
    occurred_at: datetime,
    transition_evidence: dict[str, object] | None,
) -> dict[str, object]:
    return {
        "event_type": event_type,
        "event_state": event_state.value,
        "previous_state": previous_state,
        "new_state": new_state,
        "next_state": new_state,
        "occurred_at": occurred_at.isoformat(),
        "hidden_transition": "not_permitted",
        "transition": transition_evidence or {},
    }


def immutable_evidence_snapshot(
    *,
    audit_correlation_id: str | None,
    occurred_at: datetime,
) -> dict[str, object]:
    return {
        "event_history": "append_only",
        "immutable": True,
        "mutation_allowed": False,
        "audit_correlation_id": audit_correlation_id,
        "recorded_at": occurred_at.isoformat(),
        "external_api_calls": "not_executed",
        "ai_authority": "not_used",
    }


def event_evidence(record: OperationalEventRecord) -> OperationalEventEvidence:
    return OperationalEventEvidence(
        event=record.event_snapshot or {},
        transition=(record.transition_snapshot or {}).get("transition", {}),
        immutable=record.immutable_evidence_snapshot or {},
        retry_recovery=record.retry_recovery_snapshot or {},
        reconciliation=record.reconciliation_snapshot or {},
        audit=record.audit_snapshot or {},
    )


def confirmation_event_state(
    confirmation_state: str | None,
) -> OperationalEventState | None:
    state_map = {
        "externally_confirmed": OperationalEventState.EXTERNALLY_CONFIRMED,
        "external_confirmation_failed": OperationalEventState.BLOCKED,
        "awaiting_retry": OperationalEventState.RETRY_PREPARED,
        "reconciliation_required": OperationalEventState.RECONCILIATION_REQUIRED,
    }
    return state_map.get(confirmation_state)


def confirmation_event_type(event_state: OperationalEventState) -> str:
    event_type_by_state = {
        OperationalEventState.EXTERNALLY_CONFIRMED: "external_execution.confirmed",
        OperationalEventState.BLOCKED: "external_execution.confirmation_failed",
        OperationalEventState.RETRY_PREPARED: "external_execution.retry_prepared",
        OperationalEventState.RECONCILIATION_REQUIRED: (
            "external_execution.reconciliation_required"
        ),
    }
    return event_type_by_state[event_state]


def confirmation_previous_state(event_state: OperationalEventState) -> str:
    if event_state == OperationalEventState.RETRY_PREPARED:
        return "external_confirmation_failed"
    return "awaiting_external_confirmation"


def confirmation_event_snapshot(
    route_assignment: RouteAssignment,
    event_state: OperationalEventState,
) -> dict[str, object]:
    if event_state == OperationalEventState.EXTERNALLY_CONFIRMED:
        return route_assignment.external_confirmation_snapshot or {}
    if event_state == OperationalEventState.RETRY_PREPARED:
        return route_assignment.retry_preparation_snapshot or {}
    if event_state == OperationalEventState.RECONCILIATION_REQUIRED:
        return route_assignment.reconciliation_snapshot or {}
    return route_assignment.external_failure_snapshot or {}


def build_timeline_entries(
    records: Sequence[OperationalEventRecord],
) -> tuple[EventTimelineEntry, ...]:
    ordered = sorted(
        records,
        key=lambda record: (
            record.occurred_at,
            record.recorded_at,
            record.event_type,
            str(record.id),
        ),
    )
    return tuple(
        EventTimelineEntry(
            sequence=index,
            event_type=record.event_type,
            event_state=record.event_state,
            occurred_at=record.occurred_at,
            entity_type=record.entity_type,
            entity_id=record.entity_id,
            route_assignment_id=record.route_assignment_id,
            visit_id=record.visit_id,
            audit_correlation_id=record.audit_correlation_id,
            previous_state=record.previous_state,
            new_state=record.new_state,
            event_snapshot=record.event_snapshot or {},
        )
        for index, record in enumerate(ordered, start=1)
    )


def string_value(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def dedupe_failure_reasons(
    reasons: list[OperationalEventFailureReason],
) -> tuple[OperationalEventFailureReason, ...]:
    deduped: list[OperationalEventFailureReason] = []
    seen: set[OperationalEventFailureCode] = set()
    for reason in reasons:
        if reason.code in seen:
            continue
        deduped.append(reason)
        seen.add(reason.code)
    return tuple(deduped)
