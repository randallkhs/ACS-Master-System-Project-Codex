from enum import StrEnum


class IntakeProcessingState(StrEnum):
    RAW = "raw"
    NORMALIZED = "normalized"
    VALIDATED = "validated"
    FLAGGED_FOR_REVIEW = "flagged_for_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    ARCHIVED = "archived"


class ReviewStatus(StrEnum):
    OPEN = "open"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    ARCHIVED = "archived"
