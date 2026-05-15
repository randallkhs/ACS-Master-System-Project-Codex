from collections.abc import Callable
from datetime import UTC, date, datetime
from uuid import uuid4

from app.domain.job_creation import (
    JobCreationEvidence,
    JobCreationFailureCode,
    JobCreationFailureReason,
    JobCreationLifecycleState,
    JobCreationResult,
    JobCreationTraceability,
)
from app.domain.operational_intake import OperationalLifecycleState
from app.models.audit_log import AuditLog
from app.models.intake_processing_record import IntakeProcessingRecord
from app.models.job import Job
from app.models.job_creation_record import JobCreationRecord
from app.repositories.job_creation_records import JobCreationRecordRepository
from app.repositories.jobs import JobRepository


class OperationalJobCreationService:
    def __init__(
        self,
        *,
        job_repository: JobRepository,
        creation_repository: JobCreationRecordRepository,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self.job_repository = job_repository
        self.creation_repository = creation_repository
        self.now = now or (lambda: datetime.now(UTC))

    def create_from_intake_record(
        self,
        intake_record: IntakeProcessingRecord,
    ) -> JobCreationResult:
        duplicate_result = self._duplicate_result(intake_record)
        if duplicate_result is not None:
            return duplicate_result

        failure_reasons = creation_failure_reasons(intake_record)
        if failure_reasons:
            return failed_result(intake_record, failure_reasons)

        job = build_standard_job_from_intake(intake_record)
        creation_record = build_creation_record(intake_record, job, self.now())

        self.job_repository.add(job)
        self.creation_repository.add(creation_record)
        mark_intake_job_created(intake_record, creation_record)

        return JobCreationResult(
            succeeded=True,
            lifecycle_state=JobCreationLifecycleState.AWAITING_DISPATCH,
            job=job,
            creation_record=creation_record,
            traceability=traceability(intake_record, job, creation_record),
            evidence=JobCreationEvidence(
                intake_snapshot=creation_record.intake_snapshot,
                creation_snapshot=creation_record.creation_snapshot,
                deterministic_evidence=creation_record.deterministic_evidence_snapshot,
                review_linkage=creation_record.review_linkage_snapshot,
            ),
        )

    def _duplicate_result(
        self,
        intake_record: IntakeProcessingRecord,
    ) -> JobCreationResult | None:
        if intake_record.id is None:
            return None
        existing = self.creation_repository.get_by_intake_processing_record_id(intake_record.id)
        if existing is None:
            return None
        reason = JobCreationFailureReason(
            code=JobCreationFailureCode.DUPLICATE_JOB_CREATION,
            message="A job has already been created from this intake record.",
            metadata={"job_creation_record_id": str(existing.id)},
        )
        return JobCreationResult(
            succeeded=False,
            lifecycle_state=JobCreationLifecycleState.BLOCKED,
            existing_creation_record=existing,
            failure_reasons=(reason,),
            traceability=JobCreationTraceability(
                intake_processing_record_id=intake_record.id,
                job_id=existing.job_id,
                job_creation_record_id=existing.id,
                review_item_id=intake_record.review_item_id,
                audit_correlation_id=intake_record.audit_correlation_id,
            ),
            evidence=JobCreationEvidence(failure_reasons=(reason,)),
        )

    def mark_awaiting_routing(self, creation_record: JobCreationRecord) -> JobCreationRecord:
        creation_record.lifecycle_state = JobCreationLifecycleState.AWAITING_ROUTING
        metadata = dict(creation_record.lifecycle_metadata or {})
        metadata["routing_state"] = JobCreationLifecycleState.AWAITING_ROUTING.value
        creation_record.lifecycle_metadata = metadata
        return creation_record

    @staticmethod
    def build_job_created_audit_log(creation_record: JobCreationRecord) -> AuditLog:
        return AuditLog(
            action="operational_job.created",
            entity_type="job_creation_record",
            entity_id=creation_record.id,
            audit_correlation_id=creation_record.audit_correlation_id,
            details={
                "intake_processing_record_id": str(
                    creation_record.intake_processing_record_id,
                ),
                "job_id": str(creation_record.job_id),
                "review_item_id": str(creation_record.review_item_id)
                if creation_record.review_item_id
                else None,
                "lifecycle_state": enum_value(creation_record.lifecycle_state),
            },
        )


def creation_failure_reasons(
    intake_record: IntakeProcessingRecord,
) -> tuple[JobCreationFailureReason, ...]:
    reasons: list[JobCreationFailureReason] = []
    if intake_record.id is None:
        reasons.append(
            JobCreationFailureReason(
                code=JobCreationFailureCode.MISSING_INTAKE_LINKAGE,
                message="Intake record must have a durable ID before job creation.",
            ),
        )
    if intake_record.water_emergency_separated:
        reasons.append(
            JobCreationFailureReason(
                code=JobCreationFailureCode.WATER_EMERGENCY_SEPARATED,
                message="Water Emergency intake cannot create standard jobs.",
            ),
        )
    if (
        intake_record.lifecycle_state != OperationalLifecycleState.APPROVED_FOR_DISPATCH
        or not intake_record.dispatch_eligible
    ):
        reasons.append(
            JobCreationFailureReason(
                code=JobCreationFailureCode.INVALID_LIFECYCLE,
                message="Only approved intake records can create operational jobs.",
                metadata={
                    "dispatch_eligible": intake_record.dispatch_eligible,
                    "lifecycle_state": enum_value(intake_record.lifecycle_state),
                },
            ),
        )
    if intake_record.blocked:
        reasons.append(
            JobCreationFailureReason(
                code=JobCreationFailureCode.BLOCKED_INTAKE,
                message="Blocked intake cannot create operational jobs.",
            ),
        )
    if intake_record.requires_review:
        reasons.append(
            JobCreationFailureReason(
                code=JobCreationFailureCode.REVIEW_REQUIRED,
                message="Review-required intake cannot create operational jobs.",
            ),
        )
    if intake_record.unsafe:
        reasons.append(
            JobCreationFailureReason(
                code=JobCreationFailureCode.UNSAFE_INTAKE,
                message="Unsafe intake cannot create operational jobs.",
            ),
        )
    return tuple(reasons)


def failed_result(
    intake_record: IntakeProcessingRecord,
    failure_reasons: tuple[JobCreationFailureReason, ...],
) -> JobCreationResult:
    return JobCreationResult(
        succeeded=False,
        lifecycle_state=JobCreationLifecycleState.BLOCKED,
        failure_reasons=failure_reasons,
        traceability=JobCreationTraceability(
            intake_processing_record_id=intake_record.id,
            job_id=None,
            job_creation_record_id=None,
            review_item_id=intake_record.review_item_id,
            audit_correlation_id=intake_record.audit_correlation_id,
        ),
        evidence=JobCreationEvidence(
            intake_snapshot=intake_snapshot(intake_record),
            deterministic_evidence=intake_record.deterministic_evidence_snapshot,
            review_linkage=intake_record.review_linkage_snapshot,
            failure_reasons=failure_reasons,
        ),
    )


def build_standard_job_from_intake(intake_record: IntakeProcessingRecord) -> Job:
    payload = intake_record.raw_payload_snapshot or {}
    return Job(
        id=uuid4(),
        job_type="standard",
        status=JobCreationLifecycleState.AWAITING_DISPATCH.value,
        review_status="approved",
        scheduled_date=parse_date(payload.get("scheduled_date")),
        source_system=intake_record.source_system,
        source_event_id=intake_record.source_id,
        description=payload.get("title"),
        notes="Created from approved operational intake record.",
    )


def build_creation_record(
    intake_record: IntakeProcessingRecord,
    job: Job,
    timestamp: datetime,
) -> JobCreationRecord:
    return JobCreationRecord(
        id=uuid4(),
        intake_processing_record_id=intake_record.id,
        job_id=job.id,
        review_item_id=intake_record.review_item_id,
        lifecycle_state=JobCreationLifecycleState.AWAITING_DISPATCH,
        audit_correlation_id=intake_record.audit_correlation_id,
        creation_snapshot=creation_snapshot(intake_record, job),
        intake_snapshot=intake_snapshot(intake_record),
        orchestration_snapshot=intake_record.orchestration_result_snapshot,
        dispatch_eligibility_snapshot=intake_record.dispatch_eligibility_snapshot,
        review_linkage_snapshot=intake_record.review_linkage_snapshot,
        deterministic_evidence_snapshot=intake_record.deterministic_evidence_snapshot,
        lifecycle_metadata={},
        created_from_intake_at=timestamp,
    )


def mark_intake_job_created(
    intake_record: IntakeProcessingRecord,
    creation_record: JobCreationRecord,
) -> None:
    intake_record.lifecycle_state = OperationalLifecycleState.JOB_CREATED
    metadata = dict(intake_record.lifecycle_metadata or {})
    metadata["job_creation_state"] = OperationalLifecycleState.JOB_CREATED.value
    metadata["job_creation_record_id"] = str(creation_record.id)
    metadata["job_id"] = str(creation_record.job_id)
    intake_record.lifecycle_metadata = metadata


def traceability(
    intake_record: IntakeProcessingRecord,
    job: Job,
    creation_record: JobCreationRecord,
) -> JobCreationTraceability:
    return JobCreationTraceability(
        intake_processing_record_id=intake_record.id,
        job_id=job.id,
        job_creation_record_id=creation_record.id,
        review_item_id=intake_record.review_item_id,
        audit_correlation_id=intake_record.audit_correlation_id,
    )


def creation_snapshot(intake_record: IntakeProcessingRecord, job: Job) -> dict[str, object]:
    return {
        "job": {
            "id": str(job.id),
            "status": job.status,
            "job_type": job.job_type,
            "scheduled_date": job.scheduled_date.isoformat() if job.scheduled_date else None,
            "source_system": job.source_system,
            "source_event_id": job.source_event_id,
        },
        "intake": {
            "id": str(intake_record.id),
            "lifecycle_state": enum_value(intake_record.lifecycle_state),
            "audit_correlation_id": intake_record.audit_correlation_id,
        },
        "creation_rule": "approved_standard_intake_only",
    }


def intake_snapshot(intake_record: IntakeProcessingRecord) -> dict[str, object]:
    return {
        "id": str(intake_record.id) if intake_record.id else None,
        "source_system": intake_record.source_system,
        "source_id": intake_record.source_id,
        "lifecycle_state": enum_value(intake_record.lifecycle_state),
        "review_item_id": str(intake_record.review_item_id)
        if intake_record.review_item_id
        else None,
        "audit_correlation_id": intake_record.audit_correlation_id,
    }


def parse_date(value: object) -> date | None:
    if isinstance(value, date):
        return value
    if isinstance(value, str) and value:
        return date.fromisoformat(value)
    return None


def enum_value(value: object) -> object:
    return value.value if hasattr(value, "value") else value
