from uuid import uuid4

from app.domain.intake import (
    ConfidenceLevel,
    ConfidenceScore,
    IssueSeverity,
    NormalizedIntake,
    ReviewRecommendation,
    ValidationResult,
)
from app.domain.manual_review import IntakeProcessingState, ReviewStatus
from app.models.review_item import ReviewItem
from app.repositories.review_items import ReviewItemRepository
from app.services.manual_review.classification import ReviewClassificationService
from app.services.manual_review.escalation import ReviewEscalationService


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


class ManualReviewQueueService:
    def __init__(
        self,
        repository: ReviewItemRepository,
        *,
        classifier: ReviewClassificationService | None = None,
        escalation: ReviewEscalationService | None = None,
        preparation: ManualReviewPreparationService | None = None,
    ) -> None:
        self.repository = repository
        self.classifier = classifier or ReviewClassificationService()
        self.escalation = escalation or ReviewEscalationService()
        self.preparation = preparation or ManualReviewPreparationService()

    def create_from_intake(
        self,
        intake: NormalizedIntake,
        validation: ValidationResult,
        confidence: ConfidenceScore,
    ) -> ReviewItem:
        recommendation = self.preparation.prepare(intake, validation, confidence)
        if not recommendation.required:
            msg = "Manual Review item creation requires a review recommendation"
            raise ValueError(msg)

        review_reasons = self.classifier.classify(validation, confidence)
        severity = self.escalation.severity_for(validation, confidence)
        primary_reason = review_reasons[0]["code"] if review_reasons else "MANUAL_REVIEW_REQUIRED"
        item = ReviewItem(
            id=uuid4(),
            entity_type="intake",
            source_system=intake.raw.source_system,
            source_id=intake.raw.source_id,
            reason_code=primary_reason,
            status=ReviewStatus.OPEN,
            severity=severity.value,
            intake_processing_state=IntakeProcessingState.FLAGGED_FOR_REVIEW,
            confidence_score=float(confidence.score),
            review_reasons=review_reasons,
            confidence_snapshot=confidence_snapshot(confidence),
            warning_snapshot=warning_snapshot(validation),
            normalization_snapshot=normalization_snapshot(intake),
            validation_snapshot=validation_snapshot(validation),
            source_snapshot=source_snapshot(intake),
            review_metadata={
                "dispatch_blocked": not validation.is_dispatch_safe,
                "review_required": recommendation.required,
                "recommended_action": recommendation.recommended_action,
            },
            audit_correlation_id=str(uuid4()),
            recommended_action=recommendation.recommended_action,
        )
        return self.repository.add(item)


def confidence_snapshot(confidence: ConfidenceScore) -> dict[str, object]:
    return {
        "score": confidence.score,
        "level": confidence.level.value,
        "factors": list(confidence.factors),
    }


def warning_snapshot(validation: ValidationResult) -> dict[str, object]:
    return {
        "issue_count": len(validation.issues),
        "highest_severity": validation.highest_severity.value
        if validation.highest_severity
        else None,
        "is_dispatch_safe": validation.is_dispatch_safe,
    }


def normalization_snapshot(intake: NormalizedIntake) -> dict[str, object]:
    return {
        "title": intake.title,
        "customer_name": intake.customer_name,
        "location": intake.location,
        "scheduled_date": intake.scheduled_date.isoformat() if intake.scheduled_date else None,
        "time_windows": [window.value for window in intake.time_windows],
        "states": list(intake.states),
        "cancellation": detection_snapshot(intake.cancellation),
        "water_emergency": detection_snapshot(intake.water_emergency),
        "metadata": intake.metadata,
    }


def validation_snapshot(validation: ValidationResult) -> dict[str, object]:
    return {
        "is_valid": validation.is_valid,
        "is_dispatch_safe": validation.is_dispatch_safe,
        "issue_codes": list(validation.issue_codes),
        "issues": [
            {
                "code": issue.code,
                "severity": issue.severity.value,
                "message": issue.message,
                "field_name": issue.field_name,
                "metadata": issue.metadata,
            }
            for issue in validation.issues
        ],
    }


def source_snapshot(intake: NormalizedIntake) -> dict[str, object]:
    return {
        "source_system": intake.raw.source_system,
        "source_id": intake.raw.source_id,
        "title": intake.raw.title,
        "customer_name": intake.raw.customer_name,
        "location": intake.raw.location,
        "scheduled_date": intake.raw.scheduled_date.isoformat()
        if intake.raw.scheduled_date
        else None,
        "description": intake.raw.description,
        "raw": intake.raw.raw,
    }


def detection_snapshot(detection) -> dict[str, object]:
    return {
        "detected": detection.detected,
        "confidence": detection.confidence,
        "keyword_matches": list(detection.keyword_matches),
    }
