from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any
from uuid import UUID


class JobCreationLifecycleState(StrEnum):
    INTAKE_PERSISTED = "intake_persisted"
    JOB_CREATED = "job_created"
    AWAITING_DISPATCH = "awaiting_dispatch"
    AWAITING_ROUTING = "awaiting_routing"
    AWAITING_REVIEW_RESOLUTION = "awaiting_review_resolution"
    BLOCKED = "blocked"
    ARCHIVED = "archived"


class JobCreationFailureCode(StrEnum):
    BLOCKED_INTAKE = "blocked_intake"
    REVIEW_REQUIRED = "review_required"
    UNSAFE_INTAKE = "unsafe_intake"
    WATER_EMERGENCY_SEPARATED = "water_emergency_separated"
    DUPLICATE_JOB_CREATION = "duplicate_job_creation"
    MISSING_INTAKE_LINKAGE = "missing_intake_linkage"
    INVALID_LIFECYCLE = "invalid_lifecycle"


@dataclass(frozen=True)
class JobCreationFailureReason:
    code: JobCreationFailureCode
    message: str
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class JobCreationTraceability:
    intake_processing_record_id: UUID | None
    job_id: UUID | None
    job_creation_record_id: UUID | None
    review_item_id: UUID | None
    audit_correlation_id: str | None


@dataclass(frozen=True)
class JobCreationEvidence:
    intake_snapshot: dict[str, Any] | None = None
    creation_snapshot: dict[str, Any] | None = None
    deterministic_evidence: dict[str, Any] | None = None
    review_linkage: dict[str, Any] | None = None
    failure_reasons: tuple[JobCreationFailureReason, ...] = ()


@dataclass(frozen=True)
class JobCreationResult:
    succeeded: bool
    lifecycle_state: JobCreationLifecycleState
    traceability: JobCreationTraceability
    evidence: JobCreationEvidence
    job: Any | None = None
    creation_record: Any | None = None
    existing_creation_record: Any | None = None
    failure_reasons: tuple[JobCreationFailureReason, ...] = ()

    @property
    def failure_codes(self) -> tuple[JobCreationFailureCode, ...]:
        return tuple(reason.code for reason in self.failure_reasons)
