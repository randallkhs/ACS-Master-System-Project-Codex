from app.domain.intake import (
    ConfidenceLevel,
    ConfidenceScore,
    IssueSeverity,
    NormalizedIntake,
    ReviewRecommendation,
    ValidationResult,
)


class ManualReviewPreparationService:
    def prepare(
        self,
        intake: NormalizedIntake,
        validation: ValidationResult,
        confidence: ConfidenceScore,
    ) -> ReviewRecommendation:
        required = (
            not validation.is_dispatch_safe
            or confidence.level == ConfidenceLevel.MANUAL_REVIEW
            or validation.highest_severity in {IssueSeverity.ERROR, IssueSeverity.CRITICAL}
        )
        reason_codes = validation.issue_codes
        return ReviewRecommendation(
            required=required,
            severity=validation.highest_severity,
            reason_codes=reason_codes,
            recommended_action=recommended_action(required),
            confidence_score=confidence,
        )


def recommended_action(required: bool) -> str:
    if required:
        return "Send to Manual Review before dispatch."
    return "No manual review required."


manual_review_service = ManualReviewPreparationService()
