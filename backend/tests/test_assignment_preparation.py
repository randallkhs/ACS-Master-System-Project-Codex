from datetime import UTC, date, datetime

from app.domain.assignment_preparation import (
    AssignmentPreparationBlockerCode,
    AssignmentPreparationLifecycleState,
)
from app.domain.intake import RawIntakePayload
from app.models.intake_processing_record import IntakeProcessingRecord
from app.models.job import Job
from app.models.job_creation_record import JobCreationRecord
from app.models.technician import Technician
from app.models.visit import Visit
from app.models.work_order import WorkOrder
from app.services.assignment_preparation.service import AssignmentPreparationService
from app.services.dispatch.service import DispatchOrchestrationService
from app.services.operational_intake.service import OperationalIntakePersistenceService
from app.services.operational_jobs.service import OperationalJobCreationService
from app.services.operational_work.service import OperationalWorkGenerationService


class IntakeProcessingRecordRepositoryStub:
    def add(self, record: IntakeProcessingRecord) -> IntakeProcessingRecord:
        return record


class JobRepositoryStub:
    def add(self, job: Job) -> Job:
        return job


class JobCreationRecordRepositoryStub:
    def add(self, record: JobCreationRecord) -> JobCreationRecord:
        return record

    def get_by_intake_processing_record_id(self, intake_processing_record_id):
        return None


class WorkOrderRepositoryStub:
    def add(self, work_order: WorkOrder) -> WorkOrder:
        return work_order

    def get_by_job_id(self, job_id):
        return None


class VisitRepositoryStub:
    def add(self, visit: Visit) -> Visit:
        return visit

    def get_by_work_order_id(self, work_order_id):
        return None


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


def generated_standard_visit() -> tuple[Visit, WorkOrder, JobCreationRecord]:
    orchestration = DispatchOrchestrationService().process(raw_payload())
    intake_record = OperationalIntakePersistenceService(
        IntakeProcessingRecordRepositoryStub(),
        now=lambda: datetime(2026, 5, 15, 12, 0, tzinfo=UTC),
    ).persist_orchestration_result(orchestration)
    job_creation = OperationalJobCreationService(
        job_repository=JobRepositoryStub(),
        creation_repository=JobCreationRecordRepositoryStub(),
        now=lambda: datetime(2026, 5, 15, 13, 0, tzinfo=UTC),
    ).create_from_intake_record(intake_record)
    work_generation = OperationalWorkGenerationService(
        work_order_repository=WorkOrderRepositoryStub(),
        visit_repository=VisitRepositoryStub(),
        now=lambda: datetime(2026, 5, 15, 14, 0, tzinfo=UTC),
    )
    work_order_result = work_generation.create_work_order_from_job(
        job_creation.job,
        job_creation.creation_record,
    )
    visit_result = work_generation.create_visit_from_work_order(work_order_result.work_order)
    return visit_result.visit, work_order_result.work_order, job_creation.creation_record


def active_technician() -> Technician:
    return Technician(
        full_name="Luis Technician",
        is_active=True,
        availability_status="available",
        skills=["carpet_cleaning"],
        service_areas=["DE"],
        vehicle_label="Truck 1",
    )


def test_active_technician_prepares_visit_for_assignment_and_scheduling() -> None:
    visit, work_order, creation_record = generated_standard_visit()
    technician = active_technician()

    result = AssignmentPreparationService(
        now=lambda: datetime(2026, 5, 15, 15, 0, tzinfo=UTC),
    ).prepare_visit(visit, technician=technician)

    assert result.lifecycle_state == AssignmentPreparationLifecycleState.SCHEDULING_READY
    assert result.assignment_eligibility.eligible is True
    assert result.assignment_readiness.assignment_required is False
    assert result.technician_compatibility.compatible is True
    assert result.scheduling_readiness.ready is True
    assert result.scheduling_readiness.preferred_time_window == "AM"
    assert result.scheduling_readiness.service_states == ("DE",)
    assert result.traceability.visit_id == visit.id
    assert result.traceability.work_order_id == work_order.id
    assert result.traceability.audit_correlation_id == creation_record.audit_correlation_id

    assert visit.status == "scheduling_ready"
    assert visit.technician_id is None
    assert visit.scheduled_start_at is None
    assert visit.assignment_readiness_snapshot["eligible_for_assignment"] is True
    assert visit.technician_compatibility_snapshot["compatible"] is True
    assert visit.scheduling_readiness_snapshot["preferred_time_window"] == "AM"
    assert visit.operational_readiness_snapshot["lifecycle_state"] == "scheduling_ready"
    assert visit.lifecycle_metadata["assignment_preparation_state"] == "scheduling_ready"


def test_unassigned_visit_without_candidate_requires_assignment_before_scheduling() -> None:
    visit, _, _ = generated_standard_visit()

    result = AssignmentPreparationService(
        now=lambda: datetime(2026, 5, 15, 15, 0, tzinfo=UTC),
    ).prepare_visit(visit)

    assert result.lifecycle_state == AssignmentPreparationLifecycleState.ASSIGNMENT_REQUIRED
    assert result.assignment_eligibility.eligible is True
    assert result.assignment_readiness.assignment_required is True
    assert result.technician_compatibility.evaluated is False
    assert result.scheduling_readiness.ready is False
    assert AssignmentPreparationBlockerCode.ASSIGNMENT_REQUIRED in (
        result.scheduling_readiness.blocker_codes
    )
    assert visit.status == "assignment_required"
    assert visit.technician_id is None


def test_blocked_visit_cannot_be_prepared_for_assignment() -> None:
    visit, _, _ = generated_standard_visit()
    visit.status = "blocked"

    result = AssignmentPreparationService().prepare_visit(
        visit,
        technician=active_technician(),
    )

    assert result.lifecycle_state == AssignmentPreparationLifecycleState.BLOCKED
    assert result.assignment_eligibility.eligible is False
    assert AssignmentPreparationBlockerCode.BLOCKED_VISIT in result.blocker_codes
    assert result.scheduling_readiness.ready is False
    assert visit.status == "blocked"


def test_review_required_visit_cannot_be_prepared_for_assignment() -> None:
    visit, _, _ = generated_standard_visit()
    visit.status = "review_required"

    result = AssignmentPreparationService().prepare_visit(
        visit,
        technician=active_technician(),
    )

    assert result.lifecycle_state == AssignmentPreparationLifecycleState.REVIEW_REQUIRED
    assert result.assignment_eligibility.eligible is False
    assert AssignmentPreparationBlockerCode.REVIEW_REQUIRED in result.blocker_codes
    assert result.scheduling_readiness.ready is False


def test_water_emergency_visit_cannot_use_standard_assignment_path() -> None:
    visit, _, _ = generated_standard_visit()
    visit.visit_type = "water_emergency"

    result = AssignmentPreparationService().prepare_visit(
        visit,
        technician=active_technician(),
    )

    assert result.lifecycle_state == AssignmentPreparationLifecycleState.WATER_EMERGENCY_BLOCKED
    assert result.assignment_eligibility.eligible is False
    assert result.blocker_codes[0] == AssignmentPreparationBlockerCode.WATER_EMERGENCY_VISIT
    assert result.scheduling_readiness.ready is False


def test_inactive_technician_blocks_candidate_compatibility_without_assigning() -> None:
    visit, _, _ = generated_standard_visit()
    technician = active_technician()
    technician.is_active = False

    result = AssignmentPreparationService().prepare_visit(visit, technician=technician)

    assert result.lifecycle_state == AssignmentPreparationLifecycleState.ASSIGNMENT_REQUIRED
    assert result.assignment_eligibility.eligible is True
    assert result.technician_compatibility.compatible is False
    assert AssignmentPreparationBlockerCode.TECHNICIAN_INACTIVE in result.blocker_codes
    assert result.scheduling_readiness.ready is False
    assert visit.technician_id is None
    assert visit.status == "assignment_required"


def test_assignment_preparation_audit_log_preserves_traceability() -> None:
    visit, _, creation_record = generated_standard_visit()
    service = AssignmentPreparationService(
        now=lambda: datetime(2026, 5, 15, 15, 0, tzinfo=UTC),
    )
    service.prepare_visit(visit, technician=active_technician())

    audit_log = service.build_assignment_prepared_audit_log(visit)

    assert audit_log.action == "operational_assignment.prepared"
    assert audit_log.entity_type == "visit"
    assert audit_log.entity_id == visit.id
    assert audit_log.audit_correlation_id == creation_record.audit_correlation_id
    assert audit_log.details["lifecycle_state"] == "scheduling_ready"
    assert audit_log.details["assignment_eligible"] is True
    assert audit_log.details["scheduling_ready"] is True
