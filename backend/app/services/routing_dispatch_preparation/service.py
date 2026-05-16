from collections.abc import Callable
from datetime import UTC, datetime

from app.domain.routing_dispatch_preparation import (
    RoutingDispatchBlockerCode,
    RoutingDispatchEligibility,
    RoutingDispatchEvidence,
    RoutingDispatchLifecycleState,
    RoutingDispatchPreparationResult,
    RoutingDispatchTraceability,
    RoutingReadiness,
    TechnicianReadiness,
    VisitDispatchReadiness,
)
from app.models.audit_log import AuditLog
from app.models.technician import Technician
from app.models.visit import Visit

ROUTING_PREPARABLE_STATES = {
    "awaiting_routing",
    "assignment_ready",
    "scheduling_ready",
    "routing_ready",
    "dispatch_ready",
}

HARD_BLOCKER_CODES = {
    RoutingDispatchBlockerCode.BLOCKED_VISIT,
    RoutingDispatchBlockerCode.REVIEW_REQUIRED,
    RoutingDispatchBlockerCode.WATER_EMERGENCY_VISIT,
    RoutingDispatchBlockerCode.ARCHIVED_VISIT,
    RoutingDispatchBlockerCode.INVALID_LIFECYCLE,
    RoutingDispatchBlockerCode.MISSING_VISIT_LINKAGE,
}


class RoutingDispatchPreparationService:
    def __init__(self, *, now: Callable[[], datetime] | None = None) -> None:
        self.now = now or (lambda: datetime.now(UTC))

    def prepare_visit(
        self,
        visit: Visit,
        *,
        technician: Technician | None = None,
    ) -> RoutingDispatchPreparationResult:
        timestamp = self.now()
        visit_blockers = visit_blocker_codes(visit)
        assignment_ready = assignment_is_ready(visit)
        scheduling_ready = scheduling_is_ready(visit)
        routing_blockers = routing_blockers_for(
            visit_blockers=visit_blockers,
            assignment_ready=assignment_ready,
            scheduling_ready=scheduling_ready,
        )
        routing_ready = not routing_blockers
        technician_readiness = technician_readiness_for(visit, technician)
        dispatch_blockers = dispatch_blockers_for(
            visit_blockers=visit_blockers,
            routing_ready=routing_ready,
            technician_readiness=technician_readiness,
            visit=visit,
        )
        dispatch_eligible = not dispatch_blockers
        lifecycle_state = lifecycle_state_for(
            visit_blockers=visit_blockers,
            routing_ready=routing_ready,
            dispatch_eligible=dispatch_eligible,
        )

        routing_readiness = RoutingReadiness(
            ready=routing_ready,
            schedule_window=preferred_time_window(visit),
            service_states=service_states(visit),
            assignment_ready=assignment_ready,
            scheduling_ready=scheduling_ready,
            blocker_codes=routing_blockers,
        )
        visit_dispatch_readiness = VisitDispatchReadiness(
            ready=dispatch_eligible,
            assigned=visit.technician_id is not None,
            scheduled=visit.scheduled_start_at is not None,
            routing_ready=routing_ready,
            lifecycle_state=lifecycle_state,
            scheduled_start_at=visit.scheduled_start_at,
            scheduled_end_at=visit.scheduled_end_at,
            blocker_codes=dispatch_blockers or visit_blockers,
        )
        dispatch_eligibility = RoutingDispatchEligibility(
            eligible=dispatch_eligible,
            requires_review=RoutingDispatchBlockerCode.REVIEW_REQUIRED in visit_blockers,
            blocked=bool(set(visit_blockers) & HARD_BLOCKER_CODES),
            unsafe=bool(dispatch_blockers or visit_blockers),
            blocker_codes=dispatch_blockers,
        )
        result = RoutingDispatchPreparationResult(
            lifecycle_state=lifecycle_state,
            traceability=RoutingDispatchTraceability(
                visit_id=visit.id,
                work_order_id=visit.work_order_id,
                job_id=visit.job_id,
                technician_id=visit.technician_id,
                audit_correlation_id=visit.audit_correlation_id,
            ),
            routing_readiness=routing_readiness,
            technician_readiness=technician_readiness,
            visit_dispatch_readiness=visit_dispatch_readiness,
            dispatch_eligibility=dispatch_eligibility,
            evidence=routing_dispatch_evidence(
                routing_readiness,
                technician_readiness,
                visit_dispatch_readiness,
                dispatch_eligibility,
                visit,
            ),
        )
        apply_preparation_snapshot(visit, result, timestamp)
        return result

    @staticmethod
    def build_dispatch_prepared_audit_log(visit: Visit) -> AuditLog:
        routing_snapshot = visit.routing_readiness_snapshot or {}
        dispatch_snapshot = visit.dispatch_readiness_snapshot or {}
        visit_snapshot = visit.visit_dispatch_readiness_snapshot or {}
        return AuditLog(
            action="operational_dispatch.prepared",
            entity_type="visit",
            entity_id=visit.id,
            audit_correlation_id=visit.audit_correlation_id,
            details={
                "visit_id": str(visit.id),
                "work_order_id": str(visit.work_order_id) if visit.work_order_id else None,
                "job_id": str(visit.job_id),
                "technician_id": str(visit.technician_id) if visit.technician_id else None,
                "lifecycle_state": visit_snapshot.get("lifecycle_state", visit.status),
                "routing_ready": routing_snapshot.get("ready"),
                "eligible_for_dispatch": dispatch_snapshot.get("eligible_for_dispatch"),
                "blocker_codes": visit_snapshot.get("blocker_codes", []),
                "dispatch_execution": "not_executed",
            },
        )


def visit_blocker_codes(visit: Visit) -> tuple[RoutingDispatchBlockerCode, ...]:
    blockers: list[RoutingDispatchBlockerCode] = []
    if visit.visit_type == "water_emergency":
        blockers.append(RoutingDispatchBlockerCode.WATER_EMERGENCY_VISIT)
    if visit.id is None or visit.job_id is None or visit.work_order_id is None:
        blockers.append(RoutingDispatchBlockerCode.MISSING_VISIT_LINKAGE)
    if visit.status == "blocked":
        blockers.append(RoutingDispatchBlockerCode.BLOCKED_VISIT)
    if visit.status == "review_required":
        blockers.append(RoutingDispatchBlockerCode.REVIEW_REQUIRED)
    if visit.status == "archived":
        blockers.append(RoutingDispatchBlockerCode.ARCHIVED_VISIT)
    terminal_states = {"blocked", "review_required", "archived"}
    if visit_status(visit) not in ROUTING_PREPARABLE_STATES | terminal_states:
        blockers.append(RoutingDispatchBlockerCode.INVALID_LIFECYCLE)
    operational_state = operational_lifecycle_state(visit)
    if (
        operational_state == "review_required"
        and RoutingDispatchBlockerCode.REVIEW_REQUIRED not in blockers
    ):
        blockers.append(RoutingDispatchBlockerCode.REVIEW_REQUIRED)
    if operational_state == "blocked" and RoutingDispatchBlockerCode.BLOCKED_VISIT not in blockers:
        blockers.append(RoutingDispatchBlockerCode.BLOCKED_VISIT)
    if (
        operational_state == "archived"
        and RoutingDispatchBlockerCode.ARCHIVED_VISIT not in blockers
    ):
        blockers.append(RoutingDispatchBlockerCode.ARCHIVED_VISIT)
    return tuple(blockers)


def routing_blockers_for(
    *,
    visit_blockers: tuple[RoutingDispatchBlockerCode, ...],
    assignment_ready: bool,
    scheduling_ready: bool,
) -> tuple[RoutingDispatchBlockerCode, ...]:
    hard_blockers = tuple(code for code in visit_blockers if code in HARD_BLOCKER_CODES)
    if hard_blockers:
        return hard_blockers
    blockers: list[RoutingDispatchBlockerCode] = []
    if not assignment_ready:
        blockers.append(RoutingDispatchBlockerCode.ASSIGNMENT_NOT_READY)
    if not scheduling_ready:
        blockers.append(RoutingDispatchBlockerCode.SCHEDULING_NOT_READY)
    return tuple(blockers)


def dispatch_blockers_for(
    *,
    visit_blockers: tuple[RoutingDispatchBlockerCode, ...],
    routing_ready: bool,
    technician_readiness: TechnicianReadiness,
    visit: Visit,
) -> tuple[RoutingDispatchBlockerCode, ...]:
    hard_blockers = tuple(code for code in visit_blockers if code in HARD_BLOCKER_CODES)
    if hard_blockers:
        return hard_blockers

    blockers: list[RoutingDispatchBlockerCode] = []
    if not routing_ready:
        blockers.append(RoutingDispatchBlockerCode.ROUTING_NOT_READY)
    if visit.technician_id is None:
        blockers.append(RoutingDispatchBlockerCode.UNASSIGNED_VISIT)
    if visit.scheduled_start_at is None:
        blockers.append(RoutingDispatchBlockerCode.UNSCHEDULED_VISIT)
    for blocker in technician_readiness.blocker_codes:
        if blocker not in blockers:
            blockers.append(blocker)
    return tuple(blockers)


def technician_readiness_for(
    visit: Visit,
    technician: Technician | None,
) -> TechnicianReadiness:
    if technician is None:
        return TechnicianReadiness(
            ready=visit.technician_id is not None,
            evaluated=False,
            technician_id=visit.technician_id,
        )
    if not technician.is_active:
        return TechnicianReadiness(
            ready=False,
            evaluated=True,
            technician_id=technician.id,
            is_active=technician.is_active,
            availability_status=technician.availability_status,
            skills=tuple(technician.skills or ()),
            service_areas=tuple(technician.service_areas or ()),
            vehicle_label=technician.vehicle_label,
            blocker_codes=(RoutingDispatchBlockerCode.INACTIVE_TECHNICIAN,),
        )
    return TechnicianReadiness(
        ready=True,
        evaluated=True,
        technician_id=technician.id,
        is_active=technician.is_active,
        availability_status=technician.availability_status,
        skills=tuple(technician.skills or ()),
        service_areas=tuple(technician.service_areas or ()),
        vehicle_label=technician.vehicle_label,
    )


def lifecycle_state_for(
    *,
    visit_blockers: tuple[RoutingDispatchBlockerCode, ...],
    routing_ready: bool,
    dispatch_eligible: bool,
) -> RoutingDispatchLifecycleState:
    if RoutingDispatchBlockerCode.REVIEW_REQUIRED in visit_blockers:
        return RoutingDispatchLifecycleState.REVIEW_REQUIRED
    if RoutingDispatchBlockerCode.ARCHIVED_VISIT in visit_blockers:
        return RoutingDispatchLifecycleState.ARCHIVED
    if set(visit_blockers) & HARD_BLOCKER_CODES:
        return RoutingDispatchLifecycleState.BLOCKED
    if dispatch_eligible:
        return RoutingDispatchLifecycleState.DISPATCH_READY
    if routing_ready:
        return RoutingDispatchLifecycleState.ROUTING_READY
    return RoutingDispatchLifecycleState.AWAITING_ROUTING


def apply_preparation_snapshot(
    visit: Visit,
    result: RoutingDispatchPreparationResult,
    timestamp: datetime,
) -> None:
    visit.routing_readiness_snapshot = routing_readiness_snapshot(result)
    visit.dispatch_readiness_snapshot = dispatch_readiness_snapshot(result)
    visit.technician_readiness_snapshot = technician_readiness_snapshot(result)
    visit.visit_dispatch_readiness_snapshot = visit_dispatch_readiness_snapshot(result)
    visit.routing_prepared_at = timestamp
    visit.dispatch_prepared_at = timestamp

    if result.lifecycle_state not in {
        RoutingDispatchLifecycleState.BLOCKED,
        RoutingDispatchLifecycleState.REVIEW_REQUIRED,
        RoutingDispatchLifecycleState.ARCHIVED,
    }:
        visit.status = result.lifecycle_state.value

    metadata = dict(visit.lifecycle_metadata or {})
    metadata["routing_dispatch_preparation_state"] = result.lifecycle_state.value
    metadata["routing_dispatch_preparation_blockers"] = [
        code.value for code in result.blocker_codes
    ]
    metadata["dispatch_execution"] = "not_executed"
    metadata["route_optimization"] = "not_performed"
    visit.lifecycle_metadata = metadata


def routing_readiness_snapshot(result: RoutingDispatchPreparationResult) -> dict[str, object]:
    readiness = result.routing_readiness
    return {
        "ready": readiness.ready,
        "schedule_window": readiness.schedule_window,
        "service_states": list(readiness.service_states),
        "assignment_ready": readiness.assignment_ready,
        "scheduling_ready": readiness.scheduling_ready,
        "blocker_codes": [code.value for code in readiness.blocker_codes],
        "route_optimization": "not_performed",
    }


def dispatch_readiness_snapshot(result: RoutingDispatchPreparationResult) -> dict[str, object]:
    eligibility = result.dispatch_eligibility
    return {
        "eligible_for_dispatch": eligibility.eligible,
        "requires_review": eligibility.requires_review,
        "blocked": eligibility.blocked,
        "unsafe": eligibility.unsafe,
        "blocker_codes": [code.value for code in eligibility.blocker_codes],
        "dispatch_execution": "not_executed",
    }


def technician_readiness_snapshot(result: RoutingDispatchPreparationResult) -> dict[str, object]:
    readiness = result.technician_readiness
    return {
        "ready": readiness.ready,
        "evaluated": readiness.evaluated,
        "technician": {
            "id": str(readiness.technician_id) if readiness.technician_id else None,
            "is_active": readiness.is_active,
            "availability_status": readiness.availability_status,
            "skills": list(readiness.skills),
            "service_areas": list(readiness.service_areas),
            "vehicle_label": readiness.vehicle_label,
        },
        "blocker_codes": [code.value for code in readiness.blocker_codes],
    }


def visit_dispatch_readiness_snapshot(
    result: RoutingDispatchPreparationResult,
) -> dict[str, object]:
    readiness = result.visit_dispatch_readiness
    return {
        "ready": readiness.ready,
        "assigned": readiness.assigned,
        "scheduled": readiness.scheduled,
        "routing_ready": readiness.routing_ready,
        "lifecycle_state": readiness.lifecycle_state.value,
        "scheduled_start_at": readiness.scheduled_start_at.isoformat()
        if readiness.scheduled_start_at
        else None,
        "scheduled_end_at": readiness.scheduled_end_at.isoformat()
        if readiness.scheduled_end_at
        else None,
        "blocker_codes": [code.value for code in readiness.blocker_codes],
    }


def routing_dispatch_evidence(
    routing_readiness: RoutingReadiness,
    technician_readiness: TechnicianReadiness,
    visit_dispatch_readiness: VisitDispatchReadiness,
    dispatch_eligibility: RoutingDispatchEligibility,
    visit: Visit,
) -> RoutingDispatchEvidence:
    return RoutingDispatchEvidence(
        routing={
            "ready": routing_readiness.ready,
            "blocker_codes": [code.value for code in routing_readiness.blocker_codes],
            "schedule_window": routing_readiness.schedule_window,
            "service_states": list(routing_readiness.service_states),
        },
        technician={
            "ready": technician_readiness.ready,
            "evaluated": technician_readiness.evaluated,
            "technician_id": str(technician_readiness.technician_id)
            if technician_readiness.technician_id
            else None,
            "blocker_codes": [code.value for code in technician_readiness.blocker_codes],
        },
        schedule={
            "scheduled_start_at": visit.scheduled_start_at.isoformat()
            if visit.scheduled_start_at
            else None,
            "scheduled_end_at": visit.scheduled_end_at.isoformat()
            if visit.scheduled_end_at
            else None,
            "schedule_window": routing_readiness.schedule_window,
        },
        assignment={
            "assigned": visit.technician_id is not None,
            "assignment_ready": routing_readiness.assignment_ready,
        },
        dispatch={
            "eligible": dispatch_eligibility.eligible,
            "blocker_codes": [code.value for code in dispatch_eligibility.blocker_codes],
            "dispatch_execution": "not_executed",
        },
    )


def assignment_is_ready(visit: Visit) -> bool:
    snapshot = visit.assignment_readiness_snapshot or {}
    return bool(snapshot.get("ready"))


def scheduling_is_ready(visit: Visit) -> bool:
    snapshot = visit.scheduling_readiness_snapshot or {}
    return bool(snapshot.get("ready"))


def preferred_time_window(visit: Visit) -> str | None:
    snapshot = visit.scheduling_readiness_snapshot or {}
    window = snapshot.get("preferred_time_window")
    return str(window) if window else None


def service_states(visit: Visit) -> tuple[str, ...]:
    snapshot = visit.scheduling_readiness_snapshot or {}
    states = snapshot.get("service_states") or ()
    return tuple(str(state) for state in states)


def operational_lifecycle_state(visit: Visit) -> str | None:
    snapshot = visit.operational_readiness_snapshot or {}
    state = snapshot.get("lifecycle_state")
    return str(state) if state else None


def visit_status(visit: Visit) -> str:
    return str(visit.status.value if hasattr(visit.status, "value") else visit.status)
