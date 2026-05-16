from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any
from uuid import UUID


class ExternalConfirmationLifecycleState(StrEnum):
    AWAITING_EXTERNAL_CONFIRMATION = "awaiting_external_confirmation"
    EXTERNALLY_CONFIRMED = "externally_confirmed"
    EXTERNAL_CONFIRMATION_FAILED = "external_confirmation_failed"
    AWAITING_RETRY = "awaiting_retry"
    RECONCILIATION_REQUIRED = "reconciliation_required"
    ARCHIVED = "archived"


class SimulatedExternalConfirmationState(StrEnum):
    CONFIRMED = "confirmed"
    FAILED = "failed"
    RECONCILIATION_REQUIRED = "reconciliation_required"


class ExternalConfirmationFailureCode(StrEnum):
    DUPLICATE_CONFIRMATION = "duplicate_confirmation"
    INVALID_LIFECYCLE = "invalid_lifecycle"
    BLOCKED_VISIT = "blocked_visit"
    REVIEW_REQUIRED = "review_required"
    WATER_EMERGENCY_VISIT = "water_emergency_visit"
    ARCHIVED_VISIT = "archived_visit"
    UNAUTHORIZED_ROUTE_ASSIGNMENT = "unauthorized_route_assignment"
    MISSING_ROUTE_ASSIGNMENT_LINKAGE = "missing_route_assignment_linkage"
    ADAPTER_NOT_READY_FOR_CONFIRMATION = "adapter_not_ready_for_confirmation"
    INVALID_RETRY_STATE = "invalid_retry_state"


@dataclass(frozen=True)
class ExternalConfirmationFailureReason:
    code: ExternalConfirmationFailureCode
    message: str
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class ExternalConfirmationTraceability:
    route_assignment_id: UUID | None
    visit_id: UUID | None
    work_order_id: UUID | None
    job_id: UUID | None
    technician_id: UUID | None
    audit_correlation_id: str | None


@dataclass(frozen=True)
class ExternalConfirmationEvidence:
    confirmation: dict[str, Any]
    lifecycle: dict[str, Any]
    failure: dict[str, Any]
    retry: dict[str, Any]
    reconciliation: dict[str, Any]
    audit: dict[str, Any]
    failure_reasons: tuple[ExternalConfirmationFailureReason, ...] = ()


@dataclass(frozen=True)
class ExternalConfirmationResult:
    succeeded: bool
    state: ExternalConfirmationLifecycleState
    traceability: ExternalConfirmationTraceability
    evidence: ExternalConfirmationEvidence
    failure_reasons: tuple[ExternalConfirmationFailureReason, ...] = ()

    @property
    def failure_codes(self) -> tuple[ExternalConfirmationFailureCode, ...]:
        return tuple(reason.code for reason in self.failure_reasons)
