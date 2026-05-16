from collections.abc import Callable
from datetime import UTC, datetime

from app.domain.assignment_preparation import (
    AssignmentEligibility,
    AssignmentPreparationBlockerCode,
    AssignmentPreparationLifecycleState,
    AssignmentPreparationResult,
    AssignmentPreparationTraceability,
    AssignmentReadiness,
    OperationalReadinessSnapshot,
    SchedulingReadiness,
    TechnicianCompatibility,
)
from app.models.audit_log import AuditLog
from app.models.technician import Technician
from app.models.visit import Visit

ASSIGNABLE_VISIT_STATES = {
    "awaiting_assignment",
    "assignment_required",
    "assignment_ready",
    "scheduling_ready",
}


class AssignmentPreparationService:
    def __init__(self, *, now: Callable[[], datetime] | None = None) -> None:
        self.now = now or (lambda: datetime.now(UTC))

    def prepare_visit(
        self,
        visit: Visit,
        *,
        technician: Technician | None = None,
    ) -> AssignmentPreparationResult:
        timestamp = self.now()
        blocker_codes = visit_blocker_codes(visit)
        technician_compatibility = technician_compatibility_for(technician)

        if (
            technician_compatibility.evaluated
            and not technician_compatibility.compatible
            and AssignmentPreparationBlockerCode.TECHNICIAN_INACTIVE not in blocker_codes
        ):
            blocker_codes = (
                *blocker_codes,
                AssignmentPreparationBlockerCode.TECHNICIAN_INACTIVE,
            )

        hard_blockers = hard_visit_blockers(blocker_codes)
        assignment_eligible = not hard_blockers
        assignment_required = not (
            assignment_eligible
            and technician_compatibility.evaluated
            and technician_compatibility.compatible
        )
        scheduling_ready = assignment_eligible and not assignment_required
        scheduling_blockers = () if scheduling_ready else scheduling_blockers_for(blocker_codes)

        lifecycle_state = lifecycle_state_for(
            blocker_codes=blocker_codes,
            assignment_eligible=assignment_eligible,
            assignment_required=assignment_required,
            scheduling_ready=scheduling_ready,
        )

        assignment_eligibility = AssignmentEligibility(
            eligible=assignment_eligible,
            blocker_codes=tuple(hard_blockers),
        )
        assignment_readiness = AssignmentReadiness(
            assignment_required=assignment_required,
            ready=assignment_eligible and not assignment_required,
            blocker_codes=(
                (AssignmentPreparationBlockerCode.ASSIGNMENT_REQUIRED,)
                if assignment_required and assignment_eligible
                else tuple(hard_blockers)
            ),
        )
        scheduling_readiness = SchedulingReadiness(
            ready=scheduling_ready,
            preferred_time_window=preferred_time_window(visit),
            service_states=service_states(visit),
            blocker_codes=scheduling_blockers,
        )
        operational_readiness = OperationalReadinessSnapshot(
            lifecycle_state=lifecycle_state,
            assignment_eligible=assignment_eligible,
            scheduling_ready=scheduling_ready,
            blocker_codes=blocker_codes,
            metadata={
                "dispatch_execution": "not_executed",
                "routing_execution": "not_executed",
                "technician_assignment": "not_performed",
            },
        )
        result = AssignmentPreparationResult(
            lifecycle_state=lifecycle_state,
            traceability=AssignmentPreparationTraceability(
                visit_id=visit.id,
                work_order_id=visit.work_order_id,
                job_id=visit.job_id,
                technician_id=technician.id if technician else None,
                audit_correlation_id=visit.audit_correlation_id,
            ),
            assignment_eligibility=assignment_eligibility,
            assignment_readiness=assignment_readiness,
            technician_compatibility=technician_compatibility,
            scheduling_readiness=scheduling_readiness,
            operational_readiness=operational_readiness,
        )
        apply_preparation_snapshot(visit, result, timestamp)
        return result

    @staticmethod
    def build_assignment_prepared_audit_log(visit: Visit) -> AuditLog:
        operational_snapshot = visit.operational_readiness_snapshot or {}
        assignment_snapshot = visit.assignment_readiness_snapshot or {}
        scheduling_snapshot = visit.scheduling_readiness_snapshot or {}
        return AuditLog(
            action="operational_assignment.prepared",
            entity_type="visit",
            entity_id=visit.id,
            audit_correlation_id=visit.audit_correlation_id,
            details={
                "visit_id": str(visit.id),
                "work_order_id": str(visit.work_order_id) if visit.work_order_id else None,
                "job_id": str(visit.job_id),
                "lifecycle_state": operational_snapshot.get("lifecycle_state", visit.status),
                "assignment_eligible": assignment_snapshot.get("eligible_for_assignment"),
                "scheduling_ready": scheduling_snapshot.get("ready"),
                "blocker_codes": operational_snapshot.get("blocker_codes", []),
            },
        )


def visit_blocker_codes(visit: Visit) -> tuple[AssignmentPreparationBlockerCode, ...]:
    blockers: list[AssignmentPreparationBlockerCode] = []
    if visit.visit_type == "water_emergency":
        blockers.append(AssignmentPreparationBlockerCode.WATER_EMERGENCY_VISIT)
    if visit.id is None or visit.job_id is None or visit.work_order_id is None:
        blockers.append(AssignmentPreparationBlockerCode.MISSING_VISIT_LINKAGE)
    if visit.status == "blocked":
        blockers.append(AssignmentPreparationBlockerCode.BLOCKED_VISIT)
    if visit.status == "review_required":
        blockers.append(AssignmentPreparationBlockerCode.REVIEW_REQUIRED)
    if visit.status == "archived":
        blockers.append(AssignmentPreparationBlockerCode.ARCHIVED_VISIT)
    if visit.status not in ASSIGNABLE_VISIT_STATES | {"blocked", "review_required", "archived"}:
        blockers.append(AssignmentPreparationBlockerCode.INVALID_LIFECYCLE)
    return tuple(blockers)


def technician_compatibility_for(technician: Technician | None) -> TechnicianCompatibility:
    if technician is None:
        return TechnicianCompatibility(evaluated=False, compatible=False)
    if not technician.is_active:
        return TechnicianCompatibility(
            evaluated=True,
            compatible=False,
            technician_id=technician.id,
            is_active=technician.is_active,
            availability_status=technician.availability_status,
            skills=tuple(technician.skills or ()),
            service_areas=tuple(technician.service_areas or ()),
            vehicle_label=technician.vehicle_label,
            blocker_codes=(AssignmentPreparationBlockerCode.TECHNICIAN_INACTIVE,),
        )
    return TechnicianCompatibility(
        evaluated=True,
        compatible=True,
        technician_id=technician.id,
        is_active=technician.is_active,
        availability_status=technician.availability_status,
        skills=tuple(technician.skills or ()),
        service_areas=tuple(technician.service_areas or ()),
        vehicle_label=technician.vehicle_label,
    )


def hard_visit_blockers(
    blocker_codes: tuple[AssignmentPreparationBlockerCode, ...],
) -> tuple[AssignmentPreparationBlockerCode, ...]:
    hard_codes = {
        AssignmentPreparationBlockerCode.BLOCKED_VISIT,
        AssignmentPreparationBlockerCode.REVIEW_REQUIRED,
        AssignmentPreparationBlockerCode.WATER_EMERGENCY_VISIT,
        AssignmentPreparationBlockerCode.ARCHIVED_VISIT,
        AssignmentPreparationBlockerCode.INVALID_LIFECYCLE,
        AssignmentPreparationBlockerCode.MISSING_VISIT_LINKAGE,
    }
    return tuple(code for code in blocker_codes if code in hard_codes)


def scheduling_blockers_for(
    blocker_codes: tuple[AssignmentPreparationBlockerCode, ...],
) -> tuple[AssignmentPreparationBlockerCode, ...]:
    hard_blockers = hard_visit_blockers(blocker_codes)
    if hard_blockers:
        return hard_blockers
    if AssignmentPreparationBlockerCode.TECHNICIAN_INACTIVE in blocker_codes:
        return (AssignmentPreparationBlockerCode.TECHNICIAN_INACTIVE,)
    return (AssignmentPreparationBlockerCode.ASSIGNMENT_REQUIRED,)


def lifecycle_state_for(
    *,
    blocker_codes: tuple[AssignmentPreparationBlockerCode, ...],
    assignment_eligible: bool,
    assignment_required: bool,
    scheduling_ready: bool,
) -> AssignmentPreparationLifecycleState:
    if AssignmentPreparationBlockerCode.WATER_EMERGENCY_VISIT in blocker_codes:
        return AssignmentPreparationLifecycleState.WATER_EMERGENCY_BLOCKED
    if AssignmentPreparationBlockerCode.REVIEW_REQUIRED in blocker_codes:
        return AssignmentPreparationLifecycleState.REVIEW_REQUIRED
    if AssignmentPreparationBlockerCode.ARCHIVED_VISIT in blocker_codes:
        return AssignmentPreparationLifecycleState.ARCHIVED
    if not assignment_eligible:
        return AssignmentPreparationLifecycleState.BLOCKED
    if scheduling_ready:
        return AssignmentPreparationLifecycleState.SCHEDULING_READY
    if assignment_required:
        return AssignmentPreparationLifecycleState.ASSIGNMENT_REQUIRED
    return AssignmentPreparationLifecycleState.ASSIGNMENT_READY


def apply_preparation_snapshot(
    visit: Visit,
    result: AssignmentPreparationResult,
    timestamp: datetime,
) -> None:
    visit.assignment_readiness_snapshot = assignment_readiness_snapshot(result)
    visit.technician_compatibility_snapshot = technician_compatibility_snapshot(result)
    visit.scheduling_readiness_snapshot = scheduling_readiness_snapshot(result)
    visit.operational_readiness_snapshot = operational_readiness_snapshot(result)
    visit.assignment_prepared_at = timestamp
    if result.scheduling_readiness.ready:
        visit.scheduling_prepared_at = timestamp
    if result.lifecycle_state not in {
        AssignmentPreparationLifecycleState.BLOCKED,
        AssignmentPreparationLifecycleState.REVIEW_REQUIRED,
        AssignmentPreparationLifecycleState.WATER_EMERGENCY_BLOCKED,
        AssignmentPreparationLifecycleState.ARCHIVED,
    }:
        visit.status = result.lifecycle_state.value

    metadata = dict(visit.lifecycle_metadata or {})
    metadata["assignment_preparation_state"] = result.lifecycle_state.value
    metadata["assignment_preparation_blockers"] = [code.value for code in result.blocker_codes]
    visit.lifecycle_metadata = metadata


def assignment_readiness_snapshot(result: AssignmentPreparationResult) -> dict[str, object]:
    return {
        "eligible_for_assignment": result.assignment_eligibility.eligible,
        "assignment_required": result.assignment_readiness.assignment_required,
        "ready": result.assignment_readiness.ready,
        "blocker_codes": [code.value for code in result.assignment_readiness.blocker_codes],
    }


def technician_compatibility_snapshot(result: AssignmentPreparationResult) -> dict[str, object]:
    compatibility = result.technician_compatibility
    return {
        "evaluated": compatibility.evaluated,
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


def scheduling_readiness_snapshot(result: AssignmentPreparationResult) -> dict[str, object]:
    readiness = result.scheduling_readiness
    return {
        "ready": readiness.ready,
        "preferred_time_window": readiness.preferred_time_window,
        "service_states": list(readiness.service_states),
        "blocker_codes": [code.value for code in readiness.blocker_codes],
    }


def operational_readiness_snapshot(result: AssignmentPreparationResult) -> dict[str, object]:
    readiness = result.operational_readiness
    return {
        "lifecycle_state": readiness.lifecycle_state.value,
        "assignment_eligible": readiness.assignment_eligible,
        "scheduling_ready": readiness.scheduling_ready,
        "blocker_codes": [code.value for code in readiness.blocker_codes],
        "metadata": readiness.metadata,
    }


def preferred_time_window(visit: Visit) -> str | None:
    windows = normalization_snapshot(visit).get("time_windows") or []
    return windows[0] if windows else None


def service_states(visit: Visit) -> tuple[str, ...]:
    states = normalization_snapshot(visit).get("states") or []
    return tuple(states)


def normalization_snapshot(visit: Visit) -> dict:
    evidence = visit.deterministic_evidence_snapshot or {}
    normalization = evidence.get("normalization") or {}
    return normalization if isinstance(normalization, dict) else {}
