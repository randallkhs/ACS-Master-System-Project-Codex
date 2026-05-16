from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Sequence
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.dashboard import (
    CountBucket,
    DashboardDispatchSummary,
    DashboardOverviewReadModel,
    DispatchLifecycleSummary,
    ExternalExecutionSummary,
    GovernanceAccountabilitySummary,
    ManualReviewSummary,
    OperationalDashboardSummary,
    OperationalEventTimelineSummary,
    OperationalTimelineEntry,
    ReconciliationRecoverySummary,
    RouteAssignmentSummary,
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
TERMINAL_WATER_EMERGENCY_STATUSES = {"closed", "completed", "cancelled", "canceled"}
BLOCKED_ROUTE_STATES = {"blocked", "reconciliation_blocked", "replay_blocked"}
BLOCKED_GOVERNANCE_STATES = {"governance_blocked"}
BLOCKED_ACCOUNTABILITY_STATES = {"accountability_blocked"}


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
                visits, lambda visit: visit.status == "dispatch_ready"
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

    def build_dispatch_from_session(self, session: Session) -> DashboardDispatchSummary:
        source = load_dashboard_source(session)
        return self.build_dispatch(route_assignments=source["route_assignments"])


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
        lambda record: (
            record.closed_at is None
            and normalized(record.status) not in TERMINAL_WATER_EMERGENCY_STATUSES
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
