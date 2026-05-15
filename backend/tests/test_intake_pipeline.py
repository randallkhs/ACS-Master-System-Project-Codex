from datetime import date

from app.domain.intake import ConfidenceLevel, IssueSeverity, RawIntakePayload, TimeWindow
from app.services.confidence.service import DeterministicConfidenceScoringService
from app.services.manual_review.service import ManualReviewPreparationService
from app.services.normalization.service import IntakeNormalizationService
from app.services.validation.service import IntakeValidationService


def raw_payload(
    *,
    title: str = "AM/DE Carpet cleaning",
    customer_name: str | None = "Acme Apartments",
    location: str | None = "123 Main St Wilmington DE 19801",
    scheduled_date: date | None = date(2026, 5, 16),
    description: str | None = None,
) -> RawIntakePayload:
    return RawIntakePayload(
        source_system="test",
        source_id="evt-123",
        title=title,
        customer_name=customer_name,
        location=location,
        scheduled_date=scheduled_date,
        description=description,
        raw={"id": "evt-123"},
    )


def test_normalization_cleans_text_and_extracts_operational_markers() -> None:
    normalized = IntakeNormalizationService().normalize(
        raw_payload(
            title="  PM/NJ    Upholstery   cleaning  ",
            location="  45  River   Rd   Trenton NJ 08608  ",
        ),
    )

    assert normalized.title == "PM/NJ Upholstery cleaning"
    assert normalized.location == "45 River Rd Trenton NJ 08608"
    assert normalized.time_windows == (TimeWindow.PM,)
    assert normalized.states == ("NJ",)
    assert normalized.metadata["normalization_steps"] == (
        "whitespace_cleanup",
        "marker_extraction",
        "keyword_detection",
    )


def test_normalization_detects_cancellation_misspellings() -> None:
    normalized = IntakeNormalizationService().normalize(
        raw_payload(title="Canseled - AM/DE carpet cleaning"),
    )

    assert normalized.cancellation.detected
    assert normalized.cancellation.keyword_matches == ("canseled",)
    assert normalized.cancellation.confidence < 0.9


def test_normalization_detects_water_emergency_keywords() -> None:
    normalized = IntakeNormalizationService().normalize(
        raw_payload(title="Water Emergency - extraction and drying", description="moisture check"),
    )

    assert normalized.water_emergency.detected
    assert "water emergency" in normalized.water_emergency.keyword_matches
    assert "extraction" in normalized.water_emergency.keyword_matches


def test_validation_detects_missing_required_fields_and_malformed_address() -> None:
    normalized = IntakeNormalizationService().normalize(
        raw_payload(customer_name=None, location="No street number", scheduled_date=None),
    )
    result = IntakeValidationService().validate(normalized)

    assert not result.is_valid
    assert not result.is_dispatch_safe
    assert result.issue_codes == (
        "MISSING_CUSTOMER_NAME",
        "MISSING_SCHEDULED_DATE",
        "MALFORMED_LOCATION",
    )
    assert result.highest_severity == IssueSeverity.ERROR


def test_validation_detects_conflicting_state_and_time_markers() -> None:
    normalized = IntakeNormalizationService().normalize(
        raw_payload(title="AM/DE PM/NJ carpet cleaning"),
    )
    result = IntakeValidationService().validate(normalized)

    assert not result.is_valid
    assert not result.is_dispatch_safe
    assert "CONFLICTING_STATE_MARKERS" in result.issue_codes
    assert "CONFLICTING_TIME_WINDOWS" in result.issue_codes
    assert result.highest_severity == IssueSeverity.CRITICAL


def test_confidence_scoring_is_deterministic_and_explainable() -> None:
    normalizer = IntakeNormalizationService()
    validator = IntakeValidationService()
    scorer = DeterministicConfidenceScoringService()

    clean = normalizer.normalize(raw_payload())
    clean_validation = validator.validate(clean)
    clean_score = scorer.score(clean, clean_validation)

    assert clean_score.score == 100
    assert clean_score.level == ConfidenceLevel.HIGH
    assert clean_score.factors == ("no_validation_issues",)

    unsafe = normalizer.normalize(raw_payload(title="cancelld - AM/DE carpet cleaning"))
    unsafe_validation = validator.validate(unsafe)
    unsafe_score = scorer.score(unsafe, unsafe_validation)

    assert unsafe_score.level == ConfidenceLevel.MANUAL_REVIEW
    assert unsafe_score.score < 75
    assert "CANCELLATION_DETECTED" in unsafe_score.factors


def test_review_recommendation_requires_manual_review_for_unsafe_intake() -> None:
    normalized = IntakeNormalizationService().normalize(
        raw_payload(title="Water damage extraction - AM/DE"),
    )
    validation = IntakeValidationService().validate(normalized)
    confidence = DeterministicConfidenceScoringService().score(normalized, validation)
    recommendation = ManualReviewPreparationService().prepare(
        normalized,
        validation,
        confidence,
    )

    assert recommendation.required
    assert recommendation.severity == IssueSeverity.WARNING
    assert recommendation.reason_codes == ("WATER_EMERGENCY_REQUIRES_WORKFLOW",)
    assert recommendation.recommended_action == "Send to Manual Review before dispatch."
