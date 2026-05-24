from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.dashboard import (
    CountBucket,
    DashboardDispatchSummary,
    DashboardOverviewReadModel,
    DispatchLifecycleSummary,
    ExternalExecutionSummary,
    GovernanceAccountabilitySummary,
    ManualReviewActionPreflight,
    ManualReviewAuditLedgerDryRun,
    ManualReviewCommandContract,
    ManualReviewCommandValidation,
    ManualReviewDecisionReadiness,
    ManualReviewDetailLinkedEntityContext,
    ManualReviewDetailReadModel,
    ManualReviewFilterOption,
    ManualReviewFutureActionPreview,
    ManualReviewPermissionReadiness,
    ManualReviewQueueItem,
    ManualReviewQueueReadModel,
    ManualReviewReasonEvidenceContext,
    ManualReviewResultWindowMetadata,
    ManualReviewSafetyGate,
    ManualReviewSortOption,
    ManualReviewSummary,
    ManualReviewTaxonomyMetadata,
    ManualReviewTaxonomyMetadataItem,
    OperationalDashboardSummary,
    OperationalEventTimelineSummary,
    OperationalTimelineEntry,
    ReconciliationRecoverySummary,
    RouteAssignmentSummary,
    WaterEmergencyAgingFollowUpItem,
    WaterEmergencyAgingFollowUpSummary,
    WaterEmergencyDashboardReadModel,
    WaterEmergencyDetailDryingStageContext,
    WaterEmergencyDetailEquipmentContext,
    WaterEmergencyDetailReadModel,
    WaterEmergencyDryingStageSummary,
    WaterEmergencyEquipmentNote,
    WaterEmergencyEquipmentSummary,
    WaterEmergencyFilterOption,
    WaterEmergencyGovernanceMetadata,
    WaterEmergencyGovernanceMetadataItem,
    WaterEmergencyJobReference,
    WaterEmergencyNextStepReadiness,
    WaterEmergencyNextStepReadinessSummary,
    WaterEmergencyOperatorQueueSummary,
    WaterEmergencyQueueItem,
    WaterEmergencyRecordSummary,
    WaterEmergencyResultWindowMetadata,
    WaterEmergencyReviewExceptionContext,
    WaterEmergencyReviewExceptionSummary,
    WaterEmergencyReviewIndicator,
    WaterEmergencySortOption,
    WaterEmergencyViewStateItem,
    WaterEmergencyViewStateSummary,
    WaterEmergencyVisitChain,
    WaterEmergencyVisitChainSummary,
    WaterEmergencyVisitReference,
    WaterEmergencyWorkOrderReference,
)
from app.models.intake_processing_record import IntakeProcessingRecord
from app.models.job import Job
from app.models.operational_event_record import OperationalEventRecord
from app.models.review_item import ReviewItem
from app.models.route_assignment import RouteAssignment
from app.models.visit import Visit
from app.models.water_emergency import WaterEmergency
from app.models.work_order import WorkOrder

UNRESOLVED_REVIEW_STATUSES = {
    "open",
    "pending",
    "deferred",
    "flagged_for_review",
    "review_required",
}
RESOLVED_REVIEW_STATUSES = {"approved", "rejected", "resolved", "closed"}
ESCALATION_SEVERITIES = {"high", "critical"}
TERMINAL_WATER_EMERGENCY_STATUSES = {
    "closed",
    "completed",
    "resolved",
    "cancelled",
    "canceled",
}
READY_FOR_CLOSE_REVIEW_STATUSES = {
    "ready_for_close_review",
    "ready_for_pickup",
    "pickup_scheduled",
    "completed",
}
READY_FOR_CLOSE_REVIEW_STAGES = {
    "ready_for_close_review",
    "ready_for_pickup",
    "final_verification",
    "pickup_ready",
}
BLOCKED_ROUTE_STATES = {"blocked", "reconciliation_blocked", "replay_blocked"}
BLOCKED_GOVERNANCE_STATES = {"governance_blocked"}
BLOCKED_ACCOUNTABILITY_STATES = {"accountability_blocked"}
WATER_EMERGENCY_BLOCKER_REASON_KEYWORDS = {
    "block",
    "blocked",
    "conflict",
    "critical",
    "exception",
    "missing",
    "pickup",
    "unsafe",
    "unknown",
}
MAX_SORTABLE_DATETIME = datetime.max.replace(tzinfo=UTC)
NIL_UUID = UUID("00000000-0000-0000-0000-000000000000")
NEWLY_OPENED_HOURS = 24
FOLLOWUP_DUE_HOURS = 24
FOLLOWUP_OVERDUE_HOURS = 72
STALE_EVIDENCE_HOURS = 72
WATER_EMERGENCY_FILTER_DEFINITIONS = (
    (
        "all",
        "All records",
        "Every persisted Water Emergency record in this read-only dashboard response.",
    ),
    (
        "active",
        "Active records",
        "Open Water Emergency records separated from closed or resolved records.",
    ),
    (
        "critical_attention",
        "Critical attention",
        "Records with critical persisted review or alert evidence.",
    ),
    (
        "needs_manual_review",
        "Needs Manual Review",
        "Records with Manual Review or operator-decision evidence.",
    ),
    (
        "blocked_missing_data",
        "Blocked or missing data",
        "Records with blocker, unknown, or missing-data evidence.",
    ),
    (
        "followup_due",
        "Follow-up due",
        "Records with conservative Phase 0 follow-up due visibility.",
    ),
    (
        "followup_overdue",
        "Follow-up overdue",
        "Records with conservative Phase 0 follow-up overdue visibility.",
    ),
    (
        "stale_evidence",
        "Stale evidence",
        "Records where related evidence is old enough to flag for operator awareness.",
    ),
    (
        "ready_for_close_review",
        "Ready for close review",
        "Records with persisted close-review readiness evidence.",
    ),
    (
        "needs_followup",
        "Needs follow-up",
        "Records with visit-chain follow-up visibility evidence.",
    ),
    (
        "equipment_review_needed",
        "Equipment review needed",
        "Records with equipment context that needs operator review.",
    ),
    (
        "drying_stage_review_needed",
        "Drying-stage review needed",
        "Records with drying-stage or moisture confirmation visibility.",
    ),
    (
        "needs_operator_review",
        "Needs operator review",
        "Records with no safer deterministic group than operator review.",
    ),
    (
        "unknown_timing",
        "Unknown timing",
        "Records missing enough timing evidence to avoid inferred SLA status.",
    ),
    (
        "closed_or_resolved",
        "Closed or resolved",
        "Closed or resolved records separated from active attention groups.",
    ),
)
WATER_EMERGENCY_SORT_OPTIONS = (
    WaterEmergencySortOption(
        key="attention",
        label="Attention priority",
        description="Critical, review, blocker, timing, close-review, monitoring, then closed.",
    ),
    WaterEmergencySortOption(
        key="last_activity",
        label="Last activity",
        description="Most recent persisted visit, review, event, opened, or closed timestamp.",
    ),
    WaterEmergencySortOption(
        key="status",
        label="Status and stage",
        description="Current status, drying stage, and deterministic attention rank.",
    ),
)
WATER_EMERGENCY_VIEW_FILTER_PRIORITY = (
    "critical_attention",
    "needs_manual_review",
    "blocked_missing_data",
    "followup_overdue",
    "stale_evidence",
    "followup_due",
    "ready_for_close_review",
    "needs_followup",
    "equipment_review_needed",
    "drying_stage_review_needed",
    "needs_operator_review",
    "unknown_timing",
    "active",
    "closed_or_resolved",
)
WATER_EMERGENCY_VIEW_SORT_RANKS = {
    label: index * 10 for index, label in enumerate(WATER_EMERGENCY_VIEW_FILTER_PRIORITY, start=1)
}
WATER_EMERGENCY_ATTENTION_LABEL_DEFINITIONS = (
    ("critical_attention", "Critical attention"),
    ("needs_manual_review", "Needs Manual Review"),
    ("blocked_missing_data", "Blocked or missing data"),
    ("needs_followup", "Needs follow-up"),
    ("equipment_review_needed", "Equipment review needed"),
    ("drying_stage_review_needed", "Drying-stage review needed"),
    ("ready_for_close_review", "Ready for close review"),
    ("monitoring", "Monitoring"),
    ("closed_or_resolved", "Closed or resolved"),
    ("needs_operator_review", "Needs operator review"),
)
WATER_EMERGENCY_TIMING_LABEL_DEFINITIONS = (
    ("newly_opened", "Newly opened"),
    ("active_monitoring", "Active monitoring"),
    ("followup_due", "Follow-up due"),
    ("followup_overdue", "Follow-up overdue"),
    ("stale_evidence", "Stale evidence"),
    ("waiting_for_review", "Waiting for review"),
    ("ready_for_close_review", "Ready for close review"),
    ("closed_or_resolved", "Closed or resolved"),
    ("unknown_timing", "Unknown timing"),
)
WATER_EMERGENCY_READINESS_LABEL_DEFINITIONS = (
    ("needs_manual_review", "Needs Manual Review"),
    ("needs_operator_decision", "Needs operator decision"),
    ("needs_visit_followup", "Needs visit follow-up"),
    ("needs_equipment_review", "Needs equipment review"),
    ("needs_drying_stage_confirmation", "Needs drying-stage confirmation"),
    ("ready_for_close_review", "Ready for close review"),
    ("blocked_by_missing_data", "Blocked by missing data"),
    ("awaiting_more_information", "Awaiting more information"),
    ("closed_no_active_next_step", "Closed with no active next step"),
    ("needs_operator_review", "Needs operator review"),
)
WATER_EMERGENCY_FUTURE_ROLE_VISIBILITY_ROLES = (
    "office_admin",
    "operations_manager",
    "dispatcher",
    "reviewer",
    "technician",
    "owner",
)
MANUAL_REVIEW_NEW_HOURS = 24
MANUAL_REVIEW_AGING_HOURS = 72
MANUAL_REVIEW_STALE_HOURS = 168
MANUAL_REVIEW_BLOCKER_KEYWORDS = {
    "block",
    "blocked",
    "critical",
    "invalid",
    "missing",
    "unsafe",
    "unknown",
}
MANUAL_REVIEW_MISSING_DATA_KEYWORDS = {
    "address",
    "incomplete",
    "invalid",
    "missing",
    "unknown",
}
MANUAL_REVIEW_DUPLICATE_CONFLICT_KEYWORDS = {"conflict", "duplicate"}
MANUAL_REVIEW_CANCELLATION_STATUS_KEYWORDS = {
    "cancel",
    "canceled",
    "cancelled",
    "cancellation",
    "status",
    "uncertain",
    "uncertainty",
}
MANUAL_REVIEW_DISPATCH_ENTITY_TYPES = {
    "job",
    "route_assignment",
    "standard_job",
    "visit",
    "work_order",
}
MANUAL_REVIEW_GROUP_DEFINITIONS = (
    (
        "open",
        "Open",
        "Review items still requiring human attention.",
    ),
    (
        "deferred",
        "Deferred",
        "Review items intentionally held for later human follow-up.",
    ),
    (
        "resolved",
        "Resolved",
        "Review items already resolved, approved, rejected, or closed.",
    ),
    (
        "archived",
        "Archived",
        "Review items kept as read-only history.",
    ),
    (
        "blocked",
        "Blocked",
        "Review items with blocker, critical, missing, invalid, unsafe, or unknown evidence.",
    ),
    (
        "water_emergency_related",
        "Water Emergency related",
        "Review items specifically tied to a Water Emergency record, job, or visit.",
    ),
    (
        "dispatch_related",
        "Dispatch related",
        "Review items tied to standard job, work-order, visit, or route assignment context.",
    ),
    (
        "missing_data",
        "Missing data",
        "Review items whose reason indicates missing, invalid, incomplete, or unknown data.",
    ),
    (
        "duplicate_or_conflict",
        "Duplicate or conflict",
        "Review items whose reason indicates duplicate or conflicting operational evidence.",
    ),
    (
        "cancellation_or_status_uncertainty",
        "Cancellation or status uncertainty",
        "Review items whose reason indicates cancellation or status uncertainty.",
    ),
    (
        "needs_operator_review",
        "Needs operator review",
        "Fallback visibility group when no more specific Phase 0 group is deterministic.",
    ),
)
MANUAL_REVIEW_FILTER_DEFINITIONS = (
    (
        "all",
        "All reviews",
        "Every persisted Manual Review item returned by this read-only queue.",
    ),
    (
        "open",
        "Open",
        "Open Manual Review items requiring safety visibility.",
    ),
    (
        "deferred",
        "Deferred",
        "Review items intentionally deferred for later operator follow-up.",
    ),
    (
        "resolved",
        "Resolved",
        "Resolved review items kept separate from active review needs.",
    ),
    (
        "archived",
        "Archived",
        "Archived review history separated from active review needs.",
    ),
    (
        "active_attention",
        "Active attention",
        "Open or deferred review items still requiring operator attention.",
    ),
    (
        "water_emergency_related",
        "Water Emergency related",
        "Review items specifically tied to Water Emergency records, jobs, or visits.",
    ),
    (
        "dispatch_related",
        "Dispatch related",
        "Review items tied to standard job, work-order, visit, or route evidence.",
    ),
    (
        "missing_data",
        "Missing data",
        "Review items whose reason indicates missing, invalid, incomplete, or unknown data.",
    ),
    (
        "duplicate_or_conflict",
        "Duplicate or conflict",
        "Review items whose reason indicates duplicate or conflicting evidence.",
    ),
    (
        "cancellation_or_status_uncertainty",
        "Cancellation or status uncertainty",
        "Review items whose reason indicates cancellation or status uncertainty.",
    ),
    (
        "needs_operator_review",
        "Needs operator review",
        "Fallback visibility group when no more specific Phase 0 group is deterministic.",
    ),
)
MANUAL_REVIEW_SORT_OPTIONS = (
    ManualReviewSortOption(
        key="attention",
        label="Attention priority",
        description="Active, blocker, severity, status, and created-time ordering.",
    ),
    ManualReviewSortOption(
        key="newest",
        label="Newest first",
        description="Most recently created Manual Review items first.",
    ),
    ManualReviewSortOption(
        key="status",
        label="Status and reason",
        description="Status group, reason code, attention, and created-time ordering.",
    ),
)


class DashboardReadModelService:
    def __init__(self, *, now: Callable[[], datetime] | None = None) -> None:
        self.now = now or (lambda: datetime.now(UTC))

    def build_overview(
        self,
        *,
        intake_records: Sequence[IntakeProcessingRecord] = (),
        jobs: Sequence[Job] = (),
        work_orders: Sequence[WorkOrder] = (),
        visits: Sequence[Visit] = (),
        route_assignments: Sequence[RouteAssignment] = (),
        review_items: Sequence[ReviewItem] = (),
        water_emergencies: Sequence[WaterEmergency] = (),
        operational_events: Sequence[OperationalEventRecord] = (),
        timeline_limit: int = 50,
    ) -> DashboardOverviewReadModel:
        lifecycle = self.build_lifecycle(
            intake_records=intake_records,
            jobs=jobs,
            work_orders=work_orders,
            visits=visits,
            route_assignments=route_assignments,
            water_emergencies=water_emergencies,
        )
        review = self.build_review(review_items=review_items)
        dispatch = self.build_dispatch(route_assignments=route_assignments)
        timeline = self.build_timeline(
            operational_events=operational_events,
            limit=timeline_limit,
        )
        return DashboardOverviewReadModel(
            generated_at=self.now(),
            operational_summary=OperationalDashboardSummary(
                total_jobs=len(jobs),
                total_work_orders=len(work_orders),
                total_visits=len(visits),
                total_route_assignments=len(route_assignments),
                open_manual_reviews=review.open_items + review.deferred_items,
                blocked_operations=lifecycle.blocker_count,
                escalation_indicators=(
                    review.escalation_indicators
                    + dispatch.governance_accountability.escalation_required_count
                    + dispatch.governance_accountability.incident_prepared_count
                    + dispatch.governance_accountability.accountability_blocked_count
                ),
                open_water_emergencies=count_open_water_emergencies(water_emergencies),
                audit_correlation_count=count_audit_correlation_ids(
                    intake_records,
                    work_orders,
                    visits,
                    route_assignments,
                    review_items,
                    operational_events,
                ),
            ),
            lifecycle_summary=lifecycle,
            manual_review_summary=review,
            dispatch_summary=dispatch,
            timeline_summary=timeline,
        )

    def build_lifecycle(
        self,
        *,
        intake_records: Sequence[IntakeProcessingRecord] = (),
        jobs: Sequence[Job] = (),
        work_orders: Sequence[WorkOrder] = (),
        visits: Sequence[Visit] = (),
        route_assignments: Sequence[RouteAssignment] = (),
        water_emergencies: Sequence[WaterEmergency] = (),
    ) -> DispatchLifecycleSummary:
        water_job_ids = {record.job_id for record in water_emergencies}
        return DispatchLifecycleSummary(
            intake_lifecycle_counts=count_by_attr(intake_records, "lifecycle_state"),
            job_status_counts=count_by_attr(jobs, "status"),
            work_order_status_counts=count_by_attr(work_orders, "status"),
            visit_status_counts=count_by_attr(visits, "status"),
            route_status_counts=count_by_attr(route_assignments, "status"),
            dispatch_execution_state_counts=count_by_attr(
                route_assignments,
                "dispatch_execution_state",
            ),
            dispatch_ready_visits=count_where(
                visits,
                lambda visit: (
                    visit.status == "dispatch_ready"
                    and is_standard_dispatch_visit(visit, water_job_ids=water_job_ids)
                ),
            ),
            dispatched_route_assignments=count_where(
                route_assignments,
                lambda route: (
                    route.status == "dispatched" or route.dispatch_execution_state == "dispatched"
                ),
            ),
            water_emergency_records=len(water_emergencies),
            water_emergency_separated_intake=count_where(
                intake_records,
                lambda record: bool(record.water_emergency_separated),
            ),
            blocker_count=(
                count_where(intake_records, lambda record: bool(record.blocked or record.unsafe))
                + count_where(jobs, lambda job: has_review_required_state(job.status))
                + count_where(visits, lambda visit: has_review_required_state(visit.status))
                + count_route_blockers(route_assignments)
            ),
        )

    def build_review(
        self,
        *,
        review_items: Sequence[ReviewItem] = (),
    ) -> ManualReviewSummary:
        return ManualReviewSummary(
            total_items=len(review_items),
            open_items=count_where(
                review_items,
                lambda item: normalized(item.status) == "open",
            ),
            deferred_items=count_where(
                review_items,
                lambda item: normalized(item.status) == "deferred",
            ),
            resolved_items=count_where(
                review_items,
                lambda item: (
                    normalized(item.status) in RESOLVED_REVIEW_STATUSES
                    and normalized(item.status) != "archived"
                ),
            ),
            archived_items=count_where(
                review_items,
                lambda item: normalized(item.status) == "archived",
            ),
            severity_counts=count_by_attr(review_items, "severity"),
            reason_counts=count_by_attr(review_items, "reason_code"),
            escalation_indicators=count_where(
                review_items,
                lambda item: (
                    normalized(item.status) in UNRESOLVED_REVIEW_STATUSES
                    and normalized(item.severity) in ESCALATION_SEVERITIES
                ),
            ),
            audit_correlation_count=count_audit_correlation_ids(review_items),
        )

    def build_manual_review_queue(
        self,
        *,
        jobs: Sequence[Job] = (),
        work_orders: Sequence[WorkOrder] = (),
        visits: Sequence[Visit] = (),
        route_assignments: Sequence[RouteAssignment] = (),
        review_items: Sequence[ReviewItem] = (),
        water_emergencies: Sequence[WaterEmergency] = (),
    ) -> ManualReviewQueueReadModel:
        generated_at = self.now()
        queue_items = tuple(
            sorted(
                (
                    manual_review_queue_item(
                        review,
                        jobs=jobs,
                        work_orders=work_orders,
                        visits=visits,
                        route_assignments=route_assignments,
                        water_emergencies=water_emergencies,
                        now=generated_at,
                    )
                    for review in review_items
                ),
                key=manual_review_queue_sort_key,
            ),
        )

        return ManualReviewQueueReadModel(
            generated_at=generated_at,
            total_items=len(review_items),
            open_items=count_where(
                review_items,
                lambda item: normalized(item.status) == "open",
            ),
            deferred_items=count_where(
                review_items,
                lambda item: normalized(item.status) == "deferred",
            ),
            resolved_items=count_where(review_items, is_resolved_manual_review),
            archived_items=count_where(
                review_items,
                lambda item: normalized(item.status) == "archived",
            ),
            active_attention_count=count_where(
                queue_items,
                lambda item: item.attention_indicator,
            ),
            water_emergency_related_count=count_where(
                queue_items,
                lambda item: "water_emergency_related" in item.visibility_groups,
            ),
            dispatch_related_count=count_where(
                queue_items,
                lambda item: "dispatch_related" in item.visibility_groups,
            ),
            blocked_count=count_where(
                queue_items,
                lambda item: item.blocker_indicator,
            ),
            status_counts=count_by_attr(review_items, "status"),
            reason_counts=count_by_attr(review_items, "reason_code"),
            severity_counts=count_by_attr(review_items, "severity"),
            group_counts=count_values(
                group for item in queue_items for group in item.visibility_groups
            ),
            decision_readiness_counts=count_by_attr(
                (item.decision_readiness for item in queue_items),
                "label",
            ),
            action_preflight_counts=count_by_attr(
                (item.action_preflight for item in queue_items),
                "label",
            ),
            future_action_preview_counts=count_by_attr(
                (item.future_action_preview for item in queue_items),
                "label",
            ),
            command_contract_counts=count_by_attr(
                (item.command_contract for item in queue_items),
                "label",
            ),
            audit_ledger_dry_run_counts=count_by_attr(
                (item.audit_ledger_dry_run for item in queue_items),
                "label",
            ),
            command_validation_counts=count_by_attr(
                (item.command_validation for item in queue_items),
                "label",
            ),
            permission_readiness_counts=count_by_attr(
                (item.permission_readiness for item in queue_items),
                "label",
            ),
            age_bucket_counts=count_by_attr(queue_items, "age_bucket"),
            audit_correlation_count=count_audit_correlation_ids(review_items),
            taxonomy_metadata=manual_review_taxonomy_metadata(),
            available_filters=manual_review_filter_options(queue_items),
            sort_options=MANUAL_REVIEW_SORT_OPTIONS,
            result_window_metadata=manual_review_result_window_metadata(
                queue_items=queue_items,
                generated_at=generated_at,
            ),
            items=queue_items,
        )

    def build_manual_review_detail(
        self,
        review_item_id: object,
        *,
        jobs: Sequence[Job] = (),
        work_orders: Sequence[WorkOrder] = (),
        visits: Sequence[Visit] = (),
        route_assignments: Sequence[RouteAssignment] = (),
        review_items: Sequence[ReviewItem] = (),
        water_emergencies: Sequence[WaterEmergency] = (),
        operational_events: Sequence[OperationalEventRecord] = (),
        timeline_limit: int = 25,
    ) -> ManualReviewDetailReadModel | None:
        generated_at = self.now()
        review = next(
            (item for item in review_items if item.id == review_item_id),
            None,
        )
        if review is None:
            return None

        queue_item = manual_review_queue_item(
            review,
            jobs=jobs,
            work_orders=work_orders,
            visits=visits,
            route_assignments=route_assignments,
            water_emergencies=water_emergencies,
            now=generated_at,
        )
        related_events = manual_review_related_events(
            queue_item,
            review,
            operational_events=operational_events,
        )

        return ManualReviewDetailReadModel(
            generated_at=generated_at,
            review_item=queue_item,
            reason_context=manual_review_reason_evidence_context(
                review,
                queue_item=queue_item,
            ),
            decision_readiness=queue_item.decision_readiness,
            action_preflight=queue_item.action_preflight,
            future_action_preview=queue_item.future_action_preview,
            command_contract=queue_item.command_contract,
            audit_ledger_dry_run=queue_item.audit_ledger_dry_run,
            command_validation=queue_item.command_validation,
            permission_readiness=queue_item.permission_readiness,
            linked_entity_context=manual_review_detail_linked_entity_context(
                queue_item,
                jobs=jobs,
                work_orders=work_orders,
                visits=visits,
                route_assignments=route_assignments,
                water_emergencies=water_emergencies,
                review_events=related_events,
            ),
            data_gap_counts=manual_review_detail_data_gap_counts(
                queue_item,
                related_events=related_events,
            ),
            audit_correlation_ids=unique_audit_correlation_ids((review,), related_events),
            taxonomy_metadata=manual_review_taxonomy_metadata(),
            timeline_summary=self.build_timeline(
                operational_events=related_events,
                limit=timeline_limit,
            ),
        )

    def build_water_emergency(
        self,
        *,
        jobs: Sequence[Job] = (),
        work_orders: Sequence[WorkOrder] = (),
        visits: Sequence[Visit] = (),
        review_items: Sequence[ReviewItem] = (),
        water_emergencies: Sequence[WaterEmergency] = (),
        operational_events: Sequence[OperationalEventRecord] = (),
        timeline_limit: int = 25,
    ) -> WaterEmergencyDashboardReadModel:
        water_job_ids = {record.job_id for record in water_emergencies}
        water_record_ids = {record.id for record in water_emergencies if record.id is not None}
        related_jobs = tuple(job for job in jobs if job.id in water_job_ids)
        related_work_orders = tuple(
            work_order for work_order in work_orders if work_order.job_id in water_job_ids
        )
        related_visits = tuple(visit for visit in visits if visit.job_id in water_job_ids)
        water_visit_ids = {visit.id for visit in related_visits if visit.id is not None}
        water_work_order_ids = {
            work_order.id for work_order in related_work_orders if work_order.id is not None
        }
        related_reviews = tuple(
            review
            for review in review_items
            if is_water_emergency_review_item(
                review,
                water_job_ids=water_job_ids,
                water_visit_ids=water_visit_ids,
                water_record_ids=water_record_ids,
            )
        )
        related_events = tuple(
            event
            for event in operational_events
            if is_water_emergency_event(
                event,
                water_job_ids=water_job_ids,
                water_visit_ids=water_visit_ids,
                water_work_order_ids=water_work_order_ids,
                water_record_ids=water_record_ids,
            )
        )
        open_records = tuple(
            record for record in water_emergencies if is_open_water_emergency(record)
        )
        next_step_summary = water_emergency_next_step_readiness_summary(
            water_emergencies,
            work_orders=related_work_orders,
            visits=related_visits,
            review_items=related_reviews,
            operational_events=related_events,
        )
        generated_at = self.now()
        operator_queue_summary = water_emergency_operator_queue_summary(next_step_summary)
        aging_followup_summary = water_emergency_aging_followup_summary(
            water_emergencies,
            now=generated_at,
            work_orders=related_work_orders,
            visits=related_visits,
            review_items=related_reviews,
            operational_events=related_events,
        )
        view_state_summary = water_emergency_view_state_summary(
            next_step_summary=next_step_summary,
            operator_queue_summary=operator_queue_summary,
            aging_followup_summary=aging_followup_summary,
        )
        result_window_metadata = water_emergency_result_window_metadata(
            view_state_summary=view_state_summary,
            generated_at=generated_at,
        )

        return WaterEmergencyDashboardReadModel(
            generated_at=generated_at,
            total_records=len(water_emergencies),
            open_count=len(open_records),
            closed_count=len(water_emergencies) - len(open_records),
            status_counts=count_by_attr(water_emergencies, "status"),
            stage_counts=count_by_attr(water_emergencies, "drying_stage"),
            multi_visit_count=count_multi_visit_water_emergencies(
                water_emergencies,
                visits=related_visits,
            ),
            equipment_onsite_count=count_where(
                water_emergencies,
                lambda record: bool(record.equipment_onsite),
            ),
            moisture_tracking_required_count=count_where(
                water_emergencies,
                lambda record: bool(record.moisture_tracking_required),
            ),
            equipment_summary=water_emergency_equipment_summary(
                water_emergencies,
                work_orders=related_work_orders,
            ),
            visit_chain_summary=water_emergency_visit_chain_summary(
                water_emergencies,
                visits=related_visits,
            ),
            drying_stage_summary=water_emergency_drying_stage_summary(water_emergencies),
            review_exception_summary=water_emergency_review_exception_summary(
                water_emergencies,
                visits=related_visits,
                review_items=related_reviews,
            ),
            next_step_summary=next_step_summary,
            operator_queue_summary=operator_queue_summary,
            aging_followup_summary=aging_followup_summary,
            view_state_summary=view_state_summary,
            governance_metadata=water_emergency_governance_metadata(),
            result_window_metadata=result_window_metadata,
            related_job_count=len(related_jobs),
            related_work_order_count=len(water_work_order_ids),
            related_visit_count=len(water_visit_ids),
            review_indicator_count=count_where(
                related_reviews,
                lambda review: normalized(review.status) in UNRESOLVED_REVIEW_STATUSES,
            ),
            escalation_indicator_count=count_where(
                related_reviews,
                lambda review: (
                    normalized(review.status) in UNRESOLVED_REVIEW_STATUSES
                    and normalized(review.severity) in ESCALATION_SEVERITIES
                ),
            ),
            data_gap_counts=water_emergency_data_gap_counts(
                water_emergencies,
                visits=related_visits,
                events=related_events,
            ),
            audit_correlation_count=count_audit_correlation_ids(
                related_work_orders,
                related_visits,
                related_reviews,
                related_events,
            ),
            records=tuple(
                water_emergency_record_summary(
                    record,
                    work_orders=related_work_orders,
                    visits=related_visits,
                    review_items=related_reviews,
                    operational_events=related_events,
                )
                for record in sorted(
                    water_emergencies,
                    key=lambda record: (
                        not is_open_water_emergency(record),
                        normalized(record.status),
                        str(record.job_id),
                    ),
                )
            ),
            timeline_summary=self.build_timeline(
                operational_events=related_events,
                limit=timeline_limit,
            ),
        )

    def build_water_emergency_detail(
        self,
        water_emergency_id: object,
        *,
        jobs: Sequence[Job] = (),
        work_orders: Sequence[WorkOrder] = (),
        visits: Sequence[Visit] = (),
        review_items: Sequence[ReviewItem] = (),
        water_emergencies: Sequence[WaterEmergency] = (),
        operational_events: Sequence[OperationalEventRecord] = (),
        timeline_limit: int = 25,
    ) -> WaterEmergencyDetailReadModel | None:
        record = next(
            (
                water_emergency
                for water_emergency in water_emergencies
                if water_emergency.id == water_emergency_id
            ),
            None,
        )
        if record is None:
            return None

        related_job = next((job for job in jobs if job.id == record.job_id), None)
        related_work_orders = water_emergency_related_work_orders(
            record,
            work_orders=work_orders,
        )
        related_visits = water_emergency_related_visits(record, visits=visits)
        related_reviews = water_emergency_related_reviews(
            record,
            visits=related_visits,
            review_items=review_items,
        )
        related_events = water_emergency_related_events(
            record,
            work_orders=related_work_orders,
            visits=related_visits,
            operational_events=operational_events,
        )

        return WaterEmergencyDetailReadModel(
            generated_at=self.now(),
            record=water_emergency_record_summary(
                record,
                work_orders=related_work_orders,
                visits=related_visits,
                review_items=related_reviews,
                operational_events=related_events,
            ),
            job=water_emergency_job_reference(related_job) if related_job else None,
            work_orders=tuple(
                water_emergency_work_order_reference(work_order)
                for work_order in sorted(
                    related_work_orders,
                    key=lambda work_order: (
                        normalized(work_order.work_order_number),
                        str(work_order.id),
                    ),
                )
            ),
            visits=tuple(
                water_emergency_visit_reference(visit)
                for visit in sorted(
                    related_visits,
                    key=lambda visit: (
                        sortable_datetime(visit.scheduled_start_at),
                        str(visit.id),
                    ),
                )
            ),
            review_indicators=tuple(
                water_emergency_review_indicator(review)
                for review in sorted(
                    related_reviews,
                    key=lambda review: (
                        normalized(review.status),
                        normalized(review.reason_code),
                        str(review.id),
                    ),
                )
            ),
            equipment_context=water_emergency_detail_equipment_context(
                record,
                work_orders=related_work_orders,
            ),
            visit_chain=water_emergency_detail_visit_chain(related_visits),
            drying_stage_context=water_emergency_detail_drying_stage_context(record),
            review_exception_context=water_emergency_review_exception_context(
                related_reviews,
            ),
            next_step_readiness=water_emergency_next_step_readiness(
                record,
                work_orders=related_work_orders,
                visits=related_visits,
                review_items=related_reviews,
                operational_events=related_events,
            ),
            data_gap_counts=water_emergency_detail_data_gap_counts(
                record,
                job=related_job,
                work_orders=related_work_orders,
                visits=related_visits,
                events=related_events,
            ),
            audit_correlation_ids=unique_audit_correlation_ids(
                related_work_orders,
                related_visits,
                related_reviews,
                related_events,
            ),
            timeline_summary=self.build_timeline(
                operational_events=related_events,
                limit=timeline_limit,
            ),
        )

    def build_dispatch(
        self,
        *,
        route_assignments: Sequence[RouteAssignment] = (),
    ) -> DashboardDispatchSummary:
        return DashboardDispatchSummary(
            route_assignments=RouteAssignmentSummary(
                total_assignments=len(route_assignments),
                status_counts=count_by_attr(route_assignments, "status"),
                region_counts=count_by_attr(route_assignments, "region"),
                time_window_counts=count_by_attr(route_assignments, "time_window"),
                authorization_state_counts=count_authorization_states(route_assignments),
                dispatched_count=count_where(
                    route_assignments,
                    lambda route: (
                        route.status == "dispatched"
                        or route.dispatch_execution_state == "dispatched"
                    ),
                ),
                awaiting_dispatch_execution_count=count_where(
                    route_assignments,
                    lambda route: route.dispatch_execution_state == "awaiting_dispatch_execution",
                ),
                blocked_count=count_route_blockers(route_assignments),
            ),
            external_execution=ExternalExecutionSummary(
                adapter_state_counts=count_by_attr(route_assignments, "external_adapter_state"),
                execution_state_counts=count_by_attr(route_assignments, "external_execution_state"),
                confirmation_state_counts=count_by_attr(
                    route_assignments,
                    "external_confirmation_state",
                ),
                prepared_count=count_where(
                    route_assignments,
                    lambda route: (
                        route.external_adapter_prepared_at is not None
                        or route.external_adapter_state == "awaiting_external_execution"
                    ),
                ),
                execution_completed_count=count_where(
                    route_assignments,
                    lambda route: route.external_execution_completed_at is not None,
                ),
                execution_failed_count=count_where(
                    route_assignments,
                    lambda route: (
                        route.external_execution_failed_at is not None
                        or bool(route.external_execution_failure_snapshot)
                    ),
                ),
                confirmation_failed_count=count_where(
                    route_assignments,
                    lambda route: (
                        route.external_confirmation_failed_at is not None
                        or bool(route.external_failure_snapshot)
                    ),
                ),
                retry_prepared_count=count_where(
                    route_assignments,
                    lambda route: (
                        route.retry_prepared_at is not None
                        or bool(route.retry_preparation_snapshot)
                    ),
                ),
                reconciliation_required_count=count_where(
                    route_assignments,
                    lambda route: (
                        route.reconciliation_required_at is not None
                        or route.dispatch_reconciliation_state == "reconciliation_required"
                    ),
                ),
            ),
            reconciliation_recovery=ReconciliationRecoverySummary(
                reconciliation_state_counts=count_by_attr(
                    route_assignments,
                    "dispatch_reconciliation_state",
                ),
                recovery_state_counts=count_by_attr(route_assignments, "replay_recovery_state"),
                mismatch_count=sum_mismatch_counts(route_assignments),
                divergence_count=count_where(
                    route_assignments,
                    lambda route: bool(route.dispatch_divergence_snapshot),
                ),
                replay_prepared_count=count_where(
                    route_assignments,
                    lambda route: (
                        route.replay_prepared_at is not None
                        or route.replay_recovery_state == "replay_prepared"
                    ),
                ),
                rollback_prepared_count=count_where(
                    route_assignments,
                    lambda route: (
                        route.rollback_prepared_at is not None
                        or route.replay_recovery_state == "rollback_prepared"
                    ),
                ),
                recovery_blocked_count=count_where(
                    route_assignments,
                    lambda route: (
                        route.replay_blocked_at is not None
                        or bool(route.replay_blocker_snapshot)
                        or normalized(route.replay_recovery_state) in BLOCKED_ROUTE_STATES
                    ),
                ),
            ),
            governance_accountability=GovernanceAccountabilitySummary(
                governance_state_counts=count_by_attr(route_assignments, "governance_state"),
                accountability_state_counts=count_by_attr(
                    route_assignments,
                    "accountability_state",
                ),
                operator_approved_count=count_where(
                    route_assignments,
                    lambda route: (
                        route.governance_approved_at is not None
                        or route.governance_state == "operator_approved"
                    ),
                ),
                intervention_required_count=count_where(
                    route_assignments,
                    lambda route: (
                        route.intervention_required_at is not None
                        or route.governance_state == "manual_intervention_required"
                    ),
                ),
                escalation_required_count=count_where(
                    route_assignments,
                    lambda route: (
                        route.escalation_required_at is not None
                        or route.accountability_state == "escalation_required"
                    ),
                ),
                incident_prepared_count=count_where(
                    route_assignments,
                    lambda route: (
                        route.incident_prepared_at is not None
                        or route.accountability_state == "incident_prepared"
                    ),
                ),
                accountability_blocked_count=count_where(
                    route_assignments,
                    lambda route: (
                        route.accountability_blocked_at is not None
                        or bool(route.escalation_blocker_snapshot)
                        or normalized(route.accountability_state) in BLOCKED_ACCOUNTABILITY_STATES
                    ),
                ),
            ),
        )

    def build_timeline(
        self,
        *,
        operational_events: Sequence[OperationalEventRecord] = (),
        limit: int = 50,
    ) -> OperationalEventTimelineSummary:
        ordered_events = sorted(
            operational_events,
            key=lambda event: (event.occurred_at, event.recorded_at, event.event_fingerprint),
        )
        limited_events = ordered_events[:limit]
        return OperationalEventTimelineSummary(
            total_events=len(operational_events),
            returned_events=len(limited_events),
            mutable_event_count=count_where(
                operational_events,
                lambda event: not event.is_immutable,
            ),
            audit_correlation_ids=tuple(
                sorted(
                    {
                        event.audit_correlation_id
                        for event in operational_events
                        if event.audit_correlation_id
                    },
                ),
            ),
            entries=tuple(timeline_entry(event) for event in limited_events),
        )

    def build_overview_from_session(self, session: Session) -> DashboardOverviewReadModel:
        source = load_dashboard_source(session)
        return self.build_overview(**source)

    def build_lifecycle_from_session(self, session: Session) -> DispatchLifecycleSummary:
        source = load_dashboard_source(session)
        return self.build_lifecycle(
            intake_records=source["intake_records"],
            jobs=source["jobs"],
            work_orders=source["work_orders"],
            visits=source["visits"],
            route_assignments=source["route_assignments"],
            water_emergencies=source["water_emergencies"],
        )

    def build_review_from_session(self, session: Session) -> ManualReviewSummary:
        source = load_dashboard_source(session)
        return self.build_review(review_items=source["review_items"])

    def build_manual_review_queue_from_session(
        self,
        session: Session,
    ) -> ManualReviewQueueReadModel:
        source = load_dashboard_source(session)
        return self.build_manual_review_queue(
            jobs=source["jobs"],
            work_orders=source["work_orders"],
            visits=source["visits"],
            route_assignments=source["route_assignments"],
            review_items=source["review_items"],
            water_emergencies=source["water_emergencies"],
        )

    def build_manual_review_detail_from_session(
        self,
        session: Session,
        review_item_id: object,
    ) -> ManualReviewDetailReadModel | None:
        source = load_dashboard_source(session)
        return self.build_manual_review_detail(
            review_item_id,
            jobs=source["jobs"],
            work_orders=source["work_orders"],
            visits=source["visits"],
            route_assignments=source["route_assignments"],
            review_items=source["review_items"],
            water_emergencies=source["water_emergencies"],
            operational_events=source["operational_events"],
        )

    def build_dispatch_from_session(self, session: Session) -> DashboardDispatchSummary:
        source = load_dashboard_source(session)
        return self.build_dispatch(route_assignments=source["route_assignments"])

    def build_water_emergency_from_session(
        self,
        session: Session,
    ) -> WaterEmergencyDashboardReadModel:
        source = load_dashboard_source(session)
        return self.build_water_emergency(
            jobs=source["jobs"],
            work_orders=source["work_orders"],
            visits=source["visits"],
            review_items=source["review_items"],
            water_emergencies=source["water_emergencies"],
            operational_events=source["operational_events"],
        )

    def build_water_emergency_detail_from_session(
        self,
        session: Session,
        water_emergency_id: object,
    ) -> WaterEmergencyDetailReadModel | None:
        source = load_dashboard_source(session)
        return self.build_water_emergency_detail(
            water_emergency_id,
            jobs=source["jobs"],
            work_orders=source["work_orders"],
            visits=source["visits"],
            review_items=source["review_items"],
            water_emergencies=source["water_emergencies"],
            operational_events=source["operational_events"],
        )


def load_dashboard_source(session: Session) -> dict[str, Sequence[object]]:
    return {
        "intake_records": select_all(session, IntakeProcessingRecord),
        "jobs": select_all(session, Job),
        "work_orders": select_all(session, WorkOrder),
        "visits": select_all(session, Visit),
        "route_assignments": select_all(session, RouteAssignment),
        "review_items": select_all(session, ReviewItem),
        "water_emergencies": select_all(session, WaterEmergency),
        "operational_events": select_all(session, OperationalEventRecord),
    }


def select_all(session: Session, model: type[object]) -> Sequence[object]:
    return session.scalars(select(model)).all()


def count_by_attr(items: Sequence[object], attr: str) -> tuple[CountBucket, ...]:
    return count_values(getattr(item, attr, None) for item in items)


def count_values(values: Sequence[object] | object) -> tuple[CountBucket, ...]:
    counter: Counter[str] = Counter()
    for value in values:
        label = normalized(value)
        if label:
            counter[label] += 1
    return tuple(CountBucket(label=label, count=counter[label]) for label in sorted(counter))


def normalized(value: object) -> str:
    return str(value).strip().lower() if value is not None else ""


def sortable_datetime(value: datetime | None) -> datetime:
    return value if value is not None else MAX_SORTABLE_DATETIME


def count_where(items: Sequence[object], predicate: Callable[[object], bool]) -> int:
    return sum(1 for item in items if predicate(item))


def has_review_required_state(value: object) -> bool:
    return normalized(value) in {"review_required", "needs_manual_review"}


def count_route_blockers(route_assignments: Sequence[RouteAssignment]) -> int:
    return count_where(
        route_assignments,
        lambda route: (
            normalized(route.status) in BLOCKED_ROUTE_STATES
            or normalized(route.dispatch_execution_state) in BLOCKED_ROUTE_STATES
            or normalized(route.dispatch_reconciliation_state) in BLOCKED_ROUTE_STATES
            or normalized(route.replay_recovery_state) in BLOCKED_ROUTE_STATES
            or normalized(route.governance_state) in BLOCKED_GOVERNANCE_STATES
            or normalized(route.accountability_state) in BLOCKED_ACCOUNTABILITY_STATES
            or bool(route.dispatch_reconciliation_blocker_snapshot)
            or bool(route.replay_blocker_snapshot)
            or bool(route.governance_blocker_snapshot)
            or bool(route.escalation_blocker_snapshot)
        ),
    )


def manual_review_taxonomy_metadata() -> ManualReviewTaxonomyMetadata:
    return ManualReviewTaxonomyMetadata(
        randall_authorized_phase_0_baseline=True,
        source="phase_0_visibility_heuristic",
        legal_or_insurance_policy=False,
        requires_alfonso_owner_review=False,
        baseline_note=(
            "Manual Review queue groups are Randall-authorized Phase 0 "
            "visibility baselines only. They do not approve, reject, defer, "
            "archive, dispatch, or establish final legal or insurance policy."
        ),
        group_definitions=tuple(
            ManualReviewTaxonomyMetadataItem(
                key=key,
                label=label,
                category="manual_review_visibility",
                source="phase_0_visibility_heuristic",
                randall_authorized_phase_0_baseline=True,
                legal_or_insurance_policy=False,
                requires_alfonso_owner_review=False,
                reason=reason,
            )
            for key, label, reason in MANUAL_REVIEW_GROUP_DEFINITIONS
        ),
    )


def manual_review_filter_options(
    queue_items: Sequence[ManualReviewQueueItem],
) -> tuple[ManualReviewFilterOption, ...]:
    filter_counts = Counter(
        filter_group for item in queue_items for filter_group in item.visibility_groups
    )
    filter_counts["all"] = len(queue_items)
    filter_counts["active_attention"] = count_where(
        queue_items,
        lambda item: item.attention_indicator,
    )

    return tuple(
        ManualReviewFilterOption(
            key=key,
            label=label,
            count=filter_counts[key],
            description=description,
        )
        for key, label, description in MANUAL_REVIEW_FILTER_DEFINITIONS
    )


def manual_review_result_window_metadata(
    *,
    queue_items: Sequence[ManualReviewQueueItem],
    generated_at: datetime,
) -> ManualReviewResultWindowMetadata:
    total_count = len(queue_items)
    return ManualReviewResultWindowMetadata(
        total_count=total_count,
        visible_count=total_count,
        result_limit=total_count,
        has_more=False,
        sort_key="attention",
        generated_at=generated_at,
    )


def manual_review_queue_item(
    review: ReviewItem,
    *,
    jobs: Sequence[Job],
    work_orders: Sequence[WorkOrder],
    visits: Sequence[Visit],
    route_assignments: Sequence[RouteAssignment],
    water_emergencies: Sequence[WaterEmergency],
    now: datetime,
) -> ManualReviewQueueItem:
    created_at = getattr(review, "created_at", None) or now
    updated_at = getattr(review, "updated_at", None) or created_at
    job_id = manual_review_job_id(
        review,
        work_orders=work_orders,
        visits=visits,
        route_assignments=route_assignments,
    )
    visit_id = manual_review_visit_id(review, route_assignments=route_assignments)
    work_order_id = manual_review_work_order_id(
        review,
        job_id=job_id,
        visit_id=visit_id,
        work_orders=work_orders,
        visits=visits,
    )
    route_assignment_id = manual_review_route_assignment_id(review)
    water_emergency_id = manual_review_water_emergency_id(
        review,
        job_id=job_id,
        visit_id=visit_id,
        water_emergencies=water_emergencies,
        visits=visits,
    )
    groups = manual_review_visibility_groups(
        review,
        job_id=job_id,
        work_order_id=work_order_id,
        visit_id=visit_id,
        route_assignment_id=route_assignment_id,
        water_emergency_id=water_emergency_id,
    )
    status = normalized(review.status) or "unknown"
    evidence_references = manual_review_evidence_references(
        review,
        job_id=job_id,
        work_order_id=work_order_id,
        visit_id=visit_id,
        route_assignment_id=route_assignment_id,
        water_emergency_id=water_emergency_id,
    )
    decision_readiness = manual_review_decision_readiness(
        review,
        groups=groups,
        entity_type=normalized(review.entity_type) or None,
        entity_id=review.entity_id,
        job_id=job_id,
        work_order_id=work_order_id,
        visit_id=visit_id,
        route_assignment_id=route_assignment_id,
        water_emergency_id=water_emergency_id,
        evidence_references=evidence_references,
    )
    action_preflight = manual_review_action_preflight(
        review,
        groups=groups,
        decision_readiness=decision_readiness,
        entity_type=normalized(review.entity_type) or None,
        entity_id=review.entity_id,
        job_id=job_id,
        work_order_id=work_order_id,
        visit_id=visit_id,
        route_assignment_id=route_assignment_id,
        water_emergency_id=water_emergency_id,
        evidence_references=evidence_references,
    )
    future_action_preview = manual_review_future_action_preview(
        review,
        groups=groups,
        decision_readiness=decision_readiness,
        action_preflight=action_preflight,
        job_id=job_id,
        work_order_id=work_order_id,
        visit_id=visit_id,
        route_assignment_id=route_assignment_id,
        water_emergency_id=water_emergency_id,
        evidence_references=evidence_references,
    )
    command_contract = manual_review_command_contract(
        review,
        groups=groups,
        decision_readiness=decision_readiness,
        action_preflight=action_preflight,
        future_action_preview=future_action_preview,
        job_id=job_id,
        work_order_id=work_order_id,
        visit_id=visit_id,
        route_assignment_id=route_assignment_id,
        water_emergency_id=water_emergency_id,
        evidence_references=evidence_references,
    )
    audit_ledger_dry_run = manual_review_audit_ledger_dry_run(
        review,
        groups=groups,
        action_preflight=action_preflight,
        command_contract=command_contract,
        evidence_references=evidence_references,
        water_emergency_id=water_emergency_id,
    )
    command_validation = manual_review_command_validation(
        review,
        groups=groups,
        decision_readiness=decision_readiness,
        action_preflight=action_preflight,
        future_action_preview=future_action_preview,
        command_contract=command_contract,
        audit_ledger_dry_run=audit_ledger_dry_run,
        job_id=job_id,
        work_order_id=work_order_id,
        visit_id=visit_id,
        route_assignment_id=route_assignment_id,
        water_emergency_id=water_emergency_id,
        evidence_references=evidence_references,
    )
    permission_readiness = manual_review_permission_readiness(
        review,
        groups=groups,
        command_validation=command_validation,
        command_contract=command_contract,
        water_emergency_id=water_emergency_id,
        evidence_references=evidence_references,
    )

    return ManualReviewQueueItem(
        review_item_id=review.id or NIL_UUID,
        status=status,
        severity=normalized(review.severity) or None,
        reason_code=normalized(review.reason_code) or "unspecified",
        visibility_groups=groups,
        primary_group=manual_review_primary_group(groups),
        entity_type=normalized(review.entity_type) or None,
        entity_id=review.entity_id,
        job_id=job_id,
        work_order_id=work_order_id,
        visit_id=visit_id,
        route_assignment_id=route_assignment_id,
        water_emergency_id=water_emergency_id,
        created_at=created_at,
        updated_at=updated_at,
        reviewed_at=review.reviewed_at,
        deferred_until=review.deferred_until,
        resolved_at=review.resolved_at,
        age_bucket=manual_review_age_bucket(review, now=now),
        age_hours=hours_between(created_at, now),
        blocker_indicator=is_blocker_manual_review(review),
        attention_indicator=is_active_manual_review(review),
        confidence_score=review.confidence_score,
        recommended_action=review.recommended_action,
        audit_correlation_id=review.audit_correlation_id,
        decision_readiness=decision_readiness,
        action_preflight=action_preflight,
        future_action_preview=future_action_preview,
        command_contract=command_contract,
        audit_ledger_dry_run=audit_ledger_dry_run,
        command_validation=command_validation,
        permission_readiness=permission_readiness,
        evidence_references=evidence_references,
    )


def manual_review_decision_readiness(
    review: ReviewItem,
    *,
    groups: Sequence[str],
    entity_type: str | None,
    entity_id: UUID | None,
    job_id: UUID | None,
    work_order_id: UUID | None,
    visit_id: UUID | None,
    route_assignment_id: UUID | None,
    water_emergency_id: UUID | None,
    evidence_references: Sequence[str],
) -> ManualReviewDecisionReadiness:
    status = normalized(review.status)
    reason_codes: list[str] = []

    if status in RESOLVED_REVIEW_STATUSES or status == "archived":
        label = "resolved_or_archived"
        summary = (
            "Resolved or archived Manual Review evidence is retained as read-only history; "
            "it is not an active decision need."
        )
        reason_codes.append("resolved_or_archived_status")
        return ManualReviewDecisionReadiness(
            label=label,
            summary=summary,
            reason_codes=tuple(reason_codes),
            evidence_references=tuple(evidence_references),
            is_active_decision_need=False,
            is_resolution_candidate=False,
        )

    if water_emergency_id is not None:
        label = "needs_water_emergency_review"
        summary = (
            "This Manual Review item is specifically tied to Water Emergency evidence and "
            "remains separated from standard dispatch review context."
        )
        reason_codes.append("water_emergency_related")
        if "duplicate_or_conflict" in groups:
            reason_codes.append("duplicate_or_conflict_evidence")
        if "missing_data" in groups:
            reason_codes.append("missing_data_evidence")
    elif manual_review_needs_entity_context(
        entity_type=entity_type,
        entity_id=entity_id,
        job_id=job_id,
        work_order_id=work_order_id,
        visit_id=visit_id,
        route_assignment_id=route_assignment_id,
        water_emergency_id=water_emergency_id,
    ):
        label = "needs_entity_context"
        summary = (
            "The review points to an entity that is not yet represented by a deterministic "
            "job, work-order, visit, route, or Water Emergency link."
        )
        reason_codes.append("entity_context_missing")
    elif "duplicate_or_conflict" in groups:
        label = "blocked_by_conflict"
        summary = (
            "Duplicate or conflicting evidence is present. Manual Review should keep this "
            "item blocked until an operator verifies the conflict."
        )
        reason_codes.append("duplicate_or_conflict_evidence")
    elif "missing_data" in groups:
        label = (
            "blocked_by_missing_data"
            if is_blocker_manual_review(review)
            else "needs_missing_information"
        )
        summary = (
            "Missing, invalid, incomplete, or unknown data is present. The review remains "
            "read-only and needs operator-safe information gathering before any future action."
        )
        reason_codes.append("missing_data_evidence")
    elif "dispatch_related" in groups:
        label = "needs_dispatch_review"
        summary = (
            "This Manual Review item is tied to standard dispatch, job, work-order, visit, "
            "or route evidence and remains visibility-only."
        )
        reason_codes.append("dispatch_related")
    elif status == "deferred":
        label = "ready_for_resolution_review"
        summary = (
            "Deferred Manual Review evidence is ready for a future authenticated resolution "
            "review, but no resolution is executed here."
        )
        reason_codes.append("deferred_resolution_candidate")
    elif status in UNRESOLVED_REVIEW_STATUSES:
        label = "ready_for_operator_decision"
        summary = (
            "Existing Manual Review evidence is available for future operator decision "
            "workflow design. This read model does not execute that decision."
        )
        reason_codes.append("active_review_evidence_available")
    else:
        label = "needs_operator_review"
        summary = (
            "No more specific deterministic readiness label is available, so this item "
            "remains in Manual Review for operator-safe visibility."
        )
        reason_codes.append("operator_review_required")

    if status in UNRESOLVED_REVIEW_STATUSES:
        reason_codes.append("active_manual_review")
    if is_blocker_manual_review(review):
        reason_codes.append("blocker_indicator")
    if normalized(review.severity) in ESCALATION_SEVERITIES:
        reason_codes.append("high_or_critical_severity")

    return ManualReviewDecisionReadiness(
        label=label,
        summary=summary,
        reason_codes=tuple(dict.fromkeys(reason_codes)),
        evidence_references=tuple(evidence_references),
        is_active_decision_need=status in UNRESOLVED_REVIEW_STATUSES,
        is_resolution_candidate=label
        in {"ready_for_operator_decision", "ready_for_resolution_review"},
    )


def manual_review_action_preflight(
    review: ReviewItem,
    *,
    groups: Sequence[str],
    decision_readiness: ManualReviewDecisionReadiness,
    entity_type: str | None,
    entity_id: UUID | None,
    job_id: UUID | None,
    work_order_id: UUID | None,
    visit_id: UUID | None,
    route_assignment_id: UUID | None,
    water_emergency_id: UUID | None,
    evidence_references: Sequence[str],
) -> ManualReviewActionPreflight:
    status = normalized(review.status)
    blocker_codes: list[str] = []
    required_future_controls = [
        "action_not_available_read_only_phase",
        "requires_future_auth",
        "requires_operator_identity",
        "requires_audit_reason",
    ]

    if status in RESOLVED_REVIEW_STATUSES or status == "archived":
        label = "blocked_by_resolved_or_archived_status"
        summary = (
            "Resolved or archived Manual Review items are historical visibility and are "
            "not eligible for active future review actions."
        )
        blocker_codes.append("resolved_or_archived_status")
    elif manual_review_needs_entity_context(
        entity_type=entity_type,
        entity_id=entity_id,
        job_id=job_id,
        work_order_id=work_order_id,
        visit_id=visit_id,
        route_assignment_id=route_assignment_id,
        water_emergency_id=water_emergency_id,
    ):
        label = "blocked_by_missing_entity_context"
        summary = (
            "Future Manual Review action is blocked until the review has deterministic "
            "linked entity context. This Phase 0 preflight does not execute an action."
        )
        blocker_codes.append("missing_entity_context")
    elif water_emergency_id is not None:
        label = "blocked_by_water_emergency_context"
        summary = (
            "Future Manual Review action must account for the linked Water Emergency "
            "context and remain separated from standard dispatch review actions."
        )
        blocker_codes.append("water_emergency_context_required")
        if "missing_data" in groups:
            blocker_codes.append("missing_data_context_required")
        if "duplicate_or_conflict" in groups:
            blocker_codes.append("conflict_context_required")
    elif "duplicate_or_conflict" in groups:
        label = "blocked_by_conflict"
        summary = (
            "Duplicate or conflicting evidence must remain blocked until a future "
            "operator-decision workflow is explicitly implemented."
        )
        blocker_codes.append("conflict_context_required")
    elif "missing_data" in groups:
        label = "blocked_by_missing_data"
        summary = (
            "Future Manual Review action is blocked until missing, invalid, incomplete, "
            "or unknown data has operator-safe resolution context."
        )
        blocker_codes.append("missing_data_context_required")
    elif decision_readiness.label == "ready_for_resolution_review":
        label = "eligible_for_resolution_review"
        summary = (
            "Existing evidence is ready for a future authenticated resolution review, "
            "but Phase 0 does not execute that resolution."
        )
    elif decision_readiness.label == "ready_for_operator_decision":
        label = "eligible_for_operator_decision"
        summary = (
            "Existing evidence is ready for a future authenticated operator decision, "
            "but Phase 0 does not execute approve, reject, defer, archive, or resolve actions."
        )
    else:
        label = "unknown_action_eligibility"
        summary = (
            "No deterministic future action eligibility can be selected safely, so the "
            "review remains read-only Manual Review visibility."
        )
        blocker_codes.append("unknown_action_eligibility")

    if decision_readiness.label:
        blocker_codes.append(f"readiness:{decision_readiness.label}")

    return ManualReviewActionPreflight(
        label=label,
        summary=summary,
        blocker_codes=tuple(dict.fromkeys(blocker_codes)),
        required_future_controls=tuple(required_future_controls),
        evidence_references=tuple(evidence_references),
        is_currently_executable=False,
        requires_operator_identity=True,
        requires_audit_reason=True,
    )


def manual_review_future_action_preview(
    review: ReviewItem,
    *,
    groups: Sequence[str],
    decision_readiness: ManualReviewDecisionReadiness,
    action_preflight: ManualReviewActionPreflight,
    job_id: UUID | None,
    work_order_id: UUID | None,
    visit_id: UUID | None,
    route_assignment_id: UUID | None,
    water_emergency_id: UUID | None,
    evidence_references: Sequence[str],
) -> ManualReviewFutureActionPreview:
    status = normalized(review.status)
    impacted_entity_references = manual_review_impacted_entity_references(
        review,
        job_id=job_id,
        work_order_id=work_order_id,
        visit_id=visit_id,
        route_assignment_id=route_assignment_id,
        water_emergency_id=water_emergency_id,
    )
    required_future_controls = (
        "preview_not_executable_read_only_phase",
        "requires_future_auth",
        "requires_operator_identity",
        "requires_audit_reason",
    )

    if status in RESOLVED_REVIEW_STATUSES or status == "archived":
        label = "no_action_available_resolved_or_archived"
        description = (
            "Resolved or archived Manual Review evidence is retained for history; "
            "no active future action preview is selected."
        )
        expected_outcome_summary = (
            "Future modules should keep this item separated from active action queues "
            "unless a new reviewed workflow explicitly reopens it."
        )
        blocker_codes = ("resolved_or_archived_status",)
    elif action_preflight.label == "blocked_by_missing_entity_context":
        label = "no_action_available_missing_entity_context"
        description = (
            "No future action preview is available until the review has deterministic "
            "linked entity context."
        )
        expected_outcome_summary = (
            "Future modules would need to connect this review to a known job, "
            "work order, visit, route assignment, or Water Emergency before action."
        )
        blocker_codes = ("missing_entity_context",)
    elif action_preflight.label == "blocked_by_water_emergency_context":
        label = "no_action_available_water_emergency_context"
        description = (
            "Water Emergency-related Manual Review requires separated future action "
            "design before any preview can become executable."
        )
        expected_outcome_summary = (
            "Future modules should route this item through Water Emergency-specific "
            "review preparation instead of standard dispatch action flow."
        )
        blocker_codes = ("water_emergency_context_required",)
    elif action_preflight.label == "blocked_by_conflict" or "duplicate_or_conflict" in groups:
        label = "no_action_available_conflict_blocked"
        description = (
            "Duplicate or conflicting evidence blocks future action preview until an "
            "operator-decision workflow is implemented."
        )
        expected_outcome_summary = (
            "Future modules should preserve the conflict for operator review and avoid "
            "automatic approval, rejection, or resolution."
        )
        blocker_codes = ("conflict_context_required",)
    elif action_preflight.label == "blocked_by_missing_data" or "missing_data" in groups:
        label = "future_request_information_preview"
        description = (
            "A future authenticated workflow may request or collect missing information; "
            "this read model does not resolve the review."
        )
        expected_outcome_summary = (
            "Expected non-binding outcome: gather missing information and keep Manual "
            "Review authoritative until an operator verifies the evidence."
        )
        blocker_codes = ("missing_data_context_required",)
    else:
        recommended_label = manual_review_future_action_label_for_recommendation(
            review.recommended_action,
        )
        if recommended_label is not None:
            label = recommended_label
        elif decision_readiness.label == "ready_for_resolution_review":
            label = "future_resolve_preview"
        elif decision_readiness.label == "ready_for_operator_decision":
            label = "future_operator_decision_preview"
        else:
            label = "unknown_action_preview"

        description = manual_review_future_action_description(label)
        expected_outcome_summary = manual_review_future_action_outcome(label)
        blocker_codes = ("unknown_action_preview",) if label == "unknown_action_preview" else ()

    blocker_codes = tuple(
        dict.fromkeys((*blocker_codes, *action_preflight.blocker_codes)),
    )

    return ManualReviewFutureActionPreview(
        label=label,
        description=description,
        expected_outcome_summary=expected_outcome_summary,
        impacted_entity_summary=manual_review_impacted_entity_summary(
            impacted_entity_references,
        ),
        impacted_entity_references=impacted_entity_references,
        blocker_codes=blocker_codes,
        required_future_controls=required_future_controls,
        evidence_references=tuple(evidence_references),
        is_currently_executable=False,
        requires_operator_identity=True,
        requires_audit_reason=True,
    )


def manual_review_command_contract(
    review: ReviewItem,
    *,
    groups: Sequence[str],
    decision_readiness: ManualReviewDecisionReadiness,
    action_preflight: ManualReviewActionPreflight,
    future_action_preview: ManualReviewFutureActionPreview,
    job_id: UUID | None,
    work_order_id: UUID | None,
    visit_id: UUID | None,
    route_assignment_id: UUID | None,
    water_emergency_id: UUID | None,
    evidence_references: Sequence[str],
) -> ManualReviewCommandContract:
    status = normalized(review.status)
    impacted_entity_references = manual_review_impacted_entity_references(
        review,
        job_id=job_id,
        work_order_id=work_order_id,
        visit_id=visit_id,
        route_assignment_id=route_assignment_id,
        water_emergency_id=water_emergency_id,
    )
    blocker_codes: list[str] = [
        *action_preflight.blocker_codes,
        *future_action_preview.blocker_codes,
    ]
    required_contract_labels = [
        "command_contract_read_only_phase",
        "requires_future_auth",
        "requires_operator_identity",
        "requires_role_authorization",
        "requires_audit_reason",
        "requires_idempotency_key",
        "requires_preflight_pass",
        "requires_immutable_event_recording",
        "requires_post_action_consistency_check",
        "command_not_executable_phase_0",
    ]

    if status in RESOLVED_REVIEW_STATUSES or status == "archived":
        label = "command_not_executable_phase_0"
        summary = (
            "Resolved or archived Manual Review records are retained as read-only "
            "history and do not expose active future command eligibility."
        )
        blocker_codes.append("resolved_or_archived_status")
        future_command_candidates: tuple[str, ...] = ()
    elif action_preflight.label == "blocked_by_missing_entity_context":
        label = "requires_entity_context"
        summary = (
            "Future Manual Review command execution would require deterministic "
            "linked entity context before any command contract can proceed."
        )
        blocker_codes.append("missing_entity_context")
        required_contract_labels.append("requires_entity_context")
        future_command_candidates = ()
    elif water_emergency_id is not None:
        label = "requires_water_emergency_scope_check"
        summary = (
            "Future Manual Review commands tied to Water Emergency records require "
            "a Water Emergency scope check and separated action design."
        )
        blocker_codes.append("water_emergency_context_required")
        required_contract_labels.append("requires_water_emergency_scope_check")
        future_command_candidates = manual_review_future_command_candidates(
            future_action_preview.label,
        )
    elif "duplicate_or_conflict" in groups or action_preflight.label == "blocked_by_conflict":
        label = "requires_no_conflict_blocker"
        summary = (
            "Future Manual Review commands require conflict resolution context before "
            "approval, rejection, deferral, archive, or resolution can be designed."
        )
        blocker_codes.append("conflict_context_required")
        required_contract_labels.append("requires_no_conflict_blocker")
        future_command_candidates = manual_review_future_command_candidates(
            future_action_preview.label,
        )
    elif "missing_data" in groups or action_preflight.label == "blocked_by_missing_data":
        label = "requires_preflight_pass"
        summary = (
            "Future Manual Review commands require missing-data context, preflight "
            "validation, operator identity, role authorization, and audit envelope "
            "capture before execution can be implemented."
        )
        blocker_codes.append("missing_data_context_required")
        future_command_candidates = manual_review_future_command_candidates(
            future_action_preview.label,
        )
    else:
        label = "command_contract_read_only_phase"
        summary = (
            "Future Manual Review command requirements are visible as a Phase 0 "
            "contract only. No command is executable from this read model."
        )
        future_command_candidates = manual_review_future_command_candidates(
            future_action_preview.label,
        )
        if not future_command_candidates and not decision_readiness.is_resolution_candidate:
            blocker_codes.append("unknown_command_contract")

    return ManualReviewCommandContract(
        label=label,
        summary=summary,
        future_command_candidates=future_command_candidates,
        required_contract_labels=tuple(dict.fromkeys(required_contract_labels)),
        impacted_entity_summary=manual_review_impacted_entity_summary(
            impacted_entity_references,
        ),
        impacted_entity_references=impacted_entity_references,
        blocker_codes=tuple(dict.fromkeys(blocker_codes)),
        evidence_references=tuple(evidence_references),
        is_currently_executable=False,
        not_executable_reason="Manual Review commands are not executable in Phase 0.",
        requires_operator_identity=True,
        requires_role_authorization=True,
        requires_audit_reason=True,
        requires_idempotency_key=True,
        requires_immutable_event_recording=True,
        requires_post_action_consistency_check=True,
    )


MANUAL_REVIEW_AUDIT_ENVELOPE_FIELDS = (
    "review_item_id",
    "future_command_type",
    "operator_identity_id",
    "role_authorization",
    "audit_reason",
    "idempotency_key",
    "preflight_label",
    "command_contract_label",
    "impacted_entity_references",
    "audit_correlation_id",
    "occurred_at",
    "immutable_event_fingerprint",
    "post_action_consistency_check",
)


def manual_review_audit_ledger_dry_run(
    review: ReviewItem,
    *,
    groups: Sequence[str],
    action_preflight: ManualReviewActionPreflight,
    command_contract: ManualReviewCommandContract,
    evidence_references: Sequence[str],
    water_emergency_id: UUID | None,
) -> ManualReviewAuditLedgerDryRun:
    status = normalized(review.status)
    future_command_candidates = command_contract.future_command_candidates
    primary_candidate = future_command_candidates[0] if future_command_candidates else "blocked"
    required_labels = [
        "dry_run_only_phase_0",
        "audit_envelope_required",
        "operator_identity_required",
        "role_authorization_required",
        "idempotency_key_required",
        "immutable_event_required",
        "consistency_check_required",
        "command_execution_blocked_read_only_phase",
    ]

    if status in RESOLVED_REVIEW_STATUSES or status == "archived":
        label = "command_execution_blocked_resolved_or_archived"
        summary = (
            "Resolved or archived Manual Review records retain audit-ledger "
            "visibility without active command dry-run execution."
        )
        required_labels.append("command_execution_blocked_resolved_or_archived")
        primary_candidate = "blocked"
    elif command_contract.label == "requires_entity_context":
        label = "command_execution_blocked_missing_entity"
        summary = (
            "Future command dry-run is blocked until the Manual Review item has "
            "deterministic linked entity context."
        )
        required_labels.append("command_execution_blocked_missing_entity")
    elif water_emergency_id is not None:
        label = "command_execution_blocked_water_emergency_scope"
        summary = (
            "Water Emergency-related Manual Review dry-run context requires a "
            "Water Emergency scope check and separated future action design."
        )
        required_labels.append("command_execution_blocked_water_emergency_scope")
    elif (
        "duplicate_or_conflict" in groups
        or command_contract.label == "requires_no_conflict_blocker"
    ):
        label = "command_execution_blocked_conflict"
        summary = (
            "Duplicate or conflicting evidence blocks future command execution until "
            "a future authenticated operator workflow resolves the conflict."
        )
        required_labels.append("command_execution_blocked_conflict")
    elif not future_command_candidates and command_contract.label != "requires_preflight_pass":
        label = "unknown_dry_run_readiness"
        summary = (
            "No deterministic Manual Review command dry-run candidate is available, "
            "so audit-ledger preparation remains unknown and read-only."
        )
        required_labels.append("unknown_dry_run_readiness")
    else:
        label = "dry_run_only_phase_0"
        summary = (
            "Future Manual Review command dry-run is visible for audit-ledger "
            "preparation only and cannot execute in Phase 0."
        )

    proposed_event_type = (
        f"manual_review.future_command.{primary_candidate}"
        if primary_candidate != "blocked"
        else "manual_review.future_command.blocked"
    )

    return ManualReviewAuditLedgerDryRun(
        label=label,
        summary=summary,
        future_command_type_candidates=future_command_candidates,
        required_labels=tuple(dict.fromkeys(required_labels)),
        proposed_future_event_type=proposed_event_type,
        proposed_future_event_state="proposed_not_recorded",
        proposed_future_audit_envelope_fields=MANUAL_REVIEW_AUDIT_ENVELOPE_FIELDS,
        proposed_future_idempotency_scope=(
            f"manual_review:{review.id or NIL_UUID}:{primary_candidate}"
        ),
        proposed_future_consistency_check_summary=(
            "Future command execution would re-read the review item, linked entities, "
            "immutable event fingerprint, and post-action state before presenting any outcome."
        ),
        audit_correlation_references=tuple(
            reference for reference in evidence_references if reference.startswith("audit:")
        ),
        evidence_references=tuple(evidence_references),
        is_currently_executable=False,
        phase_allows_execution=False,
        execution_unavailable_reason=(
            "Manual Review command dry-runs are visibility only; execution is not "
            "available in Phase 0."
        ),
        requires_operator_identity=True,
        requires_role_authorization=True,
        requires_audit_reason=True,
        requires_idempotency_key=True,
        requires_immutable_event_recording=True,
        requires_post_action_consistency_check=True,
    )


def manual_review_command_validation(
    review: ReviewItem,
    *,
    groups: Sequence[str],
    decision_readiness: ManualReviewDecisionReadiness,
    action_preflight: ManualReviewActionPreflight,
    future_action_preview: ManualReviewFutureActionPreview,
    command_contract: ManualReviewCommandContract,
    audit_ledger_dry_run: ManualReviewAuditLedgerDryRun,
    job_id: UUID | None,
    work_order_id: UUID | None,
    visit_id: UUID | None,
    route_assignment_id: UUID | None,
    water_emergency_id: UUID | None,
    evidence_references: Sequence[str],
) -> ManualReviewCommandValidation:
    del decision_readiness, future_action_preview
    status = normalized(review.status)
    has_entity_context = any(
        linked_id is not None
        for linked_id in (
            job_id,
            work_order_id,
            visit_id,
            route_assignment_id,
            water_emergency_id,
        )
    )
    resolved_or_archived = status in RESOLVED_REVIEW_STATUSES or status == "archived"
    has_conflict = (
        "duplicate_or_conflict" in groups
        or command_contract.label == "requires_no_conflict_blocker"
        or action_preflight.label == "blocked_by_conflict"
    )
    has_missing_data = "missing_data" in groups or action_preflight.label == (
        "blocked_by_missing_data"
    )
    requires_water_emergency_scope_check = water_emergency_id is not None
    future_command_candidates = (
        audit_ledger_dry_run.future_command_type_candidates
        or command_contract.future_command_candidates
    )
    candidate_future_command_type = (
        future_command_candidates[0] if future_command_candidates else "blocked"
    )
    validation_blockers: list[str] = ["validation_read_only_phase"]
    validation_warnings = ["validation_warning_requires_review"]

    if resolved_or_archived:
        label = "validation_blocked_resolved_or_archived"
        validation_status = "blocked_resolved_or_archived"
        summary = (
            "Resolved or archived Manual Review records remain historical visibility and "
            "cannot pass active command validation."
        )
        validation_blockers.insert(0, "validation_blocked_resolved_or_archived")
    elif not has_entity_context:
        label = "validation_blocked_missing_entity"
        validation_status = "blocked_missing_entity_context"
        summary = (
            "Manual Review command validation is blocked until deterministic linked entity "
            "context is available."
        )
        validation_blockers.insert(0, "validation_blocked_missing_entity")
    elif requires_water_emergency_scope_check:
        label = "validation_blocked_water_emergency_scope"
        validation_status = "blocked_water_emergency_scope"
        summary = (
            "Water Emergency-related Manual Review validation requires a separated Water "
            "Emergency scope check before any future command execution can be designed."
        )
        validation_blockers.insert(0, "validation_blocked_water_emergency_scope")
    elif has_conflict:
        label = "validation_blocked_conflict"
        validation_status = "blocked_conflict_context"
        summary = (
            "Duplicate or conflicting evidence blocks future Manual Review command validation "
            "until a future operator workflow resolves the conflict."
        )
        validation_blockers.insert(0, "validation_blocked_conflict")
    elif has_missing_data:
        label = "validation_warning_requires_review"
        validation_status = "warning_missing_data_review_required"
        summary = (
            "Missing-data review evidence requires operator-safe review before a future "
            "authorized command phase can treat the validation as complete."
        )
        validation_warnings.append("missing_data_review_required")
    elif not future_command_candidates:
        label = "unknown_validation_state"
        validation_status = "unknown_validation_state"
        summary = (
            "No deterministic future command candidate is available, so validation remains "
            "unknown and read-only."
        )
        validation_blockers.insert(0, "unknown_validation_state")
    else:
        label = "validation_passes_future_requirements"
        validation_status = "future_requirements_visible"
        summary = (
            "Future Manual Review command prerequisites are visible and internally consistent "
            "for a future authorized phase, but Phase 0 still blocks execution."
        )

    safety_gates = manual_review_safety_gates(
        has_entity_context=has_entity_context,
        resolved_or_archived=resolved_or_archived,
        has_conflict=has_conflict,
        has_missing_data=has_missing_data,
        requires_water_emergency_scope_check=requires_water_emergency_scope_check,
    )

    return ManualReviewCommandValidation(
        label=label,
        summary=summary,
        candidate_future_command_type=candidate_future_command_type,
        validation_status=validation_status,
        validation_blockers=tuple(dict.fromkeys(validation_blockers)),
        validation_warnings=tuple(dict.fromkeys(validation_warnings)),
        safety_gates=safety_gates,
        audit_correlation_references=tuple(
            reference for reference in evidence_references if reference.startswith("audit:")
        ),
        evidence_references=tuple(evidence_references),
        is_currently_executable=False,
        phase_allows_execution=False,
        execution_unavailable_reason=(
            "Manual Review command validation is visibility only; execution is not available "
            "in Phase 0."
        ),
        requires_audit_reason=True,
        requires_operator_identity=True,
        requires_role_authorization=True,
        requires_idempotency_key=True,
        requires_immutable_event_recording=True,
        requires_post_action_consistency_check=True,
        requires_water_emergency_scope_check=requires_water_emergency_scope_check,
        requires_linked_entity_context=True,
    )


MANUAL_REVIEW_FUTURE_OPERATOR_ROLES = (
    "owner",
    "operations_manager",
    "office_admin",
    "dispatcher",
    "reviewer",
    "technician",
    "system_service",
    "unknown_operator",
)
MANUAL_REVIEW_FORBIDDEN_FUTURE_OPERATOR_ROLES = (
    "system_service",
    "technician",
    "unknown_operator",
)
MANUAL_REVIEW_BASE_REQUIRED_PERMISSIONS = (
    "manual_review.future_command.view",
    "manual_review.future_command.prepare",
    "manual_review.audit_actor.capture",
    "manual_review.audit_reason.capture",
    "manual_review.idempotency.require",
    "manual_review.immutable_event.require",
    "manual_review.consistency_check.require",
)
MANUAL_REVIEW_PERMISSION_EXECUTION_UNAVAILABLE_REASON = (
    "Manual Review permission readiness is visibility only; auth, RBAC, and action "
    "execution are not available in Phase 0."
)
MANUAL_REVIEW_IDENTITY_UNAVAILABLE_REASON = (
    "Phase 0 does not implement login, sessions, token handling, operator identity, "
    "or RBAC; future Manual Review commands remain non-executable."
)


def manual_review_permission_readiness(
    review: ReviewItem,
    *,
    groups: Sequence[str],
    command_validation: ManualReviewCommandValidation,
    command_contract: ManualReviewCommandContract,
    water_emergency_id: UUID | None,
    evidence_references: Sequence[str],
) -> ManualReviewPermissionReadiness:
    status = normalized(review.status)
    resolved_or_archived = status in RESOLVED_REVIEW_STATUSES or status == "archived"
    requires_water_scope = (
        water_emergency_id is not None
        or command_validation.requires_water_emergency_scope_check
        or "water_emergency_related" in groups
    )
    candidate = command_validation.candidate_future_command_type or "blocked"
    required_permission_labels = [
        "permission_read_only_phase",
        "requires_future_auth",
        "requires_operator_identity",
        "requires_role_authorization",
        "requires_audit_reason",
        "requires_idempotency_key",
        "requires_immutable_event_recording",
        "requires_post_action_consistency_check",
        "service_account_not_allowed",
        "technician_action_not_allowed",
        "command_not_executable_phase_0",
    ]
    identity_requirement_labels = [
        "requires_future_auth",
        "requires_operator_identity",
        "permission_blocked_unknown_operator",
        "service_account_not_allowed",
        "technician_action_not_allowed",
    ]

    if resolved_or_archived:
        label = "permission_blocked_resolved_or_archived"
        summary = (
            "Resolved or archived Manual Review records retain read-only permission "
            "visibility but do not expose active future operator permission readiness."
        )
        future_required_roles: tuple[str, ...] = ()
        future_required_permissions: tuple[str, ...] = ()
        required_permission_labels.append("permission_blocked_resolved_or_archived")
    elif requires_water_scope:
        label = "permission_blocked_water_emergency_scope"
        summary = (
            "Water Emergency-related Manual Review commands require separated future "
            "operator identity, role authorization, owner/manager boundary, and scope "
            "review before any action module can exist."
        )
        future_required_roles = ("owner", "operations_manager", "reviewer")
        future_required_permissions = (
            *MANUAL_REVIEW_BASE_REQUIRED_PERMISSIONS,
            "manual_review.water_emergency.scope_review",
            "manual_review.owner_override.review",
        )
        required_permission_labels.extend(
            (
                "permission_blocked_water_emergency_scope",
                "requires_operations_manager_role",
                "requires_owner_role_for_override",
            ),
        )
        identity_requirement_labels.append("permission_blocked_water_emergency_scope")
    elif command_validation.label == "validation_blocked_missing_entity":
        label = "permission_blocked_unknown_operator"
        summary = (
            "Future Manual Review permission readiness is blocked because Phase 0 has "
            "no authenticated operator context and the review lacks deterministic linked "
            "entity context."
        )
        future_required_roles = ("reviewer", "operations_manager")
        future_required_permissions = MANUAL_REVIEW_BASE_REQUIRED_PERMISSIONS
    else:
        label = "permission_ready_for_future_auth_phase"
        summary = (
            "Future Manual Review permission requirements are visible for a later auth "
            "phase. Phase 0 does not authenticate an operator, enforce roles, or execute "
            "the candidate command."
        )
        future_required_roles = manual_review_future_required_roles(
            candidate,
            groups=groups,
            command_contract=command_contract,
        )
        future_required_permissions = manual_review_future_required_permissions(
            groups=groups,
            future_required_roles=future_required_roles,
        )
        required_permission_labels.append("permission_ready_for_future_auth_phase")

    required_permission_labels.extend(
        manual_review_role_requirement_labels(future_required_roles),
    )

    return ManualReviewPermissionReadiness(
        label=label,
        summary=summary,
        candidate_future_command_type=candidate,
        future_required_roles=tuple(dict.fromkeys(future_required_roles)),
        future_forbidden_roles=MANUAL_REVIEW_FORBIDDEN_FUTURE_OPERATOR_ROLES,
        future_required_permissions=tuple(dict.fromkeys(future_required_permissions)),
        required_permission_labels=tuple(dict.fromkeys(required_permission_labels)),
        identity_requirement_labels=tuple(dict.fromkeys(identity_requirement_labels)),
        audit_correlation_references=tuple(
            reference for reference in evidence_references if reference.startswith("audit:")
        ),
        evidence_references=tuple(evidence_references),
        is_currently_executable=False,
        phase_allows_execution=False,
        execution_unavailable_reason=MANUAL_REVIEW_PERMISSION_EXECUTION_UNAVAILABLE_REASON,
        identity_unavailable_reason=MANUAL_REVIEW_IDENTITY_UNAVAILABLE_REASON,
        future_operator_identity_required=True,
        future_operator_id_required=True,
        future_operator_display_name_required=True,
        future_operator_email_required=True,
        future_authentication_provider_boundary=(
            "Future ACS-FSM auth provider boundary is not implemented in Phase 0; "
            "Manual Review commands must not rely on service accounts or fake roles."
        ),
        future_role_authorization_required=True,
        future_permission_set_required=True,
        future_audit_actor_required=True,
        future_audit_reason_required=True,
        future_idempotency_key_required=True,
        future_immutable_event_required=True,
        future_post_action_consistency_check_required=True,
        impersonation_allowed=False,
        service_account_allowed=False,
        technician_action_allowed=False,
        requires_water_emergency_scope_check=requires_water_scope,
    )


def manual_review_future_required_roles(
    candidate: str,
    *,
    groups: Sequence[str],
    command_contract: ManualReviewCommandContract,
) -> tuple[str, ...]:
    if candidate == "archive":
        roles = ["operations_manager", "owner"]
    elif candidate in {"approve", "reject", "defer", "resolve", "operator_decision"}:
        roles = ["reviewer", "operations_manager"]
    elif candidate == "request_information":
        roles = ["reviewer", "office_admin", "operations_manager"]
    else:
        roles = ["reviewer", "operations_manager"]

    if "dispatch_related" in groups:
        roles.append("dispatcher")
    if "requires_no_conflict_blocker" in command_contract.required_contract_labels:
        roles.append("operations_manager")
    return tuple(role for role in MANUAL_REVIEW_FUTURE_OPERATOR_ROLES if role in roles)


def manual_review_future_required_permissions(
    *,
    groups: Sequence[str],
    future_required_roles: Sequence[str],
) -> tuple[str, ...]:
    permissions = [*MANUAL_REVIEW_BASE_REQUIRED_PERMISSIONS]
    if "dispatch_related" in groups or "dispatcher" in future_required_roles:
        permissions.append("manual_review.dispatch_review.prepare")
    if "owner" in future_required_roles:
        permissions.append("manual_review.owner_override.review")
    return tuple(permissions)


def manual_review_role_requirement_labels(
    roles: Sequence[str],
) -> tuple[str, ...]:
    labels_by_role = {
        "owner": "requires_owner_role_for_override",
        "operations_manager": "requires_operations_manager_role",
        "dispatcher": "requires_dispatcher_role",
        "reviewer": "requires_reviewer_role",
    }
    return tuple(labels_by_role[role] for role in roles if role in labels_by_role)


def manual_review_safety_gates(
    *,
    has_entity_context: bool,
    resolved_or_archived: bool,
    has_conflict: bool,
    has_missing_data: bool,
    requires_water_emergency_scope_check: bool,
) -> tuple[ManualReviewSafetyGate, ...]:
    return (
        ManualReviewSafetyGate(
            key="entity_context_present",
            label="Entity context present",
            passed=has_entity_context,
            required=True,
            reason=(
                "A future command must be tied to a deterministic job, work order, visit, "
                "route assignment, or Water Emergency record."
            ),
        ),
        ManualReviewSafetyGate(
            key="status_allows_future_action",
            label="Status allows future action",
            passed=not resolved_or_archived,
            required=True,
            reason="Resolved or archived Manual Review records cannot be active command targets.",
        ),
        ManualReviewSafetyGate(
            key="review_not_resolved_or_archived",
            label="Review not resolved or archived",
            passed=not resolved_or_archived,
            required=True,
            reason="Historical Manual Review records stay separated from active command readiness.",
        ),
        ManualReviewSafetyGate(
            key="water_emergency_scope_checked",
            label="Water Emergency scope checked",
            passed=not requires_water_emergency_scope_check,
            required=requires_water_emergency_scope_check,
            reason=(
                "Water Emergency-related reviews require separated scope checks before any "
                "future command can be considered."
            ),
        ),
        ManualReviewSafetyGate(
            key="no_conflict_blocker",
            label="No conflict blocker",
            passed=not has_conflict,
            required=True,
            reason="Duplicate or conflicting evidence must remain blocked for future review.",
        ),
        ManualReviewSafetyGate(
            key="missing_data_reviewed",
            label="Missing data reviewed",
            passed=not has_missing_data,
            required=has_missing_data,
            reason="Missing-data reviews require operator-safe evidence review before execution.",
        ),
        ManualReviewSafetyGate(
            key="operator_identity_required",
            label="Operator identity required",
            passed=True,
            required=True,
            reason=(
                "Future commands must declare operator identity capture before execution exists."
            ),
        ),
        ManualReviewSafetyGate(
            key="role_authorization_required",
            label="Role authorization required",
            passed=True,
            required=True,
            reason="Future commands must declare role authorization before execution exists.",
        ),
        ManualReviewSafetyGate(
            key="audit_reason_required",
            label="Audit reason required",
            passed=True,
            required=True,
            reason="Future commands must declare audit reason capture before execution exists.",
        ),
        ManualReviewSafetyGate(
            key="idempotency_key_required",
            label="Idempotency key required",
            passed=True,
            required=True,
            reason="Future commands must declare an idempotency key requirement.",
        ),
        ManualReviewSafetyGate(
            key="immutable_event_required",
            label="Immutable event required",
            passed=True,
            required=True,
            reason="Future commands must declare immutable event recording requirements.",
        ),
        ManualReviewSafetyGate(
            key="post_action_consistency_check_required",
            label="Post-action consistency check required",
            passed=True,
            required=True,
            reason="Future commands must declare post-action consistency checks.",
        ),
        ManualReviewSafetyGate(
            key="phase_allows_execution",
            label="Phase allows execution",
            passed=False,
            required=True,
            reason=(
                "Phase 0 exposes validation visibility only; Manual Review command execution "
                "is disabled."
            ),
        ),
    )


def manual_review_future_command_candidates(preview_label: str) -> tuple[str, ...]:
    command_by_preview = {
        "future_approve_preview": ("approve",),
        "future_reject_preview": ("reject",),
        "future_defer_preview": ("defer",),
        "future_archive_preview": ("archive",),
        "future_resolve_preview": ("resolve",),
        "future_request_information_preview": ("request_information",),
        "future_operator_decision_preview": ("operator_decision",),
    }
    return command_by_preview.get(preview_label, ())


def manual_review_future_action_label_for_recommendation(
    recommended_action: str | None,
) -> str | None:
    recommended = normalized(recommended_action)
    if not recommended:
        return None
    if "request" in recommended and ("information" in recommended or "info" in recommended):
        return "future_request_information_preview"
    if "approve" in recommended:
        return "future_approve_preview"
    if "reject" in recommended:
        return "future_reject_preview"
    if "defer" in recommended:
        return "future_defer_preview"
    if "archive" in recommended:
        return "future_archive_preview"
    if "resolve" in recommended:
        return "future_resolve_preview"
    return None


def manual_review_future_action_description(label: str) -> str:
    descriptions = {
        "future_approve_preview": (
            "Future authenticated review action may approve the reviewed outcome after "
            "operator identity and audit reason are captured."
        ),
        "future_reject_preview": (
            "Future authenticated review action may reject the reviewed outcome after "
            "operator identity and audit reason are captured."
        ),
        "future_defer_preview": (
            "Future authenticated review action may defer the review for later operator "
            "follow-up after audit context is captured."
        ),
        "future_archive_preview": (
            "Future authenticated review action may archive the review only after "
            "operator identity, audit reason, and final workflow rules exist."
        ),
        "future_resolve_preview": (
            "Future authenticated review action may resolve the review after the "
            "operator verifies evidence and records an audit reason."
        ),
        "future_operator_decision_preview": (
            "Future authenticated workflow may present an operator decision step, but "
            "Phase 0 keeps this as read-only preview context."
        ),
        "unknown_action_preview": (
            "No deterministic future action preview can be selected safely from the "
            "available evidence."
        ),
    }
    return descriptions.get(
        label,
        "Future action preview is displayed as read-only Phase 0 preparation only.",
    )


def manual_review_future_action_outcome(label: str) -> str:
    outcomes = {
        "future_approve_preview": (
            "Expected non-binding outcome: a future operator could approve the review "
            "result without bypassing Manual Review authority."
        ),
        "future_reject_preview": (
            "Expected non-binding outcome: a future operator could reject the review "
            "result while preserving audit evidence."
        ),
        "future_defer_preview": (
            "Expected non-binding outcome: a future operator could defer the review "
            "for later follow-up without changing it in Phase 0."
        ),
        "future_archive_preview": (
            "Expected non-binding outcome: a future operator could archive the review "
            "after final authority and audit rules are implemented."
        ),
        "future_resolve_preview": (
            "Expected non-binding outcome: a future operator could resolve the review "
            "after validating evidence and recording required audit context."
        ),
        "future_operator_decision_preview": (
            "Expected non-binding outcome: a future operator could choose the next "
            "review action from an authenticated workflow."
        ),
        "unknown_action_preview": (
            "Expected non-binding outcome: keep the item in Manual Review until more "
            "deterministic context exists."
        ),
    }
    return outcomes.get(
        label,
        "Expected non-binding outcome: preserve read-only visibility until a future "
        "Manual Review action module is implemented.",
    )


def manual_review_impacted_entity_references(
    review: ReviewItem,
    *,
    job_id: UUID | None,
    work_order_id: UUID | None,
    visit_id: UUID | None,
    route_assignment_id: UUID | None,
    water_emergency_id: UUID | None,
) -> tuple[str, ...]:
    references: list[str] = [f"review:{review.id or NIL_UUID}"]
    if job_id is not None:
        references.append(f"job:{job_id}")
    if work_order_id is not None:
        references.append(f"work_order:{work_order_id}")
    if visit_id is not None:
        references.append(f"visit:{visit_id}")
    if route_assignment_id is not None:
        references.append(f"route_assignment:{route_assignment_id}")
    if water_emergency_id is not None:
        references.append(f"water_emergency:{water_emergency_id}")
    return tuple(dict.fromkeys(references))


def manual_review_impacted_entity_summary(references: Sequence[str]) -> str:
    if len(references) <= 1:
        return "Impacted entities: no deterministic linked entity context."
    return "Impacted entities: " + ", ".join(references)


def manual_review_needs_entity_context(
    *,
    entity_type: str | None,
    entity_id: UUID | None,
    job_id: UUID | None,
    work_order_id: UUID | None,
    visit_id: UUID | None,
    route_assignment_id: UUID | None,
    water_emergency_id: UUID | None,
) -> bool:
    return all(
        linked_id is None
        for linked_id in (
            job_id,
            work_order_id,
            visit_id,
            route_assignment_id,
            water_emergency_id,
        )
    )


def manual_review_queue_sort_key(item: ManualReviewQueueItem) -> tuple[object, ...]:
    status_rank = {
        "open": 0,
        "pending": 0,
        "flagged_for_review": 0,
        "review_required": 0,
        "deferred": 1,
        "resolved": 3,
        "approved": 3,
        "rejected": 3,
        "closed": 3,
        "archived": 4,
    }.get(item.status, 2)
    severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(
        item.severity or "",
        4,
    )
    blocker_rank = 0 if item.blocker_indicator else 1
    return (status_rank, blocker_rank, severity_rank, item.created_at, str(item.review_item_id))


def manual_review_job_id(
    review: ReviewItem,
    *,
    work_orders: Sequence[WorkOrder],
    visits: Sequence[Visit],
    route_assignments: Sequence[RouteAssignment],
) -> UUID | None:
    if review.job_id is not None:
        return review.job_id

    entity_type = normalized(review.entity_type)
    if entity_type == "job" and review.entity_id is not None:
        return review.entity_id

    visit_id = manual_review_visit_id(review, route_assignments=route_assignments)
    for visit in visits:
        if visit.id == visit_id:
            return visit.job_id

    work_order_id = review.entity_id if entity_type == "work_order" else None
    for work_order in work_orders:
        if work_order.id == work_order_id:
            return work_order.job_id

    return None


def manual_review_work_order_id(
    review: ReviewItem,
    *,
    job_id: UUID | None,
    visit_id: UUID | None,
    work_orders: Sequence[WorkOrder],
    visits: Sequence[Visit],
) -> UUID | None:
    if normalized(review.entity_type) == "work_order" and review.entity_id is not None:
        return review.entity_id

    for visit in visits:
        if visit.id == visit_id and visit.work_order_id is not None:
            return visit.work_order_id

    related_work_order_ids = sorted(
        (work_order.id for work_order in work_orders if work_order.job_id == job_id),
        key=str,
    )
    return related_work_order_ids[0] if related_work_order_ids else None


def manual_review_visit_id(
    review: ReviewItem,
    *,
    route_assignments: Sequence[RouteAssignment],
) -> UUID | None:
    if review.visit_id is not None:
        return review.visit_id

    if normalized(review.entity_type) == "visit" and review.entity_id is not None:
        return review.entity_id

    route_assignment_id = manual_review_route_assignment_id(review)
    for route_assignment in route_assignments:
        if route_assignment.id == route_assignment_id:
            return route_assignment.visit_id

    return None


def manual_review_route_assignment_id(review: ReviewItem) -> UUID | None:
    if review.route_assignment_id is not None:
        return review.route_assignment_id
    if normalized(review.entity_type) == "route_assignment" and review.entity_id is not None:
        return review.entity_id
    return None


def manual_review_water_emergency_id(
    review: ReviewItem,
    *,
    job_id: UUID | None,
    visit_id: UUID | None,
    water_emergencies: Sequence[WaterEmergency],
    visits: Sequence[Visit],
) -> UUID | None:
    if normalized(review.entity_type) == "water_emergency" and review.entity_id is not None:
        return review.entity_id

    water_job_ids = {record.job_id: record.id for record in water_emergencies}
    if job_id in water_job_ids:
        return water_job_ids[job_id]

    for visit in visits:
        if visit.id == visit_id and visit.job_id in water_job_ids:
            return water_job_ids[visit.job_id]

    return None


def manual_review_visibility_groups(
    review: ReviewItem,
    *,
    job_id: UUID | None,
    work_order_id: UUID | None,
    visit_id: UUID | None,
    route_assignment_id: UUID | None,
    water_emergency_id: UUID | None,
) -> tuple[str, ...]:
    groups: list[str] = [manual_review_status_group(review)]

    if is_blocker_manual_review(review):
        groups.append("blocked")

    if water_emergency_id is not None:
        groups.append("water_emergency_related")
    elif (
        normalized(review.entity_type) in MANUAL_REVIEW_DISPATCH_ENTITY_TYPES
        or job_id is not None
        or work_order_id is not None
        or visit_id is not None
        or route_assignment_id is not None
    ):
        groups.append("dispatch_related")

    if manual_review_contains_keyword(review, MANUAL_REVIEW_MISSING_DATA_KEYWORDS):
        groups.append("missing_data")

    if manual_review_contains_keyword(review, MANUAL_REVIEW_DUPLICATE_CONFLICT_KEYWORDS):
        groups.append("duplicate_or_conflict")

    if manual_review_contains_keyword(review, MANUAL_REVIEW_CANCELLATION_STATUS_KEYWORDS):
        groups.append("cancellation_or_status_uncertainty")

    if len(groups) == 1:
        groups.append("needs_operator_review")

    return tuple(dict.fromkeys(groups))


def manual_review_status_group(review: ReviewItem) -> str:
    status = normalized(review.status)
    if status == "archived":
        return "archived"
    if status == "deferred":
        return "deferred"
    if status in RESOLVED_REVIEW_STATUSES:
        return "resolved"
    if status in UNRESOLVED_REVIEW_STATUSES:
        return "open"
    return "needs_operator_review"


def manual_review_primary_group(groups: Sequence[str]) -> str:
    for group in (
        "water_emergency_related",
        "missing_data",
        "duplicate_or_conflict",
        "cancellation_or_status_uncertainty",
        "blocked",
        "dispatch_related",
        "open",
        "deferred",
        "resolved",
        "archived",
    ):
        if group in groups:
            return group
    return "needs_operator_review"


def manual_review_age_bucket(review: ReviewItem, *, now: datetime) -> str:
    if normalized(review.status) == "archived" or is_resolved_manual_review(review):
        return "resolved_or_archived"

    created_at = getattr(review, "created_at", None)
    if created_at is None:
        return "unknown_timing"

    age_hours = hours_between(created_at, now)
    if age_hours is None:
        return "unknown_timing"
    if age_hours <= MANUAL_REVIEW_NEW_HOURS:
        return "new"
    if age_hours <= MANUAL_REVIEW_AGING_HOURS:
        return "active"
    if age_hours <= MANUAL_REVIEW_STALE_HOURS:
        return "aging"
    return "stale"


def is_active_manual_review(review: ReviewItem) -> bool:
    return normalized(review.status) in UNRESOLVED_REVIEW_STATUSES


def is_resolved_manual_review(review: ReviewItem) -> bool:
    status = normalized(review.status)
    return status in RESOLVED_REVIEW_STATUSES and status != "archived"


def is_blocker_manual_review(review: ReviewItem) -> bool:
    return normalized(review.severity) in ESCALATION_SEVERITIES or manual_review_contains_keyword(
        review,
        MANUAL_REVIEW_BLOCKER_KEYWORDS,
    )


def manual_review_contains_keyword(review: ReviewItem, keywords: set[str]) -> bool:
    searchable_values = (
        review.reason_code,
        review.status,
        review.severity,
        review.entity_type,
        review.recommended_action,
    )
    searchable = " ".join(normalized(value) for value in searchable_values)
    return any(keyword in searchable for keyword in keywords)


def manual_review_evidence_references(
    review: ReviewItem,
    *,
    job_id: UUID | None,
    work_order_id: UUID | None,
    visit_id: UUID | None,
    route_assignment_id: UUID | None,
    water_emergency_id: UUID | None,
) -> tuple[str, ...]:
    references: list[str] = [f"review:{review.id or NIL_UUID}"]
    if job_id is not None:
        references.append(f"job:{job_id}")
    if work_order_id is not None:
        references.append(f"work_order:{work_order_id}")
    if visit_id is not None:
        references.append(f"visit:{visit_id}")
    if route_assignment_id is not None:
        references.append(f"route_assignment:{route_assignment_id}")
    if water_emergency_id is not None:
        references.append(f"water_emergency:{water_emergency_id}")
    if review.audit_correlation_id:
        references.append(f"audit:{review.audit_correlation_id}")
    return tuple(references)


def manual_review_reason_evidence_context(
    review: ReviewItem,
    *,
    queue_item: ManualReviewQueueItem,
) -> ManualReviewReasonEvidenceContext:
    return ManualReviewReasonEvidenceContext(
        reason_code=queue_item.reason_code,
        status=queue_item.status,
        severity=queue_item.severity,
        confidence_score=review.confidence_score,
        recommended_action=review.recommended_action,
        review_reason_codes=manual_review_reason_codes(review),
        snapshot_keys=manual_review_snapshot_keys(review),
        blocker_indicator=queue_item.blocker_indicator,
        attention_indicator=queue_item.attention_indicator,
        evidence_references=queue_item.evidence_references,
    )


def manual_review_reason_codes(review: ReviewItem) -> tuple[str, ...]:
    reasons: list[str] = []
    for item in review.review_reasons or []:
        if isinstance(item, dict):
            value = item.get("code") or item.get("reason_code") or item.get("reason")
            if normalized(value):
                reasons.append(normalized(value))
        elif normalized(item):
            reasons.append(normalized(item))
    return tuple(dict.fromkeys(reasons))


def manual_review_snapshot_keys(review: ReviewItem) -> tuple[str, ...]:
    snapshot_attrs = (
        "confidence_snapshot",
        "warning_snapshot",
        "normalization_snapshot",
        "validation_snapshot",
        "source_snapshot",
        "review_metadata",
    )
    return tuple(attr for attr in snapshot_attrs if bool(getattr(review, attr, None)))


def manual_review_detail_linked_entity_context(
    item: ManualReviewQueueItem,
    *,
    jobs: Sequence[Job],
    work_orders: Sequence[WorkOrder],
    visits: Sequence[Visit],
    route_assignments: Sequence[RouteAssignment],
    water_emergencies: Sequence[WaterEmergency],
    review_events: Sequence[OperationalEventRecord],
) -> ManualReviewDetailLinkedEntityContext:
    related_job = next((job for job in jobs if job.id == item.job_id), None)
    related_work_order = next(
        (work_order for work_order in work_orders if work_order.id == item.work_order_id),
        None,
    )
    related_visit = next((visit for visit in visits if visit.id == item.visit_id), None)
    related_route_assignment = next(
        (route for route in route_assignments if route.id == item.route_assignment_id),
        None,
    )
    related_water_emergency = next(
        (record for record in water_emergencies if record.id == item.water_emergency_id),
        None,
    )
    unknown_indicators: list[str] = []
    if item.job_id is not None and related_job is None:
        unknown_indicators.append("job_reference_missing")
    if item.work_order_id is not None and related_work_order is None:
        unknown_indicators.append("work_order_reference_missing")
    if item.visit_id is not None and related_visit is None:
        unknown_indicators.append("visit_reference_missing")
    if item.route_assignment_id is not None and related_route_assignment is None:
        unknown_indicators.append("route_assignment_reference_missing")
    if item.water_emergency_id is not None and related_water_emergency is None:
        unknown_indicators.append("water_emergency_reference_missing")
    if (
        item.entity_type is not None
        and item.entity_id is not None
        and all(
            linked_id != item.entity_id
            for linked_id in (
                item.job_id,
                item.work_order_id,
                item.visit_id,
                item.route_assignment_id,
                item.water_emergency_id,
            )
        )
    ):
        unknown_indicators.append("entity_reference_not_modeled")

    return ManualReviewDetailLinkedEntityContext(
        entity_type=item.entity_type,
        entity_id=item.entity_id,
        job_id=item.job_id,
        job_status=related_job.status if related_job else None,
        job_type=related_job.job_type if related_job else None,
        work_order_id=item.work_order_id,
        work_order_status=related_work_order.status if related_work_order else None,
        visit_id=item.visit_id,
        visit_status=related_visit.status if related_visit else None,
        route_assignment_id=item.route_assignment_id,
        route_assignment_status=related_route_assignment.status
        if related_route_assignment
        else None,
        water_emergency_id=item.water_emergency_id,
        water_emergency_status=related_water_emergency.status if related_water_emergency else None,
        water_emergency_stage=related_water_emergency.drying_stage
        if related_water_emergency
        else None,
        is_water_emergency_related="water_emergency_related" in item.visibility_groups,
        is_dispatch_related="dispatch_related" in item.visibility_groups,
        unknown_indicators=tuple(dict.fromkeys(unknown_indicators)),
        audit_correlation_ids=unique_audit_correlation_ids(review_events),
    )


def manual_review_related_events(
    item: ManualReviewQueueItem,
    review: ReviewItem,
    *,
    operational_events: Sequence[OperationalEventRecord],
) -> tuple[OperationalEventRecord, ...]:
    related_ids = {
        value
        for value in (
            item.review_item_id,
            item.entity_id,
            item.job_id,
            item.work_order_id,
            item.visit_id,
            item.route_assignment_id,
            item.water_emergency_id,
        )
        if value is not None
    }
    audit_ids = {review.audit_correlation_id} if review.audit_correlation_id else set()

    return tuple(
        event
        for event in operational_events
        if (
            event.entity_id in related_ids
            or event.job_id in related_ids
            or event.work_order_id in related_ids
            or event.visit_id in related_ids
            or event.route_assignment_id in related_ids
            or event.audit_correlation_id in audit_ids
        )
    )


def manual_review_detail_data_gap_counts(
    item: ManualReviewQueueItem,
    *,
    related_events: Sequence[OperationalEventRecord],
) -> tuple[CountBucket, ...]:
    gaps: list[str] = []
    if not related_events:
        gaps.append("no_timeline_evidence")
    if not item.audit_correlation_id:
        gaps.append("audit_correlation_missing")
    if not any(
        (
            item.job_id,
            item.work_order_id,
            item.visit_id,
            item.route_assignment_id,
            item.water_emergency_id,
        ),
    ):
        gaps.append("linked_entity_context_missing")
    return count_values(gaps)


def count_authorization_states(
    route_assignments: Sequence[RouteAssignment],
) -> tuple[CountBucket, ...]:
    values: list[str] = []
    for route in route_assignments:
        snapshot = route.dispatch_authorization_snapshot or {}
        if route.dispatch_execution_state:
            values.append(route.dispatch_execution_state)
        elif snapshot.get("authorized_for_dispatch") is True:
            values.append("authorized_for_dispatch")
        elif snapshot.get("authorized_for_dispatch") is False:
            values.append("not_authorized")
    return count_values(values)


def sum_mismatch_counts(route_assignments: Sequence[RouteAssignment]) -> int:
    total = 0
    for route in route_assignments:
        snapshot = route.dispatch_mismatch_snapshot or {}
        if isinstance(snapshot.get("mismatch_count"), int):
            total += snapshot["mismatch_count"]
        elif isinstance(snapshot.get("mismatches"), list):
            total += len(snapshot["mismatches"])
    return total


def count_open_water_emergencies(water_emergencies: Sequence[WaterEmergency]) -> int:
    return count_where(
        water_emergencies,
        is_open_water_emergency,
    )


def is_open_water_emergency(record: WaterEmergency) -> bool:
    return (
        record.closed_at is None
        and normalized(record.status) not in TERMINAL_WATER_EMERGENCY_STATUSES
    )


def is_standard_dispatch_visit(
    visit: Visit,
    *,
    water_job_ids: set[object],
) -> bool:
    return visit.job_id not in water_job_ids and normalized(visit.visit_type) != "water_emergency"


def count_multi_visit_water_emergencies(
    water_emergencies: Sequence[WaterEmergency],
    *,
    visits: Sequence[Visit],
) -> int:
    return count_where(
        water_emergencies,
        lambda record: (
            count_where(
                visits,
                lambda visit: visit.job_id == record.job_id,
            )
            > 1
        ),
    )


def water_emergency_equipment_summary(
    water_emergencies: Sequence[WaterEmergency],
    *,
    work_orders: Sequence[WorkOrder],
) -> WaterEmergencyEquipmentSummary:
    gaps: list[str] = []
    if water_emergencies:
        gaps.append("equipment_inventory_not_modeled")

    return WaterEmergencyEquipmentSummary(
        equipment_onsite_count=count_where(
            water_emergencies,
            lambda record: bool(record.equipment_onsite),
        ),
        moisture_tracking_required_count=count_where(
            water_emergencies,
            lambda record: bool(record.moisture_tracking_required),
        ),
        work_orders_with_equipment_notes_count=count_where(
            work_orders,
            lambda work_order: bool(normalized(work_order.required_equipment_notes)),
        ),
        records_missing_equipment_context_count=count_where(
            water_emergencies,
            lambda record: (
                is_open_water_emergency(record)
                and not record.equipment_onsite
                and not record.moisture_tracking_required
                and not water_emergency_work_orders_include_equipment_notes(
                    record,
                    work_orders=work_orders,
                )
            ),
        ),
        inventory_entity_available=False,
        unknown_counts=count_values(gaps),
    )


def water_emergency_work_orders_include_equipment_notes(
    record: WaterEmergency,
    *,
    work_orders: Sequence[WorkOrder],
) -> bool:
    return any(
        work_order.job_id == record.job_id and bool(normalized(work_order.required_equipment_notes))
        for work_order in work_orders
    )


def water_emergency_visit_chain_summary(
    water_emergencies: Sequence[WaterEmergency],
    *,
    visits: Sequence[Visit],
) -> WaterEmergencyVisitChainSummary:
    return WaterEmergencyVisitChainSummary(
        total_visits=len(visits),
        multi_visit_record_count=count_multi_visit_water_emergencies(
            water_emergencies,
            visits=visits,
        ),
        open_records_without_visits_count=count_where(
            water_emergencies,
            lambda record: (
                is_open_water_emergency(record)
                and not any(visit.job_id == record.job_id for visit in visits)
            ),
        ),
        scheduled_visit_count=count_where(visits, is_scheduled_visit),
        completed_visit_count=count_where(visits, is_completed_visit),
        visit_status_counts=count_by_attr(visits, "status"),
    )


def water_emergency_drying_stage_summary(
    water_emergencies: Sequence[WaterEmergency],
) -> WaterEmergencyDryingStageSummary:
    open_records = tuple(record for record in water_emergencies if is_open_water_emergency(record))
    return WaterEmergencyDryingStageSummary(
        stage_counts=count_by_attr(water_emergencies, "drying_stage"),
        active_stage_counts=count_by_attr(open_records, "drying_stage"),
        missing_stage_count=count_where(
            water_emergencies,
            lambda record: not normalized(record.drying_stage),
        ),
        moisture_tracking_required_count=count_where(
            water_emergencies,
            lambda record: bool(record.moisture_tracking_required),
        ),
    )


def water_emergency_detail_equipment_context(
    record: WaterEmergency,
    *,
    work_orders: Sequence[WorkOrder],
) -> WaterEmergencyDetailEquipmentContext:
    notes = tuple(
        WaterEmergencyEquipmentNote(
            work_order_id=work_order.id,
            required_equipment_notes=work_order.required_equipment_notes or "",
        )
        for work_order in sorted(
            work_orders,
            key=lambda work_order: (
                normalized(work_order.work_order_number),
                str(work_order.id),
            ),
        )
        if normalized(work_order.required_equipment_notes)
    )
    unknowns = ["equipment_inventory_not_modeled"]
    if record.equipment_onsite and not notes:
        unknowns.append("equipment_onsite_without_equipment_notes")

    return WaterEmergencyDetailEquipmentContext(
        equipment_onsite=record.equipment_onsite,
        moisture_tracking_required=record.moisture_tracking_required,
        inventory_entity_available=False,
        required_equipment_notes=notes,
        unknown_indicators=tuple(unknowns),
    )


def water_emergency_detail_visit_chain(
    visits: Sequence[Visit],
) -> WaterEmergencyVisitChain:
    visit_datetimes = tuple(
        visit_time for visit in visits if (visit_time := visit_chain_datetime(visit)) is not None
    )
    next_scheduled_visit_at = min(
        (
            visit.scheduled_start_at
            for visit in visits
            if visit.scheduled_start_at is not None and not is_completed_visit(visit)
        ),
        default=None,
    )

    return WaterEmergencyVisitChain(
        total_visits=len(visits),
        completed_visit_count=count_where(visits, is_completed_visit),
        open_visit_count=count_where(
            visits,
            lambda visit: not is_completed_visit(visit),
        ),
        first_visit_at=min(visit_datetimes, default=None),
        latest_visit_at=max(visit_datetimes, default=None),
        next_scheduled_visit_at=next_scheduled_visit_at,
        visit_status_counts=count_by_attr(visits, "status"),
    )


def water_emergency_detail_drying_stage_context(
    record: WaterEmergency,
) -> WaterEmergencyDetailDryingStageContext:
    missing_indicators: list[str] = []
    if is_open_water_emergency(record):
        if not normalized(record.drying_stage):
            missing_indicators.append("missing_drying_stage")
        if not normalized(record.next_required_action):
            missing_indicators.append("missing_next_required_action")

    return WaterEmergencyDetailDryingStageContext(
        status=normalized(record.status),
        current_stage=normalized(record.drying_stage) or None,
        next_required_action=record.next_required_action,
        moisture_tracking_required=record.moisture_tracking_required,
        missing_indicators=tuple(missing_indicators),
    )


def water_emergency_review_exception_summary(
    water_emergencies: Sequence[WaterEmergency],
    *,
    visits: Sequence[Visit],
    review_items: Sequence[ReviewItem],
) -> WaterEmergencyReviewExceptionSummary:
    unknowns: list[str] = []
    if water_emergencies and not review_items:
        unknowns.append("no_water_emergency_review_items")

    for record in water_emergencies:
        if not is_open_water_emergency(record):
            continue
        scoped_reviews = water_emergency_related_reviews(
            record,
            visits=water_emergency_related_visits(record, visits=visits),
            review_items=review_items,
        )
        if not scoped_reviews:
            unknowns.append("open_record_without_scoped_review")

    return WaterEmergencyReviewExceptionSummary(
        total_review_count=len(review_items),
        open_review_count=count_where(
            review_items,
            lambda review: normalized(review.status) == "open",
        ),
        deferred_review_count=count_where(
            review_items,
            lambda review: normalized(review.status) == "deferred",
        ),
        resolved_review_count=count_where(
            review_items,
            lambda review: normalized(review.status) in RESOLVED_REVIEW_STATUSES,
        ),
        archived_review_count=count_where(
            review_items,
            lambda review: normalized(review.status) == "archived",
        ),
        critical_unresolved_count=count_where(review_items, is_critical_unresolved_review),
        escalation_indicator_count=count_where(review_items, is_escalation_review),
        review_reason_counts=count_by_attr(review_items, "reason_code"),
        blocker_reason_counts=count_by_attr(
            tuple(review for review in review_items if is_blocker_review_reason(review)),
            "reason_code",
        ),
        unknown_counts=count_values(unknowns),
        review_item_ids=sorted_uuid_tuple(
            {review.id for review in review_items if review.id is not None},
        ),
        audit_correlation_ids=unique_audit_correlation_ids(review_items),
    )


def water_emergency_review_exception_context(
    review_items: Sequence[ReviewItem],
) -> WaterEmergencyReviewExceptionContext:
    unknowns: list[str] = []
    if not review_items:
        unknowns.append("no_scoped_review_items")

    return WaterEmergencyReviewExceptionContext(
        total_review_count=len(review_items),
        open_review_count=count_where(
            review_items,
            lambda review: normalized(review.status) == "open",
        ),
        deferred_review_count=count_where(
            review_items,
            lambda review: normalized(review.status) == "deferred",
        ),
        resolved_review_count=count_where(
            review_items,
            lambda review: normalized(review.status) in RESOLVED_REVIEW_STATUSES,
        ),
        archived_review_count=count_where(
            review_items,
            lambda review: normalized(review.status) == "archived",
        ),
        critical_unresolved_count=count_where(review_items, is_critical_unresolved_review),
        escalation_indicator_count=count_where(review_items, is_escalation_review),
        review_reason_counts=count_by_attr(review_items, "reason_code"),
        blocker_reason_counts=count_by_attr(
            tuple(review for review in review_items if is_blocker_review_reason(review)),
            "reason_code",
        ),
        unknown_indicators=tuple(unknowns),
        review_item_ids=sorted_uuid_tuple(
            {review.id for review in review_items if review.id is not None},
        ),
        audit_correlation_ids=unique_audit_correlation_ids(review_items),
    )


def water_emergency_next_step_readiness_summary(
    water_emergencies: Sequence[WaterEmergency],
    *,
    work_orders: Sequence[WorkOrder],
    visits: Sequence[Visit],
    review_items: Sequence[ReviewItem],
    operational_events: Sequence[OperationalEventRecord],
) -> WaterEmergencyNextStepReadinessSummary:
    records = tuple(
        water_emergency_next_step_readiness(
            record,
            work_orders=work_orders,
            visits=visits,
            review_items=review_items,
            operational_events=operational_events,
        )
        for record in sorted(
            water_emergencies,
            key=lambda record: (
                not is_open_water_emergency(record),
                normalized(record.status),
                str(record.job_id),
            ),
        )
    )
    return WaterEmergencyNextStepReadinessSummary(
        total_records=len(records),
        needs_attention_count=count_where(
            records,
            lambda record: record.requires_operator_attention,
        ),
        closed_without_active_action_count=count_where(
            records,
            lambda record: record.primary_label == "closed_no_active_next_step",
        ),
        label_counts=count_values(label for record in records for label in record.labels),
        blocker_counts=count_values(
            reason_code
            for record in records
            for reason_code in record.reason_codes
            if is_next_step_blocker_reason(reason_code)
        ),
        records=records,
    )


def water_emergency_operator_queue_summary(
    next_step_summary: WaterEmergencyNextStepReadinessSummary,
) -> WaterEmergencyOperatorQueueSummary:
    items = tuple(
        sorted(
            (water_emergency_queue_item(record) for record in next_step_summary.records),
            key=lambda item: (
                item.attention_rank,
                item.queue_group,
                item.attention_label,
                str(item.water_emergency_id),
            ),
        ),
    )

    return WaterEmergencyOperatorQueueSummary(
        total_records=len(items),
        active_attention_count=count_where(
            items,
            lambda item: item.queue_group != "closed_or_resolved",
        ),
        closed_or_resolved_count=count_where(
            items,
            lambda item: item.attention_label == "closed_or_resolved",
        ),
        critical_attention_count=count_where(
            items,
            lambda item: item.attention_label == "critical_attention",
        ),
        queue_group_counts=count_values(item.queue_group for item in items),
        attention_label_counts=count_values(item.attention_label for item in items),
        items=items,
    )


def water_emergency_aging_followup_summary(
    water_emergencies: Sequence[WaterEmergency],
    *,
    now: datetime,
    work_orders: Sequence[WorkOrder],
    visits: Sequence[Visit],
    review_items: Sequence[ReviewItem],
    operational_events: Sequence[OperationalEventRecord],
) -> WaterEmergencyAgingFollowUpSummary:
    items = tuple(
        sorted(
            (
                water_emergency_aging_followup_item(
                    record,
                    now=now,
                    work_orders=work_orders,
                    visits=visits,
                    review_items=review_items,
                    operational_events=operational_events,
                )
                for record in water_emergencies
            ),
            key=lambda item: (
                item.timing_rank,
                item.timing_group,
                item.time_sensitivity_label,
                str(item.water_emergency_id),
            ),
        ),
    )

    return WaterEmergencyAgingFollowUpSummary(
        total_records=len(items),
        active_timing_risk_count=count_where(
            items,
            lambda item: item.requires_operator_attention,
        ),
        closed_or_resolved_count=count_where(
            items,
            lambda item: item.time_sensitivity_label == "closed_or_resolved",
        ),
        followup_due_count=count_where(
            items,
            lambda item: item.time_sensitivity_label == "followup_due",
        ),
        followup_overdue_count=count_where(
            items,
            lambda item: item.time_sensitivity_label == "followup_overdue",
        ),
        stale_evidence_count=count_where(
            items,
            lambda item: item.time_sensitivity_label == "stale_evidence",
        ),
        unknown_timing_count=count_where(
            items,
            lambda item: item.time_sensitivity_label == "unknown_timing",
        ),
        label_counts=count_values(item.time_sensitivity_label for item in items),
        age_bucket_counts=count_values(item.age_bucket for item in items),
        followup_bucket_counts=count_values(item.followup_bucket for item in items),
        items=items,
    )


def water_emergency_view_state_summary(
    *,
    next_step_summary: WaterEmergencyNextStepReadinessSummary,
    operator_queue_summary: WaterEmergencyOperatorQueueSummary,
    aging_followup_summary: WaterEmergencyAgingFollowUpSummary,
) -> WaterEmergencyViewStateSummary:
    readiness_by_id = {record.water_emergency_id: record for record in next_step_summary.records}
    aging_by_id = {item.water_emergency_id: item for item in aging_followup_summary.items}
    items = tuple(
        sorted(
            (
                water_emergency_view_state_item(
                    queue_item,
                    readiness=readiness_by_id[queue_item.water_emergency_id],
                    aging=aging_by_id[queue_item.water_emergency_id],
                )
                for queue_item in operator_queue_summary.items
                if queue_item.water_emergency_id in readiness_by_id
                and queue_item.water_emergency_id in aging_by_id
            ),
            key=lambda item: (
                item.sort_rank,
                item.primary_filter_group,
                normalized(item.current_status),
                normalized(item.current_stage),
                str(item.water_emergency_id),
            ),
        ),
    )
    filter_counts = Counter(filter_group for item in items for filter_group in item.filter_groups)

    return WaterEmergencyViewStateSummary(
        total_records=len(items),
        active_record_count=count_where(items, lambda item: item.is_active),
        closed_or_resolved_count=count_where(
            items,
            lambda item: item.primary_filter_group == "closed_or_resolved",
        ),
        available_filters=tuple(
            WaterEmergencyFilterOption(
                key=key,
                label=label,
                count=filter_counts[key],
                description=description,
            )
            for key, label, description in WATER_EMERGENCY_FILTER_DEFINITIONS
        ),
        sort_options=WATER_EMERGENCY_SORT_OPTIONS,
        group_counts=count_values(item.primary_filter_group for item in items),
        items=items,
    )


def water_emergency_governance_metadata() -> WaterEmergencyGovernanceMetadata:
    return WaterEmergencyGovernanceMetadata(
        randall_authorized_phase_0_baseline=True,
        source="phase_0_visibility_heuristic",
        legal_or_insurance_policy=False,
        requires_alfonso_owner_review=False,
        baseline_note=(
            "Randall-authorized Phase 0 visibility baseline for internal Water "
            "Emergency dashboard labels, filters, readiness groups, and view-state "
            "defaults."
        ),
        timing_heuristic_note=(
            "Water Emergency timing labels are conservative software visibility "
            "heuristics, not final SLA enforcement, insurance policy, drying "
            "certification language, or customer-facing promise."
        ),
        provisional_filter_groups=tuple(
            water_emergency_governance_metadata_item(
                key=key,
                label=label,
                category="filter_group",
                reason="Internal read-only filter group for dashboard view state.",
            )
            for key, label, _description in WATER_EMERGENCY_FILTER_DEFINITIONS
        ),
        provisional_attention_labels=tuple(
            water_emergency_governance_metadata_item(
                key=key,
                label=label,
                category="attention_label",
                reason="Internal read-only attention label for operator scanability.",
            )
            for key, label in WATER_EMERGENCY_ATTENTION_LABEL_DEFINITIONS
        ),
        provisional_timing_labels=tuple(
            water_emergency_governance_metadata_item(
                key=key,
                label=label,
                category="timing_label",
                reason=(
                    "Internal read-only timing label for Phase 0 follow-up visibility; "
                    "not final SLA enforcement."
                ),
            )
            for key, label in WATER_EMERGENCY_TIMING_LABEL_DEFINITIONS
        ),
        provisional_readiness_labels=tuple(
            water_emergency_governance_metadata_item(
                key=key,
                label=label,
                category="readiness_label",
                reason="Internal read-only readiness label for operator context.",
            )
            for key, label in WATER_EMERGENCY_READINESS_LABEL_DEFINITIONS
        ),
        owner_review_required_items=(
            WaterEmergencyGovernanceMetadataItem(
                key="formal_sla_or_insurance_policy",
                label="Formal SLA or insurance policy",
                category="owner_review_boundary",
                source="owner_review_required",
                randall_authorized_phase_0_baseline=False,
                legal_or_insurance_policy=True,
                requires_alfonso_owner_review=True,
                reason=(
                    "Final SLA commitments, insurance documentation, drying "
                    "certification, warranty language, or customer-facing policy "
                    "can create company liability and require Alfonso owner review."
                ),
            ),
        ),
        future_role_visibility_roles=WATER_EMERGENCY_FUTURE_ROLE_VISIBILITY_ROLES,
    )


def water_emergency_governance_metadata_item(
    *,
    key: str,
    label: str,
    category: str,
    reason: str,
) -> WaterEmergencyGovernanceMetadataItem:
    return WaterEmergencyGovernanceMetadataItem(
        key=key,
        label=label,
        category=category,
        source="phase_0_visibility_heuristic",
        randall_authorized_phase_0_baseline=True,
        legal_or_insurance_policy=False,
        requires_alfonso_owner_review=False,
        reason=reason,
    )


def water_emergency_result_window_metadata(
    *,
    view_state_summary: WaterEmergencyViewStateSummary,
    generated_at: datetime,
) -> WaterEmergencyResultWindowMetadata:
    total_count = view_state_summary.total_records
    return WaterEmergencyResultWindowMetadata(
        total_count=total_count,
        visible_count=len(view_state_summary.items),
        result_limit=total_count,
        has_more=False,
        sort_key="attention",
        generated_at=generated_at,
    )


def water_emergency_view_state_item(
    queue_item: WaterEmergencyQueueItem,
    *,
    readiness: WaterEmergencyNextStepReadiness,
    aging: WaterEmergencyAgingFollowUpItem,
) -> WaterEmergencyViewStateItem:
    filter_groups = water_emergency_view_filter_groups(
        queue_item,
        readiness=readiness,
        aging=aging,
    )
    primary_filter_group = water_emergency_primary_view_filter_group(filter_groups)

    return WaterEmergencyViewStateItem(
        water_emergency_id=queue_item.water_emergency_id,
        filter_groups=filter_groups,
        primary_filter_group=primary_filter_group,
        sort_rank=WATER_EMERGENCY_VIEW_SORT_RANKS.get(primary_filter_group, 999),
        sort_label=primary_filter_group,
        queue_group=queue_item.queue_group,
        attention_label=queue_item.attention_label,
        time_sensitivity_label=aging.time_sensitivity_label,
        readiness_label=readiness.primary_label,
        is_active=primary_filter_group != "closed_or_resolved",
        current_status=queue_item.current_status,
        current_stage=queue_item.current_stage,
        open_review_count=queue_item.open_review_count,
        critical_alert_count=queue_item.critical_alert_count,
        blocker_count=queue_item.blocker_count,
        unknown_count=queue_item.unknown_count,
        last_activity_at=latest_datetime(
            (
                aging.last_event_at,
                aging.last_review_at,
                aging.last_visit_at,
                aging.closed_at,
                aging.opened_at,
            ),
        ),
        summary=queue_item.summary,
        reason_codes=tuple(
            dict.fromkeys((*queue_item.reason_codes, *aging.reason_codes)),
        ),
        related_job_id=queue_item.related_job_id,
        related_work_order_ids=queue_item.related_work_order_ids,
        related_visit_ids=queue_item.related_visit_ids,
        audit_correlation_ids=queue_item.audit_correlation_ids,
        evidence_references=tuple(
            dict.fromkeys((*queue_item.evidence_references, *aging.evidence_references)),
        ),
    )


def water_emergency_view_filter_groups(
    queue_item: WaterEmergencyQueueItem,
    *,
    readiness: WaterEmergencyNextStepReadiness,
    aging: WaterEmergencyAgingFollowUpItem,
) -> tuple[str, ...]:
    groups: list[str] = ["all"]

    if queue_item.queue_group == "closed_or_resolved":
        groups.append("closed_or_resolved")
    else:
        groups.append("active")

    labels = set(readiness.labels)
    if queue_item.attention_label == "critical_attention":
        groups.append("critical_attention")
    if (
        queue_item.attention_label == "needs_manual_review"
        or "needs_manual_review" in labels
        or "needs_operator_decision" in labels
        or aging.time_sensitivity_label == "waiting_for_review"
    ):
        groups.append("needs_manual_review")
    if (
        queue_item.attention_label == "blocked_missing_data"
        or "blocked_by_missing_data" in labels
        or "awaiting_more_information" in labels
    ):
        groups.append("blocked_missing_data")
    if queue_item.attention_label == "needs_followup":
        groups.append("needs_followup")
    if queue_item.attention_label == "equipment_review_needed":
        groups.append("equipment_review_needed")
    if queue_item.attention_label == "drying_stage_review_needed":
        groups.append("drying_stage_review_needed")
    if (
        queue_item.attention_label == "ready_for_close_review"
        or readiness.primary_label == "ready_for_close_review"
        or aging.time_sensitivity_label == "ready_for_close_review"
    ):
        groups.append("ready_for_close_review")
    if queue_item.attention_label == "needs_operator_review":
        groups.append("needs_operator_review")
    if aging.time_sensitivity_label in {
        "followup_due",
        "followup_overdue",
        "stale_evidence",
        "unknown_timing",
    }:
        groups.append(aging.time_sensitivity_label)

    return tuple(dict.fromkeys(groups))


def water_emergency_primary_view_filter_group(filter_groups: Sequence[str]) -> str:
    group_set = set(filter_groups)
    for group in WATER_EMERGENCY_VIEW_FILTER_PRIORITY:
        if group in group_set:
            return group
    return "needs_operator_review"


def water_emergency_aging_followup_item(
    record: WaterEmergency,
    *,
    now: datetime,
    work_orders: Sequence[WorkOrder],
    visits: Sequence[Visit],
    review_items: Sequence[ReviewItem],
    operational_events: Sequence[OperationalEventRecord],
) -> WaterEmergencyAgingFollowUpItem:
    related_work_orders = water_emergency_related_work_orders(record, work_orders=work_orders)
    related_visits = water_emergency_related_visits(record, visits=visits)
    related_reviews = water_emergency_related_reviews(
        record,
        visits=related_visits,
        review_items=review_items,
    )
    related_events = water_emergency_related_events(
        record,
        work_orders=related_work_orders,
        visits=related_visits,
        operational_events=operational_events,
    )
    opened_at = water_emergency_opened_at(record)
    last_visit_at = latest_datetime(visit_chain_datetime(visit) for visit in related_visits)
    last_review_at = latest_datetime(review_timeline_datetime(review) for review in related_reviews)
    last_event_at = latest_datetime(event_timeline_datetime(event) for event in related_events)
    age_hours = hours_between(opened_at, now)
    hours_since_last_visit = hours_between(last_visit_at, now)
    hours_since_last_review = hours_between(last_review_at, now)
    hours_since_last_event = hours_between(last_event_at, now)
    unresolved_reviews = tuple(
        review
        for review in related_reviews
        if normalized(review.status) in UNRESOLVED_REVIEW_STATUSES
    )
    latest_evidence_at = latest_datetime((last_visit_at, last_review_at, last_event_at))
    label = water_emergency_time_sensitivity_label(
        record,
        now=now,
        age_hours=age_hours,
        latest_evidence_at=latest_evidence_at,
        unresolved_reviews=unresolved_reviews,
        related_visits=related_visits,
    )
    reason_codes = water_emergency_timing_reason_codes(
        record,
        label=label,
        unresolved_reviews=unresolved_reviews,
        related_visits=related_visits,
        latest_evidence_at=latest_evidence_at,
    )
    missing_indicators = water_emergency_missing_timing_indicators(
        opened_at=opened_at,
        last_visit_at=last_visit_at,
        last_review_at=last_review_at,
        last_event_at=last_event_at,
    )
    related_work_order_ids = {
        work_order.id for work_order in related_work_orders if work_order.id is not None
    }
    related_visit_ids = {visit.id for visit in related_visits if visit.id is not None}

    return WaterEmergencyAgingFollowUpItem(
        water_emergency_id=record.id,
        time_sensitivity_label=label,
        timing_group=water_emergency_timing_group(label),
        timing_rank=water_emergency_timing_rank(label),
        age_bucket=water_emergency_age_bucket(age_hours),
        followup_bucket=water_emergency_followup_bucket(label),
        age_hours=age_hours,
        hours_since_last_visit=hours_since_last_visit,
        hours_since_last_review=hours_since_last_review,
        hours_since_last_event=hours_since_last_event,
        opened_at=opened_at,
        last_visit_at=last_visit_at,
        last_review_at=last_review_at,
        last_event_at=last_event_at,
        closed_at=record.closed_at,
        summary=water_emergency_timing_summary_text(label),
        reason_codes=reason_codes,
        missing_timestamp_indicators=missing_indicators,
        stale_indicator_count=1 if label == "stale_evidence" else 0,
        requires_operator_attention=label
        not in {"newly_opened", "active_monitoring", "closed_or_resolved"},
        related_job_id=record.job_id,
        related_work_order_ids=sorted_uuid_tuple(related_work_order_ids),
        related_visit_ids=sorted_uuid_tuple(related_visit_ids),
        audit_correlation_ids=unique_audit_correlation_ids(
            related_work_orders,
            related_visits,
            related_reviews,
            related_events,
        ),
        evidence_references=water_emergency_next_step_evidence_references(
            record,
            related_work_orders=related_work_orders,
            related_visits=related_visits,
            related_reviews=related_reviews,
            related_events=related_events,
        ),
    )


def water_emergency_time_sensitivity_label(
    record: WaterEmergency,
    *,
    now: datetime,
    age_hours: int | None,
    latest_evidence_at: datetime | None,
    unresolved_reviews: Sequence[ReviewItem],
    related_visits: Sequence[Visit],
) -> str:
    if not is_open_water_emergency(record):
        return "closed_or_resolved"
    if unresolved_reviews:
        return "waiting_for_review"
    if age_hours is None:
        return "unknown_timing"
    if water_emergency_ready_for_close_review(record):
        return "ready_for_close_review"
    if age_hours <= NEWLY_OPENED_HOURS:
        return "newly_opened"

    if water_emergency_needs_visit_followup(record, related_visits):
        followup_hours = hours_between(
            latest_datetime(visit_chain_datetime(visit) for visit in related_visits),
            now,
        )
        if followup_hours is None:
            followup_hours = age_hours
        if followup_hours >= FOLLOWUP_OVERDUE_HOURS:
            return "followup_overdue"
        if followup_hours >= FOLLOWUP_DUE_HOURS:
            return "followup_due"

    evidence_age_hours = hours_between(latest_evidence_at, now)
    if evidence_age_hours is not None and evidence_age_hours >= STALE_EVIDENCE_HOURS:
        return "stale_evidence"
    if latest_evidence_at is None:
        return "unknown_timing"
    if "monitor" in normalized(record.status) or "monitor" in normalized(record.drying_stage):
        return "active_monitoring"
    return "active_monitoring"


def water_emergency_timing_group(label: str) -> str:
    return {
        "newly_opened": "active_monitoring",
        "active_monitoring": "active_monitoring",
        "followup_due": "followup_attention",
        "followup_overdue": "followup_attention",
        "stale_evidence": "stale_or_unknown",
        "waiting_for_review": "manual_review",
        "ready_for_close_review": "close_review",
        "closed_or_resolved": "closed_or_resolved",
        "unknown_timing": "stale_or_unknown",
    }.get(label, "stale_or_unknown")


def water_emergency_timing_rank(label: str) -> int:
    return {
        "followup_overdue": 10,
        "waiting_for_review": 20,
        "stale_evidence": 30,
        "followup_due": 40,
        "unknown_timing": 50,
        "ready_for_close_review": 60,
        "newly_opened": 70,
        "active_monitoring": 80,
        "closed_or_resolved": 90,
    }.get(label, 50)


def water_emergency_age_bucket(age_hours: int | None) -> str:
    if age_hours is None:
        return "unknown_age"
    if age_hours <= NEWLY_OPENED_HOURS:
        return "under_24h"
    if age_hours < FOLLOWUP_OVERDUE_HOURS:
        return "1_to_3_days"
    if age_hours < 168:
        return "3_to_7_days"
    return "over_7_days"


def water_emergency_followup_bucket(label: str) -> str:
    return {
        "followup_due": "followup_due",
        "followup_overdue": "followup_overdue",
        "unknown_timing": "unknown_followup",
        "closed_or_resolved": "closed_or_resolved",
    }.get(label, "followup_not_due")


def water_emergency_timing_reason_codes(
    record: WaterEmergency,
    *,
    label: str,
    unresolved_reviews: Sequence[ReviewItem],
    related_visits: Sequence[Visit],
    latest_evidence_at: datetime | None,
) -> tuple[str, ...]:
    reasons: list[str] = [label]
    reasons.extend(
        normalized(review.reason_code)
        for review in unresolved_reviews
        if normalized(review.reason_code)
    )
    if not related_visits and is_open_water_emergency(record):
        reasons.append("no_visit_history")
    if latest_evidence_at is None and is_open_water_emergency(record):
        reasons.append("no_timestamped_evidence")
    if record.opened_at is None and is_open_water_emergency(record):
        reasons.append("missing_opened_at")
    if not reasons:
        reasons.append("no_deterministic_timing_reason")
    return tuple(dict.fromkeys(reasons))


def water_emergency_missing_timing_indicators(
    *,
    opened_at: datetime | None,
    last_visit_at: datetime | None,
    last_review_at: datetime | None,
    last_event_at: datetime | None,
) -> tuple[str, ...]:
    missing: list[str] = []
    if opened_at is None:
        missing.append("missing_opened_at")
    if latest_datetime((last_visit_at, last_review_at, last_event_at)) is None:
        missing.append("missing_last_evidence_at")
    return tuple(missing)


def water_emergency_timing_summary_text(label: str) -> str:
    return {
        "newly_opened": (
            "The Water Emergency record was opened recently; Phase 0 shows timing context "
            "without implying an automated next action."
        ),
        "active_monitoring": (
            "Recent visit or event evidence exists, so the record is shown as active "
            "monitoring visibility only."
        ),
        "followup_due": (
            "Existing timestamp evidence suggests follow-up attention may be due; this is a "
            "conservative Phase 0 visibility label, not an SLA rule."
        ),
        "followup_overdue": (
            "Existing timestamp evidence suggests follow-up attention may be overdue; this is "
            "visibility only and does not escalate or execute work."
        ),
        "stale_evidence": (
            "The latest related evidence is old enough to be flagged as stale for operator "
            "awareness."
        ),
        "waiting_for_review": (
            "Open Manual Review evidence exists; Manual Review remains authoritative."
        ),
        "ready_for_close_review": (
            "Persisted status/stage evidence suggests close-review readiness, but no close "
            "action is executed."
        ),
        "closed_or_resolved": (
            "Closed or resolved Water Emergency record; it is separated from active timing risks."
        ),
        "unknown_timing": (
            "The record is missing enough timestamp evidence that no timing category should "
            "be inferred."
        ),
    }.get(label, "Read-only timing visibility is derived from persisted evidence only.")


def water_emergency_queue_item(
    readiness: WaterEmergencyNextStepReadiness,
) -> WaterEmergencyQueueItem:
    attention_label = water_emergency_attention_label(readiness)
    return WaterEmergencyQueueItem(
        water_emergency_id=readiness.water_emergency_id,
        attention_label=attention_label,
        queue_group=water_emergency_queue_group(attention_label),
        attention_rank=water_emergency_attention_rank(attention_label),
        readiness_labels=readiness.labels,
        summary=water_emergency_attention_summary_text(attention_label),
        reason_codes=readiness.reason_codes,
        evidence_references=readiness.evidence_references,
        current_status=readiness.current_status,
        current_stage=readiness.current_stage,
        open_review_count=readiness.open_review_count,
        critical_alert_count=readiness.critical_alert_count,
        blocker_count=readiness.blocker_count,
        unknown_count=readiness.unknown_count,
        related_job_id=readiness.related_job_id,
        related_work_order_ids=readiness.related_work_order_ids,
        related_visit_ids=readiness.related_visit_ids,
        audit_correlation_ids=readiness.audit_correlation_ids,
    )


def water_emergency_attention_label(
    readiness: WaterEmergencyNextStepReadiness,
) -> str:
    labels = set(readiness.labels)
    if readiness.primary_label == "closed_no_active_next_step":
        return "closed_or_resolved"
    if readiness.critical_alert_count > 0:
        return "critical_attention"
    if "needs_manual_review" in labels or "needs_operator_decision" in labels:
        return "needs_manual_review"
    if "needs_equipment_review" in labels:
        return "equipment_review_needed"
    if "needs_drying_stage_confirmation" in labels and readiness.unknown_count <= 2:
        return "drying_stage_review_needed"
    if "blocked_by_missing_data" in labels or "awaiting_more_information" in labels:
        return "blocked_missing_data"
    if "needs_visit_followup" in labels:
        return "needs_followup"
    if "ready_for_close_review" in labels:
        return "ready_for_close_review"
    if "monitor" in normalized(readiness.current_status) or "monitor" in normalized(
        readiness.current_stage
    ):
        return "monitoring"
    return "needs_operator_review"


def water_emergency_queue_group(attention_label: str) -> str:
    return {
        "critical_attention": "active_attention",
        "needs_manual_review": "manual_review",
        "blocked_missing_data": "blocked_or_missing_info",
        "needs_followup": "readiness_followup",
        "equipment_review_needed": "readiness_followup",
        "drying_stage_review_needed": "readiness_followup",
        "ready_for_close_review": "close_review",
        "monitoring": "monitoring",
        "closed_or_resolved": "closed_or_resolved",
        "needs_operator_review": "operator_review",
    }.get(attention_label, "operator_review")


def water_emergency_attention_rank(attention_label: str) -> int:
    return {
        "critical_attention": 10,
        "needs_manual_review": 20,
        "blocked_missing_data": 30,
        "equipment_review_needed": 40,
        "drying_stage_review_needed": 45,
        "needs_followup": 50,
        "needs_operator_review": 60,
        "ready_for_close_review": 70,
        "monitoring": 80,
        "closed_or_resolved": 90,
    }.get(attention_label, 60)


def water_emergency_attention_summary_text(attention_label: str) -> str:
    return {
        "critical_attention": (
            "Critical unresolved Water Emergency evidence exists; operator attention is "
            "needed before any future emergency workflow step."
        ),
        "needs_manual_review": (
            "Open Manual Review or operator-decision evidence exists; Manual Review remains "
            "authoritative."
        ),
        "blocked_missing_data": (
            "Persisted blocker, unknown, or missing-data evidence exists; the record needs "
            "safe operator review before future progress."
        ),
        "needs_followup": (
            "The visit chain indicates follow-up visibility is needed before future workflow "
            "modules can safely proceed."
        ),
        "equipment_review_needed": (
            "Equipment evidence needs operator review; this is visibility only and not "
            "equipment execution."
        ),
        "drying_stage_review_needed": (
            "Drying-stage or moisture-tracking evidence needs confirmation before future "
            "workflow modules can proceed."
        ),
        "ready_for_close_review": (
            "Persisted evidence suggests close-review readiness, but no close action is "
            "executed by the dashboard."
        ),
        "monitoring": (
            "Persisted status/stage evidence indicates monitoring visibility without an "
            "active workflow action."
        ),
        "closed_or_resolved": (
            "Closed or resolved Water Emergency record; it is separated from active "
            "attention items."
        ),
        "needs_operator_review": (
            "No deterministic queue category is safer than operator review from the current "
            "evidence."
        ),
    }.get(
        attention_label,
        "Read-only Water Emergency queue visibility is derived from persisted evidence only.",
    )


def water_emergency_next_step_readiness(
    record: WaterEmergency,
    *,
    work_orders: Sequence[WorkOrder],
    visits: Sequence[Visit],
    review_items: Sequence[ReviewItem],
    operational_events: Sequence[OperationalEventRecord],
) -> WaterEmergencyNextStepReadiness:
    related_work_orders = water_emergency_related_work_orders(record, work_orders=work_orders)
    related_visits = water_emergency_related_visits(record, visits=visits)
    related_reviews = water_emergency_related_reviews(
        record,
        visits=related_visits,
        review_items=review_items,
    )
    related_events = water_emergency_related_events(
        record,
        work_orders=related_work_orders,
        visits=related_visits,
        operational_events=operational_events,
    )
    related_work_order_ids = {
        work_order.id for work_order in related_work_orders if work_order.id is not None
    }
    related_visit_ids = {visit.id for visit in related_visits if visit.id is not None}
    unresolved_reviews = tuple(
        review
        for review in related_reviews
        if normalized(review.status) in UNRESOLVED_REVIEW_STATUSES
    )
    data_gap_labels = tuple(
        bucket.label
        for bucket in water_emergency_detail_data_gap_counts(
            record,
            job=None,
            work_orders=related_work_orders,
            visits=related_visits,
            events=related_events,
        )
        if bucket.label != "missing_job_reference"
    )
    equipment_context = water_emergency_detail_equipment_context(
        record,
        work_orders=related_work_orders,
    )
    drying_context = water_emergency_detail_drying_stage_context(record)
    needs_equipment_review = water_emergency_needs_equipment_review(
        record,
        equipment_context=equipment_context,
    )
    equipment_unknowns = (
        tuple(equipment_context.unknown_indicators) if needs_equipment_review else ()
    )
    drying_unknowns = tuple(drying_context.missing_indicators)
    unknown_labels = tuple(
        dict.fromkeys((*data_gap_labels, *equipment_unknowns, *drying_unknowns)),
    )
    blocker_count = count_where(unresolved_reviews, is_blocker_review_reason)
    critical_alert_count = count_where(unresolved_reviews, is_critical_unresolved_review)

    labels: list[str] = []
    reason_codes: list[str] = []

    if not is_open_water_emergency(record):
        labels.append("closed_no_active_next_step")
        reason_codes.append("water_emergency_closed_or_resolved")
        summary = (
            "Closed or resolved Water Emergency record; no active next-step action is implied."
        )
    else:
        if unresolved_reviews:
            labels.extend(("needs_manual_review", "needs_operator_decision"))
            reason_codes.extend(
                normalized(review.reason_code)
                for review in unresolved_reviews
                if normalized(review.reason_code)
            )

        if blocker_count > 0 or unknown_labels:
            labels.extend(("blocked_by_missing_data", "awaiting_more_information"))
            reason_codes.extend(unknown_labels)

        if not related_visits:
            labels.append("needs_visit_followup")
            reason_codes.append("no_visit_history")
        elif water_emergency_needs_visit_followup(record, related_visits):
            labels.append("needs_visit_followup")
            reason_codes.append("open_visit_chain_followup_needed")

        if needs_equipment_review:
            labels.append("needs_equipment_review")
            reason_codes.extend(equipment_unknowns or ("equipment_context_review_needed",))

        if water_emergency_needs_drying_stage_confirmation(
            record,
            drying_context=drying_context,
        ):
            labels.append("needs_drying_stage_confirmation")
            reason_codes.extend(drying_unknowns or ("drying_stage_confirmation_needed",))

        if not labels and water_emergency_ready_for_close_review(record):
            labels.append("ready_for_close_review")
            reason_codes.append("ready_for_close_review_evidence")

        if not labels:
            labels.append("needs_operator_review")
            reason_codes.append("no_deterministic_next_step")

        summary = water_emergency_next_step_summary_text(labels[0])

    labels_tuple = tuple(dict.fromkeys(labels))
    reason_codes_tuple = tuple(dict.fromkeys(reason_codes))
    evidence_references = water_emergency_next_step_evidence_references(
        record,
        related_work_orders=related_work_orders,
        related_visits=related_visits,
        related_reviews=related_reviews,
        related_events=related_events,
    )
    return WaterEmergencyNextStepReadiness(
        water_emergency_id=record.id,
        primary_label=labels_tuple[0],
        labels=labels_tuple,
        summary=summary,
        reason_codes=reason_codes_tuple,
        evidence_references=evidence_references,
        current_status=normalized(record.status),
        current_stage=normalized(record.drying_stage) or None,
        open_review_count=len(unresolved_reviews),
        critical_alert_count=critical_alert_count,
        blocker_count=blocker_count,
        unknown_count=len(unknown_labels),
        requires_operator_attention=labels_tuple[0] != "closed_no_active_next_step",
        related_job_id=record.job_id,
        related_work_order_ids=sorted_uuid_tuple(related_work_order_ids),
        related_visit_ids=sorted_uuid_tuple(related_visit_ids),
        audit_correlation_ids=unique_audit_correlation_ids(
            related_work_orders,
            related_visits,
            related_reviews,
            related_events,
        ),
    )


def water_emergency_needs_visit_followup(
    record: WaterEmergency,
    visits: Sequence[Visit],
) -> bool:
    if not is_open_water_emergency(record):
        return False
    if water_emergency_ready_for_close_review(record):
        return False
    return not any(
        not is_completed_visit(visit) and (is_scheduled_visit(visit) or visit.arrived_at)
        for visit in visits
    )


def water_emergency_needs_equipment_review(
    record: WaterEmergency,
    *,
    equipment_context: WaterEmergencyDetailEquipmentContext,
) -> bool:
    if not is_open_water_emergency(record):
        return False
    return record.equipment_onsite and (
        bool(equipment_context.unknown_indicators) or not equipment_context.required_equipment_notes
    )


def water_emergency_needs_drying_stage_confirmation(
    record: WaterEmergency,
    *,
    drying_context: WaterEmergencyDetailDryingStageContext,
) -> bool:
    if not is_open_water_emergency(record):
        return False
    return record.moisture_tracking_required and bool(drying_context.missing_indicators)


def water_emergency_ready_for_close_review(record: WaterEmergency) -> bool:
    status = normalized(record.status)
    stage = normalized(record.drying_stage)
    next_action = normalized(record.next_required_action)
    return (
        status in READY_FOR_CLOSE_REVIEW_STATUSES
        or stage in READY_FOR_CLOSE_REVIEW_STAGES
        or ("close" in next_action and "review" in next_action)
    )


def is_next_step_blocker_reason(reason_code: str) -> bool:
    normalized_reason = normalized(reason_code)
    return (
        "missing" in normalized_reason
        or "blocker" in normalized_reason
        or "unknown" in normalized_reason
        or normalized_reason.startswith("no_")
        or (
            "review" in normalized_reason and normalized_reason != "ready_for_close_review_evidence"
        )
    )


def water_emergency_next_step_summary_text(label: str) -> str:
    return {
        "needs_manual_review": (
            "Open Manual Review evidence exists; operator review remains required before any "
            "future Water Emergency workflow step."
        ),
        "blocked_by_missing_data": (
            "Persisted blocker or missing-data evidence exists; the record needs more "
            "information before future workflow progress."
        ),
        "needs_visit_followup": (
            "The visit chain indicates follow-up visibility is needed before future workflow "
            "modules can safely proceed."
        ),
        "needs_equipment_review": (
            "Equipment context needs review because existing evidence is incomplete or equipment "
            "inventory is not modeled yet."
        ),
        "needs_drying_stage_confirmation": (
            "Drying or moisture-tracking context needs confirmation from persisted evidence."
        ),
        "ready_for_close_review": (
            "Persisted status evidence suggests the record can be reviewed for future closure "
            "readiness, but no close action is executed."
        ),
        "needs_operator_review": (
            "No deterministic next-step label can be selected from current evidence; operator "
            "review is needed."
        ),
    }.get(label, "Read-only next-step visibility is derived from persisted evidence only.")


def water_emergency_next_step_evidence_references(
    record: WaterEmergency,
    *,
    related_work_orders: Sequence[WorkOrder],
    related_visits: Sequence[Visit],
    related_reviews: Sequence[ReviewItem],
    related_events: Sequence[OperationalEventRecord],
) -> tuple[str, ...]:
    references = [
        f"job:{record.job_id}",
        f"water_emergency:{record.id}",
    ]
    references.extend(
        f"work_order:{work_order.id}"
        for work_order in related_work_orders
        if work_order.id is not None
    )
    references.extend(f"visit:{visit.id}" for visit in related_visits if visit.id is not None)
    references.extend(f"review:{review.id}" for review in related_reviews if review.id is not None)
    references.extend(f"event:{event.id}" for event in related_events if event.id is not None)
    return tuple(dict.fromkeys(references))


def is_critical_unresolved_review(review: ReviewItem) -> bool:
    return (
        normalized(review.status) in UNRESOLVED_REVIEW_STATUSES
        and normalized(review.severity) == "critical"
    )


def is_escalation_review(review: ReviewItem) -> bool:
    return (
        normalized(review.status) in UNRESOLVED_REVIEW_STATUSES
        and normalized(review.severity) in ESCALATION_SEVERITIES
    )


def is_blocker_review_reason(review: ReviewItem) -> bool:
    reason_code = normalized(review.reason_code)
    return any(keyword in reason_code for keyword in WATER_EMERGENCY_BLOCKER_REASON_KEYWORDS)


def is_scheduled_visit(visit: Visit) -> bool:
    return visit.scheduled_start_at is not None or normalized(visit.status) == "scheduled"


def is_completed_visit(visit: Visit) -> bool:
    return visit.completed_at is not None or normalized(visit.status) in {
        "complete",
        "completed",
        "closed",
    }


def visit_chain_datetime(visit: Visit) -> datetime | None:
    return visit.completed_at or visit.arrived_at or visit.scheduled_start_at


def review_timeline_datetime(review: ReviewItem) -> datetime | None:
    return review.resolved_at or review.reviewed_at or review.deferred_until or review.created_at


def event_timeline_datetime(event: OperationalEventRecord) -> datetime | None:
    return event.occurred_at or event.recorded_at


def water_emergency_opened_at(record: WaterEmergency) -> datetime | None:
    return record.opened_at


def latest_datetime(values: Sequence[datetime | None] | object) -> datetime | None:
    datetimes = tuple(value for value in values if value is not None)
    if not datetimes:
        return None
    return max(datetimes)


def hours_between(start: datetime | None, end: datetime | None) -> int | None:
    if start is None or end is None:
        return None
    if start.tzinfo is None and end.tzinfo is not None:
        start = start.replace(tzinfo=end.tzinfo)
    if end.tzinfo is None and start.tzinfo is not None:
        end = end.replace(tzinfo=start.tzinfo)
    delta_hours = int((end - start).total_seconds() // 3600)
    return max(delta_hours, 0)


def is_water_emergency_review_item(
    review: ReviewItem,
    *,
    water_job_ids: set[object],
    water_visit_ids: set[object],
    water_record_ids: set[object],
) -> bool:
    reason_code = normalized(review.reason_code)
    return (
        normalized(review.entity_type) == "water_emergency"
        or review.entity_id in water_record_ids
        or review.job_id in water_job_ids
        or review.visit_id in water_visit_ids
        or "water_emergency" in reason_code
    )


def is_water_emergency_event(
    event: OperationalEventRecord,
    *,
    water_job_ids: set[object],
    water_visit_ids: set[object],
    water_work_order_ids: set[object],
    water_record_ids: set[object],
) -> bool:
    return (
        normalized(event.entity_type) == "water_emergency"
        or event.entity_id in water_record_ids
        or event.job_id in water_job_ids
        or event.visit_id in water_visit_ids
        or event.work_order_id in water_work_order_ids
    )


def water_emergency_related_work_orders(
    record: WaterEmergency,
    *,
    work_orders: Sequence[WorkOrder],
) -> tuple[WorkOrder, ...]:
    return tuple(work_order for work_order in work_orders if work_order.job_id == record.job_id)


def water_emergency_related_visits(
    record: WaterEmergency,
    *,
    visits: Sequence[Visit],
) -> tuple[Visit, ...]:
    return tuple(visit for visit in visits if visit.job_id == record.job_id)


def water_emergency_related_reviews(
    record: WaterEmergency,
    *,
    visits: Sequence[Visit],
    review_items: Sequence[ReviewItem],
) -> tuple[ReviewItem, ...]:
    related_visit_ids = {visit.id for visit in visits if visit.id is not None}
    return tuple(
        review
        for review in review_items
        if is_review_related_to_water_emergency_record(
            review,
            record=record,
            related_visit_ids=related_visit_ids,
        )
    )


def is_review_related_to_water_emergency_record(
    review: ReviewItem,
    *,
    record: WaterEmergency,
    related_visit_ids: set[object],
) -> bool:
    return (
        review.job_id == record.job_id
        or review.entity_id == record.id
        or review.visit_id in related_visit_ids
        or (normalized(review.entity_type) == "water_emergency" and review.entity_id == record.id)
    )


def water_emergency_related_events(
    record: WaterEmergency,
    *,
    work_orders: Sequence[WorkOrder],
    visits: Sequence[Visit],
    operational_events: Sequence[OperationalEventRecord],
) -> tuple[OperationalEventRecord, ...]:
    related_visit_ids = {visit.id for visit in visits if visit.id is not None}
    related_work_order_ids = {
        work_order.id for work_order in work_orders if work_order.id is not None
    }
    return tuple(
        event
        for event in operational_events
        if (
            event.job_id == record.job_id
            or event.entity_id == record.id
            or event.visit_id in related_visit_ids
            or event.work_order_id in related_work_order_ids
            or (normalized(event.entity_type) == "water_emergency" and event.entity_id == record.id)
        )
    )


def water_emergency_data_gap_counts(
    water_emergencies: Sequence[WaterEmergency],
    *,
    visits: Sequence[Visit],
    events: Sequence[OperationalEventRecord],
) -> tuple[CountBucket, ...]:
    gaps: list[str] = []
    for record in water_emergencies:
        if not is_open_water_emergency(record):
            continue
        if not normalized(record.drying_stage):
            gaps.append("missing_drying_stage")
        if not normalized(record.next_required_action):
            gaps.append("missing_next_required_action")
        if not any(visit.job_id == record.job_id for visit in visits):
            gaps.append("no_visit_history")
        if not any(
            event.job_id == record.job_id
            or event.entity_id == record.id
            or (normalized(event.entity_type) == "water_emergency" and event.entity_id == record.id)
            for event in events
        ):
            gaps.append("no_timeline_evidence")
    return count_values(gaps)


def water_emergency_detail_data_gap_counts(
    record: WaterEmergency,
    *,
    job: Job | None,
    work_orders: Sequence[WorkOrder],
    visits: Sequence[Visit],
    events: Sequence[OperationalEventRecord],
) -> tuple[CountBucket, ...]:
    gaps: list[str] = []
    if job is None:
        gaps.append("missing_job_reference")
    if not work_orders:
        gaps.append("no_work_order_reference")
    if not visits:
        gaps.append("no_visit_history")
    if not events:
        gaps.append("no_timeline_evidence")
    if is_open_water_emergency(record):
        if not normalized(record.drying_stage):
            gaps.append("missing_drying_stage")
        if not normalized(record.next_required_action):
            gaps.append("missing_next_required_action")
    return count_values(gaps)


def water_emergency_job_reference(job: Job) -> WaterEmergencyJobReference:
    return WaterEmergencyJobReference(
        job_id=job.id,
        job_type=job.job_type,
        status=normalized(job.status),
        review_status=normalized(job.review_status) or None,
        priority=job.priority,
        requested_date=job.requested_date,
        scheduled_date=job.scheduled_date,
        source_system=job.source_system,
        source_event_id=job.source_event_id,
    )


def water_emergency_work_order_reference(
    work_order: WorkOrder,
) -> WaterEmergencyWorkOrderReference:
    return WaterEmergencyWorkOrderReference(
        work_order_id=work_order.id,
        work_order_number=work_order.work_order_number,
        status=normalized(work_order.status),
        dispatch_status=normalized(work_order.dispatch_status) or None,
        assigned_technician_id=work_order.assigned_technician_id,
        audit_correlation_id=work_order.audit_correlation_id,
    )


def water_emergency_visit_reference(visit: Visit) -> WaterEmergencyVisitReference:
    return WaterEmergencyVisitReference(
        visit_id=visit.id,
        work_order_id=visit.work_order_id,
        technician_id=visit.technician_id,
        visit_type=visit.visit_type,
        status=normalized(visit.status),
        scheduled_start_at=visit.scheduled_start_at,
        scheduled_end_at=visit.scheduled_end_at,
        arrived_at=visit.arrived_at,
        completed_at=visit.completed_at,
        audit_correlation_id=visit.audit_correlation_id,
    )


def water_emergency_review_indicator(review: ReviewItem) -> WaterEmergencyReviewIndicator:
    return WaterEmergencyReviewIndicator(
        review_item_id=review.id,
        status=normalized(review.status),
        severity=normalized(review.severity) or None,
        reason_code=normalized(review.reason_code),
        confidence_score=review.confidence_score,
        entity_type=normalized(review.entity_type) or None,
        entity_id=review.entity_id,
        job_id=review.job_id,
        visit_id=review.visit_id,
        audit_correlation_id=review.audit_correlation_id,
        recommended_action=review.recommended_action,
    )


def water_emergency_record_summary(
    record: WaterEmergency,
    *,
    work_orders: Sequence[WorkOrder],
    visits: Sequence[Visit],
    review_items: Sequence[ReviewItem],
    operational_events: Sequence[OperationalEventRecord],
) -> WaterEmergencyRecordSummary:
    related_work_orders = water_emergency_related_work_orders(
        record,
        work_orders=work_orders,
    )
    related_visits = water_emergency_related_visits(record, visits=visits)
    related_visit_ids = {visit.id for visit in related_visits if visit.id is not None}
    related_work_order_ids = {
        work_order.id for work_order in related_work_orders if work_order.id is not None
    }
    related_reviews = water_emergency_related_reviews(
        record,
        visits=related_visits,
        review_items=review_items,
    )
    related_events = water_emergency_related_events(
        record,
        work_orders=related_work_orders,
        visits=related_visits,
        operational_events=operational_events,
    )

    return WaterEmergencyRecordSummary(
        water_emergency_id=record.id,
        job_id=record.job_id,
        status=normalized(record.status),
        drying_stage=normalized(record.drying_stage) or None,
        next_required_action=record.next_required_action,
        is_open=is_open_water_emergency(record),
        equipment_onsite=record.equipment_onsite,
        moisture_tracking_required=record.moisture_tracking_required,
        opened_at=record.opened_at,
        closed_at=record.closed_at,
        related_work_order_ids=sorted_uuid_tuple(related_work_order_ids),
        related_visit_ids=sorted_uuid_tuple(related_visit_ids),
        open_review_count=count_where(
            related_reviews,
            lambda review: normalized(review.status) in UNRESOLVED_REVIEW_STATUSES,
        ),
        timeline_event_count=len(related_events),
        audit_correlation_ids=unique_audit_correlation_ids(
            related_work_orders,
            related_visits,
            related_reviews,
            related_events,
        ),
    )


def sorted_uuid_tuple(values: set[object]) -> tuple[object, ...]:
    return tuple(sorted(values, key=str))


def unique_audit_correlation_ids(*groups: Sequence[object]) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                value
                for group in groups
                for item in group
                if (value := getattr(item, "audit_correlation_id", None))
            },
        ),
    )


def count_audit_correlation_ids(*groups: Sequence[object]) -> int:
    return len(
        {
            value
            for group in groups
            for item in group
            if (value := getattr(item, "audit_correlation_id", None))
        },
    )


def timeline_entry(event: OperationalEventRecord) -> OperationalTimelineEntry:
    return OperationalTimelineEntry(
        occurred_at=event.occurred_at,
        event_type=event.event_type,
        event_state=event.event_state,
        entity_type=event.entity_type,
        entity_id=event.entity_id,
        route_assignment_id=event.route_assignment_id,
        visit_id=event.visit_id,
        work_order_id=event.work_order_id,
        job_id=event.job_id,
        technician_id=event.technician_id,
        audit_correlation_id=event.audit_correlation_id,
        previous_state=event.previous_state,
        new_state=event.new_state,
        is_immutable=event.is_immutable,
    )
