from app.domain.intake import (
    ConfidenceScore,
    NormalizedIntake,
    RawIntakePayload,
    ReviewRecommendation,
    ValidationResult,
)
from app.domain.orchestration import (
    DispatchEligibility,
    IntakeProcessingResult,
    OrchestrationDecisionResult,
    OrchestrationEvidence,
    OrchestrationState,
    OrchestrationWarning,
)
from app.services.confidence.service import DeterministicConfidenceScoringService
from app.services.manual_review.classification import ReviewClassificationService
from app.services.manual_review.escalation import ReviewEscalationService
from app.services.manual_review.service import (
    ManualReviewPreparationService,
    confidence_snapshot,
    normalization_snapshot,
    validation_snapshot,
)
from app.services.normalization.service import IntakeNormalizationService
from app.services.validation.service import IntakeValidationService


class DispatchOrchestrationService:
    def __init__(
        self,
        *,
        normalizer: IntakeNormalizationService | None = None,
        validator: IntakeValidationService | None = None,
        confidence_scorer: DeterministicConfidenceScoringService | None = None,
        review_preparation: ManualReviewPreparationService | None = None,
        review_classifier: ReviewClassificationService | None = None,
        review_escalation: ReviewEscalationService | None = None,
    ) -> None:
        self.normalizer = normalizer or IntakeNormalizationService()
        self.validator = validator or IntakeValidationService()
        self.confidence_scorer = confidence_scorer or DeterministicConfidenceScoringService()
        self.review_preparation = review_preparation or ManualReviewPreparationService()
        self.review_classifier = review_classifier or ReviewClassificationService()
        self.review_escalation = review_escalation or ReviewEscalationService()

    def process(self, payload: RawIntakePayload) -> IntakeProcessingResult:
        normalized = self.normalizer.normalize(payload)
        validation = self.validator.validate(normalized)
        confidence = self.confidence_scorer.score(normalized, validation)
        review_recommendation = self.review_preparation.prepare(
            normalized,
            validation,
            confidence,
        )
        review_reasons = self._review_reasons(validation, confidence, review_recommendation)
        escalation_severity = self.review_escalation.severity_for(validation, confidence)
        deterministic_reason_codes = tuple(reason["code"] for reason in review_reasons)
        eligibility = dispatch_eligibility(
            normalized=normalized,
            validation=validation,
            review_recommendation=review_recommendation,
            deterministic_reason_codes=deterministic_reason_codes,
        )
        state = orchestration_state(eligibility)
        decision = OrchestrationDecisionResult(
            state=state,
            dispatch_eligibility=eligibility,
            review_recommendation=review_recommendation,
            review_reasons=review_reasons,
            escalation_severity=escalation_severity,
            deterministic_reason_codes=deterministic_reason_codes,
        )
        warnings = tuple(OrchestrationWarning.from_issue(issue) for issue in validation.issues)

        return IntakeProcessingResult(
            raw_payload=payload,
            normalized=normalized,
            validation=validation,
            confidence=confidence,
            review_recommendation=review_recommendation,
            decision=decision,
            warnings=warnings,
            evidence=orchestration_evidence(
                normalized=normalized,
                validation=validation,
                confidence=confidence,
                review_recommendation=review_recommendation,
                decision=decision,
            ),
        )

    def _review_reasons(
        self,
        validation: ValidationResult,
        confidence: ConfidenceScore,
        review_recommendation: ReviewRecommendation,
    ) -> tuple[dict[str, str], ...]:
        if not review_recommendation.required:
            return ()
        return tuple(self.review_classifier.classify(validation, confidence))


def dispatch_eligibility(
    *,
    normalized: NormalizedIntake,
    validation: ValidationResult,
    review_recommendation: ReviewRecommendation,
    deterministic_reason_codes: tuple[str, ...],
) -> DispatchEligibility:
    water_emergency_separated = normalized.water_emergency.detected
    unsafe = not validation.is_dispatch_safe
    requires_review = review_recommendation.required
    blocked = requires_review or unsafe or water_emergency_separated
    eligible_for_dispatch = not blocked

    return DispatchEligibility(
        eligible_for_dispatch=eligible_for_dispatch,
        requires_review=requires_review,
        blocked=blocked,
        deferred=False,
        unsafe=unsafe,
        water_emergency_separated=water_emergency_separated,
        reason_codes=deterministic_reason_codes if blocked else (),
    )


def orchestration_state(eligibility: DispatchEligibility) -> OrchestrationState:
    if eligibility.deferred:
        return OrchestrationState.DEFERRED
    if eligibility.requires_review:
        return OrchestrationState.REVIEW_REQUIRED
    if eligibility.eligible_for_dispatch:
        return OrchestrationState.ELIGIBLE_FOR_DISPATCH
    if eligibility.blocked:
        return OrchestrationState.BLOCKED
    return OrchestrationState.VALIDATED


def orchestration_evidence(
    *,
    normalized: NormalizedIntake,
    validation: ValidationResult,
    confidence: ConfidenceScore,
    review_recommendation: ReviewRecommendation,
    decision: OrchestrationDecisionResult,
) -> OrchestrationEvidence:
    eligibility = decision.dispatch_eligibility
    return OrchestrationEvidence(
        normalization=normalization_snapshot(normalized),
        validation=validation_snapshot(validation),
        confidence=confidence_snapshot(confidence),
        review={
            "required": review_recommendation.required,
            "severity": review_recommendation.severity.value
            if review_recommendation.severity
            else None,
            "reason_codes": list(review_recommendation.reason_codes),
            "review_reasons": list(decision.review_reasons),
            "recommended_action": review_recommendation.recommended_action,
            "escalation_severity": decision.escalation_severity.value
            if decision.escalation_severity
            else None,
        },
        decision={
            "state": decision.state.value,
            "eligible_for_dispatch": eligibility.eligible_for_dispatch,
            "requires_review": eligibility.requires_review,
            "dispatch_blocked": eligibility.blocked,
            "deferred": eligibility.deferred,
            "unsafe": eligibility.unsafe,
            "water_emergency_separated": eligibility.water_emergency_separated,
            "deterministic_reason_codes": list(decision.deterministic_reason_codes),
        },
    )


dispatch_service = DispatchOrchestrationService()
dispatch_orchestration_service = dispatch_service
