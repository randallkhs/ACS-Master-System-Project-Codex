from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any
from uuid import UUID


class AccountabilityLifecycleState(StrEnum):
    ESCALATION_REQUIRED = "escalation_required"
    INCIDENT_PREPARED = "incident_prepared"
    AWAITING_OPERATIONAL_REVIEW = "awaiting_operational_review"
    CRITICAL_INTERVENTION_REQUIRED = "critical_intervention_required"
    ACCOUNTABILITY_BLOCKED = "accountability_blocked"
    ARCHIVED = "archived"


class AccountabilityEscalationType(StrEnum):
    REPLAY_RECOVERY = "replay_recovery"
    ROLLBACK = "rollback"
    RECONCILIATION = "reconciliation"
    CRITICAL_DIVERGENCE = "critical_divergence"
    MANUAL_INTERVENTION = "manual_intervention"


class AccountabilityFailureCode(StrEnum):
    MISSING_ROUTE_ASSIGNMENT_LINKAGE = "missing_route_assignment_linkage"
    MISSING_AUDIT_CORRELATION = "missing_audit_correlation"
    MISSING_OPERATOR_ID = "missing_operator_id"
    REVIEW_REQUIRED = "review_required"
    WATER_EMERGENCY_VISIT = "water_emergency_visit"
    INVALID_LIFECYCLE = "invalid_lifecycle"
    UNAUTHORIZED_ROUTE_ASSIGNMENT = "unauthorized_route_assignment"
    GOVERNANCE_REQUIRED = "governance_required"
    UNAUTHORIZED_OPERATOR_ACTION = "unauthorized_operator_action"
    UNAUTHORIZED_INTERVENTION_ESCALATION = "unauthorized_intervention_escalation"
    DUPLICATE_ESCALATION = "duplicate_escalation"
    IMMUTABLE_HISTORY_VIOLATION = "immutable_history_violation"
    NO_ACCOUNTABILITY_CONTEXT = "no_accountability_context"


@dataclass(frozen=True)
class AccountabilityBlocker:
    code: AccountabilityFailureCode
    message: str
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class AccountabilityTraceability:
    route_assignment_id: UUID | None
    visit_id: UUID | None
    work_order_id: UUID | None
    job_id: UUID | None
    technician_id: UUID | None
    audit_correlation_id: str | None
    operator_id: str | None


@dataclass(frozen=True)
class EscalationResult:
    escalation_required: bool
    escalation_type: AccountabilityEscalationType
    escalation_execution: str
    evidence: dict[str, Any]


@dataclass(frozen=True)
class IncidentPreparationResult:
    incident_prepared: bool
    incident_type: str | None
    incident_execution: str
    evidence: dict[str, Any]


@dataclass(frozen=True)
class InterventionEscalationEvidence:
    intervention_escalation_required: bool
    authorized_for_intervention_escalation: bool
    intervention_execution: str
    evidence: dict[str, Any]


@dataclass(frozen=True)
class OperationalIncidentEvidence:
    incident_prepared: bool
    incident_type: str | None
    incident_execution: str
    evidence: dict[str, Any]


@dataclass(frozen=True)
class AccountabilityAuditEvidence:
    action: str
    operator_id: str | None
    operator_role: str | None
    evidence: dict[str, Any]


@dataclass(frozen=True)
class AccountabilityEvidence:
    accountability: dict[str, Any]
    escalation: dict[str, Any]
    incident: dict[str, Any]
    intervention_escalation: dict[str, Any]
    blockers: dict[str, Any]
    audit: dict[str, Any]
    failure_reasons: tuple[AccountabilityBlocker, ...] = ()


@dataclass(frozen=True)
class AccountabilityResult:
    succeeded: bool
    state: AccountabilityLifecycleState
    traceability: AccountabilityTraceability
    evidence: AccountabilityEvidence
    escalation: EscalationResult
    incident: IncidentPreparationResult
    intervention_escalation: InterventionEscalationEvidence
    operational_incident: OperationalIncidentEvidence
    audit: AccountabilityAuditEvidence
    failure_reasons: tuple[AccountabilityBlocker, ...] = ()

    @property
    def failure_codes(self) -> tuple[AccountabilityFailureCode, ...]:
        return tuple(reason.code for reason in self.failure_reasons)
