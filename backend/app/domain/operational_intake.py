from enum import StrEnum


class OperationalLifecycleState(StrEnum):
    INTAKE_RECEIVED = "intake_received"
    INTAKE_PERSISTED = "intake_persisted"
    NORMALIZED = "normalized"
    VALIDATED = "validated"
    REVIEW_REQUIRED = "review_required"
    APPROVED_FOR_DISPATCH = "approved_for_dispatch"
    JOB_CREATED = "job_created"
    AWAITING_DISPATCH = "awaiting_dispatch"
    AWAITING_ROUTING = "awaiting_routing"
    AWAITING_REVIEW_RESOLUTION = "awaiting_review_resolution"
    BLOCKED = "blocked"
    DEFERRED = "deferred"
    ARCHIVED = "archived"
