from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any
from uuid import UUID


class ReconciliationLifecycleState(StrEnum):
    CONSISTENCY_VERIFIED = "consistency_verified"
    RECONCILIATION_REQUIRED = "reconciliation_required"
    RECONCILIATION_BLOCKED = "reconciliation_blocked"
    DIVERGENCE_DETECTED = "divergence_detected"
    AWAITING_MANUAL_RESOLUTION = "awaiting_manual_resolution"
    ARCHIVED = "archived"


class ReconciliationMismatchCode(StrEnum):
    INTERNAL_LIFECYCLE_MISMATCH = "internal_lifecycle_mismatch"
    EXTERNAL_EXECUTION_MISMATCH = "external_execution_mismatch"
    EXTERNAL_CONFIRMATION_MISMATCH = "external_confirmation_mismatch"
    RETRY_RECOVERY_MISMATCH = "retry_recovery_mismatch"


class ReconciliationFailureCode(StrEnum):
    MISSING_ROUTE_ASSIGNMENT_LINKAGE = "missing_route_assignment_linkage"
    MISSING_AUDIT_CORRELATION = "missing_audit_correlation"
    REVIEW_REQUIRED = "review_required"
    WATER_EMERGENCY_VISIT = "water_emergency_visit"
    INVALID_LIFECYCLE = "invalid_lifecycle"
    UNAUTHORIZED_ROUTE_ASSIGNMENT = "unauthorized_route_assignment"
    DUPLICATE_RECONCILIATION = "duplicate_reconciliation"
    IMMUTABLE_HISTORY_VIOLATION = "immutable_history_violation"


@dataclass(frozen=True)
class ReconciliationBlocker:
    code: ReconciliationFailureCode
    message: str
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class MismatchEvidence:
    code: ReconciliationMismatchCode
    message: str
    expected: str | None = None
    actual: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class DivergenceEvidence:
    divergence_detected: bool
    mismatch_count: int
    mismatch_codes: tuple[ReconciliationMismatchCode, ...]
    manual_resolution_required: bool
    evidence: dict[str, Any]


@dataclass(frozen=True)
class ConsistencyVerificationResult:
    is_consistent: bool
    divergence_detected: bool
    internal_lifecycle_state: str | None
    external_execution_state: str | None
    external_confirmation_state: str | None
    mismatch_evidence: tuple[MismatchEvidence, ...] = ()


@dataclass(frozen=True)
class ReconciliationTraceability:
    route_assignment_id: UUID | None
    visit_id: UUID | None
    work_order_id: UUID | None
    job_id: UUID | None
    technician_id: UUID | None
    audit_correlation_id: str | None


@dataclass(frozen=True)
class ReconciliationEvidence:
    consistency: dict[str, Any]
    divergence: dict[str, Any]
    mismatch: dict[str, Any]
    blockers: dict[str, Any]
    audit: dict[str, Any]
    failure_reasons: tuple[ReconciliationBlocker, ...] = ()


@dataclass(frozen=True)
class ReconciliationResult:
    succeeded: bool
    state: ReconciliationLifecycleState
    consistency: ConsistencyVerificationResult
    traceability: ReconciliationTraceability
    evidence: ReconciliationEvidence
    divergence: DivergenceEvidence | None = None
    failure_reasons: tuple[ReconciliationBlocker, ...] = ()

    @property
    def failure_codes(self) -> tuple[ReconciliationFailureCode, ...]:
        return tuple(reason.code for reason in self.failure_reasons)

    @property
    def mismatch_codes(self) -> tuple[ReconciliationMismatchCode, ...]:
        return tuple(mismatch.code for mismatch in self.consistency.mismatch_evidence)
