from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID


class DispatchExecutionState(StrEnum):
    DISPATCH_AUTHORIZED = "dispatch_authorized"
    DISPATCHED = "dispatched"
    DISPATCH_BLOCKED = "dispatch_blocked"
    DISPATCH_FAILED = "dispatch_failed"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    ARCHIVED = "archived"


class DispatchExecutionBlockerCode(StrEnum):
    BLOCKED_VISIT = "blocked_visit"
    REVIEW_REQUIRED = "review_required"
    WATER_EMERGENCY_VISIT = "water_emergency_visit"
    ARCHIVED_VISIT = "archived_visit"
    INVALID_LIFECYCLE = "invalid_lifecycle"
    INACTIVE_TECHNICIAN = "inactive_technician"
    UNASSIGNED_VISIT = "unassigned_visit"
    UNSCHEDULED_VISIT = "unscheduled_visit"
    UNAUTHORIZED_ROUTE_ASSIGNMENT = "unauthorized_route_assignment"
    ROUTE_ASSIGNMENT_NOT_READY = "route_assignment_not_ready"
    MISSING_ROUTE_ASSIGNMENT_LINKAGE = "missing_route_assignment_linkage"
    DUPLICATE_DISPATCH = "duplicate_dispatch"
    INVALID_EXECUTION_STATE = "invalid_execution_state"


@dataclass(frozen=True)
class DispatchExecutionFailureReason:
    code: DispatchExecutionBlockerCode
    message: str
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class DispatchExecutionTraceability:
    route_assignment_id: UUID | None
    visit_id: UUID | None
    work_order_id: UUID | None
    job_id: UUID | None
    technician_id: UUID | None
    audit_correlation_id: str | None


@dataclass(frozen=True)
class DispatchLifecycleTransition:
    previous_state: str | None
    new_state: DispatchExecutionState
    transitioned_at: datetime
    external_integrations: str = "not_executed"


@dataclass(frozen=True)
class DispatchExecutionEvidence:
    execution: dict[str, Any]
    lifecycle: dict[str, Any]
    route_assignment: dict[str, Any]
    audit: dict[str, Any]
    failure_reasons: tuple[DispatchExecutionFailureReason, ...] = ()


@dataclass(frozen=True)
class DispatchExecutionResult:
    succeeded: bool
    state: DispatchExecutionState
    traceability: DispatchExecutionTraceability
    evidence: DispatchExecutionEvidence
    lifecycle_transition: DispatchLifecycleTransition | None = None
    failure_reasons: tuple[DispatchExecutionFailureReason, ...] = ()

    @property
    def blocker_codes(self) -> tuple[DispatchExecutionBlockerCode, ...]:
        return tuple(reason.code for reason in self.failure_reasons)
