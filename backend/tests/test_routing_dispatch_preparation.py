from datetime import UTC, date, datetime
from uuid import uuid4

from app.domain.intake import RawIntakePayload
from app.domain.routing_dispatch_preparation import (
    RoutingDispatchBlockerCode,
    RoutingDispatchLifecycleState,
)
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
from app.services.routing_dispatch_preparation.service import RoutingDispatchPreparationService


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
        id=uuid4(),
        full_name="Luis Technician",
        is_active=True,
        availability_status="available",
        skills=["carpet_cleaning"],
        service_areas=["DE"],
        vehicle_label="Truck 1",
    )


def prepared_visit_with_active_technician() -> tuple[Visit, Technician, JobCreationRecord]:
    visit, _, creation_record = generated_standard_visit()
    technician = active_technician()
    AssignmentPreparationService(
        now=lambda: datetime(2026, 5, 15, 15, 0, tzinfo=UTC),
    ).prepare_visit(visit, technician=technician)
    return visit, technician, creation_record


def test_assigned_scheduled_visit_becomes_dispatch_ready_with_traceability() -> None:
    visit, technician, creation_record = prepared_visit_with_active_technician()
    visit.technician_id = technician.id
    visit.scheduled_start_at = datetime(2026, 5, 16, 9, 0, tzinfo=UTC)
    visit.scheduled_end_at = datetime(2026, 5, 16, 11, 0, tzinfo=UTC)

    result = RoutingDispatchPreparationService(
        now=lambda: datetime(2026, 5, 15, 16, 0, tzinfo=UTC),
    ).prepare_visit(visit, technician=technician)

    assert result.lifecycle_state == RoutingDispatchLifecycleState.DISPATCH_READY
    assert result.routing_readiness.ready is True
    assert result.dispatch_eligibility.eligible is True
    assert result.technician_readiness.ready is True
    assert result.visit_dispatch_readiness.ready is True
    assert result.traceability.visit_id == visit.id
    assert result.traceability.job_id == visit.job_id
    assert result.traceability.technician_id == technician.id
    assert result.traceability.audit_correlation_id == creation_record.audit_correlation_id

    assert visit.status == "dispatch_ready"
    assert visit.routing_readiness_snapshot["ready"] is True
    assert visit.dispatch_readiness_snapshot["eligible_for_dispatch"] is True
    assert visit.technician_readiness_snapshot["technician"]["is_active"] is True
    assert visit.visit_dispatch_readiness_snapshot["ready"] is True
    assert visit.lifecycle_metadata["routing_dispatch_preparation_state"] == "dispatch_ready"


def test_scheduling_ready_visit_without_assignment_is_routing_ready_not_dispatch_ready() -> None:
    visit, technician, _ = prepared_visit_with_active_technician()
    visit.scheduled_start_at = datetime(2026, 5, 16, 9, 0, tzinfo=UTC)

    result = RoutingDispatchPreparationService().prepare_visit(visit, technician=technician)

    assert result.lifecycle_state == RoutingDispatchLifecycleState.ROUTING_READY
    assert result.routing_readiness.ready is True
    assert result.dispatch_eligibility.eligible is False
    assert RoutingDispatchBlockerCode.UNASSIGNED_VISIT in result.dispatch_eligibility.blocker_codes
    assert visit.status == "routing_ready"


def test_assigned_visit_without_schedule_blocks_dispatch_readiness() -> None:
    visit, technician, _ = prepared_visit_with_active_technician()
    visit.technician_id = technician.id

    result = RoutingDispatchPreparationService().prepare_visit(visit, technician=technician)

    assert result.lifecycle_state == RoutingDispatchLifecycleState.ROUTING_READY
    assert result.routing_readiness.ready is True
    assert result.dispatch_eligibility.eligible is False
    assert RoutingDispatchBlockerCode.UNSCHEDULED_VISIT in result.dispatch_eligibility.blocker_codes
    assert visit.status == "routing_ready"


def test_blocked_visit_cannot_become_dispatch_ready() -> None:
    visit, technician, _ = prepared_visit_with_active_technician()
    visit.status = "blocked"
    visit.technician_id = technician.id
    visit.scheduled_start_at = datetime(2026, 5, 16, 9, 0, tzinfo=UTC)

    result = RoutingDispatchPreparationService().prepare_visit(visit, technician=technician)

    assert result.lifecycle_state == RoutingDispatchLifecycleState.BLOCKED
    assert result.dispatch_eligibility.eligible is False
    assert RoutingDispatchBlockerCode.BLOCKED_VISIT in result.blocker_codes
    assert visit.status == "blocked"


def test_inactive_technician_blocks_dispatch_readiness() -> None:
    visit, technician, _ = prepared_visit_with_active_technician()
    technician.is_active = False
    visit.technician_id = technician.id
    visit.scheduled_start_at = datetime(2026, 5, 16, 9, 0, tzinfo=UTC)

    result = RoutingDispatchPreparationService().prepare_visit(visit, technician=technician)

    assert result.lifecycle_state == RoutingDispatchLifecycleState.ROUTING_READY
    assert result.technician_readiness.ready is False
    assert result.dispatch_eligibility.eligible is False
    blocker_codes = result.dispatch_eligibility.blocker_codes
    assert RoutingDispatchBlockerCode.INACTIVE_TECHNICIAN in blocker_codes
    assert visit.status == "routing_ready"


def test_review_required_visit_blocks_dispatch_preparation() -> None:
    visit, technician, _ = prepared_visit_with_active_technician()
    visit.status = "review_required"
    visit.technician_id = technician.id
    visit.scheduled_start_at = datetime(2026, 5, 16, 9, 0, tzinfo=UTC)

    result = RoutingDispatchPreparationService().prepare_visit(visit, technician=technician)

    assert result.lifecycle_state == RoutingDispatchLifecycleState.REVIEW_REQUIRED
    assert result.dispatch_eligibility.eligible is False
    assert RoutingDispatchBlockerCode.REVIEW_REQUIRED in result.blocker_codes
    assert visit.status == "review_required"


def test_water_emergency_visit_blocks_standard_routing_dispatch_path() -> None:
    visit, technician, _ = prepared_visit_with_active_technician()
    visit.visit_type = "water_emergency"
    visit.technician_id = technician.id
    visit.scheduled_start_at = datetime(2026, 5, 16, 9, 0, tzinfo=UTC)

    result = RoutingDispatchPreparationService().prepare_visit(visit, technician=technician)

    assert result.lifecycle_state == RoutingDispatchLifecycleState.BLOCKED
    assert result.dispatch_eligibility.eligible is False
    assert result.blocker_codes[0] == RoutingDispatchBlockerCode.WATER_EMERGENCY_VISIT
    assert visit.status == "scheduling_ready"


def test_dispatch_preparation_audit_log_preserves_deterministic_evidence() -> None:
    visit, technician, creation_record = prepared_visit_with_active_technician()
    visit.technician_id = technician.id
    visit.scheduled_start_at = datetime(2026, 5, 16, 9, 0, tzinfo=UTC)
    service = RoutingDispatchPreparationService(
        now=lambda: datetime(2026, 5, 15, 16, 0, tzinfo=UTC),
    )
    service.prepare_visit(visit, technician=technician)

    audit_log = service.build_dispatch_prepared_audit_log(visit)

    assert audit_log.action == "operational_dispatch.prepared"
    assert audit_log.entity_type == "visit"
    assert audit_log.entity_id == visit.id
    assert audit_log.audit_correlation_id == creation_record.audit_correlation_id
    assert audit_log.details["lifecycle_state"] == "dispatch_ready"
    assert audit_log.details["routing_ready"] is True
    assert audit_log.details["eligible_for_dispatch"] is True
    assert audit_log.details["dispatch_execution"] == "not_executed"
