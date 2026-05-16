from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any
from uuid import UUID


class AssignmentPreparationLifecycleState(StrEnum):
    ASSIGNMENT_REQUIRED = "assignment_required"
    ASSIGNMENT_READY = "assignment_ready"
    SCHEDULING_READY = "scheduling_ready"
    BLOCKED = "blocked"
    REVIEW_REQUIRED = "review_required"
    WATER_EMERGENCY_BLOCKED = "water_emergency_blocked"
    ARCHIVED = "archived"


class AssignmentPreparationBlockerCode(StrEnum):
    ASSIGNMENT_REQUIRED = "assignment_required"
    BLOCKED_VISIT = "blocked_visit"
    REVIEW_REQUIRED = "review_required"
    WATER_EMERGENCY_VISIT = "water_emergency_visit"
    ARCHIVED_VISIT = "archived_visit"
    INVALID_LIFECYCLE = "invalid_lifecycle"
    MISSING_VISIT_LINKAGE = "missing_visit_linkage"
    TECHNICIAN_INACTIVE = "technician_inactive"


@dataclass(frozen=True)
class AssignmentPreparationTraceability:
    visit_id: UUID | None
    work_order_id: UUID | None
    job_id: UUID | None
    technician_id: UUID | None
    audit_correlation_id: str | None


@dataclass(frozen=True)
class AssignmentEligibility:
    eligible: bool
    blocker_codes: tuple[AssignmentPreparationBlockerCode, ...] = ()


@dataclass(frozen=True)
class AssignmentReadiness:
    assignment_required: bool
    ready: bool
    blocker_codes: tuple[AssignmentPreparationBlockerCode, ...] = ()


@dataclass(frozen=True)
class TechnicianCompatibility:
    evaluated: bool
    compatible: bool
    technician_id: UUID | None = None
    is_active: bool | None = None
    availability_status: str | None = None
    skills: tuple[str, ...] = ()
    service_areas: tuple[str, ...] = ()
    vehicle_label: str | None = None
    blocker_codes: tuple[AssignmentPreparationBlockerCode, ...] = ()


@dataclass(frozen=True)
class SchedulingReadiness:
    ready: bool
    preferred_time_window: str | None = None
    service_states: tuple[str, ...] = ()
    blocker_codes: tuple[AssignmentPreparationBlockerCode, ...] = ()


@dataclass(frozen=True)
class OperationalReadinessSnapshot:
    lifecycle_state: AssignmentPreparationLifecycleState
    assignment_eligible: bool
    scheduling_ready: bool
    blocker_codes: tuple[AssignmentPreparationBlockerCode, ...] = ()
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class AssignmentPreparationResult:
    lifecycle_state: AssignmentPreparationLifecycleState
    traceability: AssignmentPreparationTraceability
    assignment_eligibility: AssignmentEligibility
    assignment_readiness: AssignmentReadiness
    technician_compatibility: TechnicianCompatibility
    scheduling_readiness: SchedulingReadiness
    operational_readiness: OperationalReadinessSnapshot

    @property
    def blocker_codes(self) -> tuple[AssignmentPreparationBlockerCode, ...]:
        return self.operational_readiness.blocker_codes
