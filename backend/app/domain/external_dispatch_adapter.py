from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID


class ExternalAdapterLifecycleState(StrEnum):
    INTERNAL_DISPATCH_COMPLETE = "internal_dispatch_complete"
    ADAPTER_PREPARED = "adapter_prepared"
    AWAITING_EXTERNAL_EXECUTION = "awaiting_external_execution"
    EXTERNAL_EXECUTION_BLOCKED = "external_execution_blocked"
    EXTERNAL_EXECUTION_FAILED = "external_execution_failed"
    AWAITING_EXTERNAL_CONFIRMATION = "awaiting_external_confirmation"


class ExternalAdapterFailureCode(StrEnum):
    VISIT_NOT_DISPATCHED = "visit_not_dispatched"
    INTERNAL_DISPATCH_NOT_COMPLETE = "internal_dispatch_not_complete"
    BLOCKED_VISIT = "blocked_visit"
    REVIEW_REQUIRED = "review_required"
    WATER_EMERGENCY_VISIT = "water_emergency_visit"
    ARCHIVED_VISIT = "archived_visit"
    INVALID_LIFECYCLE = "invalid_lifecycle"
    UNAUTHORIZED_ROUTE_ASSIGNMENT = "unauthorized_route_assignment"
    DUPLICATE_ADAPTER_PREPARATION = "duplicate_adapter_preparation"
    MISSING_ROUTE_ASSIGNMENT_LINKAGE = "missing_route_assignment_linkage"


@dataclass(frozen=True)
class AdapterFailureReason:
    code: ExternalAdapterFailureCode
    message: str
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class AdapterExecutionRequest:
    route_assignment_id: UUID | None
    visit_id: UUID | None
    work_order_id: UUID | None
    job_id: UUID | None
    technician_id: UUID | None
    audit_correlation_id: str | None
    target_adapters: tuple[str, ...]
    requested_at: datetime
    execution_mode: str = "prepare_only"


@dataclass(frozen=True)
class AdapterExecutionEvidence:
    adapter_execution: dict[str, Any]
    lifecycle: dict[str, Any]
    payloads: dict[str, dict[str, Any]]
    dispatch_execution: dict[str, Any]
    audit: dict[str, Any]
    failure_reasons: tuple[AdapterFailureReason, ...] = ()


@dataclass(frozen=True)
class AdapterExecutionResult:
    succeeded: bool
    state: ExternalAdapterLifecycleState
    request: AdapterExecutionRequest
    evidence: AdapterExecutionEvidence
    failure_reasons: tuple[AdapterFailureReason, ...] = ()

    @property
    def failure_codes(self) -> tuple[ExternalAdapterFailureCode, ...]:
        return tuple(reason.code for reason in self.failure_reasons)
