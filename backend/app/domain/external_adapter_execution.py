from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID


class ExternalExecutionLifecycleState(StrEnum):
    ADAPTER_PREPARED = "adapter_prepared"
    EXTERNAL_EXECUTION_STARTED = "external_execution_started"
    EXTERNAL_EXECUTION_COMPLETED = "external_execution_completed"
    EXTERNAL_EXECUTION_FAILED = "external_execution_failed"
    AWAITING_EXTERNAL_CONFIRMATION = "awaiting_external_confirmation"
    RECONCILIATION_REQUIRED = "reconciliation_required"
    ARCHIVED = "archived"


class ProviderExecutionState(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"
    RECONCILIATION_REQUIRED = "reconciliation_required"


class ExternalExecutionFailureCode(StrEnum):
    ADAPTER_NOT_PREPARED = "adapter_not_prepared"
    BLOCKED_VISIT = "blocked_visit"
    REVIEW_REQUIRED = "review_required"
    WATER_EMERGENCY_VISIT = "water_emergency_visit"
    ARCHIVED_VISIT = "archived_visit"
    INVALID_LIFECYCLE = "invalid_lifecycle"
    UNAUTHORIZED_EXECUTION = "unauthorized_execution"
    DUPLICATE_EXTERNAL_EXECUTION = "duplicate_external_execution"
    MISSING_ROUTE_ASSIGNMENT_LINKAGE = "missing_route_assignment_linkage"
    MISSING_PROVIDER_PAYLOAD = "missing_provider_payload"


@dataclass(frozen=True)
class ExternalExecutionFailureReason:
    code: ExternalExecutionFailureCode
    message: str
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class ExternalExecutionRequest:
    route_assignment_id: UUID | None
    visit_id: UUID | None
    work_order_id: UUID | None
    job_id: UUID | None
    technician_id: UUID | None
    audit_correlation_id: str | None
    providers: tuple[str, ...]
    requested_at: datetime
    execution_mode: str = "simulated_controlled_execution"


@dataclass(frozen=True)
class ExecutionProviderResult:
    provider: str
    state: ProviderExecutionState
    correlation_id: str
    evidence: dict[str, Any]


@dataclass(frozen=True)
class ExternalExecutionLifecycleTransition:
    previous_state: str | None
    new_state: ExternalExecutionLifecycleState
    transitioned_at: datetime
    evidence: dict[str, Any]


@dataclass(frozen=True)
class ExternalExecutionEvidence:
    execution: dict[str, Any]
    lifecycle: dict[str, Any]
    providers: dict[str, dict[str, Any]]
    failure: dict[str, Any]
    adapter: dict[str, Any]
    audit: dict[str, Any]
    failure_reasons: tuple[ExternalExecutionFailureReason, ...] = ()


@dataclass(frozen=True)
class ExternalExecutionResult:
    succeeded: bool
    state: ExternalExecutionLifecycleState
    request: ExternalExecutionRequest
    provider_results: dict[str, ExecutionProviderResult]
    evidence: ExternalExecutionEvidence
    failure_reasons: tuple[ExternalExecutionFailureReason, ...] = ()

    @property
    def failure_codes(self) -> tuple[ExternalExecutionFailureCode, ...]:
        return tuple(reason.code for reason in self.failure_reasons)
