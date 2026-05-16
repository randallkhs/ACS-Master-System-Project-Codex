from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any
from uuid import UUID


class GovernanceLifecycleState(StrEnum):
    AWAITING_OPERATOR_APPROVAL = "awaiting_operator_approval"
    OPERATOR_APPROVED = "operator_approved"
    OPERATOR_REJECTED = "operator_rejected"
    INTERVENTION_REQUIRED = "intervention_required"
    GOVERNANCE_BLOCKED = "governance_blocked"
    ARCHIVED = "archived"


class GovernanceOperation(StrEnum):
    REPLAY = "replay"
    ROLLBACK = "rollback"
    RECONCILIATION = "reconciliation"
    MANUAL_INTERVENTION = "manual_intervention"


class GovernanceFailureCode(StrEnum):
    MISSING_ROUTE_ASSIGNMENT_LINKAGE = "missing_route_assignment_linkage"
    MISSING_AUDIT_CORRELATION = "missing_audit_correlation"
    MISSING_OPERATOR_ID = "missing_operator_id"
    REVIEW_REQUIRED = "review_required"
    WATER_EMERGENCY_VISIT = "water_emergency_visit"
    INVALID_LIFECYCLE = "invalid_lifecycle"
    UNAUTHORIZED_OPERATOR_ACTION = "unauthorized_operator_action"
    DUPLICATE_APPROVAL = "duplicate_approval"
    IMMUTABLE_HISTORY_VIOLATION = "immutable_history_violation"
    REPLAY_NOT_PREPARED = "replay_not_prepared"
    ROLLBACK_NOT_PREPARED = "rollback_not_prepared"
    RECONCILIATION_NOT_PREPARED = "reconciliation_not_prepared"


@dataclass(frozen=True)
class GovernanceBlocker:
    code: GovernanceFailureCode
    message: str
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class GovernanceTraceability:
    route_assignment_id: UUID | None
    visit_id: UUID | None
    work_order_id: UUID | None
    job_id: UUID | None
    technician_id: UUID | None
    audit_correlation_id: str | None
    operator_id: str | None


@dataclass(frozen=True)
class ReplayAuthorizationEvidence:
    authorized_for_replay: bool
    replay_execution: str
    evidence: dict[str, Any]


@dataclass(frozen=True)
class RollbackAuthorizationEvidence:
    authorized_for_rollback: bool
    rollback_execution: str
    evidence: dict[str, Any]


@dataclass(frozen=True)
class ReconciliationApprovalEvidence:
    approved_for_reconciliation: bool
    reconciliation_execution: str
    evidence: dict[str, Any]


@dataclass(frozen=True)
class InterventionAuthorizationResult:
    intervention_required: bool
    authorized_for_intervention: bool
    intervention_execution: str
    evidence: dict[str, Any]


@dataclass(frozen=True)
class GovernanceAuditEvidence:
    action: str
    operator_id: str | None
    operator_role: str | None
    evidence: dict[str, Any]


@dataclass(frozen=True)
class GovernanceEvidence:
    approval: dict[str, Any]
    intervention: dict[str, Any]
    replay_authorization: dict[str, Any]
    rollback_authorization: dict[str, Any]
    reconciliation_approval: dict[str, Any]
    blockers: dict[str, Any]
    audit: dict[str, Any]
    failure_reasons: tuple[GovernanceBlocker, ...] = ()


@dataclass(frozen=True)
class GovernanceApprovalResult:
    succeeded: bool
    state: GovernanceLifecycleState
    operation: GovernanceOperation
    traceability: GovernanceTraceability
    evidence: GovernanceEvidence
    replay_authorization: ReplayAuthorizationEvidence
    rollback_authorization: RollbackAuthorizationEvidence
    reconciliation_approval: ReconciliationApprovalEvidence
    intervention_authorization: InterventionAuthorizationResult
    audit: GovernanceAuditEvidence
    failure_reasons: tuple[GovernanceBlocker, ...] = ()

    @property
    def failure_codes(self) -> tuple[GovernanceFailureCode, ...]:
        return tuple(reason.code for reason in self.failure_reasons)
