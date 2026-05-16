from datetime import UTC, date, datetime
from uuid import uuid4

from app.domain.dispatch_execution import (
    DispatchExecutionBlockerCode,
    DispatchExecutionState,
)
from app.domain.intake import RawIntakePayload
from app.models.intake_processing_record import IntakeProcessingRecord
from app.models.job import Job
from app.models.job_creation_record import JobCreationRecord
from app.models.route_assignment import RouteAssignment
from app.models.technician import Technician
from app.models.visit import Visit
from app.models.work_order import WorkOrder
from app.services.assignment_preparation.service import AssignmentPreparationService
from app.services.dispatch.service import DispatchOrchestrationService
from app.services.dispatch_execution.service import DispatchExecutionService
from app.services.operational_intake.service import OperationalIntakePersistenceService
from app.services.operational_jobs.service import OperationalJobCreationService
from app.services.operational_work.service import OperationalWorkGenerationService
from app.services.route_assignment_preparation.service import RouteAssignmentPreparationService
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


class RouteAssignmentRepositoryStub:
    def __init__(self) -> None:
        self.records: list[RouteAssignment] = []

    def add(self, route_assignment: RouteAssignment) -> RouteAssignment:
        self.records.append(route_assignment)
        return route_assignment

    def get_by_visit_id(self, visit_id):
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


def authorized_route_assignment() -> tuple[RouteAssignment, Visit, Technician, JobCreationRecord]:
    visit, _, creation_record = generated_standard_visit()
    technician = active_technician()
    AssignmentPreparationService(
        now=lambda: datetime(2026, 5, 15, 15, 0, tzinfo=UTC),
    ).prepare_visit(visit, technician=technician)
    visit.technician_id = technician.id
    visit.scheduled_start_at = datetime(2026, 5, 16, 9, 0, tzinfo=UTC)
    visit.scheduled_end_at = datetime(2026, 5, 16, 11, 0, tzinfo=UTC)
    RoutingDispatchPreparationService(
        now=lambda: datetime(2026, 5, 15, 16, 0, tzinfo=UTC),
    ).prepare_visit(visit, technician=technician)
    route_assignment_result = RouteAssignmentPreparationService(
        route_assignment_repository=RouteAssignmentRepositoryStub(),
        now=lambda: datetime(2026, 5, 15, 17, 0, tzinfo=UTC),
    ).prepare_route_assignment(visit, technician=technician)
    return route_assignment_result.route_assignment, visit, technician, creation_record


def test_dispatch_authorized_route_assignment_transitions_to_dispatched() -> None:
    route_assignment, visit, technician, creation_record = authorized_route_assignment()

    result = DispatchExecutionService(
        now=lambda: datetime(2026, 5, 15, 18, 0, tzinfo=UTC),
    ).execute_dispatch(route_assignment, visit=visit, technician=technician)

    assert result.succeeded is True
    assert result.state == DispatchExecutionState.DISPATCHED
    assert result.traceability.route_assignment_id == route_assignment.id
    assert result.traceability.visit_id == visit.id
    assert result.traceability.audit_correlation_id == creation_record.audit_correlation_id
    assert route_assignment.status == "dispatched"
    assert route_assignment.dispatch_execution_state == "dispatched"
    assert route_assignment.dispatched_at == datetime(2026, 5, 15, 18, 0, tzinfo=UTC)
    assert route_assignment.dispatch_execution_snapshot["external_integrations"] == "not_executed"
    assert route_assignment.dispatch_lifecycle_snapshot["previous_state"] == (
        "awaiting_dispatch_execution"
    )
    assert visit.status == "dispatched"
    assert visit.lifecycle_metadata["dispatch_execution"] == "executed_internal_only"


def test_blocked_visit_cannot_dispatch() -> None:
    route_assignment, visit, technician, _ = authorized_route_assignment()
    visit.status = "blocked"

    result = DispatchExecutionService().execute_dispatch(
        route_assignment,
        visit=visit,
        technician=technician,
    )

    assert result.succeeded is False
    assert result.state == DispatchExecutionState.DISPATCH_BLOCKED
    assert DispatchExecutionBlockerCode.BLOCKED_VISIT in result.blocker_codes
    assert route_assignment.status == "awaiting_dispatch_execution"


def test_review_required_visit_blocks_dispatch_execution() -> None:
    route_assignment, visit, technician, _ = authorized_route_assignment()
    visit.status = "review_required"

    result = DispatchExecutionService().execute_dispatch(
        route_assignment,
        visit=visit,
        technician=technician,
    )

    assert result.succeeded is False
    assert result.state == DispatchExecutionState.DISPATCH_BLOCKED
    assert DispatchExecutionBlockerCode.REVIEW_REQUIRED in result.blocker_codes


def test_water_emergency_visit_blocks_standard_dispatch_execution() -> None:
    route_assignment, visit, technician, _ = authorized_route_assignment()
    visit.visit_type = "water_emergency"

    result = DispatchExecutionService().execute_dispatch(
        route_assignment,
        visit=visit,
        technician=technician,
    )

    assert result.succeeded is False
    assert result.state == DispatchExecutionState.DISPATCH_BLOCKED
    assert result.blocker_codes[0] == DispatchExecutionBlockerCode.WATER_EMERGENCY_VISIT


def test_inactive_technician_blocks_dispatch_execution() -> None:
    route_assignment, visit, technician, _ = authorized_route_assignment()
    technician.is_active = False

    result = DispatchExecutionService().execute_dispatch(
        route_assignment,
        visit=visit,
        technician=technician,
    )

    assert result.succeeded is False
    assert DispatchExecutionBlockerCode.INACTIVE_TECHNICIAN in result.blocker_codes


def test_unauthorized_route_assignment_blocks_dispatch_execution() -> None:
    route_assignment, visit, technician, _ = authorized_route_assignment()
    route_assignment.dispatch_authorization_snapshot["authorized_for_dispatch"] = False

    result = DispatchExecutionService().execute_dispatch(
        route_assignment,
        visit=visit,
        technician=technician,
    )

    assert result.succeeded is False
    assert result.state == DispatchExecutionState.DISPATCH_BLOCKED
    assert DispatchExecutionBlockerCode.UNAUTHORIZED_ROUTE_ASSIGNMENT in result.blocker_codes
    assert route_assignment.status == "awaiting_dispatch_execution"


def test_duplicate_dispatch_is_blocked() -> None:
    route_assignment, visit, technician, _ = authorized_route_assignment()
    service = DispatchExecutionService(
        now=lambda: datetime(2026, 5, 15, 18, 0, tzinfo=UTC),
    )
    service.execute_dispatch(route_assignment, visit=visit, technician=technician)

    result = service.execute_dispatch(route_assignment, visit=visit, technician=technician)

    assert result.succeeded is False
    assert result.state == DispatchExecutionState.DISPATCH_BLOCKED
    assert DispatchExecutionBlockerCode.DUPLICATE_DISPATCH in result.blocker_codes
    assert route_assignment.status == "dispatched"


def test_unassigned_or_unscheduled_visit_cannot_dispatch() -> None:
    route_assignment, visit, technician, _ = authorized_route_assignment()
    visit.technician_id = None
    visit.scheduled_start_at = None

    result = DispatchExecutionService().execute_dispatch(
        route_assignment,
        visit=visit,
        technician=technician,
    )

    assert result.succeeded is False
    assert DispatchExecutionBlockerCode.UNASSIGNED_VISIT in result.blocker_codes
    assert DispatchExecutionBlockerCode.UNSCHEDULED_VISIT in result.blocker_codes


def test_dispatch_execution_audit_log_preserves_traceability() -> None:
    route_assignment, visit, technician, creation_record = authorized_route_assignment()
    service = DispatchExecutionService(
        now=lambda: datetime(2026, 5, 15, 18, 0, tzinfo=UTC),
    )
    service.execute_dispatch(route_assignment, visit=visit, technician=technician)

    audit_log = service.build_dispatch_executed_audit_log(route_assignment)

    assert audit_log.action == "operational_dispatch.executed"
    assert audit_log.entity_type == "route_assignment"
    assert audit_log.entity_id == route_assignment.id
    assert audit_log.audit_correlation_id == creation_record.audit_correlation_id
    assert audit_log.details["dispatch_execution_state"] == "dispatched"
    assert audit_log.details["external_integrations"] == "not_executed"
    assert audit_log.details["visit_id"] == str(visit.id)
