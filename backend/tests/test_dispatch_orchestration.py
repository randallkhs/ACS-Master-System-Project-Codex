from datetime import date

from app.domain.intake import ConfidenceLevel, IssueSeverity, RawIntakePayload
from app.domain.orchestration import OrchestrationState
from app.services.dispatch.service import DispatchOrchestrationService


def raw_payload(
    *,
    title: str = "AM/DE Carpet cleaning",
    customer_name: str | None = "Acme Apartments",
    location: str | None = "123 Main St Wilmington DE 19801",
    scheduled_date: date | None = date(2026, 5, 16),
    description: str | None = None,
) -> RawIntakePayload:
    return RawIntakePayload(
        source_system="test_calendar",
        source_id="evt-123",
        title=title,
        customer_name=customer_name,
        location=location,
        scheduled_date=scheduled_date,
        description=description,
        raw={"id": "evt-123", "summary": title},
    )


def orchestrate(payload: RawIntakePayload):
    return DispatchOrchestrationService().process(payload)


def test_valid_intake_flow_is_dispatch_eligible_without_review() -> None:
    result = orchestrate(raw_payload())

    assert result.state == OrchestrationState.ELIGIBLE_FOR_DISPATCH
    assert result.decision.state == OrchestrationState.ELIGIBLE_FOR_DISPATCH
    assert result.normalized.title == "AM/DE Carpet cleaning"
    assert result.validation.is_valid
    assert result.confidence.level == ConfidenceLevel.HIGH
    assert result.warnings == ()
    assert result.review_recommendation.required is False

    eligibility = result.decision.dispatch_eligibility
    assert eligibility.eligible_for_dispatch is True
    assert eligibility.requires_review is False
    assert eligibility.blocked is False
    assert eligibility.deferred is False
    assert eligibility.unsafe is False
    assert eligibility.water_emergency_separated is False
    assert eligibility.reason_codes == ()

    assert result.evidence.normalization["states"] == ["DE"]
    assert result.evidence.validation["issue_codes"] == []
    assert result.evidence.confidence["score"] == 100
    assert result.evidence.review["required"] is False
    assert result.evidence.decision["state"] == "eligible_for_dispatch"


def test_cancellation_flow_blocks_dispatch_and_requires_review() -> None:
    result = orchestrate(raw_payload(title="Canceled - AM/DE carpet cleaning"))

    assert result.state == OrchestrationState.REVIEW_REQUIRED
    assert result.review_recommendation.required is True
    assert result.decision.escalation_severity == IssueSeverity.CRITICAL
    assert [warning.code for warning in result.warnings] == ["CANCELLATION_DETECTED"]

    eligibility = result.decision.dispatch_eligibility
    assert eligibility.eligible_for_dispatch is False
    assert eligibility.requires_review is True
    assert eligibility.blocked is True
    assert eligibility.unsafe is True
    assert eligibility.reason_codes == (
        "CANCELLATION_DETECTED",
        "UNSAFE_DISPATCH_BLOCKED",
    )

    assert result.decision.review_reasons[0]["category"] == "cancellation_review"
    assert result.evidence.decision["dispatch_blocked"] is True


def test_malformed_intake_flow_preserves_validation_evidence() -> None:
    result = orchestrate(raw_payload(location="No street number"))

    assert result.state == OrchestrationState.REVIEW_REQUIRED
    assert result.decision.dispatch_eligibility.requires_review is True
    assert result.decision.dispatch_eligibility.unsafe is True
    assert result.decision.escalation_severity == IssueSeverity.ERROR
    assert result.review_recommendation.reason_codes == ("MALFORMED_LOCATION",)
    assert [warning.code for warning in result.warnings] == ["MALFORMED_LOCATION"]
    assert result.evidence.validation["issue_codes"] == ["MALFORMED_LOCATION"]


def test_water_emergency_flow_is_separated_from_standard_dispatch() -> None:
    result = orchestrate(raw_payload(title="Water Emergency extraction - AM/DE"))

    assert result.state == OrchestrationState.REVIEW_REQUIRED
    assert result.decision.dispatch_eligibility.eligible_for_dispatch is False
    assert result.decision.dispatch_eligibility.requires_review is True
    assert result.decision.dispatch_eligibility.blocked is True
    assert result.decision.dispatch_eligibility.water_emergency_separated is True
    assert result.review_recommendation.reason_codes == ("WATER_EMERGENCY_REQUIRES_WORKFLOW",)
    assert result.decision.review_reasons[0]["category"] == "water_emergency_review"
    assert result.evidence.normalization["water_emergency"]["detected"] is True
    assert result.evidence.decision["water_emergency_separated"] is True


def test_low_confidence_flow_preserves_low_confidence_review_reason() -> None:
    result = orchestrate(raw_payload(title="cancelld - AM/DE carpet cleaning"))

    assert result.confidence.level == ConfidenceLevel.MANUAL_REVIEW
    assert "LOW_CONFIDENCE_CANCELLATION_MATCH" in result.confidence.factors
    assert result.decision.dispatch_eligibility.requires_review is True
    assert result.decision.dispatch_eligibility.unsafe is True
    assert "LOW_CONFIDENCE_REVIEW" in result.decision.deterministic_reason_codes
    assert {reason["category"] for reason in result.decision.review_reasons} == {
        "cancellation_review",
        "low_confidence_review",
        "unsafe_dispatch_review",
    }


def test_conflicting_state_flow_blocks_dispatch_with_conflict_reasons() -> None:
    result = orchestrate(raw_payload(title="AM/DE PM/NJ carpet cleaning"))

    assert result.state == OrchestrationState.REVIEW_REQUIRED
    assert result.decision.dispatch_eligibility.eligible_for_dispatch is False
    assert result.decision.dispatch_eligibility.unsafe is True
    assert result.decision.escalation_severity == IssueSeverity.CRITICAL
    assert result.review_recommendation.reason_codes == (
        "CONFLICTING_STATE_MARKERS",
        "CONFLICTING_TIME_WINDOWS",
    )
    assert [warning.code for warning in result.warnings] == [
        "CONFLICTING_STATE_MARKERS",
        "CONFLICTING_TIME_WINDOWS",
    ]


def test_unsafe_dispatch_flow_blocks_missing_required_customer_data() -> None:
    result = orchestrate(raw_payload(customer_name=None))

    assert result.state == OrchestrationState.REVIEW_REQUIRED
    assert result.decision.dispatch_eligibility.eligible_for_dispatch is False
    assert result.decision.dispatch_eligibility.blocked is True
    assert result.decision.dispatch_eligibility.unsafe is True
    assert result.review_recommendation.reason_codes == ("MISSING_CUSTOMER_NAME",)
    assert result.evidence.validation["is_dispatch_safe"] is False


def test_review_required_flow_blocks_missing_schedule_before_dispatch() -> None:
    result = orchestrate(raw_payload(scheduled_date=None))

    assert result.state == OrchestrationState.REVIEW_REQUIRED
    assert result.decision.dispatch_eligibility.requires_review is True
    assert result.decision.dispatch_eligibility.eligible_for_dispatch is False
    assert result.decision.dispatch_eligibility.deferred is False
    assert result.review_recommendation.required is True
    assert result.review_recommendation.reason_codes == ("MISSING_SCHEDULED_DATE",)
    assert result.evidence.review["recommended_action"] == "Send to Manual Review before dispatch."
