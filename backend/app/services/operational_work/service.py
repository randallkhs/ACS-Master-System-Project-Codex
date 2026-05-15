from collections.abc import Callable
from datetime import UTC, datetime
from uuid import uuid4

from app.domain.operational_generation import (
    OperationalGenerationEvidence,
    OperationalGenerationFailureCode,
    OperationalGenerationFailureReason,
    OperationalGenerationLifecycleState,
    OperationalGenerationTraceability,
    VisitGenerationResult,
    WorkOrderGenerationResult,
)
from app.models.audit_log import AuditLog
from app.models.job import Job
from app.models.job_creation_record import JobCreationRecord
from app.models.visit import Visit
from app.models.work_order import WorkOrder
from app.repositories.visits import VisitRepository
from app.repositories.work_orders import WorkOrderRepository


class OperationalWorkGenerationService:
    def __init__(
        self,
        *,
        work_order_repository: WorkOrderRepository,
        visit_repository: VisitRepository,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self.work_order_repository = work_order_repository
        self.visit_repository = visit_repository
        self.now = now or (lambda: datetime.now(UTC))

    def create_work_order_from_job(
        self,
        job: Job,
        job_creation_record: JobCreationRecord,
    ) -> WorkOrderGenerationResult:
        duplicate_result = self._duplicate_work_order_result(job, job_creation_record)
        if duplicate_result is not None:
            return duplicate_result

        failure_reasons = work_order_failure_reasons(job, job_creation_record)
        if failure_reasons:
            return failed_work_order_result(job, job_creation_record, failure_reasons)

        timestamp = self.now()
        work_order = build_work_order(job, job_creation_record, timestamp)
        self.work_order_repository.add(work_order)
        mark_job_work_order_created(job, work_order)

        return WorkOrderGenerationResult(
            succeeded=True,
            lifecycle_state=OperationalGenerationLifecycleState.WORK_ORDER_CREATED,
            work_order=work_order,
            traceability=work_order_traceability(job, job_creation_record, work_order),
            evidence=OperationalGenerationEvidence(
                generation_snapshot=work_order.generation_snapshot,
                intake_snapshot=work_order.intake_snapshot,
                orchestration_snapshot=work_order.orchestration_snapshot,
                dispatch_eligibility_snapshot=work_order.dispatch_eligibility_snapshot,
                deterministic_evidence=work_order.deterministic_evidence_snapshot,
                review_linkage=work_order.review_linkage_snapshot,
            ),
        )

    def create_visit_from_work_order(self, work_order: WorkOrder) -> VisitGenerationResult:
        duplicate_result = self._duplicate_visit_result(work_order)
        if duplicate_result is not None:
            return duplicate_result

        failure_reasons = visit_failure_reasons(work_order)
        if failure_reasons:
            return failed_visit_result(work_order, failure_reasons)

        timestamp = self.now()
        visit = build_visit(work_order, timestamp)
        self.visit_repository.add(visit)
        mark_work_order_visit_created(work_order, visit)

        return VisitGenerationResult(
            succeeded=True,
            lifecycle_state=OperationalGenerationLifecycleState.VISIT_CREATED,
            visit=visit,
            traceability=visit_traceability(work_order, visit),
            evidence=OperationalGenerationEvidence(
                generation_snapshot=visit.generation_snapshot,
                deterministic_evidence=visit.deterministic_evidence_snapshot,
                review_linkage=visit.review_linkage_snapshot,
            ),
        )

    def _duplicate_work_order_result(
        self,
        job: Job,
        job_creation_record: JobCreationRecord,
    ) -> WorkOrderGenerationResult | None:
        if job.id is None:
            return None
        existing = self.work_order_repository.get_by_job_id(job.id)
        if existing is None:
            return None

        reason = OperationalGenerationFailureReason(
            code=OperationalGenerationFailureCode.DUPLICATE_WORK_ORDER_GENERATION,
            message="A work order has already been generated for this job.",
            metadata={"work_order_id": str(existing.id)},
        )
        return WorkOrderGenerationResult(
            succeeded=False,
            lifecycle_state=OperationalGenerationLifecycleState.BLOCKED,
            existing_work_order=existing,
            failure_reasons=(reason,),
            traceability=OperationalGenerationTraceability(
                job_id=job.id,
                work_order_id=existing.id,
                job_creation_record_id=job_creation_record.id,
                review_item_id=job_creation_record.review_item_id,
                audit_correlation_id=job_creation_record.audit_correlation_id,
            ),
            evidence=OperationalGenerationEvidence(failure_reasons=(reason,)),
        )

    def _duplicate_visit_result(self, work_order: WorkOrder) -> VisitGenerationResult | None:
        if work_order.id is None:
            return None
        existing = self.visit_repository.get_by_work_order_id(work_order.id)
        if existing is None:
            return None

        reason = OperationalGenerationFailureReason(
            code=OperationalGenerationFailureCode.DUPLICATE_VISIT_GENERATION,
            message="A visit has already been generated for this work order.",
            metadata={"visit_id": str(existing.id)},
        )
        return VisitGenerationResult(
            succeeded=False,
            lifecycle_state=OperationalGenerationLifecycleState.BLOCKED,
            existing_visit=existing,
            failure_reasons=(reason,),
            traceability=OperationalGenerationTraceability(
                job_id=work_order.job_id,
                work_order_id=work_order.id,
                visit_id=existing.id,
                job_creation_record_id=work_order.job_creation_record_id,
                review_item_id=work_order.review_item_id,
                audit_correlation_id=work_order.audit_correlation_id,
            ),
            evidence=OperationalGenerationEvidence(failure_reasons=(reason,)),
        )

    @staticmethod
    def build_work_order_generated_audit_log(work_order: WorkOrder) -> AuditLog:
        return AuditLog(
            action="operational_work_order.generated",
            entity_type="work_order",
            entity_id=work_order.id,
            audit_correlation_id=work_order.audit_correlation_id,
            details={
                "job_id": str(work_order.job_id),
                "job_creation_record_id": str(work_order.job_creation_record_id)
                if work_order.job_creation_record_id
                else None,
                "review_item_id": str(work_order.review_item_id)
                if work_order.review_item_id
                else None,
                "lifecycle_state": work_order.status,
            },
        )

    @staticmethod
    def build_visit_generated_audit_log(visit: Visit) -> AuditLog:
        return AuditLog(
            action="operational_visit.generated",
            entity_type="visit",
            entity_id=visit.id,
            audit_correlation_id=visit.audit_correlation_id,
            details={
                "job_id": str(visit.job_id),
                "work_order_id": str(visit.work_order_id) if visit.work_order_id else None,
                "lifecycle_state": visit.status,
            },
        )


def work_order_failure_reasons(
    job: Job,
    job_creation_record: JobCreationRecord,
) -> tuple[OperationalGenerationFailureReason, ...]:
    reasons: list[OperationalGenerationFailureReason] = []
    if job.id is None or job_creation_record.id is None or job_creation_record.job_id != job.id:
        reasons.append(
            OperationalGenerationFailureReason(
                code=OperationalGenerationFailureCode.MISSING_JOB_LINKAGE,
                message="Job and job creation record linkage is required.",
                metadata={
                    "job_id": str(job.id) if job.id else None,
                    "job_creation_record_job_id": str(job_creation_record.job_id)
                    if job_creation_record.job_id
                    else None,
                },
            ),
        )
    if enum_value(job.job_type) == "water_emergency":
        reasons.append(
            OperationalGenerationFailureReason(
                code=OperationalGenerationFailureCode.WATER_EMERGENCY_JOB,
                message="Water Emergency jobs require a separated work order path.",
            ),
        )
    if enum_value(job.status) == OperationalGenerationLifecycleState.BLOCKED.value:
        reasons.append(
            OperationalGenerationFailureReason(
                code=OperationalGenerationFailureCode.BLOCKED_JOB,
                message="Blocked jobs cannot generate work orders.",
            ),
        )
    if job.review_status != "approved":
        reasons.append(
            OperationalGenerationFailureReason(
                code=OperationalGenerationFailureCode.REVIEW_REQUIRED_JOB,
                message="Review-required jobs cannot generate work orders.",
                metadata={"review_status": job.review_status},
            ),
        )
    if enum_value(job.status) != OperationalGenerationLifecycleState.AWAITING_DISPATCH.value:
        reasons.append(
            OperationalGenerationFailureReason(
                code=OperationalGenerationFailureCode.INVALID_LIFECYCLE,
                message="Only awaiting-dispatch jobs can generate work orders.",
                metadata={"job_status": enum_value(job.status)},
            ),
        )
    return tuple(reasons)


def visit_failure_reasons(work_order: WorkOrder) -> tuple[OperationalGenerationFailureReason, ...]:
    reasons: list[OperationalGenerationFailureReason] = []
    if work_order.id is None or work_order.job_id is None:
        reasons.append(
            OperationalGenerationFailureReason(
                code=OperationalGenerationFailureCode.MISSING_WORK_ORDER_LINKAGE,
                message="Work order must have durable job and work order linkage.",
            ),
        )
    if enum_value(work_order.status) != OperationalGenerationLifecycleState.AWAITING_SCHEDULE.value:
        reasons.append(
            OperationalGenerationFailureReason(
                code=OperationalGenerationFailureCode.INVALID_LIFECYCLE,
                message="Only awaiting-schedule work orders can generate visits.",
                metadata={"work_order_status": enum_value(work_order.status)},
            ),
        )
    return tuple(reasons)


def failed_work_order_result(
    job: Job,
    job_creation_record: JobCreationRecord,
    failure_reasons: tuple[OperationalGenerationFailureReason, ...],
) -> WorkOrderGenerationResult:
    return WorkOrderGenerationResult(
        succeeded=False,
        lifecycle_state=OperationalGenerationLifecycleState.BLOCKED,
        failure_reasons=failure_reasons,
        traceability=OperationalGenerationTraceability(
            job_id=job.id,
            job_creation_record_id=job_creation_record.id,
            review_item_id=job_creation_record.review_item_id,
            audit_correlation_id=job_creation_record.audit_correlation_id,
        ),
        evidence=OperationalGenerationEvidence(
            deterministic_evidence=job_creation_record.deterministic_evidence_snapshot,
            review_linkage=job_creation_record.review_linkage_snapshot,
            failure_reasons=failure_reasons,
        ),
    )


def failed_visit_result(
    work_order: WorkOrder,
    failure_reasons: tuple[OperationalGenerationFailureReason, ...],
) -> VisitGenerationResult:
    return VisitGenerationResult(
        succeeded=False,
        lifecycle_state=OperationalGenerationLifecycleState.BLOCKED,
        failure_reasons=failure_reasons,
        traceability=OperationalGenerationTraceability(
            job_id=work_order.job_id,
            work_order_id=work_order.id,
            job_creation_record_id=work_order.job_creation_record_id,
            review_item_id=work_order.review_item_id,
            audit_correlation_id=work_order.audit_correlation_id,
        ),
        evidence=OperationalGenerationEvidence(
            deterministic_evidence=work_order.deterministic_evidence_snapshot,
            review_linkage=work_order.review_linkage_snapshot,
            failure_reasons=failure_reasons,
        ),
    )


def build_work_order(
    job: Job,
    job_creation_record: JobCreationRecord,
    timestamp: datetime,
) -> WorkOrder:
    work_order = WorkOrder(
        id=uuid4(),
        job_id=job.id,
        job_creation_record_id=job_creation_record.id,
        review_item_id=job_creation_record.review_item_id,
        work_order_number=work_order_number(job),
        status=OperationalGenerationLifecycleState.AWAITING_SCHEDULE.value,
        dispatch_status="not_dispatched",
        audit_correlation_id=job_creation_record.audit_correlation_id,
        service_instructions=job.description,
        generation_snapshot={},
        intake_snapshot=job_creation_record.intake_snapshot,
        orchestration_snapshot=job_creation_record.orchestration_snapshot,
        dispatch_eligibility_snapshot=job_creation_record.dispatch_eligibility_snapshot,
        review_linkage_snapshot=job_creation_record.review_linkage_snapshot,
        deterministic_evidence_snapshot=job_creation_record.deterministic_evidence_snapshot,
        lifecycle_metadata={
            "generation_state": OperationalGenerationLifecycleState.WORK_ORDER_CREATED.value,
        },
        generated_from_job_at=timestamp,
    )
    work_order.generation_snapshot = work_order_generation_snapshot(
        job,
        job_creation_record,
        work_order,
        timestamp,
    )
    return work_order


def build_visit(work_order: WorkOrder, timestamp: datetime) -> Visit:
    visit = Visit(
        id=uuid4(),
        job_id=work_order.job_id,
        work_order_id=work_order.id,
        visit_type="standard",
        status=OperationalGenerationLifecycleState.AWAITING_ASSIGNMENT.value,
        audit_correlation_id=work_order.audit_correlation_id,
        notes="Generated from standard work order; technician assignment not performed.",
        generation_snapshot={},
        work_order_snapshot=work_order_snapshot(work_order),
        review_linkage_snapshot=work_order.review_linkage_snapshot,
        deterministic_evidence_snapshot=work_order.deterministic_evidence_snapshot,
        lifecycle_metadata={
            "generation_state": OperationalGenerationLifecycleState.VISIT_CREATED.value,
            "assignment_state": OperationalGenerationLifecycleState.AWAITING_ASSIGNMENT.value,
        },
        generated_from_work_order_at=timestamp,
    )
    visit.generation_snapshot = visit_generation_snapshot(work_order, visit, timestamp)
    return visit


def mark_job_work_order_created(job: Job, work_order: WorkOrder) -> None:
    job.status = OperationalGenerationLifecycleState.WORK_ORDER_CREATED.value


def mark_work_order_visit_created(work_order: WorkOrder, visit: Visit) -> None:
    work_order.status = OperationalGenerationLifecycleState.VISIT_CREATED.value
    metadata = dict(work_order.lifecycle_metadata or {})
    metadata["visit_generation_state"] = OperationalGenerationLifecycleState.VISIT_CREATED.value
    metadata["visit_id"] = str(visit.id)
    work_order.lifecycle_metadata = metadata


def work_order_traceability(
    job: Job,
    job_creation_record: JobCreationRecord,
    work_order: WorkOrder,
) -> OperationalGenerationTraceability:
    return OperationalGenerationTraceability(
        job_id=job.id,
        work_order_id=work_order.id,
        job_creation_record_id=job_creation_record.id,
        review_item_id=job_creation_record.review_item_id,
        audit_correlation_id=job_creation_record.audit_correlation_id,
    )


def visit_traceability(work_order: WorkOrder, visit: Visit) -> OperationalGenerationTraceability:
    return OperationalGenerationTraceability(
        job_id=work_order.job_id,
        work_order_id=work_order.id,
        visit_id=visit.id,
        job_creation_record_id=work_order.job_creation_record_id,
        review_item_id=work_order.review_item_id,
        audit_correlation_id=work_order.audit_correlation_id,
    )


def work_order_generation_snapshot(
    job: Job,
    job_creation_record: JobCreationRecord,
    work_order: WorkOrder,
    timestamp: datetime,
) -> dict[str, object]:
    return {
        "generated_at": timestamp.isoformat(),
        "job": {
            "id": str(job.id),
            "status": enum_value(job.status),
            "job_type": job.job_type,
            "scheduled_date": job.scheduled_date.isoformat() if job.scheduled_date else None,
        },
        "job_creation_record": {
            "id": str(job_creation_record.id),
            "audit_correlation_id": job_creation_record.audit_correlation_id,
        },
        "work_order": {
            "id": str(work_order.id),
            "status": work_order.status,
            "dispatch_status": work_order.dispatch_status,
            "work_order_number": work_order.work_order_number,
        },
        "generation_rule": "approved_standard_job_only",
    }


def visit_generation_snapshot(
    work_order: WorkOrder,
    visit: Visit,
    timestamp: datetime,
) -> dict[str, object]:
    return {
        "generated_at": timestamp.isoformat(),
        "work_order": {
            "id": str(work_order.id),
            "status": work_order.status,
            "job_id": str(work_order.job_id),
        },
        "visit": {
            "id": str(visit.id),
            "status": visit.status,
            "visit_type": visit.visit_type,
            "technician_id": str(visit.technician_id) if visit.technician_id else None,
        },
        "generation_rule": "standard_visit_from_standard_work_order",
    }


def work_order_snapshot(work_order: WorkOrder) -> dict[str, object]:
    return {
        "id": str(work_order.id),
        "job_id": str(work_order.job_id),
        "job_creation_record_id": str(work_order.job_creation_record_id)
        if work_order.job_creation_record_id
        else None,
        "status": work_order.status,
        "dispatch_status": work_order.dispatch_status,
        "audit_correlation_id": work_order.audit_correlation_id,
    }


def work_order_number(job: Job) -> str:
    return f"WO-{str(job.id).replace('-', '')[:12].upper()}"


def enum_value(value: object) -> object:
    return value.value if hasattr(value, "value") else value
