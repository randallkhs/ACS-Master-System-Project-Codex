from datetime import UTC, date, datetime, timedelta

import pytest

from app.domain.intake import RawIntakePayload
from app.domain.manual_review import IntakeProcessingState, ReviewStatus
from app.models.review_item import ReviewItem
from app.services.confidence.service import DeterministicConfidenceScoringService
from app.services.manual_review.audit import ReviewAuditTraceBuilder
from app.services.manual_review.service import ManualReviewQueueService
from app.services.manual_review.transitions import ReviewStateTransitionService
from app.services.normalization.service import IntakeNormalizationService
from app.services.validation.service import IntakeValidationService


class ReviewRepositoryStub:
    def __init__(self) -> None:
        self.added: list[ReviewItem] = []

    def add(self, item: ReviewItem) -> ReviewItem:
        self.added.append(item)
        return item


def build_review_item(title: str) -> ReviewItem:
    payload = RawIntakePayload(
        source_system="test_calendar",
        source_id="evt-456",
        title=title,
        customer_name="Acme Apartments",
        location="123 Main St Wilmington DE 19801",
        scheduled_date=date(2026, 5, 16),
        raw={"id": "evt-456", "summary": title},
    )
    normalized = IntakeNormalizationService().normalize(payload)
    validation = IntakeValidationService().validate(normalized)
    confidence = DeterministicConfidenceScoringService().score(normalized, validation)
    repository = ReviewRepositoryStub()
    return ManualReviewQueueService(repository).create_from_intake(
        normalized,
        validation,
        confidence,
    )


def test_review_item_creation_persists_traceable_queue_fields() -> None:
    repository = ReviewRepositoryStub()
    payload = RawIntakePayload(
        source_system="test_calendar",
        source_id="evt-water",
        title="Water damage extraction - AM/DE",
        customer_name="Acme Apartments",
        location="123 Main St Wilmington DE 19801",
        scheduled_date=date(2026, 5, 16),
        raw={"id": "evt-water", "summary": "Water damage extraction - AM/DE"},
    )
    normalized = IntakeNormalizationService().normalize(payload)
    validation = IntakeValidationService().validate(normalized)
    confidence = DeterministicConfidenceScoringService().score(normalized, validation)

    item = ManualReviewQueueService(repository).create_from_intake(
        normalized,
        validation,
        confidence,
    )

    assert repository.added == [item]
    assert item.status == ReviewStatus.OPEN
    assert item.intake_processing_state == IntakeProcessingState.FLAGGED_FOR_REVIEW
    assert item.severity == "warning"
    assert item.reason_code == "WATER_EMERGENCY_REQUIRES_WORKFLOW"
    assert item.review_reasons[0] == {
        "code": "WATER_EMERGENCY_REQUIRES_WORKFLOW",
        "category": "water_emergency_review",
        "severity": "warning",
    }
    assert {reason["category"] for reason in item.review_reasons} == {
        "water_emergency_review",
        "unsafe_dispatch_review",
    }
    assert item.confidence_snapshot["score"] == confidence.score
    assert item.source_system == "test_calendar"
    assert item.source_id == "evt-water"
    assert item.review_metadata["dispatch_blocked"] is True
    assert item.normalization_snapshot["water_emergency"]["detected"] is True
    assert item.validation_snapshot["issue_codes"] == ["WATER_EMERGENCY_REQUIRES_WORKFLOW"]
    assert item.warning_snapshot["issue_count"] == 1
    assert item.audit_correlation_id


def test_cancellation_review_escalates_to_critical_and_blocks_dispatch() -> None:
    item = build_review_item("cancelld - AM/DE carpet cleaning")

    assert item.severity == "critical"
    assert item.reason_code == "CANCELLATION_DETECTED"
    assert item.review_reasons[0]["category"] == "cancellation_review"
    assert item.review_metadata["dispatch_blocked"] is True
    assert item.recommended_action == "Send to Manual Review before dispatch."


def test_state_transition_approve_requires_operator_decision() -> None:
    item = build_review_item("Water damage extraction - AM/DE")
    item.deferred_until = datetime(2026, 5, 15, 16, 0, tzinfo=UTC)
    transition_service = ReviewStateTransitionService(
        now=lambda: datetime(2026, 5, 15, 12, 0, tzinfo=UTC),
    )

    with pytest.raises(ValueError):
        transition_service.approve(item, operator_decision="")

    transition_service.approve(
        item,
        operator_decision="Reviewed and safe for next workflow step.",
        operator_notes="Confirmed by dispatcher.",
    )

    assert item.status == ReviewStatus.APPROVED
    assert item.intake_processing_state == IntakeProcessingState.APPROVED
    assert item.operator_decision == "Reviewed and safe for next workflow step."
    assert item.operator_notes == "Confirmed by dispatcher."
    assert item.reviewed_at == datetime(2026, 5, 15, 12, 0, tzinfo=UTC)
    assert item.deferred_until is None
    assert item.resolved_at == datetime(2026, 5, 15, 12, 0, tzinfo=UTC)


def test_state_transition_defer_records_deferred_until_and_keeps_item_unresolved() -> None:
    item = build_review_item("Water damage extraction - AM/DE")
    now = datetime(2026, 5, 15, 12, 0, tzinfo=UTC)
    transition_service = ReviewStateTransitionService(now=lambda: now)
    deferred_until = now + timedelta(hours=4)

    transition_service.defer(
        item,
        operator_decision="Need property manager confirmation.",
        deferred_until=deferred_until,
    )

    assert item.status == ReviewStatus.DEFERRED
    assert item.intake_processing_state == IntakeProcessingState.DEFERRED
    assert item.deferred_until == deferred_until
    assert item.resolved_at is None


def test_audit_traceability_includes_flagging_evidence() -> None:
    item = build_review_item("AM/DE PM/NJ carpet cleaning")
    audit_log = ReviewAuditTraceBuilder().build_flagged_log(item)

    assert audit_log.action == "manual_review.flagged"
    assert audit_log.entity_type == "review_item"
    assert audit_log.entity_id == item.id
    assert audit_log.audit_correlation_id == item.audit_correlation_id
    assert audit_log.details["why_flagged"] == item.review_reasons
    assert audit_log.details["validation_evidence"] == item.validation_snapshot
    assert audit_log.details["normalization_evidence"] == item.normalization_snapshot
    assert audit_log.details["confidence_explanation"] == item.confidence_snapshot
    assert audit_log.details["deterministic_reason_codes"] == item.review_reasons
