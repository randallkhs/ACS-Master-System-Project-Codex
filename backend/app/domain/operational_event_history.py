from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID


class OperationalEventState(StrEnum):
    CREATED = "created"
    TRANSITIONED = "transitioned"
    BLOCKED = "blocked"
    DISPATCHED = "dispatched"
    EXTERNALLY_CONFIRMED = "externally_confirmed"
    RETRY_PREPARED = "retry_prepared"
    RECONCILIATION_REQUIRED = "reconciliation_required"
    ARCHIVED = "archived"


class OperationalEventFailureCode(StrEnum):
    DUPLICATE_EVENT = "duplicate_event"
    INVALID_EVENT = "invalid_event"
    INVALID_TRANSITION = "invalid_transition"
    MISSING_ENTITY_LINKAGE = "missing_entity_linkage"
    MISSING_AUDIT_CORRELATION = "missing_audit_correlation"
    MISSING_TRANSITION_STATE = "missing_transition_state"
    UNSUPPORTED_CONFIRMATION_STATE = "unsupported_confirmation_state"


@dataclass(frozen=True)
class OperationalEventFailureReason:
    code: OperationalEventFailureCode
    message: str
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class OperationalEventTraceability:
    entity_type: str | None
    entity_id: UUID | None
    route_assignment_id: UUID | None = None
    visit_id: UUID | None = None
    work_order_id: UUID | None = None
    job_id: UUID | None = None
    technician_id: UUID | None = None
    audit_correlation_id: str | None = None


@dataclass(frozen=True)
class LifecycleEventRecord:
    event_type: str
    event_state: OperationalEventState
    previous_state: str | None
    new_state: str | None
    occurred_at: datetime
    traceability: OperationalEventTraceability


@dataclass(frozen=True)
class TransitionEvidence:
    previous_state: str | None
    new_state: str | None
    event_state: str
    occurred_at: str
    transition: dict[str, Any]


@dataclass(frozen=True)
class RetryRecoveryEventEvidence:
    retry: dict[str, Any]
    recovery: dict[str, Any]


@dataclass(frozen=True)
class ReconciliationEventEvidence:
    reconciliation: dict[str, Any]


@dataclass(frozen=True)
class ImmutableAuditEvidence:
    immutable: bool
    append_only: bool
    audit_correlation_id: str | None
    evidence: dict[str, Any]


@dataclass(frozen=True)
class OperationalEventEvidence:
    event: dict[str, Any]
    transition: dict[str, Any]
    immutable: dict[str, Any]
    retry_recovery: dict[str, Any]
    reconciliation: dict[str, Any]
    audit: dict[str, Any]
    failure_reasons: tuple[OperationalEventFailureReason, ...] = ()


@dataclass(frozen=True)
class EventTimelineEntry:
    sequence: int
    event_type: str
    event_state: str
    occurred_at: datetime
    entity_type: str
    entity_id: UUID
    route_assignment_id: UUID | None
    visit_id: UUID | None
    audit_correlation_id: str
    previous_state: str | None
    new_state: str | None
    event_snapshot: dict[str, Any]


@dataclass(frozen=True)
class OperationalEventResult:
    succeeded: bool
    state: OperationalEventState
    traceability: OperationalEventTraceability
    evidence: OperationalEventEvidence
    event_record: Any | None = None
    failure_reasons: tuple[OperationalEventFailureReason, ...] = ()

    @property
    def failure_codes(self) -> tuple[OperationalEventFailureCode, ...]:
        return tuple(reason.code for reason in self.failure_reasons)
