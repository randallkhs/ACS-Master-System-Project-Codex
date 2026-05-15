from app.models.audit_log import AuditLog
from app.models.review_item import ReviewItem


class ReviewAuditTraceBuilder:
    def build_flagged_log(self, review_item: ReviewItem) -> AuditLog:
        return AuditLog(
            action="manual_review.flagged",
            entity_type="review_item",
            entity_id=review_item.id,
            audit_correlation_id=review_item.audit_correlation_id,
            details={
                "audit_correlation_id": review_item.audit_correlation_id,
                "why_flagged": review_item.review_reasons,
                "validation_evidence": review_item.validation_snapshot,
                "normalization_evidence": review_item.normalization_snapshot,
                "confidence_explanation": review_item.confidence_snapshot,
                "deterministic_reason_codes": review_item.review_reasons,
                "dispatch_blocked": review_item.review_metadata.get("dispatch_blocked")
                if review_item.review_metadata
                else None,
            },
        )
