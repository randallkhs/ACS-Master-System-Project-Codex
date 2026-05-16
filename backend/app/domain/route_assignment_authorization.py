from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Any
from uuid import UUID


class DispatchExecutionAuthorizationState(StrEnum):
    AUTHORIZED_FOR_DISPATCH = "authorized_for_dispatch"
    BLOCKED_FROM_DISPATCH = "blocked_from_dispatch"
    REVIEW_REQUIRED = "review_required"
    UNSAFE = "unsafe"
    AWAITING_ROUTE_ASSIGNMENT = "awaiting_route_assignment"
    AWAITING_DISPATCH_EXECUTION = "awaiting_dispatch_execution"


class RouteAssignmentAuthorizationBlockerCode(StrEnum):
    BLOCKED_VISIT = "blocked_visit"
    REVIEW_REQUIRED = "review_required"
    WATER_EMERGENCY_VISIT = "water_emergency_visit"
    ARCHIVED_VISIT = "archived_visit"
    INVALID_LIFECYCLE = "invalid_lifecycle"
    MISSING_VISIT_LINKAGE = "missing_visit_linkage"
    DISPATCH_NOT_READY = "dispatch_not_ready"
    ROUTE_NOT_READY = "route_not_ready"
    INACTIVE_TECHNICIAN = "inactive_technician"
    UNASSIGNED_VISIT = "unassigned_visit"
    UNSCHEDULED_VISIT = "unscheduled_visit"
    MISSING_ROUTE_DATE = "missing_route_date"


@dataclass(frozen=True)
class RouteAssignmentAuthorizationTraceability:
    route_assignment_id: UUID | None
    visit_id: UUID | None
    work_order_id: UUID | None
    job_id: UUID | None
    technician_id: UUID | None
    audit_correlation_id: str | None


@dataclass(frozen=True)
class RouteGroupingPreparation:
    ready: bool
    route_date: date | None
    route_group_key: str | None
    region: str | None
    time_window: str | None
    service_states: tuple[str, ...] = ()
    blocker_codes: tuple[RouteAssignmentAuthorizationBlockerCode, ...] = ()


@dataclass(frozen=True)
class RouteAssignmentReadiness:
    ready: bool
    route_date: date | None
    route_group_key: str | None
    visit_id: UUID | None
    technician_id: UUID | None
    blocker_codes: tuple[RouteAssignmentAuthorizationBlockerCode, ...] = ()


@dataclass(frozen=True)
class TechnicianRouteCompatibility:
    compatible: bool
    technician_id: UUID | None
    is_active: bool | None = None
    availability_status: str | None = None
    skills: tuple[str, ...] = ()
    service_areas: tuple[str, ...] = ()
    vehicle_label: str | None = None
    blocker_codes: tuple[RouteAssignmentAuthorizationBlockerCode, ...] = ()


@dataclass(frozen=True)
class DispatchAuthorizationReadiness:
    ready: bool
    state: DispatchExecutionAuthorizationState
    authorized_for_dispatch: bool
    blocker_codes: tuple[RouteAssignmentAuthorizationBlockerCode, ...] = ()


@dataclass(frozen=True)
class DispatchExecutionAuthorization:
    state: DispatchExecutionAuthorizationState
    authorized_for_dispatch: bool
    blocked_from_dispatch: bool
    review_required: bool
    unsafe: bool
    awaiting_route_assignment: bool
    awaiting_dispatch_execution: bool
    blocker_codes: tuple[RouteAssignmentAuthorizationBlockerCode, ...] = ()


@dataclass(frozen=True)
class RouteAssignmentAuthorizationEvidence:
    route_grouping: dict[str, Any]
    route_assignment: dict[str, Any]
    technician: dict[str, Any]
    dispatch_authorization: dict[str, Any]
    execution_boundary: dict[str, Any]


@dataclass(frozen=True)
class RouteAssignmentAuthorizationResult:
    authorization: DispatchExecutionAuthorization
    traceability: RouteAssignmentAuthorizationTraceability
    route_grouping: RouteGroupingPreparation
    route_assignment_readiness: RouteAssignmentReadiness
    technician_route_compatibility: TechnicianRouteCompatibility
    dispatch_authorization_readiness: DispatchAuthorizationReadiness
    evidence: RouteAssignmentAuthorizationEvidence
    route_assignment: Any | None = None

    @property
    def blocker_codes(self) -> tuple[RouteAssignmentAuthorizationBlockerCode, ...]:
        return self.authorization.blocker_codes
