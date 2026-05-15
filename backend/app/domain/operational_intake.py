from enum import StrEnum


class OperationalLifecycleState(StrEnum):
    INTAKE_RECEIVED = "intake_received"
    NORMALIZED = "normalized"
    VALIDATED = "validated"
    REVIEW_REQUIRED = "review_required"
    APPROVED_FOR_DISPATCH = "approved_for_dispatch"
    BLOCKED = "blocked"
    DEFERRED = "deferred"
    ARCHIVED = "archived"
