from datetime import UTC, date, datetime
from uuid import uuid4

import pytest

from app.domain.intake import RawIntakePayload
from app.domain.operational_intake import OperationalLifecycleState
from app.models.intake_processing_record import IntakeProcessingRecord
from app.models.review_item import ReviewItem
from app.services.dispatch.service import DispatchOrchestrationService
from app.services.operational_intake.service import OperationalIntakePersistenceService


class IntakeProcessingRecordRepositoryStub:
    def __init__(self) -> None:
        self.added: list[IntakeProcessingRecord] = []

    def add(self, record: IntakeProcessingRecord) -> IntakeProcessingRecord:
        self.added.append(record)
        return record


def raw_payload(
    *,
    title: str = "AM/DE Carpet cleaning",
    customer_name: str | None = "Acme Apartments",
    location: str | None = "123 Main St Wilmington DE 19801",
    scheduled_date: date | None = date(2026, 5, 16),
) -> RawIntakePayload:
    return RawIntakePayload(
        source_system="test_calendar",
        source_id="evt-123",
        title=title,
        customer_name=customer_name,
        location=location,
        scheduled_date=scheduled_date,
        raw={"id": "evt-123", "summary": title},
    )


def persistence_service(
    repository: IntakeProcessingRecordRepositoryStub,
) -> OperationalIntakePersistenceService:
    return OperationalIntakePersistenceService(
        repository,
        now=lambda: datetime(2026, 5, 15, 12, 0, tzinfo=UTC),
    )


def orchestrate(payload: RawIntakePayload):
    return DispatchOrchestrationService().process(payload)


def test_persist_orchestration_outcome_creates_dispatch_approved_intake_record() -> None:
    repository = IntakeProcessingRecordRepositoryStub()
    result = orchestrate(raw_payload())

    record = persistence_service(repository).persist_orchestration_result(result)

    assert repository.added == [record]
    assert record.lifecycle_state == OperationalLifecycleState.APPROVED_FOR_DISPATCH
    assert record.orchestration_state == "eligible_for_dispatch"
    assert record.source_system == "test_calendar"
    assert record.source_id == "evt-123"
    assert record.review_item_id is None
    assert record.dispatch_eligible is True
    assert record.requires_review is False
    assert record.blocked is False
    assert record.unsafe is False
    assert record.water_emergency_separated is False
    assert record.dispatch_eligibility_snapshot["eligible_for_dispatch"] is True
    assert record.orchestration_result_snapshot["state"] == "eligible_for_dispatch"
    assert record.validation_snapshot["issue_codes"] == []
    assert record.confidence_snapshot["score"] == 100
    assert record.deterministic_evidence_snapshot["decision"]["state"] == "eligible_for_dispatch"
    assert record.approved_for_dispatch_at == datetime(2026, 5, 15, 12, 0, tzinfo=UTC)
    assert record.audit_correlation_id


def test_review_required_orchestration_can_link_to_review_item_and_correlation() -> None:
    repository = IntakeProcessingRecordRepositoryStub()
    result = orchestrate(raw_payload(title="Water Emergency extraction - AM/DE"))
    review_item_id = uuid4()
    review_item = ReviewItem(
        id=review_item_id,
        reason_code="WATER_EMERGENCY_REQUIRES_WORKFLOW",
        audit_correlation_id="review-correlation-123",
    )

    record = persistence_service(repository).persist_orchestration_result(
        result,
        review_item=review_item,
    )

    assert record.lifecycle_state == OperationalLifecycleState.REVIEW_REQUIRED
    assert record.review_item_id == review_item_id
    assert record.audit_correlation_id == "review-correlation-123"
    assert record.review_linkage_snapshot == {
        "review_item_id": str(review_item_id),
        "reason_code": "WATER_EMERGENCY_REQUIRES_WORKFLOW",
        "audit_correlation_id": "review-correlation-123",
    }
    assert record.dispatch_eligibility_snapshot["water_emergency_separated"] is True
    assert record.review_snapshot["required"] is True


def test_lifecycle_transition_helpers_defer_and_archive_records() -> None:
    repository = IntakeProcessingRecordRepositoryStub()
    record = persistence_service(repository).persist_orchestration_result(
        orchestrate(raw_payload()),
    )

    service = persistence_service(repository)
    service.defer(record, reason="Waiting for dispatcher confirmation.")

    assert record.lifecycle_state == OperationalLifecycleState.DEFERRED
    assert record.deferred_at == datetime(2026, 5, 15, 12, 0, tzinfo=UTC)
    assert record.lifecycle_metadata["defer_reason"] == "Waiting for dispatcher confirmation."
    assert record.approved_for_dispatch_at is None

    service.archive(record, reason="Imported during test cleanup.")

    assert record.lifecycle_state == OperationalLifecycleState.ARCHIVED
    assert record.archived_at == datetime(2026, 5, 15, 12, 0, tzinfo=UTC)
    assert record.lifecycle_metadata["archive_reason"] == "Imported during test cleanup."


def test_unsafe_records_cannot_be_marked_approved_for_dispatch() -> None:
    repository = IntakeProcessingRecordRepositoryStub()
    result = orchestrate(raw_payload(title="Canceled - AM/DE carpet cleaning"))
    record = persistence_service(repository).persist_orchestration_result(result)

    with pytest.raises(ValueError, match="Unsafe intake cannot be approved for dispatch"):
        persistence_service(repository).mark_approved_for_dispatch(
            record,
            review_resolved=True,
        )

    assert record.lifecycle_state == OperationalLifecycleState.REVIEW_REQUIRED
    assert record.approved_for_dispatch_at is None


def test_water_emergency_records_cannot_enter_standard_dispatch_approval() -> None:
    repository = IntakeProcessingRecordRepositoryStub()
    result = orchestrate(raw_payload(title="Water Emergency extraction - AM/DE"))
    record = persistence_service(repository).persist_orchestration_result(result)

    with pytest.raises(ValueError, match="Water Emergency intake requires separated workflow"):
        persistence_service(repository).mark_approved_for_dispatch(
            record,
            review_resolved=True,
        )

    assert record.lifecycle_state == OperationalLifecycleState.REVIEW_REQUIRED
    assert record.water_emergency_separated is True


def test_deterministic_evidence_persists_for_conflicting_intake() -> None:
    repository = IntakeProcessingRecordRepositoryStub()
    result = orchestrate(raw_payload(title="AM/DE PM/NJ carpet cleaning"))

    record = persistence_service(repository).persist_orchestration_result(result)

    assert record.lifecycle_state == OperationalLifecycleState.REVIEW_REQUIRED
    assert record.blocked is True
    assert record.unsafe is True
    assert record.validation_snapshot["issue_codes"] == [
        "CONFLICTING_STATE_MARKERS",
        "CONFLICTING_TIME_WINDOWS",
    ]
    assert record.warning_snapshot["issue_count"] == 2
    assert record.confidence_snapshot["level"] == "manual_review"
    assert record.orchestration_result_snapshot["deterministic_reason_codes"] == [
        "CONFLICTING_STATE_MARKERS",
        "CONFLICTING_TIME_WINDOWS",
        "UNSAFE_DISPATCH_BLOCKED",
    ]
    assert record.deterministic_evidence_snapshot["validation"] == record.validation_snapshot


def test_persisted_audit_log_uses_record_correlation_and_traceability() -> None:
    repository = IntakeProcessingRecordRepositoryStub()
    record = persistence_service(repository).persist_orchestration_result(
        orchestrate(raw_payload()),
    )

    audit_log = OperationalIntakePersistenceService.build_persisted_audit_log(record)

    assert audit_log.action == "intake_processing.persisted"
    assert audit_log.entity_type == "intake_processing_record"
    assert audit_log.entity_id == record.id
    assert audit_log.audit_correlation_id == record.audit_correlation_id
    assert audit_log.details["lifecycle_state"] == "approved_for_dispatch"
    assert audit_log.details["source_system"] == "test_calendar"
    assert audit_log.details["source_id"] == "evt-123"
    assert audit_log.details["orchestration_state"] == "eligible_for_dispatch"
