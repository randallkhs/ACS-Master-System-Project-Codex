from collections.abc import Callable
from datetime import UTC, datetime
from uuid import uuid4

from app.domain.intake import RawIntakePayload
from app.domain.operational_intake import OperationalLifecycleState
from app.models.audit_log import AuditLog
from app.models.intake_processing_record import IntakeProcessingRecord
from app.models.review_item import ReviewItem
from app.repositories.intake_processing_records import IntakeProcessingRecordRepository


class OperationalIntakePersistenceService:
    def __init__(
        self,
        repository: IntakeProcessingRecordRepository,
        *,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self.repository = repository
        self.now = now or (lambda: datetime.now(UTC))

    def persist_orchestration_result(
        self,
        orchestration_result,
        *,
        review_item: ReviewItem | None = None,
        audit_correlation_id: str | None = None,
    ) -> IntakeProcessingRecord:
        eligibility = orchestration_result.decision.dispatch_eligibility
        lifecycle_state = lifecycle_state_from_orchestration(orchestration_result)
        correlation_id = (
            review_item.audit_correlation_id
            if review_item and review_item.audit_correlation_id
            else audit_correlation_id or str(uuid4())
        )
        approved_at = (
            self.now()
            if lifecycle_state == OperationalLifecycleState.APPROVED_FOR_DISPATCH
            else None
        )
        record = IntakeProcessingRecord(
            id=uuid4(),
            source_system=orchestration_result.raw_payload.source_system,
            source_id=orchestration_result.raw_payload.source_id,
            lifecycle_state=lifecycle_state,
            orchestration_state=orchestration_result.state.value,
            review_item_id=review_item.id if review_item else None,
            audit_correlation_id=correlation_id,
            dispatch_eligible=eligibility.eligible_for_dispatch,
            requires_review=eligibility.requires_review,
            blocked=eligibility.blocked,
            unsafe=eligibility.unsafe,
            water_emergency_separated=eligibility.water_emergency_separated,
            raw_payload_snapshot=raw_payload_snapshot(orchestration_result.raw_payload),
            orchestration_result_snapshot=orchestration_result_snapshot(orchestration_result),
            dispatch_eligibility_snapshot=dispatch_eligibility_snapshot(orchestration_result),
            normalized_snapshot=orchestration_result.evidence.normalization,
            validation_snapshot=orchestration_result.evidence.validation,
            confidence_snapshot=orchestration_result.evidence.confidence,
            review_snapshot=orchestration_result.evidence.review,
            warning_snapshot=warning_snapshot(orchestration_result),
            deterministic_evidence_snapshot=deterministic_evidence_snapshot(orchestration_result),
            review_linkage_snapshot=review_linkage_snapshot(review_item),
            lifecycle_metadata={},
            approved_for_dispatch_at=approved_at,
        )
        return self.repository.add(record)

    def mark_approved_for_dispatch(
        self,
        record: IntakeProcessingRecord,
        *,
        review_resolved: bool = False,
    ) -> IntakeProcessingRecord:
        if record.water_emergency_separated:
            msg = "Water Emergency intake requires separated workflow"
            raise ValueError(msg)
        if record.unsafe:
            msg = "Unsafe intake cannot be approved for dispatch"
            raise ValueError(msg)
        if record.requires_review and not review_resolved:
            msg = "Review-required intake cannot be approved without review resolution"
            raise ValueError(msg)

        record.lifecycle_state = OperationalLifecycleState.APPROVED_FOR_DISPATCH
        record.dispatch_eligible = True
        record.blocked = False
        record.approved_for_dispatch_at = self.now()
        record.deferred_at = None
        return record

    def defer(
        self,
        record: IntakeProcessingRecord,
        *,
        reason: str | None = None,
    ) -> IntakeProcessingRecord:
        record.lifecycle_state = OperationalLifecycleState.DEFERRED
        record.dispatch_eligible = False
        record.blocked = True
        record.approved_for_dispatch_at = None
        record.deferred_at = self.now()
        metadata = dict(record.lifecycle_metadata or {})
        if reason:
            metadata["defer_reason"] = reason
        record.lifecycle_metadata = metadata
        return record

    def archive(
        self,
        record: IntakeProcessingRecord,
        *,
        reason: str | None = None,
    ) -> IntakeProcessingRecord:
        record.lifecycle_state = OperationalLifecycleState.ARCHIVED
        record.dispatch_eligible = False
        record.approved_for_dispatch_at = None
        record.archived_at = self.now()
        metadata = dict(record.lifecycle_metadata or {})
        if reason:
            metadata["archive_reason"] = reason
        record.lifecycle_metadata = metadata
        return record

    @staticmethod
    def build_persisted_audit_log(record: IntakeProcessingRecord) -> AuditLog:
        return AuditLog(
            action="intake_processing.persisted",
            entity_type="intake_processing_record",
            entity_id=record.id,
            audit_correlation_id=record.audit_correlation_id,
            details={
                "lifecycle_state": record.lifecycle_state,
                "source_system": record.source_system,
                "source_id": record.source_id,
                "orchestration_state": record.orchestration_state,
                "dispatch_eligible": record.dispatch_eligible,
                "requires_review": record.requires_review,
                "blocked": record.blocked,
                "unsafe": record.unsafe,
                "water_emergency_separated": record.water_emergency_separated,
                "review_item_id": str(record.review_item_id) if record.review_item_id else None,
            },
        )


def lifecycle_state_from_orchestration(orchestration_result) -> OperationalLifecycleState:
    eligibility = orchestration_result.decision.dispatch_eligibility
    if eligibility.deferred:
        return OperationalLifecycleState.DEFERRED
    if eligibility.requires_review:
        return OperationalLifecycleState.REVIEW_REQUIRED
    if eligibility.blocked:
        return OperationalLifecycleState.BLOCKED
    if eligibility.eligible_for_dispatch:
        return OperationalLifecycleState.APPROVED_FOR_DISPATCH
    return OperationalLifecycleState.VALIDATED


def raw_payload_snapshot(payload: RawIntakePayload) -> dict[str, object]:
    return {
        "source_system": payload.source_system,
        "source_id": payload.source_id,
        "title": payload.title,
        "customer_name": payload.customer_name,
        "location": payload.location,
        "scheduled_date": payload.scheduled_date.isoformat() if payload.scheduled_date else None,
        "description": payload.description,
        "raw": payload.raw,
    }


def orchestration_result_snapshot(orchestration_result) -> dict[str, object]:
    return {
        "state": orchestration_result.state.value,
        "orchestration_state": orchestration_result.decision.state.value,
        "warnings": [
            {
                "code": warning.code,
                "severity": warning.severity.value,
                "message": warning.message,
                "field_name": warning.field_name,
                "metadata": warning.metadata,
            }
            for warning in orchestration_result.warnings
        ],
        "deterministic_reason_codes": list(
            orchestration_result.decision.deterministic_reason_codes,
        ),
        "review_reasons": list(orchestration_result.decision.review_reasons),
    }


def dispatch_eligibility_snapshot(orchestration_result) -> dict[str, object]:
    eligibility = orchestration_result.decision.dispatch_eligibility
    return {
        "eligible_for_dispatch": eligibility.eligible_for_dispatch,
        "requires_review": eligibility.requires_review,
        "blocked": eligibility.blocked,
        "deferred": eligibility.deferred,
        "unsafe": eligibility.unsafe,
        "water_emergency_separated": eligibility.water_emergency_separated,
        "reason_codes": list(eligibility.reason_codes),
    }


def warning_snapshot(orchestration_result) -> dict[str, object]:
    return {
        "issue_count": len(orchestration_result.warnings),
        "warnings": [
            {
                "code": warning.code,
                "severity": warning.severity.value,
                "message": warning.message,
                "field_name": warning.field_name,
                "metadata": warning.metadata,
            }
            for warning in orchestration_result.warnings
        ],
    }


def deterministic_evidence_snapshot(orchestration_result) -> dict[str, object]:
    return {
        "normalization": orchestration_result.evidence.normalization,
        "validation": orchestration_result.evidence.validation,
        "confidence": orchestration_result.evidence.confidence,
        "review": orchestration_result.evidence.review,
        "decision": orchestration_result.evidence.decision,
    }


def review_linkage_snapshot(review_item: ReviewItem | None) -> dict[str, object] | None:
    if review_item is None:
        return None
    return {
        "review_item_id": str(review_item.id),
        "reason_code": review_item.reason_code,
        "audit_correlation_id": review_item.audit_correlation_id,
    }
