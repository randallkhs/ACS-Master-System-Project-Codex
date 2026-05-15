from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from app.domain.intake import (
    ConfidenceScore,
    IntakeIssue,
    IssueSeverity,
    NormalizedIntake,
    RawIntakePayload,
    ReviewRecommendation,
    ValidationResult,
)


class OrchestrationState(StrEnum):
    RAW_RECEIVED = "raw_received"
    NORMALIZED = "normalized"
    VALIDATED = "validated"
    REVIEW_REQUIRED = "review_required"
    ELIGIBLE_FOR_DISPATCH = "eligible_for_dispatch"
    BLOCKED = "blocked"
    DEFERRED = "deferred"


@dataclass(frozen=True)
class OrchestrationWarning:
    code: str
    severity: IssueSeverity
    message: str
    field_name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_issue(cls, issue: IntakeIssue) -> OrchestrationWarning:
        return cls(
            code=issue.code,
            severity=issue.severity,
            message=issue.message,
            field_name=issue.field_name,
            metadata=issue.metadata,
        )


@dataclass(frozen=True)
class DispatchEligibility:
    eligible_for_dispatch: bool
    requires_review: bool
    blocked: bool
    deferred: bool
    unsafe: bool
    water_emergency_separated: bool
    reason_codes: tuple[str, ...] = ()


@dataclass(frozen=True)
class OrchestrationEvidence:
    normalization: dict[str, Any]
    validation: dict[str, Any]
    confidence: dict[str, Any]
    review: dict[str, Any]
    decision: dict[str, Any]


@dataclass(frozen=True)
class OrchestrationDecisionResult:
    state: OrchestrationState
    dispatch_eligibility: DispatchEligibility
    review_recommendation: ReviewRecommendation
    review_reasons: tuple[dict[str, str], ...] = ()
    escalation_severity: IssueSeverity | None = None
    deterministic_reason_codes: tuple[str, ...] = ()


@dataclass(frozen=True)
class IntakeProcessingResult:
    raw_payload: RawIntakePayload
    normalized: NormalizedIntake
    validation: ValidationResult
    confidence: ConfidenceScore
    review_recommendation: ReviewRecommendation
    decision: OrchestrationDecisionResult
    warnings: tuple[OrchestrationWarning, ...]
    evidence: OrchestrationEvidence

    @property
    def state(self) -> OrchestrationState:
        return self.decision.state
