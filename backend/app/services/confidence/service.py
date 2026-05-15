from app.domain.intake import (
    ConfidenceLevel,
    ConfidenceScore,
    IssueSeverity,
    NormalizedIntake,
    ValidationResult,
)

SEVERITY_DEDUCTIONS = {
    IssueSeverity.INFO: 0,
    IssueSeverity.WARNING: 10,
    IssueSeverity.ERROR: 25,
    IssueSeverity.CRITICAL: 35,
}


class DeterministicConfidenceScoringService:
    def score(self, intake: NormalizedIntake, validation: ValidationResult) -> ConfidenceScore:
        if not validation.issues:
            return ConfidenceScore(
                score=100,
                level=ConfidenceLevel.HIGH,
                factors=("no_validation_issues",),
            )

        score = 100
        factors: list[str] = []
        for issue in validation.issues:
            score -= SEVERITY_DEDUCTIONS[issue.severity]
            factors.append(issue.code)

        if intake.cancellation.detected and intake.cancellation.confidence < 0.9:
            score -= 10
            factors.append("LOW_CONFIDENCE_CANCELLATION_MATCH")

        if not validation.is_dispatch_safe:
            score = min(score, 74)

        score = max(score, 0)
        return ConfidenceScore(
            score=score,
            level=confidence_level(score),
            factors=tuple(factors),
        )


def confidence_level(score: int) -> ConfidenceLevel:
    if score >= 95:
        return ConfidenceLevel.HIGH
    if score >= 75:
        return ConfidenceLevel.WARNING
    return ConfidenceLevel.MANUAL_REVIEW


confidence_scoring_service = DeterministicConfidenceScoringService()
