from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any
from uuid import UUID


class OperationalGenerationLifecycleState(StrEnum):
    JOB_CREATED = "job_created"
    WORK_ORDER_CREATED = "work_order_created"
    VISIT_CREATED = "visit_created"
    AWAITING_ASSIGNMENT = "awaiting_assignment"
    AWAITING_SCHEDULE = "awaiting_schedule"
    AWAITING_DISPATCH = "awaiting_dispatch"
    BLOCKED = "blocked"
    ARCHIVED = "archived"


class OperationalGenerationFailureCode(StrEnum):
    BLOCKED_JOB = "blocked_job"
    REVIEW_REQUIRED_JOB = "review_required_job"
    WATER_EMERGENCY_JOB = "water_emergency_job"
    DUPLICATE_WORK_ORDER_GENERATION = "duplicate_work_order_generation"
    DUPLICATE_VISIT_GENERATION = "duplicate_visit_generation"
    MISSING_JOB_LINKAGE = "missing_job_linkage"
    MISSING_WORK_ORDER_LINKAGE = "missing_work_order_linkage"
    INVALID_LIFECYCLE = "invalid_lifecycle"


@dataclass(frozen=True)
class OperationalGenerationFailureReason:
    code: OperationalGenerationFailureCode
    message: str
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class OperationalGenerationTraceability:
    job_id: UUID | None
    work_order_id: UUID | None = None
    visit_id: UUID | None = None
    job_creation_record_id: UUID | None = None
    review_item_id: UUID | None = None
    audit_correlation_id: str | None = None


@dataclass(frozen=True)
class OperationalGenerationEvidence:
    generation_snapshot: dict[str, Any] | None = None
    intake_snapshot: dict[str, Any] | None = None
    orchestration_snapshot: dict[str, Any] | None = None
    dispatch_eligibility_snapshot: dict[str, Any] | None = None
    deterministic_evidence: dict[str, Any] | None = None
    review_linkage: dict[str, Any] | None = None
    failure_reasons: tuple[OperationalGenerationFailureReason, ...] = ()


@dataclass(frozen=True)
class WorkOrderGenerationResult:
    succeeded: bool
    lifecycle_state: OperationalGenerationLifecycleState
    traceability: OperationalGenerationTraceability
    evidence: OperationalGenerationEvidence
    work_order: Any | None = None
    existing_work_order: Any | None = None
    failure_reasons: tuple[OperationalGenerationFailureReason, ...] = ()

    @property
    def failure_codes(self) -> tuple[OperationalGenerationFailureCode, ...]:
        return tuple(reason.code for reason in self.failure_reasons)


@dataclass(frozen=True)
class VisitGenerationResult:
    succeeded: bool
    lifecycle_state: OperationalGenerationLifecycleState
    traceability: OperationalGenerationTraceability
    evidence: OperationalGenerationEvidence
    visit: Any | None = None
    existing_visit: Any | None = None
    failure_reasons: tuple[OperationalGenerationFailureReason, ...] = ()

    @property
    def failure_codes(self) -> tuple[OperationalGenerationFailureCode, ...]:
        return tuple(reason.code for reason in self.failure_reasons)
