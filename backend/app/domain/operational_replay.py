from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any
from uuid import UUID


class ReplayRecoveryLifecycleState(StrEnum):
    REPLAY_PREPARED = "replay_prepared"
    REPLAY_BLOCKED = "replay_blocked"
    ROLLBACK_PREPARED = "rollback_prepared"
    RECOVERY_REQUIRED = "recovery_required"
    AWAITING_MANUAL_RECOVERY = "awaiting_manual_recovery"
    ARCHIVED = "archived"


class ReplayRecoveryFailureCode(StrEnum):
    MISSING_ROUTE_ASSIGNMENT_LINKAGE = "missing_route_assignment_linkage"
    MISSING_AUDIT_CORRELATION = "missing_audit_correlation"
    REVIEW_REQUIRED = "review_required"
    WATER_EMERGENCY_VISIT = "water_emergency_visit"
    INVALID_LIFECYCLE = "invalid_lifecycle"
    UNAUTHORIZED_ROUTE_ASSIGNMENT = "unauthorized_route_assignment"
    DUPLICATE_REPLAY_PREPARATION = "duplicate_replay_preparation"
    IMMUTABLE_HISTORY_VIOLATION = "immutable_history_violation"
    NO_RECOVERY_CONTEXT = "no_recovery_context"


@dataclass(frozen=True)
class ReplayRecoveryBlocker:
    code: ReplayRecoveryFailureCode
    message: str
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class ReplayEligibilityEvidence:
    eligible_for_replay: bool
    has_reconciliation_context: bool
    has_retry_context: bool
    has_failure_context: bool
    immutable_event_count: int
    evidence: dict[str, Any]


@dataclass(frozen=True)
class RollbackPreparationEvidence:
    rollback_prepared: bool
    rollback_execution: str
    evidence: dict[str, Any]


@dataclass(frozen=True)
class RecoveryCoordinationResult:
    recovery_required: bool
    manual_recovery_required: bool
    recovery_state: ReplayRecoveryLifecycleState
    evidence: dict[str, Any]


@dataclass(frozen=True)
class ReplayRecoveryTraceability:
    route_assignment_id: UUID | None
    visit_id: UUID | None
    work_order_id: UUID | None
    job_id: UUID | None
    technician_id: UUID | None
    audit_correlation_id: str | None


@dataclass(frozen=True)
class ReplayRecoveryEvidence:
    replay: dict[str, Any]
    rollback: dict[str, Any]
    eligibility: dict[str, Any]
    blockers: dict[str, Any]
    recovery_coordination: dict[str, Any]
    audit: dict[str, Any]
    failure_reasons: tuple[ReplayRecoveryBlocker, ...] = ()


@dataclass(frozen=True)
class ReplayPreparationResult:
    succeeded: bool
    state: ReplayRecoveryLifecycleState
    traceability: ReplayRecoveryTraceability
    evidence: ReplayRecoveryEvidence
    replay_eligibility: ReplayEligibilityEvidence
    rollback_preparation: RollbackPreparationEvidence
    recovery_coordination: RecoveryCoordinationResult
    failure_reasons: tuple[ReplayRecoveryBlocker, ...] = ()

    @property
    def failure_codes(self) -> tuple[ReplayRecoveryFailureCode, ...]:
        return tuple(reason.code for reason in self.failure_reasons)
