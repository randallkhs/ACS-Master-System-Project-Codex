from datetime import UTC, date, datetime
from uuid import uuid4

from app.domain.intake import RawIntakePayload
from app.domain.job_creation import JobCreationFailureCode, JobCreationLifecycleState
from app.domain.operational_intake import OperationalLifecycleState
from app.models.intake_processing_record import IntakeProcessingRecord
from app.models.job import Job
from app.models.job_creation_record import JobCreationRecord
from app.services.dispatch.service import DispatchOrchestrationService
from app.services.operational_intake.service import OperationalIntakePersistenceService
from app.services.operational_jobs.service import OperationalJobCreationService


class IntakeProcessingRecordRepositoryStub:
    def __init__(self) -> None:
        self.added: list[IntakeProcessingRecord] = []

    def add(self, record: IntakeProcessingRecord) -> IntakeProcessingRecord:
        self.added.append(record)
        return record


class JobRepositoryStub:
    def __init__(self) -> None:
        self.added: list[Job] = []

    def add(self, job: Job) -> Job:
        self.added.append(job)
        return job


class JobCreationRecordRepositoryStub:
    def __init__(self) -> None:
        self.added: list[JobCreationRecord] = []
        self.existing_by_intake: dict[object, JobCreationRecord] = {}

    def add(self, record: JobCreationRecord) -> JobCreationRecord:
        self.added.append(record)
        return record

    def get_by_intake_processing_record_id(self, intake_processing_record_id):
        return self.existing_by_intake.get(intake_processing_record_id)


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


def approved_intake_record() -> IntakeProcessingRecord:
    return persisted_intake_record(raw_payload())


def persisted_intake_record(payload: RawIntakePayload) -> IntakeProcessingRecord:
    orchestration = DispatchOrchestrationService().process(payload)
    return OperationalIntakePersistenceService(
        IntakeProcessingRecordRepositoryStub(),
        now=lambda: datetime(2026, 5, 15, 12, 0, tzinfo=UTC),
    ).persist_orchestration_result(orchestration)


def creation_service(
    job_repository: JobRepositoryStub,
    creation_repository: JobCreationRecordRepositoryStub,
) -> OperationalJobCreationService:
    return OperationalJobCreationService(
        job_repository=job_repository,
        creation_repository=creation_repository,
        now=lambda: datetime(2026, 5, 15, 13, 0, tzinfo=UTC),
    )


def test_approved_intake_creates_job_and_creation_record() -> None:
    intake_record = approved_intake_record()
    job_repository = JobRepositoryStub()
    creation_repository = JobCreationRecordRepositoryStub()

    result = creation_service(job_repository, creation_repository).create_from_intake_record(
        intake_record,
    )

    assert result.succeeded is True
    assert result.job in job_repository.added
    assert result.creation_record in creation_repository.added
    assert result.failure_reasons == ()
    assert result.lifecycle_state == JobCreationLifecycleState.AWAITING_DISPATCH

    job = result.job
    creation_record = result.creation_record

    assert job.status == "awaiting_dispatch"
    assert job.review_status == "approved"
    assert job.source_system == "test_calendar"
    assert job.source_event_id == "evt-123"
    assert job.scheduled_date == date(2026, 5, 16)
    assert job.description == "AM/DE Carpet cleaning"

    assert creation_record.intake_processing_record_id == intake_record.id
    assert creation_record.job_id == job.id
    assert creation_record.lifecycle_state == JobCreationLifecycleState.AWAITING_DISPATCH
    assert creation_record.audit_correlation_id == intake_record.audit_correlation_id
    assert creation_record.creation_snapshot["job"]["status"] == "awaiting_dispatch"
    assert creation_record.deterministic_evidence_snapshot == (
        intake_record.deterministic_evidence_snapshot
    )
    assert result.traceability.intake_processing_record_id == intake_record.id
    assert result.traceability.job_id == job.id
    assert intake_record.lifecycle_state == OperationalLifecycleState.JOB_CREATED
    assert intake_record.lifecycle_metadata["job_creation_state"] == "job_created"


def test_blocked_intake_fails_job_creation() -> None:
    intake_record = persisted_intake_record(raw_payload(title="Canceled - AM/DE carpet cleaning"))
    job_repository = JobRepositoryStub()
    creation_repository = JobCreationRecordRepositoryStub()

    result = creation_service(job_repository, creation_repository).create_from_intake_record(
        intake_record,
    )

    assert result.succeeded is False
    assert result.job is None
    assert result.creation_record is None
    assert JobCreationFailureCode.BLOCKED_INTAKE in result.failure_codes
    assert JobCreationFailureCode.UNSAFE_INTAKE in result.failure_codes
    assert job_repository.added == []
    assert creation_repository.added == []
    assert intake_record.lifecycle_state == OperationalLifecycleState.REVIEW_REQUIRED


def test_water_emergency_intake_cannot_create_standard_job() -> None:
    intake_record = persisted_intake_record(raw_payload(title="Water Emergency extraction - AM/DE"))
    result = creation_service(
        JobRepositoryStub(),
        JobCreationRecordRepositoryStub(),
    ).create_from_intake_record(intake_record)

    assert result.succeeded is False
    assert JobCreationFailureCode.WATER_EMERGENCY_SEPARATED in result.failure_codes
    assert (
        result.evidence.failure_reasons[0].code == JobCreationFailureCode.WATER_EMERGENCY_SEPARATED
    )


def test_review_required_intake_cannot_create_job_without_resolution() -> None:
    intake_record = approved_intake_record()
    intake_record.lifecycle_state = OperationalLifecycleState.REVIEW_REQUIRED
    intake_record.dispatch_eligible = False
    intake_record.requires_review = True
    intake_record.blocked = True

    result = creation_service(
        JobRepositoryStub(),
        JobCreationRecordRepositoryStub(),
    ).create_from_intake_record(intake_record)

    assert result.succeeded is False
    assert JobCreationFailureCode.REVIEW_REQUIRED in result.failure_codes
    assert JobCreationFailureCode.INVALID_LIFECYCLE in result.failure_codes


def test_inconsistent_dispatch_eligibility_blocks_job_creation() -> None:
    intake_record = approved_intake_record()
    intake_record.dispatch_eligible = False

    result = creation_service(
        JobRepositoryStub(),
        JobCreationRecordRepositoryStub(),
    ).create_from_intake_record(intake_record)

    assert result.succeeded is False
    assert result.failure_codes == (JobCreationFailureCode.INVALID_LIFECYCLE,)
    assert result.failure_reasons[0].metadata["dispatch_eligible"] is False


def test_duplicate_job_creation_is_prevented_for_same_intake_record() -> None:
    intake_record = approved_intake_record()
    existing_creation = JobCreationRecord(
        id=uuid4(),
        intake_processing_record_id=intake_record.id,
        job_id=uuid4(),
        lifecycle_state=JobCreationLifecycleState.AWAITING_DISPATCH,
        audit_correlation_id=intake_record.audit_correlation_id,
    )
    job_repository = JobRepositoryStub()
    creation_repository = JobCreationRecordRepositoryStub()
    creation_repository.existing_by_intake[intake_record.id] = existing_creation

    result = creation_service(job_repository, creation_repository).create_from_intake_record(
        intake_record,
    )

    assert result.succeeded is False
    assert result.existing_creation_record is existing_creation
    assert result.failure_codes == (JobCreationFailureCode.DUPLICATE_JOB_CREATION,)
    assert job_repository.added == []
    assert creation_repository.added == []


def test_missing_intake_linkage_blocks_job_creation() -> None:
    intake_record = approved_intake_record()
    intake_record.id = None

    result = creation_service(
        JobRepositoryStub(),
        JobCreationRecordRepositoryStub(),
    ).create_from_intake_record(intake_record)

    assert result.succeeded is False
    assert JobCreationFailureCode.MISSING_INTAKE_LINKAGE in result.failure_codes


def test_job_creation_audit_log_preserves_traceability() -> None:
    intake_record = approved_intake_record()
    result = creation_service(
        JobRepositoryStub(),
        JobCreationRecordRepositoryStub(),
    ).create_from_intake_record(intake_record)

    audit_log = OperationalJobCreationService.build_job_created_audit_log(
        result.creation_record,
    )

    assert audit_log.action == "operational_job.created"
    assert audit_log.entity_type == "job_creation_record"
    assert audit_log.entity_id == result.creation_record.id
    assert audit_log.audit_correlation_id == intake_record.audit_correlation_id
    assert audit_log.details["intake_processing_record_id"] == str(intake_record.id)
    assert audit_log.details["job_id"] == str(result.job.id)
    assert audit_log.details["lifecycle_state"] == "awaiting_dispatch"


def test_creation_lifecycle_can_advance_to_awaiting_routing_without_dispatch() -> None:
    intake_record = approved_intake_record()
    service = creation_service(JobRepositoryStub(), JobCreationRecordRepositoryStub())
    result = service.create_from_intake_record(intake_record)

    service.mark_awaiting_routing(result.creation_record)

    assert result.creation_record.lifecycle_state == JobCreationLifecycleState.AWAITING_ROUTING
    assert result.creation_record.lifecycle_metadata["routing_state"] == "awaiting_routing"
    assert result.job.status == "awaiting_dispatch"
