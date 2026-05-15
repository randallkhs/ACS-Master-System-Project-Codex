from collections.abc import Callable
from datetime import UTC, datetime

from app.domain.manual_review import IntakeProcessingState, ReviewStatus
from app.models.review_item import ReviewItem


class ReviewStateTransitionService:
    def __init__(self, now: Callable[[], datetime] | None = None) -> None:
        self.now = now or (lambda: datetime.now(UTC))

    def approve(
        self,
        review_item: ReviewItem,
        *,
        operator_decision: str,
        operator_notes: str | None = None,
    ) -> ReviewItem:
        timestamp = self.now()
        self._require_operator_decision(operator_decision)
        review_item.status = ReviewStatus.APPROVED
        review_item.intake_processing_state = IntakeProcessingState.APPROVED
        review_item.operator_decision = operator_decision
        review_item.operator_notes = operator_notes
        review_item.reviewed_at = timestamp
        review_item.deferred_until = None
        review_item.resolved_at = timestamp
        return review_item

    def reject(
        self,
        review_item: ReviewItem,
        *,
        operator_decision: str,
        operator_notes: str | None = None,
    ) -> ReviewItem:
        timestamp = self.now()
        self._require_operator_decision(operator_decision)
        review_item.status = ReviewStatus.REJECTED
        review_item.intake_processing_state = IntakeProcessingState.REJECTED
        review_item.operator_decision = operator_decision
        review_item.operator_notes = operator_notes
        review_item.reviewed_at = timestamp
        review_item.deferred_until = None
        review_item.resolved_at = timestamp
        return review_item

    def defer(
        self,
        review_item: ReviewItem,
        *,
        operator_decision: str,
        deferred_until: datetime,
        operator_notes: str | None = None,
    ) -> ReviewItem:
        timestamp = self.now()
        self._require_operator_decision(operator_decision)
        review_item.status = ReviewStatus.DEFERRED
        review_item.intake_processing_state = IntakeProcessingState.DEFERRED
        review_item.operator_decision = operator_decision
        review_item.operator_notes = operator_notes
        review_item.reviewed_at = timestamp
        review_item.deferred_until = deferred_until
        review_item.resolved_at = None
        return review_item

    def archive(
        self,
        review_item: ReviewItem,
        *,
        operator_decision: str,
        operator_notes: str | None = None,
    ) -> ReviewItem:
        timestamp = self.now()
        self._require_operator_decision(operator_decision)
        review_item.status = ReviewStatus.ARCHIVED
        review_item.intake_processing_state = IntakeProcessingState.ARCHIVED
        review_item.operator_decision = operator_decision
        review_item.operator_notes = operator_notes
        review_item.reviewed_at = timestamp
        review_item.deferred_until = None
        review_item.resolved_at = timestamp
        return review_item

    def _require_operator_decision(self, operator_decision: str) -> None:
        if not operator_decision.strip():
            msg = "operator_decision is required for review state transitions"
            raise ValueError(msg)
