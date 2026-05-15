from datetime import UTC, date, datetime
from uuid import uuid4

from app.domain.intake import RawIntakePayload
from app.domain.operational_generation import (
    OperationalGenerationFailureCode,
    OperationalGenerationLifecycleState,
)
from app.models.intake_processing_record import IntakeProcessingRecord
from app.models.job import Job
from app.models.job_creation_record import JobCreationRecord
from app.models.visit import Visit
from app.models.work_order import WorkOrder
from app.services.dispatch.service import DispatchOrchestrationService
from app.services.operational_intake.service import OperationalIntakePersistenceService
from app.services.operational_jobs.service import OperationalJobCreationService
from app.services.operational_work.service import OperationalWorkGenerationService


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


class WorkOrderRepositoryStub:
    def __init__(self) -> None:
        self.added: list[WorkOrder] = []
        self.existing_by_job: dict[object, WorkOrder] = {}

    def add(self, work_order: WorkOrder) -> WorkOrder:
        self.added.append(work_order)
        return work_order

    def get_by_job_id(self, job_id):
        return self.existing_by_job.get(job_id)


class VisitRepositoryStub:
    def __init__(self) -> None:
        self.added: list[Visit] = []
        self.existing_by_work_order: dict[object, Visit] = {}

    def add(self, visit: Visit) -> Visit:
        self.added.append(visit)
        return visit

    def get_by_work_order_id(self, work_order_id):
        return self.existing_by_work_order.get(work_order_id)


def raw_payload(
    *,
    title: str = "AM/DE Carpet cleaning",
    scheduled_date: date | None = date(2026, 5, 16),
) -> RawIntakePayload:
    return RawIntakePayload(
        source_system="test_calendar",
        source_id="evt-123",
        title=title,
        customer_name="Acme Apartments",
        location="123 Main St Wilmington DE 19801",
        scheduled_date=scheduled_date,
        raw={"id": "evt-123", "summary": title},
    )


def approved_job_and_creation_record() -> tuple[Job, JobCreationRecord]:
    orchestration = DispatchOrchestrationService().process(raw_payload())
    intake_record = OperationalIntakePersistenceService(
        IntakeProcessingRecordRepositoryStub(),
        now=lambda: datetime(2026, 5, 15, 12, 0, tzinfo=UTC),
    ).persist_orchestration_result(orchestration)
    creation_result = OperationalJobCreationService(
        job_repository=JobRepositoryStub(),
        creation_repository=JobCreationRecordRepositoryStub(),
        now=lambda: datetime(2026, 5, 15, 13, 0, tzinfo=UTC),
    ).create_from_intake_record(intake_record)
    return creation_result.job, creation_result.creation_record


def generation_service(
    work_order_repository: WorkOrderRepositoryStub,
    visit_repository: VisitRepositoryStub,
) -> OperationalWorkGenerationService:
    return OperationalWorkGenerationService(
        work_order_repository=work_order_repository,
        visit_repository=visit_repository,
        now=lambda: datetime(2026, 5, 15, 14, 0, tzinfo=UTC),
    )


def test_approved_standard_job_creates_work_order_with_traceability() -> None:
    job, creation_record = approved_job_and_creation_record()
    work_order_repository = WorkOrderRepositoryStub()
    service = generation_service(work_order_repository, VisitRepositoryStub())

    result = service.create_work_order_from_job(job, creation_record)

    assert result.succeeded is True
    assert result.work_order in work_order_repository.added
    assert result.failure_reasons == ()
    assert result.lifecycle_state == OperationalGenerationLifecycleState.WORK_ORDER_CREATED

    work_order = result.work_order
    assert work_order.job_id == job.id
    assert work_order.job_creation_record_id == creation_record.id
    assert work_order.review_item_id == creation_record.review_item_id
    assert work_order.status == "awaiting_schedule"
    assert work_order.dispatch_status == "not_dispatched"
    assert work_order.audit_correlation_id == creation_record.audit_correlation_id
    assert work_order.deterministic_evidence_snapshot == (
        creation_record.deterministic_evidence_snapshot
    )
    assert work_order.orchestration_snapshot == creation_record.orchestration_snapshot
    assert work_order.generation_snapshot["work_order"]["status"] == "awaiting_schedule"
    assert result.traceability.job_id == job.id
    assert result.traceability.work_order_id == work_order.id
    assert result.traceability.job_creation_record_id == creation_record.id
    assert job.status == "work_order_created"
    assert job.notes == "Created from approved operational intake record."


def test_work_order_creates_visit_without_assignment_or_dispatch() -> None:
    job, creation_record = approved_job_and_creation_record()
    service = generation_service(WorkOrderRepositoryStub(), VisitRepositoryStub())
    work_order_result = service.create_work_order_from_job(job, creation_record)

    visit_result = service.create_visit_from_work_order(work_order_result.work_order)

    assert visit_result.succeeded is True
    assert visit_result.visit in service.visit_repository.added
    assert visit_result.failure_reasons == ()
    assert visit_result.lifecycle_state == OperationalGenerationLifecycleState.VISIT_CREATED

    visit = visit_result.visit
    assert visit.job_id == job.id
    assert visit.work_order_id == work_order_result.work_order.id
    assert visit.status == "awaiting_assignment"
    assert visit.visit_type == "standard"
    assert visit.technician_id is None
    assert visit.scheduled_start_at is None
    assert visit.audit_correlation_id == creation_record.audit_correlation_id
    assert visit.deterministic_evidence_snapshot == (
        work_order_result.work_order.deterministic_evidence_snapshot
    )
    assert visit.generation_snapshot["visit"]["status"] == "awaiting_assignment"
    assert work_order_result.work_order.status == "visit_created"
    assert (
        work_order_result.work_order.lifecycle_metadata["visit_generation_state"] == "visit_created"
    )


def test_blocked_job_cannot_create_work_order() -> None:
    job, creation_record = approved_job_and_creation_record()
    job.status = "blocked"
    work_order_repository = WorkOrderRepositoryStub()

    result = generation_service(
        work_order_repository,
        VisitRepositoryStub(),
    ).create_work_order_from_job(job, creation_record)

    assert result.succeeded is False
    assert result.work_order is None
    assert OperationalGenerationFailureCode.BLOCKED_JOB in result.failure_codes
    assert work_order_repository.added == []


def test_review_required_job_cannot_create_work_order() -> None:
    job, creation_record = approved_job_and_creation_record()
    job.review_status = "requires_review"

    result = generation_service(
        WorkOrderRepositoryStub(),
        VisitRepositoryStub(),
    ).create_work_order_from_job(job, creation_record)

    assert result.succeeded is False
    assert OperationalGenerationFailureCode.REVIEW_REQUIRED_JOB in result.failure_codes


def test_water_emergency_job_cannot_use_standard_work_order_path() -> None:
    job, creation_record = approved_job_and_creation_record()
    job.job_type = "water_emergency"

    result = generation_service(
        WorkOrderRepositoryStub(),
        VisitRepositoryStub(),
    ).create_work_order_from_job(job, creation_record)

    assert result.succeeded is False
    assert OperationalGenerationFailureCode.WATER_EMERGENCY_JOB in result.failure_codes
    assert result.evidence.failure_reasons[0].code == (
        OperationalGenerationFailureCode.WATER_EMERGENCY_JOB
    )


def test_duplicate_work_order_generation_is_prevented() -> None:
    job, creation_record = approved_job_and_creation_record()
    existing_work_order = WorkOrder(
        id=uuid4(),
        job_id=job.id,
        status="awaiting_schedule",
        audit_correlation_id=creation_record.audit_correlation_id,
    )
    work_order_repository = WorkOrderRepositoryStub()
    work_order_repository.existing_by_job[job.id] = existing_work_order

    result = generation_service(
        work_order_repository,
        VisitRepositoryStub(),
    ).create_work_order_from_job(job, creation_record)

    assert result.succeeded is False
    assert result.existing_work_order is existing_work_order
    assert result.failure_codes == (
        OperationalGenerationFailureCode.DUPLICATE_WORK_ORDER_GENERATION,
    )
    assert work_order_repository.added == []


def test_duplicate_visit_generation_is_prevented() -> None:
    job, creation_record = approved_job_and_creation_record()
    service = generation_service(WorkOrderRepositoryStub(), VisitRepositoryStub())
    work_order_result = service.create_work_order_from_job(job, creation_record)
    existing_visit = Visit(
        id=uuid4(),
        job_id=job.id,
        work_order_id=work_order_result.work_order.id,
        status="awaiting_assignment",
    )
    service.visit_repository.existing_by_work_order[work_order_result.work_order.id] = (
        existing_visit
    )

    result = service.create_visit_from_work_order(work_order_result.work_order)

    assert result.succeeded is False
    assert result.existing_visit is existing_visit
    assert result.failure_codes == (OperationalGenerationFailureCode.DUPLICATE_VISIT_GENERATION,)
    assert service.visit_repository.added == []


def test_generation_audit_logs_preserve_correlation() -> None:
    job, creation_record = approved_job_and_creation_record()
    service = generation_service(WorkOrderRepositoryStub(), VisitRepositoryStub())
    work_order_result = service.create_work_order_from_job(job, creation_record)
    visit_result = service.create_visit_from_work_order(work_order_result.work_order)

    work_order_audit = OperationalWorkGenerationService.build_work_order_generated_audit_log(
        work_order_result.work_order,
    )
    visit_audit = OperationalWorkGenerationService.build_visit_generated_audit_log(
        visit_result.visit,
    )

    assert work_order_audit.action == "operational_work_order.generated"
    assert work_order_audit.entity_type == "work_order"
    assert work_order_audit.entity_id == work_order_result.work_order.id
    assert work_order_audit.audit_correlation_id == creation_record.audit_correlation_id
    assert work_order_audit.details["job_creation_record_id"] == str(creation_record.id)

    assert visit_audit.action == "operational_visit.generated"
    assert visit_audit.entity_type == "visit"
    assert visit_audit.entity_id == visit_result.visit.id
    assert visit_audit.audit_correlation_id == creation_record.audit_correlation_id
    assert visit_audit.details["work_order_id"] == str(work_order_result.work_order.id)
