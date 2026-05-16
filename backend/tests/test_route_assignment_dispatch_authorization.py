from datetime import UTC, date, datetime
from uuid import uuid4

from app.domain.intake import RawIntakePayload
from app.domain.route_assignment_authorization import (
    DispatchExecutionAuthorizationState,
    RouteAssignmentAuthorizationBlockerCode,
)
from app.models.intake_processing_record import IntakeProcessingRecord
from app.models.job import Job
from app.models.job_creation_record import JobCreationRecord
from app.models.route_assignment import RouteAssignment
from app.models.technician import Technician
from app.models.visit import Visit
from app.models.work_order import WorkOrder
from app.services.assignment_preparation.service import AssignmentPreparationService
from app.services.dispatch.service import DispatchOrchestrationService
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


def dispatch_ready_visit() -> tuple[Visit, Technician, JobCreationRecord]:
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
    return visit, technician, creation_record


def test_dispatch_ready_visit_creates_authorized_route_assignment_boundary() -> None:
    visit, technician, creation_record = dispatch_ready_visit()
    repository = RouteAssignmentRepositoryStub()

    result = RouteAssignmentPreparationService(
        route_assignment_repository=repository,
        now=lambda: datetime(2026, 5, 15, 17, 0, tzinfo=UTC),
    ).prepare_route_assignment(visit, technician=technician)

    assert result.authorization.state == (
        DispatchExecutionAuthorizationState.AWAITING_DISPATCH_EXECUTION
    )
    assert result.authorization.authorized_for_dispatch is True
    assert result.authorization.awaiting_dispatch_execution is True
    assert result.route_assignment is repository.records[0]
    assert result.route_assignment.status == "awaiting_dispatch_execution"
    assert result.route_assignment.route_date == date(2026, 5, 16)
    assert result.route_assignment.technician_id == technician.id
    assert result.route_assignment.visit_id == visit.id
    assert result.route_assignment.job_id == visit.job_id
    assert result.traceability.audit_correlation_id == creation_record.audit_correlation_id
    assert visit.status == "awaiting_dispatch_execution"


def test_route_grouping_readiness_preserves_future_grouping_evidence() -> None:
    visit, technician, _ = dispatch_ready_visit()

    result = RouteAssignmentPreparationService(
        route_assignment_repository=RouteAssignmentRepositoryStub(),
    ).prepare_route_assignment(visit, technician=technician)

    assert result.route_grouping.ready is True
    assert result.route_grouping.region == "DE"
    assert result.route_grouping.time_window == "AM"
    assert result.route_grouping.service_states == ("DE",)
    assert result.route_grouping.route_group_key == "2026-05-16:DE:AM"
    assert result.route_assignment.route_group_key == "2026-05-16:DE:AM"
    assert result.route_assignment.route_grouping_snapshot["grouping_method"] == (
        "deterministic_preparation_only"
    )
    assert result.route_assignment.dispatch_execution_boundary_snapshot["dispatch_execution"] == (
        "not_executed"
    )


def test_route_unready_visit_cannot_be_authorized_for_dispatch() -> None:
    visit, technician, _ = dispatch_ready_visit()
    visit.routing_readiness_snapshot["ready"] = False

    result = RouteAssignmentPreparationService(
        route_assignment_repository=RouteAssignmentRepositoryStub(),
    ).prepare_route_assignment(visit, technician=technician)

    assert result.authorization.state == DispatchExecutionAuthorizationState.BLOCKED_FROM_DISPATCH
    assert result.authorization.authorized_for_dispatch is False
    assert result.route_assignment is None
    assert RouteAssignmentAuthorizationBlockerCode.ROUTE_NOT_READY in result.blocker_codes
    assert visit.status == "dispatch_ready"


def test_blocked_visit_cannot_be_dispatch_authorized() -> None:
    visit, technician, _ = dispatch_ready_visit()
    visit.status = "blocked"

    result = RouteAssignmentPreparationService(
        route_assignment_repository=RouteAssignmentRepositoryStub(),
    ).prepare_route_assignment(visit, technician=technician)

    assert result.authorization.state == DispatchExecutionAuthorizationState.BLOCKED_FROM_DISPATCH
    assert result.authorization.blocked_from_dispatch is True
    assert RouteAssignmentAuthorizationBlockerCode.BLOCKED_VISIT in result.blocker_codes


def test_inactive_technician_blocks_dispatch_authorization() -> None:
    visit, technician, _ = dispatch_ready_visit()
    technician.is_active = False

    result = RouteAssignmentPreparationService(
        route_assignment_repository=RouteAssignmentRepositoryStub(),
    ).prepare_route_assignment(visit, technician=technician)

    assert result.authorization.authorized_for_dispatch is False
    assert result.technician_route_compatibility.compatible is False
    assert RouteAssignmentAuthorizationBlockerCode.INACTIVE_TECHNICIAN in result.blocker_codes


def test_review_required_visit_blocks_dispatch_authorization() -> None:
    visit, technician, _ = dispatch_ready_visit()
    visit.status = "review_required"

    result = RouteAssignmentPreparationService(
        route_assignment_repository=RouteAssignmentRepositoryStub(),
    ).prepare_route_assignment(visit, technician=technician)

    assert result.authorization.state == DispatchExecutionAuthorizationState.REVIEW_REQUIRED
    assert result.authorization.review_required is True
    assert RouteAssignmentAuthorizationBlockerCode.REVIEW_REQUIRED in result.blocker_codes


def test_water_emergency_visit_blocks_standard_dispatch_authorization() -> None:
    visit, technician, _ = dispatch_ready_visit()
    visit.visit_type = "water_emergency"

    result = RouteAssignmentPreparationService(
        route_assignment_repository=RouteAssignmentRepositoryStub(),
    ).prepare_route_assignment(visit, technician=technician)

    assert result.authorization.state == DispatchExecutionAuthorizationState.BLOCKED_FROM_DISPATCH
    assert result.authorization.authorized_for_dispatch is False
    assert result.blocker_codes[0] == RouteAssignmentAuthorizationBlockerCode.WATER_EMERGENCY_VISIT


def test_unassigned_visit_cannot_be_dispatch_authorized() -> None:
    visit, technician, _ = dispatch_ready_visit()
    visit.technician_id = None

    result = RouteAssignmentPreparationService(
        route_assignment_repository=RouteAssignmentRepositoryStub(),
    ).prepare_route_assignment(visit, technician=technician)

    assert result.authorization.authorized_for_dispatch is False
    assert RouteAssignmentAuthorizationBlockerCode.UNASSIGNED_VISIT in result.blocker_codes


def test_unscheduled_visit_cannot_be_dispatch_authorized() -> None:
    visit, technician, _ = dispatch_ready_visit()
    visit.scheduled_start_at = None

    result = RouteAssignmentPreparationService(
        route_assignment_repository=RouteAssignmentRepositoryStub(),
    ).prepare_route_assignment(visit, technician=technician)

    assert result.authorization.authorized_for_dispatch is False
    assert RouteAssignmentAuthorizationBlockerCode.UNSCHEDULED_VISIT in result.blocker_codes


def test_dispatch_authorization_audit_log_preserves_deterministic_evidence() -> None:
    visit, technician, creation_record = dispatch_ready_visit()
    service = RouteAssignmentPreparationService(
        route_assignment_repository=RouteAssignmentRepositoryStub(),
        now=lambda: datetime(2026, 5, 15, 17, 0, tzinfo=UTC),
    )
    result = service.prepare_route_assignment(visit, technician=technician)

    audit_log = service.build_dispatch_authorized_audit_log(result.route_assignment)

    assert audit_log.action == "operational_dispatch.authorized"
    assert audit_log.entity_type == "route_assignment"
    assert audit_log.entity_id == result.route_assignment.id
    assert audit_log.audit_correlation_id == creation_record.audit_correlation_id
    assert audit_log.details["authorized_for_dispatch"] is True
    assert audit_log.details["dispatch_execution"] == "not_executed"
    assert audit_log.details["route_optimization"] == "not_performed"
