from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

from app.db.base import Base
from app.domain.operational_event_history import (
    OperationalEventFailureCode,
    OperationalEventState,
)
from app.models.operational_event_record import OperationalEventRecord
from app.models.route_assignment import RouteAssignment
from app.models.visit import Visit
from app.services.operational_event_history.service import (
    OperationalEventHistoryService,
    build_timeline_entries,
)


class OperationalEventRecordRepositoryStub:
    def __init__(self) -> None:
        self.added: list[OperationalEventRecord] = []
        self.existing_by_fingerprint: dict[str, OperationalEventRecord] = {}
        self.timeline_records: list[OperationalEventRecord] = []

    def add(self, record: OperationalEventRecord) -> OperationalEventRecord:
        self.added.append(record)
        self.existing_by_fingerprint[record.event_fingerprint] = record
        return record

    def get_by_event_fingerprint(self, event_fingerprint: str) -> OperationalEventRecord | None:
        return self.existing_by_fingerprint.get(event_fingerprint)

    def list_for_route_assignment(self, route_assignment_id):
        return self.timeline_records

    def list_for_visit(self, visit_id):
        return self.timeline_records


def event_history_service(
    repository: OperationalEventRecordRepositoryStub,
    *,
    timestamp: datetime = datetime(2026, 5, 16, 9, 0, tzinfo=UTC),
) -> OperationalEventHistoryService:
    return OperationalEventHistoryService(
        repository,
        now=lambda: timestamp,
    )


def dispatched_route_assignment() -> tuple[RouteAssignment, Visit]:
    route_assignment_id = uuid4()
    visit_id = uuid4()
    work_order_id = uuid4()
    job_id = uuid4()
    technician_id = uuid4()
    audit_correlation_id = "audit-module-17"
    dispatched_at = datetime(2026, 5, 16, 8, 30, tzinfo=UTC)

    visit = Visit(
        id=visit_id,
        job_id=job_id,
        work_order_id=work_order_id,
        technician_id=technician_id,
        visit_type="standard",
        status="dispatched",
        audit_correlation_id=audit_correlation_id,
        scheduled_start_at=datetime(2026, 5, 16, 9, 0, tzinfo=UTC),
    )
    route_assignment = RouteAssignment(
        id=route_assignment_id,
        route_date=date(2026, 5, 16),
        technician_id=technician_id,
        job_id=job_id,
        visit_id=visit_id,
        route_order=1,
        region="DE",
        time_window="AM",
        status="dispatched",
        audit_correlation_id=audit_correlation_id,
        dispatch_authorization_snapshot={"authorized_for_dispatch": True},
        dispatch_execution_boundary_snapshot={"authorized_for_dispatch": True},
        dispatch_execution_state="dispatched",
        dispatch_execution_snapshot={
            "state": "dispatched",
            "dispatch_execution": "executed_internal_only",
            "external_integrations": "not_executed",
        },
        dispatch_lifecycle_snapshot={
            "previous_state": "awaiting_dispatch_execution",
            "new_state": "dispatched",
            "transitioned_at": dispatched_at.isoformat(),
        },
        dispatch_audit_snapshot={
            "action": "operational_dispatch.executed",
            "external_integrations": "not_executed",
        },
        dispatched_at=dispatched_at,
    )
    return route_assignment, visit


def test_operational_event_history_table_supports_immutable_timeline_fields() -> None:
    columns = Base.metadata.tables["operational_event_records"].columns

    expected_columns = {
        "occurred_at",
        "recorded_at",
        "event_type",
        "event_state",
        "entity_type",
        "entity_id",
        "route_assignment_id",
        "visit_id",
        "work_order_id",
        "job_id",
        "technician_id",
        "audit_correlation_id",
        "previous_state",
        "new_state",
        "event_fingerprint",
        "is_immutable",
        "event_snapshot",
        "transition_snapshot",
        "immutable_evidence_snapshot",
        "retry_recovery_snapshot",
        "reconciliation_snapshot",
        "audit_snapshot",
    }

    assert expected_columns.issubset(set(columns.keys()))


def test_lifecycle_transition_recording_creates_append_only_event() -> None:
    repository = OperationalEventRecordRepositoryStub()
    entity_id = uuid4()

    result = event_history_service(repository).record_lifecycle_transition(
        event_type="visit.lifecycle.transitioned",
        entity_type="visit",
        entity_id=entity_id,
        previous_state="dispatch_ready",
        new_state="dispatched",
        event_state=OperationalEventState.TRANSITIONED,
        audit_correlation_id="audit-module-17",
        route_assignment_id=uuid4(),
        visit_id=entity_id,
        transition_evidence={"transition_rule": "deterministic"},
    )

    assert result.succeeded is True
    assert repository.added == [result.event_record]
    assert result.event_record.event_state == "transitioned"
    assert result.event_record.entity_type == "visit"
    assert result.event_record.entity_id == entity_id
    assert result.event_record.audit_correlation_id == "audit-module-17"
    assert result.event_record.is_immutable is True
    assert result.event_record.transition_snapshot["previous_state"] == "dispatch_ready"
    assert result.event_record.transition_snapshot["new_state"] == "dispatched"
    assert result.event_record.immutable_evidence_snapshot["event_history"] == "append_only"
    assert result.evidence.transition["transition_rule"] == "deterministic"


def test_duplicate_event_prevention_blocks_same_transition_fingerprint() -> None:
    repository = OperationalEventRecordRepositoryStub()
    service = event_history_service(repository)
    entity_id = uuid4()

    first = service.record_lifecycle_transition(
        event_type="visit.lifecycle.transitioned",
        entity_type="visit",
        entity_id=entity_id,
        previous_state="dispatch_ready",
        new_state="dispatched",
        event_state=OperationalEventState.TRANSITIONED,
        audit_correlation_id="audit-module-17",
    )
    second = service.record_lifecycle_transition(
        event_type="visit.lifecycle.transitioned",
        entity_type="visit",
        entity_id=entity_id,
        previous_state="dispatch_ready",
        new_state="dispatched",
        event_state=OperationalEventState.TRANSITIONED,
        audit_correlation_id="audit-module-17",
    )

    assert first.succeeded is True
    assert second.succeeded is False
    assert second.failure_codes == (OperationalEventFailureCode.DUPLICATE_EVENT,)
    assert repository.added == [first.event_record]


def test_invalid_transition_event_is_blocked_without_mutating_history() -> None:
    repository = OperationalEventRecordRepositoryStub()

    result = event_history_service(repository).record_lifecycle_transition(
        event_type="visit.lifecycle.transitioned",
        entity_type="visit",
        entity_id=uuid4(),
        previous_state="dispatched",
        new_state="dispatched",
        event_state=OperationalEventState.TRANSITIONED,
        audit_correlation_id=None,
    )

    assert result.succeeded is False
    assert OperationalEventFailureCode.INVALID_TRANSITION in result.failure_codes
    assert OperationalEventFailureCode.MISSING_AUDIT_CORRELATION in result.failure_codes
    assert repository.added == []


def test_dispatch_execution_event_records_timeline_evidence() -> None:
    repository = OperationalEventRecordRepositoryStub()
    route_assignment, visit = dispatched_route_assignment()

    result = event_history_service(repository).record_dispatch_execution(
        route_assignment,
        visit=visit,
    )

    assert result.succeeded is True
    assert result.event_record.event_type == "operational_dispatch.executed"
    assert result.event_record.event_state == "dispatched"
    assert result.event_record.route_assignment_id == route_assignment.id
    assert result.event_record.visit_id == visit.id
    assert result.event_record.transition_snapshot["new_state"] == "dispatched"
    assert result.event_record.event_snapshot["dispatch_execution"] == "executed_internal_only"
    assert result.event_record.audit_snapshot["action"] == "operational_dispatch.executed"


def test_adapter_preparation_event_records_external_boundary_without_execution() -> None:
    repository = OperationalEventRecordRepositoryStub()
    route_assignment, visit = dispatched_route_assignment()
    route_assignment.external_adapter_state = "awaiting_external_confirmation"
    route_assignment.external_adapter_evidence_snapshot = {
        "adapter_preparation": "prepared",
        "external_api_calls": "not_executed",
    }
    route_assignment.external_adapter_lifecycle_snapshot = {
        "previous_state": "internal_dispatch_complete",
        "next_state": "awaiting_external_confirmation",
    }

    result = event_history_service(repository).record_adapter_preparation(
        route_assignment,
        visit=visit,
    )

    assert result.succeeded is True
    assert result.event_record.event_type == "external_dispatch_adapter.prepared"
    assert result.event_record.event_state == "transitioned"
    assert result.event_record.event_snapshot["external_api_calls"] == "not_executed"
    assert result.event_record.transition_snapshot["next_state"] == "awaiting_external_confirmation"


def test_retry_and_reconciliation_events_preserve_recovery_evidence() -> None:
    retry_repository = OperationalEventRecordRepositoryStub()
    retry_route_assignment, retry_visit = dispatched_route_assignment()
    retry_route_assignment.external_confirmation_state = "awaiting_retry"
    retry_route_assignment.retry_preparation_snapshot = {
        "retry_eligible": True,
        "retry_execution": "not_executed",
    }

    retry_result = event_history_service(retry_repository).record_confirmation_recovery(
        retry_route_assignment,
        visit=retry_visit,
    )

    reconciliation_repository = OperationalEventRecordRepositoryStub()
    reconciliation_route_assignment, reconciliation_visit = dispatched_route_assignment()
    reconciliation_route_assignment.external_confirmation_state = "reconciliation_required"
    reconciliation_route_assignment.reconciliation_snapshot = {
        "reconciliation_required": True,
        "reconciliation_execution": "not_executed",
    }

    reconciliation_result = event_history_service(
        reconciliation_repository,
    ).record_confirmation_recovery(
        reconciliation_route_assignment,
        visit=reconciliation_visit,
    )

    assert retry_result.succeeded is True
    assert retry_result.event_record.event_state == "retry_prepared"
    assert retry_result.event_record.retry_recovery_snapshot["retry_execution"] == "not_executed"

    assert reconciliation_result.succeeded is True
    assert reconciliation_result.event_record.event_state == "reconciliation_required"
    assert (
        reconciliation_result.event_record.reconciliation_snapshot["reconciliation_execution"]
        == "not_executed"
    )


def test_timeline_entries_are_chronologically_ordered() -> None:
    base_time = datetime(2026, 5, 16, 9, 0, tzinfo=UTC)
    route_assignment_id = uuid4()
    later = OperationalEventRecord(
        occurred_at=base_time + timedelta(minutes=10),
        recorded_at=base_time + timedelta(minutes=10),
        event_type="external_execution.confirmed",
        event_state="externally_confirmed",
        entity_type="route_assignment",
        entity_id=route_assignment_id,
        route_assignment_id=route_assignment_id,
        audit_correlation_id="audit-module-17",
        event_fingerprint="later",
        previous_state="awaiting_external_confirmation",
        new_state="externally_confirmed",
        is_immutable=True,
    )
    earlier = OperationalEventRecord(
        occurred_at=base_time,
        recorded_at=base_time,
        event_type="operational_dispatch.executed",
        event_state="dispatched",
        entity_type="route_assignment",
        entity_id=route_assignment_id,
        route_assignment_id=route_assignment_id,
        audit_correlation_id="audit-module-17",
        event_fingerprint="earlier",
        previous_state="awaiting_dispatch_execution",
        new_state="dispatched",
        is_immutable=True,
    )

    entries = build_timeline_entries([later, earlier])

    assert [entry.event_type for entry in entries] == [
        "operational_dispatch.executed",
        "external_execution.confirmed",
    ]
    assert entries[0].sequence == 1
    assert entries[1].sequence == 2
