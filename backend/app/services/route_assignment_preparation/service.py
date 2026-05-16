from collections.abc import Callable
from datetime import UTC, datetime
from uuid import uuid4

from app.domain.route_assignment_authorization import (
    DispatchAuthorizationReadiness,
    DispatchExecutionAuthorization,
    DispatchExecutionAuthorizationState,
    RouteAssignmentAuthorizationBlockerCode,
    RouteAssignmentAuthorizationEvidence,
    RouteAssignmentAuthorizationResult,
    RouteAssignmentAuthorizationTraceability,
    RouteAssignmentReadiness,
    RouteGroupingPreparation,
    TechnicianRouteCompatibility,
)
from app.models.audit_log import AuditLog
from app.models.route_assignment import RouteAssignment
from app.models.technician import Technician
from app.models.visit import Visit
from app.repositories.route_assignments import RouteAssignmentRepository

AUTHORIZABLE_VISIT_STATES = {
    "dispatch_ready",
    "awaiting_route_assignment",
    "awaiting_dispatch_execution",
}

HARD_BLOCKER_CODES = {
    RouteAssignmentAuthorizationBlockerCode.BLOCKED_VISIT,
    RouteAssignmentAuthorizationBlockerCode.REVIEW_REQUIRED,
    RouteAssignmentAuthorizationBlockerCode.WATER_EMERGENCY_VISIT,
    RouteAssignmentAuthorizationBlockerCode.ARCHIVED_VISIT,
    RouteAssignmentAuthorizationBlockerCode.INVALID_LIFECYCLE,
    RouteAssignmentAuthorizationBlockerCode.MISSING_VISIT_LINKAGE,
}


class RouteAssignmentPreparationService:
    def __init__(
        self,
        *,
        route_assignment_repository: RouteAssignmentRepository,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self.route_assignment_repository = route_assignment_repository
        self.now = now or (lambda: datetime.now(UTC))

    def prepare_route_assignment(
        self,
        visit: Visit,
        *,
        technician: Technician | None = None,
    ) -> RouteAssignmentAuthorizationResult:
        timestamp = self.now()
        visit_blockers = visit_blocker_codes(visit)
        technician_compatibility = technician_route_compatibility_for(visit, technician)
        route_grouping = route_grouping_preparation_for(visit, visit_blockers)
        route_assignment_readiness = route_assignment_readiness_for(
            visit,
            route_grouping,
            visit_blockers,
        )
        all_blockers = merged_blockers(
            visit_blockers,
            route_grouping.blocker_codes,
            route_assignment_readiness.blocker_codes,
            technician_compatibility.blocker_codes,
        )
        authorization = dispatch_execution_authorization_for(all_blockers)
        dispatch_authorization_readiness = DispatchAuthorizationReadiness(
            ready=authorization.authorized_for_dispatch,
            state=authorization.state,
            authorized_for_dispatch=authorization.authorized_for_dispatch,
            blocker_codes=authorization.blocker_codes,
        )
        route_assignment = None
        if authorization.authorized_for_dispatch:
            route_assignment = build_route_assignment(
                visit,
                route_grouping,
                route_assignment_readiness,
                technician_compatibility,
                dispatch_authorization_readiness,
                authorization,
                timestamp,
            )
            self.route_assignment_repository.add(route_assignment)
            mark_visit_awaiting_dispatch_execution(visit, route_assignment, authorization)

        return RouteAssignmentAuthorizationResult(
            authorization=authorization,
            traceability=RouteAssignmentAuthorizationTraceability(
                route_assignment_id=route_assignment.id if route_assignment else None,
                visit_id=visit.id,
                work_order_id=visit.work_order_id,
                job_id=visit.job_id,
                technician_id=visit.technician_id,
                audit_correlation_id=visit.audit_correlation_id,
            ),
            route_grouping=route_grouping,
            route_assignment_readiness=route_assignment_readiness,
            technician_route_compatibility=technician_compatibility,
            dispatch_authorization_readiness=dispatch_authorization_readiness,
            evidence=authorization_evidence(
                route_grouping,
                route_assignment_readiness,
                technician_compatibility,
                dispatch_authorization_readiness,
                authorization,
            ),
            route_assignment=route_assignment,
        )

    @staticmethod
    def build_dispatch_authorized_audit_log(route_assignment: RouteAssignment) -> AuditLog:
        authorization_snapshot = route_assignment.dispatch_authorization_snapshot or {}
        execution_snapshot = route_assignment.dispatch_execution_boundary_snapshot or {}
        return AuditLog(
            action="operational_dispatch.authorized",
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
                "authorized_for_dispatch": authorization_snapshot.get(
                    "authorized_for_dispatch",
                ),
                "authorization_state": authorization_snapshot.get("state"),
                "dispatch_execution": execution_snapshot.get("dispatch_execution"),
                "route_optimization": execution_snapshot.get("route_optimization"),
            },
        )


def visit_blocker_codes(visit: Visit) -> tuple[RouteAssignmentAuthorizationBlockerCode, ...]:
    blockers: list[RouteAssignmentAuthorizationBlockerCode] = []
    if visit.visit_type == "water_emergency":
        blockers.append(RouteAssignmentAuthorizationBlockerCode.WATER_EMERGENCY_VISIT)
    if visit.id is None or visit.job_id is None or visit.work_order_id is None:
        blockers.append(RouteAssignmentAuthorizationBlockerCode.MISSING_VISIT_LINKAGE)
    if visit.status == "blocked":
        blockers.append(RouteAssignmentAuthorizationBlockerCode.BLOCKED_VISIT)
    if visit.status == "review_required":
        blockers.append(RouteAssignmentAuthorizationBlockerCode.REVIEW_REQUIRED)
    if visit.status == "archived":
        blockers.append(RouteAssignmentAuthorizationBlockerCode.ARCHIVED_VISIT)
    if visit_status(visit) not in AUTHORIZABLE_VISIT_STATES | {
        "blocked",
        "review_required",
        "archived",
    }:
        blockers.append(RouteAssignmentAuthorizationBlockerCode.INVALID_LIFECYCLE)
    if dispatch_snapshot_requires_review(visit):
        blockers.append(RouteAssignmentAuthorizationBlockerCode.REVIEW_REQUIRED)
    if not route_ready(visit):
        blockers.append(RouteAssignmentAuthorizationBlockerCode.ROUTE_NOT_READY)
    if not dispatch_ready(visit):
        blockers.append(RouteAssignmentAuthorizationBlockerCode.DISPATCH_NOT_READY)
    if visit.technician_id is None:
        blockers.append(RouteAssignmentAuthorizationBlockerCode.UNASSIGNED_VISIT)
    if visit.scheduled_start_at is None:
        blockers.append(RouteAssignmentAuthorizationBlockerCode.UNSCHEDULED_VISIT)
    return tuple(dict.fromkeys(blockers))


def route_grouping_preparation_for(
    visit: Visit,
    visit_blockers: tuple[RouteAssignmentAuthorizationBlockerCode, ...],
) -> RouteGroupingPreparation:
    route_date = visit.scheduled_start_at.date() if visit.scheduled_start_at else None
    service_state_values = service_states(visit)
    region = service_state_values[0] if service_state_values else None
    time_window = preferred_time_window(visit)
    blockers = route_grouping_blockers(visit_blockers, route_date)
    route_group_key = None
    if route_date and region:
        route_group_key = f"{route_date.isoformat()}:{region}:{time_window or 'ANY'}"
    return RouteGroupingPreparation(
        ready=not blockers,
        route_date=route_date,
        route_group_key=route_group_key,
        region=region,
        time_window=time_window,
        service_states=service_state_values,
        blocker_codes=blockers,
    )


def route_assignment_readiness_for(
    visit: Visit,
    route_grouping: RouteGroupingPreparation,
    visit_blockers: tuple[RouteAssignmentAuthorizationBlockerCode, ...],
) -> RouteAssignmentReadiness:
    blockers: list[RouteAssignmentAuthorizationBlockerCode] = []
    if visit_blockers:
        blockers.extend(visit_blockers)
    if not route_grouping.ready:
        blockers.extend(route_grouping.blocker_codes)
    return RouteAssignmentReadiness(
        ready=not blockers,
        route_date=route_grouping.route_date,
        route_group_key=route_grouping.route_group_key,
        visit_id=visit.id,
        technician_id=visit.technician_id,
        blocker_codes=tuple(dict.fromkeys(blockers)),
    )


def technician_route_compatibility_for(
    visit: Visit,
    technician: Technician | None,
) -> TechnicianRouteCompatibility:
    if technician is None:
        return TechnicianRouteCompatibility(
            compatible=visit.technician_id is not None,
            technician_id=visit.technician_id,
        )
    if not technician.is_active:
        return TechnicianRouteCompatibility(
            compatible=False,
            technician_id=technician.id,
            is_active=technician.is_active,
            availability_status=technician.availability_status,
            skills=tuple(technician.skills or ()),
            service_areas=tuple(technician.service_areas or ()),
            vehicle_label=technician.vehicle_label,
            blocker_codes=(RouteAssignmentAuthorizationBlockerCode.INACTIVE_TECHNICIAN,),
        )
    return TechnicianRouteCompatibility(
        compatible=True,
        technician_id=technician.id,
        is_active=technician.is_active,
        availability_status=technician.availability_status,
        skills=tuple(technician.skills or ()),
        service_areas=tuple(technician.service_areas or ()),
        vehicle_label=technician.vehicle_label,
    )


def route_grouping_blockers(
    visit_blockers: tuple[RouteAssignmentAuthorizationBlockerCode, ...],
    route_date,
) -> tuple[RouteAssignmentAuthorizationBlockerCode, ...]:
    blockers: list[RouteAssignmentAuthorizationBlockerCode] = []
    blockers.extend(code for code in visit_blockers if code in HARD_BLOCKER_CODES)
    if RouteAssignmentAuthorizationBlockerCode.ROUTE_NOT_READY in visit_blockers:
        blockers.append(RouteAssignmentAuthorizationBlockerCode.ROUTE_NOT_READY)
    if route_date is None:
        blockers.append(RouteAssignmentAuthorizationBlockerCode.MISSING_ROUTE_DATE)
    return tuple(dict.fromkeys(blockers))


def dispatch_execution_authorization_for(
    blockers: tuple[RouteAssignmentAuthorizationBlockerCode, ...],
) -> DispatchExecutionAuthorization:
    if RouteAssignmentAuthorizationBlockerCode.REVIEW_REQUIRED in blockers:
        state = DispatchExecutionAuthorizationState.REVIEW_REQUIRED
    elif blockers:
        state = DispatchExecutionAuthorizationState.BLOCKED_FROM_DISPATCH
    else:
        state = DispatchExecutionAuthorizationState.AWAITING_DISPATCH_EXECUTION
    return DispatchExecutionAuthorization(
        state=state,
        authorized_for_dispatch=not blockers,
        blocked_from_dispatch=(
            bool(blockers) and state is DispatchExecutionAuthorizationState.BLOCKED_FROM_DISPATCH
        ),
        review_required=state is DispatchExecutionAuthorizationState.REVIEW_REQUIRED,
        unsafe=bool(blockers),
        awaiting_route_assignment=False,
        awaiting_dispatch_execution=(
            state is DispatchExecutionAuthorizationState.AWAITING_DISPATCH_EXECUTION
        ),
        blocker_codes=blockers,
    )


def build_route_assignment(
    visit: Visit,
    route_grouping: RouteGroupingPreparation,
    route_assignment_readiness: RouteAssignmentReadiness,
    technician_route_compatibility: TechnicianRouteCompatibility,
    dispatch_authorization_readiness: DispatchAuthorizationReadiness,
    authorization: DispatchExecutionAuthorization,
    timestamp: datetime,
) -> RouteAssignment:
    route_assignment = RouteAssignment(
        id=uuid4(),
        route_date=route_grouping.route_date,
        technician_id=visit.technician_id,
        job_id=visit.job_id,
        visit_id=visit.id,
        region=route_grouping.region,
        time_window=route_grouping.time_window,
        status=DispatchExecutionAuthorizationState.AWAITING_DISPATCH_EXECUTION.value,
        route_group_key=route_grouping.route_group_key,
        audit_correlation_id=visit.audit_correlation_id,
        route_grouping_snapshot=route_grouping_snapshot(route_grouping),
        route_assignment_readiness_snapshot=route_assignment_readiness_snapshot(
            route_assignment_readiness,
        ),
        technician_route_compatibility_snapshot=technician_route_compatibility_snapshot(
            technician_route_compatibility,
        ),
        dispatch_authorization_snapshot=dispatch_authorization_snapshot(
            dispatch_authorization_readiness,
        ),
        dispatch_execution_boundary_snapshot=dispatch_execution_boundary_snapshot(
            authorization,
        ),
        deterministic_evidence_snapshot=deterministic_evidence_snapshot(
            route_grouping,
            route_assignment_readiness,
            technician_route_compatibility,
            authorization,
        ),
        authorization_prepared_at=timestamp,
        authorized_for_dispatch_at=timestamp,
    )
    return route_assignment


def mark_visit_awaiting_dispatch_execution(
    visit: Visit,
    route_assignment: RouteAssignment,
    authorization: DispatchExecutionAuthorization,
) -> None:
    visit.status = DispatchExecutionAuthorizationState.AWAITING_DISPATCH_EXECUTION.value
    metadata = dict(visit.lifecycle_metadata or {})
    metadata["route_assignment_preparation_state"] = authorization.state.value
    metadata["dispatch_authorization_state"] = authorization.state.value
    metadata["dispatch_authorization_blockers"] = [
        code.value for code in authorization.blocker_codes
    ]
    metadata["route_assignment_id"] = str(route_assignment.id)
    metadata["dispatch_execution"] = "not_executed"
    metadata["route_optimization"] = "not_performed"
    visit.lifecycle_metadata = metadata


def route_grouping_snapshot(route_grouping: RouteGroupingPreparation) -> dict[str, object]:
    return {
        "ready": route_grouping.ready,
        "route_date": route_grouping.route_date.isoformat() if route_grouping.route_date else None,
        "route_group_key": route_grouping.route_group_key,
        "region": route_grouping.region,
        "time_window": route_grouping.time_window,
        "service_states": list(route_grouping.service_states),
        "blocker_codes": [code.value for code in route_grouping.blocker_codes],
        "grouping_method": "deterministic_preparation_only",
    }


def route_assignment_readiness_snapshot(
    readiness: RouteAssignmentReadiness,
) -> dict[str, object]:
    return {
        "ready": readiness.ready,
        "route_date": readiness.route_date.isoformat() if readiness.route_date else None,
        "route_group_key": readiness.route_group_key,
        "visit_id": str(readiness.visit_id) if readiness.visit_id else None,
        "technician_id": str(readiness.technician_id) if readiness.technician_id else None,
        "blocker_codes": [code.value for code in readiness.blocker_codes],
    }


def technician_route_compatibility_snapshot(
    compatibility: TechnicianRouteCompatibility,
) -> dict[str, object]:
    return {
        "compatible": compatibility.compatible,
        "technician": {
            "id": str(compatibility.technician_id) if compatibility.technician_id else None,
            "is_active": compatibility.is_active,
            "availability_status": compatibility.availability_status,
            "skills": list(compatibility.skills),
            "service_areas": list(compatibility.service_areas),
            "vehicle_label": compatibility.vehicle_label,
        },
        "blocker_codes": [code.value for code in compatibility.blocker_codes],
    }


def dispatch_authorization_snapshot(
    readiness: DispatchAuthorizationReadiness,
) -> dict[str, object]:
    return {
        "ready": readiness.ready,
        "state": readiness.state.value,
        "authorized_for_dispatch": readiness.authorized_for_dispatch,
        "blocker_codes": [code.value for code in readiness.blocker_codes],
    }


def dispatch_execution_boundary_snapshot(
    authorization: DispatchExecutionAuthorization,
) -> dict[str, object]:
    return {
        "state": authorization.state.value,
        "authorized_for_dispatch": authorization.authorized_for_dispatch,
        "awaiting_dispatch_execution": authorization.awaiting_dispatch_execution,
        "dispatch_execution": "not_executed",
        "route_optimization": "not_performed",
        "integration_execution": "not_executed",
        "blocker_codes": [code.value for code in authorization.blocker_codes],
    }


def deterministic_evidence_snapshot(
    route_grouping: RouteGroupingPreparation,
    route_assignment_readiness: RouteAssignmentReadiness,
    technician_route_compatibility: TechnicianRouteCompatibility,
    authorization: DispatchExecutionAuthorization,
) -> dict[str, object]:
    return {
        "route_grouping": route_grouping_snapshot(route_grouping),
        "route_assignment_readiness": route_assignment_readiness_snapshot(
            route_assignment_readiness,
        ),
        "technician_route_compatibility": technician_route_compatibility_snapshot(
            technician_route_compatibility,
        ),
        "dispatch_authorization": dispatch_execution_boundary_snapshot(authorization),
    }


def authorization_evidence(
    route_grouping: RouteGroupingPreparation,
    route_assignment_readiness: RouteAssignmentReadiness,
    technician_route_compatibility: TechnicianRouteCompatibility,
    dispatch_authorization_readiness: DispatchAuthorizationReadiness,
    authorization: DispatchExecutionAuthorization,
) -> RouteAssignmentAuthorizationEvidence:
    return RouteAssignmentAuthorizationEvidence(
        route_grouping=route_grouping_snapshot(route_grouping),
        route_assignment=route_assignment_readiness_snapshot(route_assignment_readiness),
        technician=technician_route_compatibility_snapshot(technician_route_compatibility),
        dispatch_authorization=dispatch_authorization_snapshot(
            dispatch_authorization_readiness,
        ),
        execution_boundary=dispatch_execution_boundary_snapshot(authorization),
    )


def merged_blockers(
    *blocker_groups: tuple[RouteAssignmentAuthorizationBlockerCode, ...],
) -> tuple[RouteAssignmentAuthorizationBlockerCode, ...]:
    blockers: list[RouteAssignmentAuthorizationBlockerCode] = []
    for blocker_group in blocker_groups:
        blockers.extend(blocker_group)
    return tuple(dict.fromkeys(blockers))


def route_ready(visit: Visit) -> bool:
    snapshot = visit.routing_readiness_snapshot or {}
    return bool(snapshot.get("ready"))


def dispatch_ready(visit: Visit) -> bool:
    snapshot = visit.dispatch_readiness_snapshot or {}
    return bool(snapshot.get("eligible_for_dispatch"))


def dispatch_snapshot_requires_review(visit: Visit) -> bool:
    snapshot = visit.dispatch_readiness_snapshot or {}
    return bool(snapshot.get("requires_review"))


def preferred_time_window(visit: Visit) -> str | None:
    snapshot = visit.routing_readiness_snapshot or {}
    window = snapshot.get("schedule_window")
    return str(window) if window else None


def service_states(visit: Visit) -> tuple[str, ...]:
    snapshot = visit.routing_readiness_snapshot or {}
    states = snapshot.get("service_states") or ()
    return tuple(str(state) for state in states)


def visit_status(visit: Visit) -> str:
    return str(visit.status.value if hasattr(visit.status, "value") else visit.status)
