from app.domain.intake import ConfidenceLevel, ConfidenceScore, ValidationResult

REVIEW_CATEGORY_BY_ISSUE_CODE = {
    "CANCELLATION_DETECTED": "cancellation_review",
    "WATER_EMERGENCY_REQUIRES_WORKFLOW": "water_emergency_review",
    "MALFORMED_LOCATION": "malformed_address_review",
    "MISSING_CUSTOMER_NAME": "missing_field_review",
    "MISSING_LOCATION": "missing_field_review",
    "MISSING_SCHEDULED_DATE": "missing_field_review",
    "MISSING_TITLE": "missing_field_review",
    "CONFLICTING_STATE_MARKERS": "conflicting_state_review",
    "CONFLICTING_TIME_WINDOWS": "conflicting_state_review",
    "MISSING_STATE_MARKER": "missing_field_review",
}


class ReviewClassificationService:
    def classify(
        self,
        validation: ValidationResult,
        confidence: ConfidenceScore,
    ) -> list[dict[str, str]]:
        reasons = [
            {
                "code": issue.code,
                "category": REVIEW_CATEGORY_BY_ISSUE_CODE.get(
                    issue.code,
                    "unsafe_dispatch_review",
                ),
                "severity": issue.severity.value,
            }
            for issue in validation.issues
        ]

        has_low_confidence_evidence = any(
            "LOW_CONFIDENCE" in factor for factor in confidence.factors
        )
        if (
            confidence.level == ConfidenceLevel.MANUAL_REVIEW
            and has_low_confidence_evidence
            and not any(reason["category"] == "low_confidence_review" for reason in reasons)
        ):
            reasons.append(
                {
                    "code": "LOW_CONFIDENCE_REVIEW",
                    "category": "low_confidence_review",
                    "severity": "warning",
                },
            )

        if not validation.is_dispatch_safe and not any(
            reason["category"] == "unsafe_dispatch_review" for reason in reasons
        ):
            reasons.append(
                {
                    "code": "UNSAFE_DISPATCH_BLOCKED",
                    "category": "unsafe_dispatch_review",
                    "severity": "critical",
                },
            )

        return reasons
