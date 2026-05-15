from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from typing import Any


class TimeWindow(StrEnum):
    AM = "AM"
    PM = "PM"


class IssueSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ConfidenceLevel(StrEnum):
    HIGH = "high"
    WARNING = "warning"
    MANUAL_REVIEW = "manual_review"


@dataclass(frozen=True)
class RawIntakePayload:
    source_system: str
    title: str
    source_id: str | None = None
    customer_name: str | None = None
    location: str | None = None
    scheduled_date: date | None = None
    description: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DetectionResult:
    detected: bool = False
    confidence: float = 0.0
    keyword_matches: tuple[str, ...] = ()


@dataclass(frozen=True)
class NormalizedIntake:
    raw: RawIntakePayload
    title: str
    customer_name: str | None
    location: str | None
    scheduled_date: date | None
    description: str | None
    combined_text: str
    time_windows: tuple[TimeWindow, ...] = ()
    states: tuple[str, ...] = ()
    cancellation: DetectionResult = field(default_factory=DetectionResult)
    water_emergency: DetectionResult = field(default_factory=DetectionResult)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class IntakeIssue:
    code: str
    severity: IssueSeverity
    message: str
    field_name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidationResult:
    issues: tuple[IntakeIssue, ...] = ()
    is_dispatch_safe: bool = True

    @property
    def is_valid(self) -> bool:
        return not any(
            issue.severity in {IssueSeverity.ERROR, IssueSeverity.CRITICAL} for issue in self.issues
        )

    @property
    def issue_codes(self) -> tuple[str, ...]:
        return tuple(issue.code for issue in self.issues)

    @property
    def highest_severity(self) -> IssueSeverity | None:
        severity_order = {
            IssueSeverity.INFO: 0,
            IssueSeverity.WARNING: 1,
            IssueSeverity.ERROR: 2,
            IssueSeverity.CRITICAL: 3,
        }
        if not self.issues:
            return None
        return max((issue.severity for issue in self.issues), key=severity_order.get)


@dataclass(frozen=True)
class ConfidenceScore:
    score: int
    level: ConfidenceLevel
    factors: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReviewRecommendation:
    required: bool
    severity: IssueSeverity | None
    reason_codes: tuple[str, ...] = ()
    recommended_action: str = "No manual review required."
    confidence_score: ConfidenceScore | None = None
