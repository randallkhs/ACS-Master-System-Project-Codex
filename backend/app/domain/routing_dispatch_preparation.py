from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID


class RoutingDispatchLifecycleState(StrEnum):
    AWAITING_ROUTING = "awaiting_routing"
    ROUTING_READY = "routing_ready"
    DISPATCH_READY = "dispatch_ready"
    BLOCKED = "blocked"
    REVIEW_REQUIRED = "review_required"
    ARCHIVED = "archived"


class RoutingDispatchBlockerCode(StrEnum):
    BLOCKED_VISIT = "blocked_visit"
    REVIEW_REQUIRED = "review_required"
    WATER_EMERGENCY_VISIT = "water_emergency_visit"
    ARCHIVED_VISIT = "archived_visit"
    INVALID_LIFECYCLE = "invalid_lifecycle"
    MISSING_VISIT_LINKAGE = "missing_visit_linkage"
    ASSIGNMENT_NOT_READY = "assignment_not_ready"
    SCHEDULING_NOT_READY = "scheduling_not_ready"
    ROUTING_NOT_READY = "routing_not_ready"
    UNASSIGNED_VISIT = "unassigned_visit"
    UNSCHEDULED_VISIT = "unscheduled_visit"
    INACTIVE_TECHNICIAN = "inactive_technician"


@dataclass(frozen=True)
class RoutingDispatchTraceability:
    visit_id: UUID | None
    work_order_id: UUID | None
    job_id: UUID | None
    technician_id: UUID | None
    audit_correlation_id: str | None


@dataclass(frozen=True)
class RoutingReadiness:
    ready: bool
    schedule_window: str | None = None
    service_states: tuple[str, ...] = ()
    assignment_ready: bool = False
    scheduling_ready: bool = False
    blocker_codes: tuple[RoutingDispatchBlockerCode, ...] = ()


@dataclass(frozen=True)
class TechnicianReadiness:
    ready: bool
    evaluated: bool
    technician_id: UUID | None = None
    is_active: bool | None = None
    availability_status: str | None = None
    skills: tuple[str, ...] = ()
    service_areas: tuple[str, ...] = ()
    vehicle_label: str | None = None
    blocker_codes: tuple[RoutingDispatchBlockerCode, ...] = ()


@dataclass(frozen=True)
class VisitDispatchReadiness:
    ready: bool
    assigned: bool
    scheduled: bool
    routing_ready: bool
    lifecycle_state: RoutingDispatchLifecycleState
    scheduled_start_at: datetime | None = None
    scheduled_end_at: datetime | None = None
    blocker_codes: tuple[RoutingDispatchBlockerCode, ...] = ()


@dataclass(frozen=True)
class RoutingDispatchEligibility:
    eligible: bool
    requires_review: bool = False
    blocked: bool = False
    unsafe: bool = False
    blocker_codes: tuple[RoutingDispatchBlockerCode, ...] = ()


@dataclass(frozen=True)
class RoutingDispatchEvidence:
    routing: dict[str, Any]
    technician: dict[str, Any]
    schedule: dict[str, Any]
    assignment: dict[str, Any]
    dispatch: dict[str, Any]


@dataclass(frozen=True)
class RoutingDispatchPreparationResult:
    lifecycle_state: RoutingDispatchLifecycleState
    traceability: RoutingDispatchTraceability
    routing_readiness: RoutingReadiness
    technician_readiness: TechnicianReadiness
    visit_dispatch_readiness: VisitDispatchReadiness
    dispatch_eligibility: RoutingDispatchEligibility
    evidence: RoutingDispatchEvidence

    @property
    def blocker_codes(self) -> tuple[RoutingDispatchBlockerCode, ...]:
        return self.visit_dispatch_readiness.blocker_codes
