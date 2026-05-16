from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from sqlalchemy import create_engine, select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core.config import LOCAL_DATABASE_HOSTS, PLACEHOLDER_DATABASE_PASSWORDS, Settings
from app.models.customer import Customer
from app.models.intake_processing_record import IntakeProcessingRecord
from app.models.job import Job
from app.models.operational_event_record import OperationalEventRecord
from app.models.property import Property
from app.models.review_item import ReviewItem
from app.models.route_assignment import RouteAssignment
from app.models.technician import Technician
from app.models.visit import Visit
from app.models.water_emergency import WaterEmergency
from app.models.work_order import WorkOrder

SEED_SOURCE_SYSTEM = "module27_dev_seed"
SEED_AUDIT_CORRELATION_ID = "module27-dashboard-demo-001"

CUSTOMER_ID = UUID("11111111-1111-4111-8111-111111111111")
PROPERTY_ID = UUID("22222222-2222-4222-8222-222222222222")
TECHNICIAN_ID = UUID("33333333-3333-4333-8333-333333333333")
STANDARD_JOB_ID = UUID("44444444-4444-4444-8444-444444444444")
WATER_JOB_ID = UUID("55555555-5555-4555-8555-555555555555")
WORK_ORDER_ID = UUID("66666666-6666-4666-8666-666666666666")
STANDARD_VISIT_ID = UUID("77777777-7777-4777-8777-777777777777")
WATER_VISIT_ID = UUID("88888888-8888-4888-8888-888888888888")
ROUTE_ASSIGNMENT_ID = UUID("99999999-9999-4999-8999-999999999999")
BLOCKED_ROUTE_ASSIGNMENT_ID = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
OPEN_REVIEW_ID = UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")
WATER_REVIEW_ID = UUID("cccccccc-cccc-4ccc-8ccc-cccccccccccc")
WATER_EMERGENCY_ID = UUID("dddddddd-dddd-4ddd-8ddd-dddddddddddd")
DISPATCH_EVENT_ID = UUID("eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee")
ADAPTER_EVENT_ID = UUID("ffffffff-ffff-4fff-8fff-ffffffffffff")


@dataclass(frozen=True)
class DashboardDevSeedResult:
    inserted: bool
    record_count: int
    source_system: str
    message: str


@dataclass(frozen=True)
class DashboardDevSeedRecords:
    records: tuple[object, ...]

    @property
    def record_count(self) -> int:
        return len(self.records)


def validate_seed_settings(settings: Settings) -> None:
    database_url = make_url(settings.database_url)
    host = (database_url.host or "").lower()
    password = database_url.password or ""

    if settings.is_production:
        raise RuntimeError("dashboard dev seed refuses to run in production")
    if host not in LOCAL_DATABASE_HOSTS or host == "0.0.0.0":
        raise RuntimeError("dashboard dev seed requires a local PostgreSQL host")
    if ".example." in host or host.startswith("db.example"):
        raise RuntimeError("dashboard dev seed refuses placeholder example hosts")
    if password in PLACEHOLDER_DATABASE_PASSWORDS:
        raise RuntimeError("dashboard dev seed refuses placeholder database credentials")


def build_dashboard_dev_seed_records(
    *,
    now: datetime | None = None,
) -> DashboardDevSeedRecords:
    generated_at = now or datetime.now(UTC)
    route_date = date(generated_at.year, generated_at.month, generated_at.day)
    scheduled_start = datetime.combine(route_date, datetime.min.time(), tzinfo=UTC) + timedelta(
        hours=13,
    )
    scheduled_end = scheduled_start + timedelta(hours=2)

    return DashboardDevSeedRecords(
        records=(
            Customer(
                id=CUSTOMER_ID,
                display_name="Module 27 Demo Customer",
                company_name="ACS Local Development Demo",
                phone="555-0100",
                email="demo.customer@example.invalid",
                tags=["demo", "local-dev"],
                notes="Synthetic dashboard seed data. Not production customer data.",
            ),
            Property(
                id=PROPERTY_ID,
                customer_id=CUSTOMER_ID,
                property_name="Module 27 Demo Property",
                street_address="100 Local Dev Way",
                city="Wilmington",
                state="DE",
                postal_code="19801",
                access_notes="Synthetic local dashboard seed location.",
            ),
            Technician(
                id=TECHNICIAN_ID,
                full_name="Module 27 Demo Technician",
                role="technician",
                skills=["standard_cleaning"],
                service_areas=["DE"],
                vehicle_label="Demo Truck 1",
                availability_status="available",
                is_active=True,
            ),
            Job(
                id=STANDARD_JOB_ID,
                customer_id=CUSTOMER_ID,
                property_id=PROPERTY_ID,
                job_type="standard",
                status="awaiting_dispatch",
                priority="normal",
                requested_date=route_date,
                scheduled_date=route_date,
                source_system=SEED_SOURCE_SYSTEM,
                source_event_id="module27-standard-job",
                description="Synthetic standard job for local dashboard verification.",
            ),
            Job(
                id=WATER_JOB_ID,
                customer_id=CUSTOMER_ID,
                property_id=PROPERTY_ID,
                job_type="water_emergency",
                status="active",
                priority="urgent",
                requested_date=route_date,
                scheduled_date=route_date,
                source_system=SEED_SOURCE_SYSTEM,
                source_event_id="module27-water-emergency-job",
                description="Synthetic Water Emergency record for separation verification.",
            ),
            WorkOrder(
                id=WORK_ORDER_ID,
                job_id=STANDARD_JOB_ID,
                assigned_technician_id=TECHNICIAN_ID,
                work_order_number="MOD27-DEMO-WO-001",
                status="generated",
                dispatch_status="not_dispatched",
                audit_correlation_id=SEED_AUDIT_CORRELATION_ID,
                service_instructions="Synthetic local verification work order.",
                generation_snapshot={"source": SEED_SOURCE_SYSTEM, "production_data": False},
            ),
            Visit(
                id=STANDARD_VISIT_ID,
                job_id=STANDARD_JOB_ID,
                work_order_id=WORK_ORDER_ID,
                technician_id=TECHNICIAN_ID,
                visit_type="standard",
                status="dispatch_ready",
                audit_correlation_id=SEED_AUDIT_CORRELATION_ID,
                scheduled_start_at=scheduled_start,
                scheduled_end_at=scheduled_end,
                notes="Synthetic dispatch-ready visit for read-only dashboard verification.",
                dispatch_readiness_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "dispatch_execution": "not_executed",
                },
            ),
            Visit(
                id=WATER_VISIT_ID,
                job_id=WATER_JOB_ID,
                visit_type="water_emergency",
                status="review_required",
                audit_correlation_id="module27-dashboard-demo-water",
                notes="Synthetic Water Emergency visit kept separated from standard dispatch.",
            ),
            RouteAssignment(
                id=ROUTE_ASSIGNMENT_ID,
                route_date=route_date,
                technician_id=TECHNICIAN_ID,
                job_id=STANDARD_JOB_ID,
                visit_id=STANDARD_VISIT_ID,
                route_order=1,
                region="DE",
                time_window="PM",
                status="dispatched",
                route_group_key=f"DE-PM-{route_date.isoformat()}",
                audit_correlation_id=SEED_AUDIT_CORRELATION_ID,
                dispatch_authorization_snapshot={"authorized_for_dispatch": True},
                dispatch_execution_state="dispatched",
                dispatched_at=scheduled_start - timedelta(hours=1),
                external_adapter_state="awaiting_external_execution",
                external_adapter_prepared_at=scheduled_start - timedelta(minutes=55),
                external_execution_state="awaiting_external_confirmation",
                external_execution_completed_at=scheduled_start - timedelta(minutes=50),
                external_confirmation_state="failed",
                external_failure_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "provider_execution": "not_executed",
                },
                external_confirmation_failed_at=scheduled_start - timedelta(minutes=45),
                retry_preparation_snapshot={"retry_execution": "not_executed"},
                retry_prepared_at=scheduled_start - timedelta(minutes=40),
                dispatch_reconciliation_state="reconciliation_required",
                dispatch_divergence_snapshot={"synthetic_divergence": True},
                dispatch_mismatch_snapshot={"mismatch_count": 1},
                replay_recovery_state="replay_prepared",
                replay_preparation_snapshot={"replay_execution": "not_executed"},
                replay_prepared_at=scheduled_start - timedelta(minutes=35),
                governance_state="operator_approved",
                governance_approved_at=scheduled_start - timedelta(minutes=30),
                accountability_state="escalation_required",
                escalation_required_at=scheduled_start - timedelta(minutes=25),
            ),
            RouteAssignment(
                id=BLOCKED_ROUTE_ASSIGNMENT_ID,
                route_date=route_date,
                job_id=STANDARD_JOB_ID,
                visit_id=STANDARD_VISIT_ID,
                route_order=2,
                region="DE",
                time_window="PM",
                status="blocked",
                audit_correlation_id="module27-dashboard-demo-blocked",
                dispatch_execution_state="blocked",
                dispatch_reconciliation_state="reconciliation_blocked",
                dispatch_reconciliation_blocker_snapshot={"blocked": True},
                replay_recovery_state="replay_blocked",
                replay_blocker_snapshot={"blocked": True},
                governance_state="governance_blocked",
                governance_blocker_snapshot={"blocked": True},
                accountability_state="accountability_blocked",
                escalation_blocker_snapshot={"blocked": True},
            ),
            ReviewItem(
                id=OPEN_REVIEW_ID,
                entity_type="intake_processing_record",
                reason_code="module27_demo_manual_review",
                status="open",
                severity="critical",
                source_system=SEED_SOURCE_SYSTEM,
                source_id="module27-open-review",
                confidence_score=64.0,
                audit_correlation_id=SEED_AUDIT_CORRELATION_ID,
                recommended_action="Review synthetic demo blocker before dispatch.",
            ),
            ReviewItem(
                id=WATER_REVIEW_ID,
                job_id=WATER_JOB_ID,
                visit_id=WATER_VISIT_ID,
                entity_type="water_emergency",
                reason_code="module27_demo_water_emergency_review",
                status="deferred",
                severity="high",
                source_system=SEED_SOURCE_SYSTEM,
                source_id="module27-water-review",
                confidence_score=70.0,
                audit_correlation_id="module27-dashboard-demo-water",
                recommended_action="Keep Water Emergency separated from standard dispatch.",
            ),
            IntakeProcessingRecord(
                source_system=SEED_SOURCE_SYSTEM,
                source_id="module27-approved-intake",
                lifecycle_state="approved_for_dispatch",
                orchestration_state="eligible",
                audit_correlation_id=SEED_AUDIT_CORRELATION_ID,
                dispatch_eligible=True,
                deterministic_evidence_snapshot={"production_data": False},
            ),
            IntakeProcessingRecord(
                source_system=SEED_SOURCE_SYSTEM,
                source_id="module27-blocked-intake",
                lifecycle_state="blocked",
                orchestration_state="blocked",
                review_item_id=OPEN_REVIEW_ID,
                audit_correlation_id="module27-dashboard-demo-blocked",
                requires_review=True,
                blocked=True,
                unsafe=True,
                deterministic_evidence_snapshot={"reason": "synthetic_demo_blocker"},
            ),
            IntakeProcessingRecord(
                source_system=SEED_SOURCE_SYSTEM,
                source_id="module27-water-intake",
                lifecycle_state="review_required",
                orchestration_state="water_emergency_separated",
                review_item_id=WATER_REVIEW_ID,
                audit_correlation_id="module27-dashboard-demo-water",
                requires_review=True,
                water_emergency_separated=True,
                deterministic_evidence_snapshot={"water_emergency_separated": True},
            ),
            WaterEmergency(
                id=WATER_EMERGENCY_ID,
                job_id=WATER_JOB_ID,
                status="DRYING_IN_PROGRESS",
                drying_stage="monitoring",
                next_required_action="Synthetic review of drying progress.",
                equipment_onsite=True,
                moisture_tracking_required=True,
                opened_at=scheduled_start - timedelta(hours=4),
                notes="Synthetic Water Emergency seed data. Not production data.",
            ),
            OperationalEventRecord(
                id=DISPATCH_EVENT_ID,
                occurred_at=scheduled_start - timedelta(hours=1),
                recorded_at=scheduled_start - timedelta(hours=1),
                event_type="dispatch_execution.dispatched",
                event_state="dispatched",
                entity_type="route_assignment",
                entity_id=ROUTE_ASSIGNMENT_ID,
                route_assignment_id=ROUTE_ASSIGNMENT_ID,
                visit_id=STANDARD_VISIT_ID,
                work_order_id=WORK_ORDER_ID,
                job_id=STANDARD_JOB_ID,
                technician_id=TECHNICIAN_ID,
                audit_correlation_id=SEED_AUDIT_CORRELATION_ID,
                previous_state="authorized",
                new_state="dispatched",
                event_fingerprint="module27-dashboard-demo-dispatched",
                is_immutable=True,
                event_snapshot={"source": SEED_SOURCE_SYSTEM, "production_data": False},
            ),
            OperationalEventRecord(
                id=ADAPTER_EVENT_ID,
                occurred_at=scheduled_start - timedelta(minutes=55),
                recorded_at=scheduled_start - timedelta(minutes=55),
                event_type="external_adapter.prepared",
                event_state="awaiting_external_execution",
                entity_type="route_assignment",
                entity_id=ROUTE_ASSIGNMENT_ID,
                route_assignment_id=ROUTE_ASSIGNMENT_ID,
                visit_id=STANDARD_VISIT_ID,
                work_order_id=WORK_ORDER_ID,
                job_id=STANDARD_JOB_ID,
                technician_id=TECHNICIAN_ID,
                audit_correlation_id=SEED_AUDIT_CORRELATION_ID,
                previous_state="dispatched",
                new_state="awaiting_external_execution",
                event_fingerprint="module27-dashboard-demo-adapter-prepared",
                is_immutable=True,
                event_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "external_execution": "not_executed",
                },
            ),
        ),
    )


def seed_dashboard_dev_data(session: Session) -> DashboardDevSeedResult:
    existing_seed = session.scalar(
        select(IntakeProcessingRecord.id)
        .where(IntakeProcessingRecord.source_system == SEED_SOURCE_SYSTEM)
        .limit(1),
    )
    if existing_seed is not None:
        return DashboardDevSeedResult(
            inserted=False,
            record_count=0,
            source_system=SEED_SOURCE_SYSTEM,
            message="dashboard dev seed data already exists",
        )

    records = build_dashboard_dev_seed_records()
    session.add_all(records.records)
    return DashboardDevSeedResult(
        inserted=True,
        record_count=records.record_count,
        source_system=SEED_SOURCE_SYSTEM,
        message="dashboard dev seed data inserted",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Seed synthetic read-only dashboard data into a local ACS FSM dev database.",
    )
    parser.add_argument(
        "--confirm-dev-seed",
        action="store_true",
        help="Required safety acknowledgement for local synthetic seed data.",
    )
    args = parser.parse_args()

    if not args.confirm_dev_seed:
        parser.error("--confirm-dev-seed is required")

    settings = Settings()
    validate_seed_settings(settings)

    engine = create_engine(
        settings.database_url,
        echo=settings.database_echo,
        pool_pre_ping=settings.database_pool_pre_ping,
    )
    with Session(engine) as session:
        try:
            result = seed_dashboard_dev_data(session)
            session.commit()
        except Exception:
            session.rollback()
            raise

    print(json.dumps(asdict(result), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
