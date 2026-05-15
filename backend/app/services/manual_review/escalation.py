from app.domain.intake import ConfidenceLevel, ConfidenceScore, IssueSeverity, ValidationResult

SEVERITY_RANK = {
    IssueSeverity.INFO: 0,
    IssueSeverity.WARNING: 1,
    IssueSeverity.ERROR: 2,
    IssueSeverity.CRITICAL: 3,
}


class ReviewEscalationService:
    def severity_for(
        self,
        validation: ValidationResult,
        confidence: ConfidenceScore,
    ) -> IssueSeverity:
        severity = validation.highest_severity or IssueSeverity.INFO
        if (
            not validation.is_dispatch_safe
            and SEVERITY_RANK[severity] < SEVERITY_RANK[IssueSeverity.WARNING]
        ):
            severity = IssueSeverity.WARNING
        if (
            confidence.level == ConfidenceLevel.MANUAL_REVIEW
            and SEVERITY_RANK[severity] < SEVERITY_RANK[IssueSeverity.WARNING]
        ):
            severity = IssueSeverity.WARNING
        return severity
