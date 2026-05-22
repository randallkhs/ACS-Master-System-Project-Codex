from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from sqlalchemy import create_engine, select
from sqlalchemy.engine import make_url
from sqlalchemy.inspection import inspect
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
SEED_SCENARIO_VERSION = "module37_live_dashboard_seed"
SEED_SCENARIO_LABELS = (
    "standard_dispatch_ready",
    "manual_review_blocked",
    "external_confirmation_failed",
    "external_confirmation_succeeded",
    "reconciliation_recovery_required",
    "governance_accountability_required",
    "water_emergency_separated",
    "water_emergency_closed",
    "water_emergency_next_step_readiness",
    "water_emergency_missing_data_blocked",
    "water_emergency_ready_for_close_review",
    "water_emergency_operator_queue",
    "water_emergency_visit_followup_needed",
    "water_emergency_equipment_review_needed",
    "water_emergency_monitoring",
    "water_emergency_aging_newly_opened",
    "water_emergency_followup_due",
    "water_emergency_followup_overdue",
    "water_emergency_stale_evidence",
    "water_emergency_unknown_timing",
)

CUSTOMER_ID = UUID("11111111-1111-4111-8111-111111111111")
COMMERCIAL_CUSTOMER_ID = UUID("11111111-2222-4111-8111-111111111111")
PROPERTY_ID = UUID("22222222-2222-4222-8222-222222222222")
COMMERCIAL_PROPERTY_ID = UUID("22222222-3333-4222-8222-222222222222")
TECHNICIAN_ID = UUID("33333333-3333-4333-8333-333333333333")
SECONDARY_TECHNICIAN_ID = UUID("33333333-4444-4333-8333-333333333333")
STANDARD_JOB_ID = UUID("44444444-4444-4444-8444-444444444444")
WATER_JOB_ID = UUID("55555555-5555-4555-8555-555555555555")
READY_JOB_ID = UUID("44444444-5555-4444-8444-444444444444")
CONFIRMED_JOB_ID = UUID("44444444-6666-4444-8444-444444444444")
RECOVERY_JOB_ID = UUID("44444444-7777-4444-8444-444444444444")
CLOSED_WATER_JOB_ID = UUID("55555555-8888-4555-8555-555555555555")
MISSING_WATER_JOB_ID = UUID("55555555-9999-4555-8555-555555555555")
READY_CLOSE_WATER_JOB_ID = UUID("55555555-aaaa-4555-8555-555555555555")
FOLLOWUP_WATER_JOB_ID = UUID("55555555-bbbb-4555-8555-555555555555")
EQUIPMENT_REVIEW_WATER_JOB_ID = UUID("55555555-cccc-4555-8555-555555555555")
MONITORING_WATER_JOB_ID = UUID("55555555-dddd-4555-8555-555555555555")
NEWLY_OPENED_WATER_JOB_ID = UUID("55555555-eeee-4555-8555-555555555555")
STALE_EVIDENCE_WATER_JOB_ID = UUID("55555555-ffff-4555-8555-555555555555")
WORK_ORDER_ID = UUID("66666666-6666-4666-8666-666666666666")
READY_WORK_ORDER_ID = UUID("66666666-7777-4666-8666-666666666666")
CONFIRMED_WORK_ORDER_ID = UUID("66666666-8888-4666-8666-666666666666")
RECOVERY_WORK_ORDER_ID = UUID("66666666-9999-4666-8666-666666666666")
WATER_WORK_ORDER_ID = UUID("66666666-abcd-4666-8666-666666666666")
READY_CLOSE_WATER_WORK_ORDER_ID = UUID("66666666-bbbb-4666-8666-666666666666")
FOLLOWUP_WATER_WORK_ORDER_ID = UUID("66666666-cccc-4666-8666-666666666666")
EQUIPMENT_REVIEW_WATER_WORK_ORDER_ID = UUID("66666666-dddd-4666-8666-666666666666")
MONITORING_WATER_WORK_ORDER_ID = UUID("66666666-eeee-4666-8666-666666666666")
NEWLY_OPENED_WATER_WORK_ORDER_ID = UUID("66666666-ffff-4666-8666-666666666666")
STALE_EVIDENCE_WATER_WORK_ORDER_ID = UUID("66666666-1111-4666-8666-777777777777")
STANDARD_VISIT_ID = UUID("77777777-7777-4777-8777-777777777777")
WATER_VISIT_ID = UUID("88888888-8888-4888-8888-888888888888")
WATER_FOLLOWUP_VISIT_ID = UUID("88888888-9999-4888-8888-888888888888")
READY_CLOSE_WATER_VISIT_ID = UUID("88888888-aaaa-4888-8888-888888888888")
FOLLOWUP_WATER_VISIT_ID = UUID("88888888-bbbb-4888-8888-888888888888")
EQUIPMENT_REVIEW_WATER_VISIT_ID = UUID("88888888-cccc-4888-8888-888888888888")
MONITORING_WATER_VISIT_ID = UUID("88888888-dddd-4888-8888-888888888888")
STALE_EVIDENCE_WATER_VISIT_ID = UUID("88888888-eeee-4888-8888-888888888888")
READY_VISIT_ID = UUID("77777777-8888-4777-8777-777777777777")
CONFIRMED_VISIT_ID = UUID("77777777-9999-4777-8777-777777777777")
RECOVERY_VISIT_ID = UUID("77777777-aaaa-4777-8777-777777777777")
ROUTE_ASSIGNMENT_ID = UUID("99999999-9999-4999-8999-999999999999")
BLOCKED_ROUTE_ASSIGNMENT_ID = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
READY_ROUTE_ASSIGNMENT_ID = UUID("99999999-aaaa-4999-8999-999999999999")
CONFIRMED_ROUTE_ASSIGNMENT_ID = UUID("99999999-bbbb-4999-8999-999999999999")
RECOVERY_ROUTE_ASSIGNMENT_ID = UUID("99999999-cccc-4999-8999-999999999999")
OPEN_REVIEW_ID = UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")
WATER_REVIEW_ID = UUID("cccccccc-cccc-4ccc-8ccc-cccccccccccc")
WATER_OPEN_REVIEW_ID = UUID("cccccccc-dddd-4ccc-8ccc-cccccccccccc")
WATER_ARCHIVED_REVIEW_ID = UUID("cccccccc-eeee-4ccc-8ccc-cccccccccccc")
RESOLVED_REVIEW_ID = UUID("bbbbbbbb-cccc-4bbb-8bbb-bbbbbbbbbbbb")
ARCHIVED_REVIEW_ID = UUID("bbbbbbbb-dddd-4bbb-8bbb-bbbbbbbbbbbb")
RECOVERY_REVIEW_ID = UUID("bbbbbbbb-eeee-4bbb-8bbb-bbbbbbbbbbbb")
WATER_EMERGENCY_ID = UUID("dddddddd-dddd-4ddd-8ddd-dddddddddddd")
CLOSED_WATER_EMERGENCY_ID = UUID("dddddddd-eeee-4ddd-8ddd-dddddddddddd")
MISSING_WATER_EMERGENCY_ID = UUID("dddddddd-ffff-4ddd-8ddd-dddddddddddd")
READY_CLOSE_WATER_EMERGENCY_ID = UUID("dddddddd-1111-4ddd-8ddd-dddddddddddd")
FOLLOWUP_WATER_EMERGENCY_ID = UUID("dddddddd-2222-4ddd-8ddd-dddddddddddd")
EQUIPMENT_REVIEW_WATER_EMERGENCY_ID = UUID("dddddddd-3333-4ddd-8ddd-dddddddddddd")
MONITORING_WATER_EMERGENCY_ID = UUID("dddddddd-4444-4ddd-8ddd-dddddddddddd")
NEWLY_OPENED_WATER_EMERGENCY_ID = UUID("dddddddd-5555-4ddd-8ddd-dddddddddddd")
STALE_EVIDENCE_WATER_EMERGENCY_ID = UUID("dddddddd-6666-4ddd-8ddd-dddddddddddd")
DISPATCH_EVENT_ID = UUID("eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee")
ADAPTER_EVENT_ID = UUID("ffffffff-ffff-4fff-8fff-ffffffffffff")
CONFIRMATION_EVENT_ID = UUID("eeeeeeee-1111-4eee-8eee-eeeeeeeeeeee")
READY_EVENT_ID = UUID("eeeeeeee-2222-4eee-8eee-eeeeeeeeeeee")
EXTERNAL_CONFIRMED_EVENT_ID = UUID("eeeeeeee-3333-4eee-8eee-eeeeeeeeeeee")
RECOVERY_EVENT_ID = UUID("eeeeeeee-4444-4eee-8eee-eeeeeeeeeeee")
GOVERNANCE_EVENT_ID = UUID("eeeeeeee-5555-4eee-8eee-eeeeeeeeeeee")
INCIDENT_EVENT_ID = UUID("eeeeeeee-6666-4eee-8eee-eeeeeeeeeeee")
WATER_EMERGENCY_EVENT_ID = UUID("eeeeeeee-7777-4eee-8eee-eeeeeeeeeeee")
WATER_DRYING_CHECK_EVENT_ID = UUID("eeeeeeee-8888-4eee-8eee-eeeeeeeeeeee")
WATER_EXCEPTION_EVENT_ID = UUID("eeeeeeee-9999-4eee-8eee-eeeeeeeeeeee")
READY_CLOSE_WATER_EVENT_ID = UUID("eeeeeeee-aaaa-4eee-8eee-eeeeeeeeeeee")
FOLLOWUP_WATER_EVENT_ID = UUID("eeeeeeee-bbbb-4eee-8eee-eeeeeeeeeeee")
EQUIPMENT_REVIEW_WATER_EVENT_ID = UUID("eeeeeeee-cccc-4eee-8eee-eeeeeeeeeeee")
MONITORING_WATER_EVENT_ID = UUID("eeeeeeee-dddd-4eee-8eee-eeeeeeeeeeee")
NEWLY_OPENED_WATER_EVENT_ID = UUID("eeeeeeee-1212-4eee-8eee-eeeeeeeeeeee")
STALE_EVIDENCE_WATER_EVENT_ID = UUID("eeeeeeee-ffff-4eee-8eee-eeeeeeeeeeee")


@dataclass(frozen=True)
class DashboardDevSeedResult:
    inserted: bool
    record_count: int
    inserted_count: int
    updated_count: int
    scenario_count: int
    scenario_labels: tuple[str, ...]
    source_system: str
    message: str


@dataclass(frozen=True)
class DashboardDevSeedRecords:
    records: tuple[object, ...]
    scenario_labels: tuple[str, ...]

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
    morning_start = scheduled_start - timedelta(hours=4)
    morning_end = morning_start + timedelta(hours=2)
    recovery_start = scheduled_start + timedelta(hours=3)
    recovery_end = recovery_start + timedelta(hours=2)

    return DashboardDevSeedRecords(
        scenario_labels=SEED_SCENARIO_LABELS,
        records=(
            Customer(
                id=CUSTOMER_ID,
                display_name="Module 29 Demo Residential Account",
                company_name="ACS Local Development Demo",
                phone="555-0100",
                email="demo.customer@example.invalid",
                tags=["demo", "local-dev"],
                notes="Synthetic dashboard seed data. Not production customer data.",
            ),
            Customer(
                id=COMMERCIAL_CUSTOMER_ID,
                display_name="Module 29 Demo Property Manager",
                company_name="Synthetic Facilities Group",
                phone="555-0199",
                email="demo.manager@example.invalid",
                tags=["demo", "commercial", "local-dev"],
                notes="Synthetic commercial account for local dashboard data quality checks.",
            ),
            Property(
                id=PROPERTY_ID,
                customer_id=CUSTOMER_ID,
                property_name="Module 29 Demo Residence",
                street_address="100 Local Dev Way",
                city="Wilmington",
                state="DE",
                postal_code="19801",
                access_notes="Synthetic local dashboard seed location.",
            ),
            Property(
                id=COMMERCIAL_PROPERTY_ID,
                customer_id=COMMERCIAL_CUSTOMER_ID,
                property_name="Synthetic Office Park",
                street_address="200 Synthetic Service Blvd",
                city="Dover",
                state="DE",
                postal_code="00000",
                access_notes="Clearly fake property for local dashboard verification only.",
            ),
            Technician(
                id=TECHNICIAN_ID,
                full_name="Module 29 Demo Technician A",
                role="technician",
                skills=["standard_cleaning"],
                service_areas=["DE"],
                vehicle_label="Demo Truck 1",
                availability_status="available",
                is_active=True,
            ),
            Technician(
                id=SECONDARY_TECHNICIAN_ID,
                full_name="Module 29 Demo Technician B",
                role="technician",
                skills=["standard_cleaning", "water_emergency_support"],
                service_areas=["DE", "MD"],
                vehicle_label="Demo Truck 2",
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
                id=READY_JOB_ID,
                customer_id=COMMERCIAL_CUSTOMER_ID,
                property_id=COMMERCIAL_PROPERTY_ID,
                job_type="standard",
                status="awaiting_dispatch",
                priority="normal",
                requested_date=route_date,
                scheduled_date=route_date,
                source_system=SEED_SOURCE_SYSTEM,
                source_event_id="module29-dispatch-ready-job",
                description="Synthetic dispatch-ready job awaiting internal execution.",
            ),
            Job(
                id=CONFIRMED_JOB_ID,
                customer_id=COMMERCIAL_CUSTOMER_ID,
                property_id=COMMERCIAL_PROPERTY_ID,
                job_type="standard",
                status="dispatched",
                priority="normal",
                requested_date=route_date,
                scheduled_date=route_date,
                source_system=SEED_SOURCE_SYSTEM,
                source_event_id="module29-confirmed-job",
                description="Synthetic job with confirmed external execution evidence.",
            ),
            Job(
                id=RECOVERY_JOB_ID,
                customer_id=COMMERCIAL_CUSTOMER_ID,
                property_id=COMMERCIAL_PROPERTY_ID,
                job_type="standard",
                status="review_required",
                priority="high",
                requested_date=route_date,
                scheduled_date=route_date,
                source_system=SEED_SOURCE_SYSTEM,
                source_event_id="module29-recovery-job",
                description=(
                    "Synthetic job requiring recovery, governance, and accountability review."
                ),
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
            Job(
                id=CLOSED_WATER_JOB_ID,
                customer_id=COMMERCIAL_CUSTOMER_ID,
                property_id=COMMERCIAL_PROPERTY_ID,
                job_type="water_emergency",
                status="closed",
                priority="urgent",
                requested_date=route_date,
                scheduled_date=route_date,
                source_system=SEED_SOURCE_SYSTEM,
                source_event_id="module29-closed-water-emergency-job",
                description=(
                    "Synthetic closed Water Emergency scenario for open/closed count checks."
                ),
            ),
            Job(
                id=MISSING_WATER_JOB_ID,
                customer_id=CUSTOMER_ID,
                property_id=PROPERTY_ID,
                job_type="water_emergency",
                status="review_required",
                priority="urgent",
                requested_date=route_date,
                scheduled_date=route_date,
                source_system=SEED_SOURCE_SYSTEM,
                source_event_id="module35-missing-water-emergency-job",
                description=(
                    "Synthetic Water Emergency with missing detail evidence for next-step "
                    "readiness checks."
                ),
            ),
            Job(
                id=READY_CLOSE_WATER_JOB_ID,
                customer_id=COMMERCIAL_CUSTOMER_ID,
                property_id=COMMERCIAL_PROPERTY_ID,
                job_type="water_emergency",
                status="ready_for_close_review",
                priority="urgent",
                requested_date=route_date,
                scheduled_date=route_date,
                source_system=SEED_SOURCE_SYSTEM,
                source_event_id="module35-ready-close-water-emergency-job",
                description=("Synthetic Water Emergency ready for close-review visibility only."),
            ),
            Job(
                id=FOLLOWUP_WATER_JOB_ID,
                customer_id=CUSTOMER_ID,
                property_id=PROPERTY_ID,
                job_type="water_emergency",
                status="active",
                priority="urgent",
                requested_date=route_date,
                scheduled_date=route_date,
                source_system=SEED_SOURCE_SYSTEM,
                source_event_id="module36-followup-water-emergency-job",
                description=("Synthetic Water Emergency needing visit follow-up queue visibility."),
            ),
            Job(
                id=EQUIPMENT_REVIEW_WATER_JOB_ID,
                customer_id=COMMERCIAL_CUSTOMER_ID,
                property_id=COMMERCIAL_PROPERTY_ID,
                job_type="water_emergency",
                status="active",
                priority="urgent",
                requested_date=route_date,
                scheduled_date=route_date,
                source_system=SEED_SOURCE_SYSTEM,
                source_event_id="module36-equipment-review-water-emergency-job",
                description=(
                    "Synthetic Water Emergency needing equipment-review queue visibility."
                ),
            ),
            Job(
                id=MONITORING_WATER_JOB_ID,
                customer_id=CUSTOMER_ID,
                property_id=PROPERTY_ID,
                job_type="water_emergency",
                status="active",
                priority="urgent",
                requested_date=route_date,
                scheduled_date=route_date,
                source_system=SEED_SOURCE_SYSTEM,
                source_event_id="module36-monitoring-water-emergency-job",
                description=(
                    "Synthetic Water Emergency monitoring state for operator queue visibility."
                ),
            ),
            Job(
                id=NEWLY_OPENED_WATER_JOB_ID,
                customer_id=CUSTOMER_ID,
                property_id=PROPERTY_ID,
                job_type="water_emergency",
                status="active",
                priority="urgent",
                requested_date=route_date,
                scheduled_date=route_date,
                source_system=SEED_SOURCE_SYSTEM,
                source_event_id="module37-newly-opened-water-emergency-job",
                description=(
                    "Synthetic newly opened Water Emergency for aging visibility. No "
                    "production data."
                ),
            ),
            Job(
                id=STALE_EVIDENCE_WATER_JOB_ID,
                customer_id=COMMERCIAL_CUSTOMER_ID,
                property_id=COMMERCIAL_PROPERTY_ID,
                job_type="water_emergency",
                status="active",
                priority="urgent",
                requested_date=route_date,
                scheduled_date=route_date,
                source_system=SEED_SOURCE_SYSTEM,
                source_event_id="module37-stale-evidence-water-emergency-job",
                description=(
                    "Synthetic Water Emergency with stale evidence for timing visibility. "
                    "No production data."
                ),
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
            WorkOrder(
                id=READY_WORK_ORDER_ID,
                job_id=READY_JOB_ID,
                assigned_technician_id=SECONDARY_TECHNICIAN_ID,
                work_order_number="MOD29-DEMO-WO-READY",
                status="generated",
                dispatch_status="awaiting_dispatch_execution",
                audit_correlation_id="module29-dashboard-demo-ready",
                service_instructions="Synthetic work order ready for dispatch execution.",
                generation_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "scenario": "standard_dispatch_ready",
                    "production_data": False,
                },
            ),
            WorkOrder(
                id=CONFIRMED_WORK_ORDER_ID,
                job_id=CONFIRMED_JOB_ID,
                assigned_technician_id=TECHNICIAN_ID,
                work_order_number="MOD29-DEMO-WO-CONFIRMED",
                status="dispatched",
                dispatch_status="externally_confirmed",
                audit_correlation_id="module29-dashboard-demo-confirmed",
                service_instructions="Synthetic work order with confirmed external execution.",
                generation_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "scenario": "external_confirmation_succeeded",
                    "production_data": False,
                },
            ),
            WorkOrder(
                id=RECOVERY_WORK_ORDER_ID,
                job_id=RECOVERY_JOB_ID,
                assigned_technician_id=SECONDARY_TECHNICIAN_ID,
                work_order_number="MOD29-DEMO-WO-RECOVERY",
                status="review_required",
                dispatch_status="recovery_required",
                audit_correlation_id="module29-dashboard-demo-recovery",
                service_instructions=(
                    "Synthetic recovery workflow evidence. No external action executed."
                ),
                generation_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "scenario": "reconciliation_recovery_required",
                    "production_data": False,
                },
            ),
            WorkOrder(
                id=WATER_WORK_ORDER_ID,
                job_id=WATER_JOB_ID,
                assigned_technician_id=SECONDARY_TECHNICIAN_ID,
                work_order_number="MOD33-DEMO-WO-WATER",
                status="generated",
                dispatch_status="water_emergency_separated",
                audit_correlation_id="module33-dashboard-demo-water-equipment",
                service_instructions=(
                    "Synthetic Water Emergency work-order context for read-only "
                    "equipment visibility."
                ),
                required_equipment_notes=(
                    "Synthetic-only equipment context: air movers, dehumidifier, "
                    "and moisture meter placeholders."
                ),
                generation_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "scenario": "water_emergency_separated",
                    "production_data": False,
                    "water_emergency_execution": "not_executed",
                },
            ),
            WorkOrder(
                id=READY_CLOSE_WATER_WORK_ORDER_ID,
                job_id=READY_CLOSE_WATER_JOB_ID,
                assigned_technician_id=SECONDARY_TECHNICIAN_ID,
                work_order_number="MOD35-DEMO-WO-WATER-CLOSE",
                status="completed",
                dispatch_status="water_emergency_separated",
                audit_correlation_id="module35-dashboard-demo-water-close-review",
                service_instructions=(
                    "Synthetic Water Emergency close-review readiness context. "
                    "No close action is executed."
                ),
                generation_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "scenario": "water_emergency_ready_for_close_review",
                    "production_data": False,
                    "water_emergency_execution": "not_executed",
                },
            ),
            WorkOrder(
                id=FOLLOWUP_WATER_WORK_ORDER_ID,
                job_id=FOLLOWUP_WATER_JOB_ID,
                assigned_technician_id=SECONDARY_TECHNICIAN_ID,
                work_order_number="MOD36-DEMO-WO-WATER-FOLLOWUP",
                status="generated",
                dispatch_status="water_emergency_separated",
                audit_correlation_id="module36-dashboard-demo-water-followup-needed",
                service_instructions=(
                    "Synthetic Water Emergency follow-up context. No visit is scheduled here."
                ),
                generation_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "scenario": "water_emergency_visit_followup_needed",
                    "production_data": False,
                    "water_emergency_execution": "not_executed",
                },
            ),
            WorkOrder(
                id=EQUIPMENT_REVIEW_WATER_WORK_ORDER_ID,
                job_id=EQUIPMENT_REVIEW_WATER_JOB_ID,
                assigned_technician_id=SECONDARY_TECHNICIAN_ID,
                work_order_number="MOD36-DEMO-WO-WATER-EQUIPMENT",
                status="generated",
                dispatch_status="water_emergency_separated",
                audit_correlation_id="module36-dashboard-demo-water-equipment-review",
                service_instructions=(
                    "Synthetic Water Emergency equipment-review context without final "
                    "inventory taxonomy."
                ),
                generation_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "scenario": "water_emergency_equipment_review_needed",
                    "production_data": False,
                    "water_emergency_execution": "not_executed",
                },
            ),
            WorkOrder(
                id=MONITORING_WATER_WORK_ORDER_ID,
                job_id=MONITORING_WATER_JOB_ID,
                assigned_technician_id=SECONDARY_TECHNICIAN_ID,
                work_order_number="MOD36-DEMO-WO-WATER-MONITORING",
                status="generated",
                dispatch_status="water_emergency_separated",
                audit_correlation_id="module36-dashboard-demo-water-monitoring",
                service_instructions=(
                    "Synthetic Water Emergency monitoring context for queue visibility only."
                ),
                generation_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "scenario": "water_emergency_monitoring",
                    "production_data": False,
                    "water_emergency_execution": "not_executed",
                },
            ),
            WorkOrder(
                id=NEWLY_OPENED_WATER_WORK_ORDER_ID,
                job_id=NEWLY_OPENED_WATER_JOB_ID,
                assigned_technician_id=SECONDARY_TECHNICIAN_ID,
                work_order_number="MOD37-DEMO-WO-WATER-NEW",
                status="generated",
                dispatch_status="water_emergency_separated",
                audit_correlation_id="module37-dashboard-demo-water-newly-opened",
                service_instructions=(
                    "Synthetic newly opened Water Emergency context for read-only aging visibility."
                ),
                generation_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "scenario": "water_emergency_aging_newly_opened",
                    "production_data": False,
                    "water_emergency_execution": "not_executed",
                },
            ),
            WorkOrder(
                id=STALE_EVIDENCE_WATER_WORK_ORDER_ID,
                job_id=STALE_EVIDENCE_WATER_JOB_ID,
                assigned_technician_id=SECONDARY_TECHNICIAN_ID,
                work_order_number="MOD37-DEMO-WO-WATER-STALE",
                status="generated",
                dispatch_status="water_emergency_separated",
                audit_correlation_id="module37-dashboard-demo-water-stale",
                service_instructions=(
                    "Synthetic stale Water Emergency evidence context. No workflow action "
                    "is executed."
                ),
                generation_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "scenario": "water_emergency_stale_evidence",
                    "production_data": False,
                    "water_emergency_execution": "not_executed",
                },
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
                id=READY_VISIT_ID,
                job_id=READY_JOB_ID,
                work_order_id=READY_WORK_ORDER_ID,
                technician_id=SECONDARY_TECHNICIAN_ID,
                visit_type="standard",
                status="dispatch_ready",
                audit_correlation_id="module29-dashboard-demo-ready",
                scheduled_start_at=morning_start,
                scheduled_end_at=morning_end,
                notes="Synthetic visit ready for dispatch execution but not dispatched.",
                dispatch_readiness_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "scenario": "standard_dispatch_ready",
                    "dispatch_execution": "not_executed",
                },
            ),
            Visit(
                id=CONFIRMED_VISIT_ID,
                job_id=CONFIRMED_JOB_ID,
                work_order_id=CONFIRMED_WORK_ORDER_ID,
                technician_id=TECHNICIAN_ID,
                visit_type="standard",
                status="dispatched",
                audit_correlation_id="module29-dashboard-demo-confirmed",
                scheduled_start_at=morning_start + timedelta(hours=2),
                scheduled_end_at=morning_end + timedelta(hours=2),
                notes="Synthetic visit with external confirmation evidence.",
                dispatch_readiness_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "scenario": "external_confirmation_succeeded",
                },
            ),
            Visit(
                id=RECOVERY_VISIT_ID,
                job_id=RECOVERY_JOB_ID,
                work_order_id=RECOVERY_WORK_ORDER_ID,
                technician_id=SECONDARY_TECHNICIAN_ID,
                visit_type="standard",
                status="review_required",
                audit_correlation_id="module29-dashboard-demo-recovery",
                scheduled_start_at=recovery_start,
                scheduled_end_at=recovery_end,
                notes="Synthetic visit blocked for recovery and governance review.",
                dispatch_readiness_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "scenario": "reconciliation_recovery_required",
                    "manual_review_required": True,
                },
            ),
            Visit(
                id=WATER_VISIT_ID,
                job_id=WATER_JOB_ID,
                work_order_id=WATER_WORK_ORDER_ID,
                technician_id=SECONDARY_TECHNICIAN_ID,
                visit_type="water_emergency",
                status="review_required",
                audit_correlation_id="module27-dashboard-demo-water",
                scheduled_start_at=scheduled_start - timedelta(hours=4),
                scheduled_end_at=scheduled_start - timedelta(hours=2, minutes=30),
                notes="Synthetic Water Emergency visit kept separated from standard dispatch.",
            ),
            Visit(
                id=WATER_FOLLOWUP_VISIT_ID,
                job_id=WATER_JOB_ID,
                work_order_id=WATER_WORK_ORDER_ID,
                technician_id=SECONDARY_TECHNICIAN_ID,
                visit_type="water_emergency",
                status="scheduled",
                audit_correlation_id="module33-dashboard-demo-water-followup",
                scheduled_start_at=scheduled_start + timedelta(days=1),
                scheduled_end_at=scheduled_start + timedelta(days=1, hours=1),
                notes=(
                    "Synthetic follow-up Water Emergency drying check for visit-chain "
                    "visibility only."
                ),
            ),
            Visit(
                id=READY_CLOSE_WATER_VISIT_ID,
                job_id=READY_CLOSE_WATER_JOB_ID,
                work_order_id=READY_CLOSE_WATER_WORK_ORDER_ID,
                technician_id=SECONDARY_TECHNICIAN_ID,
                visit_type="water_emergency",
                status="completed",
                audit_correlation_id="module35-dashboard-demo-water-close-review",
                scheduled_start_at=morning_start - timedelta(days=1, hours=1),
                scheduled_end_at=morning_start - timedelta(days=1),
                completed_at=morning_start - timedelta(days=1),
                notes=(
                    "Synthetic completed Water Emergency visit used only for close-review "
                    "readiness visibility."
                ),
            ),
            Visit(
                id=FOLLOWUP_WATER_VISIT_ID,
                job_id=FOLLOWUP_WATER_JOB_ID,
                work_order_id=FOLLOWUP_WATER_WORK_ORDER_ID,
                technician_id=SECONDARY_TECHNICIAN_ID,
                visit_type="water_emergency",
                status="completed",
                audit_correlation_id="module36-dashboard-demo-water-followup-needed",
                scheduled_start_at=morning_start - timedelta(days=1, hours=5),
                scheduled_end_at=morning_start - timedelta(days=1, hours=4),
                completed_at=morning_start - timedelta(days=1, hours=4),
                notes=(
                    "Synthetic completed Water Emergency visit that leaves follow-up "
                    "visibility needed."
                ),
            ),
            Visit(
                id=EQUIPMENT_REVIEW_WATER_VISIT_ID,
                job_id=EQUIPMENT_REVIEW_WATER_JOB_ID,
                work_order_id=EQUIPMENT_REVIEW_WATER_WORK_ORDER_ID,
                technician_id=SECONDARY_TECHNICIAN_ID,
                visit_type="water_emergency",
                status="completed",
                audit_correlation_id="module36-dashboard-demo-water-equipment-review",
                scheduled_start_at=morning_start - timedelta(days=4, hours=4),
                scheduled_end_at=morning_start - timedelta(days=4, hours=3),
                completed_at=morning_start - timedelta(days=4, hours=3),
                notes=("Synthetic Water Emergency visit for equipment-review visibility only."),
            ),
            Visit(
                id=MONITORING_WATER_VISIT_ID,
                job_id=MONITORING_WATER_JOB_ID,
                work_order_id=MONITORING_WATER_WORK_ORDER_ID,
                technician_id=SECONDARY_TECHNICIAN_ID,
                visit_type="water_emergency",
                status="scheduled",
                audit_correlation_id="module36-dashboard-demo-water-monitoring",
                scheduled_start_at=morning_start + timedelta(hours=6),
                scheduled_end_at=morning_start + timedelta(hours=7),
                notes="Synthetic Water Emergency monitoring visit. No action is executed.",
            ),
            Visit(
                id=STALE_EVIDENCE_WATER_VISIT_ID,
                job_id=STALE_EVIDENCE_WATER_JOB_ID,
                work_order_id=STALE_EVIDENCE_WATER_WORK_ORDER_ID,
                technician_id=SECONDARY_TECHNICIAN_ID,
                visit_type="water_emergency",
                status="in_progress",
                audit_correlation_id="module37-dashboard-demo-water-stale",
                arrived_at=morning_start - timedelta(days=4, hours=2),
                notes=(
                    "Synthetic Water Emergency stale evidence visit. No follow-up or "
                    "dispatch action is executed."
                ),
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
                id=READY_ROUTE_ASSIGNMENT_ID,
                route_date=route_date,
                technician_id=SECONDARY_TECHNICIAN_ID,
                job_id=READY_JOB_ID,
                visit_id=READY_VISIT_ID,
                route_order=1,
                region="DE",
                time_window="AM",
                status="authorized",
                route_group_key=f"DE-AM-{route_date.isoformat()}",
                audit_correlation_id="module29-dashboard-demo-ready",
                estimated_arrival_at=morning_start,
                estimated_drive_time_minutes=18,
                dispatch_authorization_snapshot={
                    "authorized_for_dispatch": True,
                    "scenario": "standard_dispatch_ready",
                },
                dispatch_execution_boundary_snapshot={"dispatch_execution": "not_executed"},
                dispatch_execution_state="awaiting_dispatch_execution",
                authorization_prepared_at=morning_start - timedelta(hours=1),
                authorized_for_dispatch_at=morning_start - timedelta(minutes=45),
                deterministic_evidence_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "production_data": False,
                },
            ),
            RouteAssignment(
                id=CONFIRMED_ROUTE_ASSIGNMENT_ID,
                route_date=route_date,
                technician_id=TECHNICIAN_ID,
                job_id=CONFIRMED_JOB_ID,
                visit_id=CONFIRMED_VISIT_ID,
                route_order=2,
                region="DE",
                time_window="AM",
                status="dispatched",
                route_group_key=f"DE-AM-{route_date.isoformat()}",
                audit_correlation_id="module29-dashboard-demo-confirmed",
                estimated_arrival_at=morning_start + timedelta(hours=2),
                estimated_drive_time_minutes=22,
                dispatch_authorization_snapshot={
                    "authorized_for_dispatch": True,
                    "scenario": "external_confirmation_succeeded",
                },
                dispatch_execution_state="dispatched",
                dispatched_at=morning_start + timedelta(hours=1, minutes=45),
                external_adapter_state="awaiting_external_execution",
                external_adapter_prepared_at=morning_start + timedelta(hours=1, minutes=50),
                external_execution_state="awaiting_external_confirmation",
                external_execution_completed_at=morning_start + timedelta(hours=1, minutes=55),
                external_confirmation_state="confirmed",
                external_confirmed_at=morning_start + timedelta(hours=2),
                dispatch_reconciliation_state="consistency_verified",
                dispatch_consistency_snapshot={"consistent": True},
                dispatch_consistency_verified_at=morning_start + timedelta(hours=2, minutes=5),
                replay_recovery_state="not_required",
                governance_state="operator_approved",
                governance_approved_at=morning_start + timedelta(hours=2, minutes=10),
                accountability_state="not_required",
                deterministic_evidence_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "provider_execution": "not_executed",
                    "production_data": False,
                },
            ),
            RouteAssignment(
                id=RECOVERY_ROUTE_ASSIGNMENT_ID,
                route_date=route_date,
                technician_id=SECONDARY_TECHNICIAN_ID,
                job_id=RECOVERY_JOB_ID,
                visit_id=RECOVERY_VISIT_ID,
                route_order=3,
                region="MD",
                time_window="PM",
                status="blocked",
                route_group_key=f"MD-PM-{route_date.isoformat()}",
                audit_correlation_id="module29-dashboard-demo-recovery",
                estimated_arrival_at=recovery_start,
                estimated_drive_time_minutes=44,
                dispatch_authorization_snapshot={
                    "authorized_for_dispatch": False,
                    "scenario": "reconciliation_recovery_required",
                },
                dispatch_execution_state="blocked",
                external_adapter_state="awaiting_external_execution",
                external_adapter_prepared_at=recovery_start - timedelta(minutes=50),
                external_execution_state="failed",
                external_execution_failure_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "provider_execution": "not_executed",
                    "failure_mode": "synthetic_provider_timeout",
                },
                external_execution_failed_at=recovery_start - timedelta(minutes=45),
                dispatch_reconciliation_state="reconciliation_required",
                dispatch_divergence_snapshot={"synthetic_divergence": True},
                dispatch_mismatch_snapshot={
                    "mismatch_count": 2,
                    "mismatches": [
                        {"code": "external_execution_failed"},
                        {"code": "operator_intervention_required"},
                    ],
                },
                dispatch_reconciliation_prepared_at=recovery_start - timedelta(minutes=35),
                replay_recovery_state="rollback_prepared",
                rollback_preparation_snapshot={"rollback_execution": "not_executed"},
                rollback_prepared_at=recovery_start - timedelta(minutes=30),
                governance_state="manual_intervention_required",
                intervention_required_at=recovery_start - timedelta(minutes=25),
                accountability_state="incident_prepared",
                incident_preparation_snapshot={"incident_execution": "not_executed"},
                incident_prepared_at=recovery_start - timedelta(minutes=20),
                deterministic_evidence_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "production_data": False,
                },
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
            ReviewItem(
                id=WATER_OPEN_REVIEW_ID,
                job_id=WATER_JOB_ID,
                visit_id=WATER_FOLLOWUP_VISIT_ID,
                entity_type="water_emergency",
                entity_id=WATER_EMERGENCY_ID,
                reason_code="module34_demo_water_equipment_unknown_blocker",
                status="open",
                severity="critical",
                source_system=SEED_SOURCE_SYSTEM,
                source_id="module34-water-open-review",
                confidence_score=54.0,
                audit_correlation_id="module34-dashboard-demo-water-critical",
                recommended_action=(
                    "Review synthetic Water Emergency equipment and drying evidence; "
                    "no action is executed by the dashboard."
                ),
                review_metadata={
                    "scenario": "water_emergency_separated",
                    "production_data": False,
                    "water_emergency_execution": "not_executed",
                    "visibility_only": True,
                },
            ),
            ReviewItem(
                id=WATER_ARCHIVED_REVIEW_ID,
                job_id=CLOSED_WATER_JOB_ID,
                entity_type="water_emergency",
                entity_id=CLOSED_WATER_EMERGENCY_ID,
                reason_code="module34_demo_water_review_archived_exception",
                status="archived",
                severity="low",
                source_system=SEED_SOURCE_SYSTEM,
                source_id="module34-water-archived-review",
                confidence_score=91.0,
                audit_correlation_id="module34-dashboard-demo-water-archived",
                recommended_action=(
                    "Synthetic archived Water Emergency review for read-only count coverage."
                ),
                operator_decision="archived synthetic local Water Emergency review example",
                resolved_at=morning_start - timedelta(hours=2),
                review_metadata={
                    "scenario": "water_emergency_closed",
                    "production_data": False,
                    "visibility_only": True,
                },
            ),
            ReviewItem(
                id=RECOVERY_REVIEW_ID,
                job_id=RECOVERY_JOB_ID,
                visit_id=RECOVERY_VISIT_ID,
                route_assignment_id=RECOVERY_ROUTE_ASSIGNMENT_ID,
                entity_type="route_assignment",
                entity_id=RECOVERY_ROUTE_ASSIGNMENT_ID,
                reason_code="module29_demo_recovery_review",
                status="open",
                severity="high",
                source_system=SEED_SOURCE_SYSTEM,
                source_id="module29-recovery-review",
                confidence_score=58.0,
                audit_correlation_id="module29-dashboard-demo-recovery",
                recommended_action="Review synthetic recovery evidence before any operator action.",
                review_metadata={
                    "scenario": "reconciliation_recovery_required",
                    "dispatch_blocked": True,
                    "production_data": False,
                },
            ),
            ReviewItem(
                id=RESOLVED_REVIEW_ID,
                entity_type="intake_processing_record",
                reason_code="module29_demo_operator_resolved",
                status="approved",
                severity="low",
                source_system=SEED_SOURCE_SYSTEM,
                source_id="module29-resolved-review",
                confidence_score=96.0,
                audit_correlation_id="module29-dashboard-demo-resolved",
                recommended_action="Synthetic resolved review for dashboard count coverage.",
                operator_decision="approved for future workflow preparation only",
                resolved_at=morning_start - timedelta(minutes=30),
            ),
            ReviewItem(
                id=ARCHIVED_REVIEW_ID,
                entity_type="intake_processing_record",
                reason_code="module29_demo_archived_review",
                status="archived",
                severity="medium",
                source_system=SEED_SOURCE_SYSTEM,
                source_id="module29-archived-review",
                confidence_score=88.0,
                audit_correlation_id="module29-dashboard-demo-archived",
                recommended_action="Synthetic archived review for dashboard count coverage.",
                operator_decision="archived synthetic local example",
                resolved_at=morning_start - timedelta(hours=1),
            ),
            IntakeProcessingRecord(
                source_system=SEED_SOURCE_SYSTEM,
                source_id="module27-approved-intake",
                lifecycle_state="approved_for_dispatch",
                orchestration_state="eligible",
                audit_correlation_id=SEED_AUDIT_CORRELATION_ID,
                dispatch_eligible=True,
                requires_review=False,
                blocked=False,
                unsafe=False,
                water_emergency_separated=False,
                deterministic_evidence_snapshot={"production_data": False},
            ),
            IntakeProcessingRecord(
                source_system=SEED_SOURCE_SYSTEM,
                source_id="module29-ready-intake",
                lifecycle_state="approved_for_dispatch",
                orchestration_state="dispatch_ready",
                audit_correlation_id="module29-dashboard-demo-ready",
                dispatch_eligible=True,
                requires_review=False,
                blocked=False,
                unsafe=False,
                water_emergency_separated=False,
                approved_for_dispatch_at=morning_start - timedelta(hours=2),
                deterministic_evidence_snapshot={
                    "scenario": "standard_dispatch_ready",
                    "production_data": False,
                },
            ),
            IntakeProcessingRecord(
                source_system=SEED_SOURCE_SYSTEM,
                source_id="module27-blocked-intake",
                lifecycle_state="blocked",
                orchestration_state="blocked",
                review_item_id=OPEN_REVIEW_ID,
                audit_correlation_id="module27-dashboard-demo-blocked",
                dispatch_eligible=False,
                requires_review=True,
                blocked=True,
                unsafe=True,
                water_emergency_separated=False,
                deterministic_evidence_snapshot={"reason": "synthetic_demo_blocker"},
            ),
            IntakeProcessingRecord(
                source_system=SEED_SOURCE_SYSTEM,
                source_id="module29-deferred-intake",
                lifecycle_state="deferred",
                orchestration_state="manual_review_deferred",
                review_item_id=ARCHIVED_REVIEW_ID,
                audit_correlation_id="module29-dashboard-demo-archived",
                dispatch_eligible=False,
                requires_review=True,
                blocked=False,
                unsafe=False,
                water_emergency_separated=False,
                deferred_at=morning_start - timedelta(hours=3),
                deterministic_evidence_snapshot={
                    "scenario": "manual_review_blocked",
                    "production_data": False,
                },
            ),
            IntakeProcessingRecord(
                source_system=SEED_SOURCE_SYSTEM,
                source_id="module29-job-created-intake",
                lifecycle_state="job_created",
                orchestration_state="job_creation_recorded",
                audit_correlation_id="module29-dashboard-demo-confirmed",
                dispatch_eligible=True,
                requires_review=False,
                blocked=False,
                unsafe=False,
                water_emergency_separated=False,
                deterministic_evidence_snapshot={
                    "scenario": "external_confirmation_succeeded",
                    "production_data": False,
                },
            ),
            IntakeProcessingRecord(
                source_system=SEED_SOURCE_SYSTEM,
                source_id="module27-water-intake",
                lifecycle_state="review_required",
                orchestration_state="water_emergency_separated",
                review_item_id=WATER_REVIEW_ID,
                audit_correlation_id="module27-dashboard-demo-water",
                dispatch_eligible=False,
                requires_review=True,
                blocked=False,
                unsafe=False,
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
            WaterEmergency(
                id=CLOSED_WATER_EMERGENCY_ID,
                job_id=CLOSED_WATER_JOB_ID,
                status="closed",
                drying_stage="closed_after_monitoring",
                next_required_action="No action. Synthetic closed Water Emergency example.",
                equipment_onsite=False,
                moisture_tracking_required=False,
                opened_at=morning_start - timedelta(days=2),
                closed_at=morning_start - timedelta(days=1),
                notes="Synthetic closed Water Emergency seed data. Not production data.",
            ),
            WaterEmergency(
                id=MISSING_WATER_EMERGENCY_ID,
                job_id=MISSING_WATER_JOB_ID,
                status="DRYING_IN_PROGRESS",
                drying_stage=None,
                next_required_action=None,
                equipment_onsite=False,
                moisture_tracking_required=True,
                opened_at=None,
                notes=(
                    "Synthetic Module 35 missing-data Water Emergency example. Not production data."
                ),
            ),
            WaterEmergency(
                id=READY_CLOSE_WATER_EMERGENCY_ID,
                job_id=READY_CLOSE_WATER_JOB_ID,
                status="READY_FOR_PICKUP",
                drying_stage="ready_for_pickup",
                next_required_action="Synthetic ready for close-review visibility.",
                equipment_onsite=False,
                moisture_tracking_required=False,
                opened_at=morning_start - timedelta(days=1, hours=4),
                notes=(
                    "Synthetic Module 35 ready-for-close-review Water Emergency example. "
                    "Not production data."
                ),
            ),
            WaterEmergency(
                id=FOLLOWUP_WATER_EMERGENCY_ID,
                job_id=FOLLOWUP_WATER_JOB_ID,
                status="DRYING_IN_PROGRESS",
                drying_stage="monitoring",
                next_required_action="Synthetic follow-up visit visibility needed.",
                equipment_onsite=False,
                moisture_tracking_required=False,
                opened_at=morning_start - timedelta(days=2),
                notes=(
                    "Synthetic Module 36 visit-follow-up Water Emergency example. "
                    "Not production data."
                ),
            ),
            WaterEmergency(
                id=EQUIPMENT_REVIEW_WATER_EMERGENCY_ID,
                job_id=EQUIPMENT_REVIEW_WATER_JOB_ID,
                status="DRYING_IN_PROGRESS",
                drying_stage="monitoring",
                next_required_action="Synthetic equipment context review needed.",
                equipment_onsite=True,
                moisture_tracking_required=False,
                opened_at=morning_start - timedelta(days=5),
                notes=(
                    "Synthetic Module 36 equipment-review Water Emergency example. "
                    "Not production data."
                ),
            ),
            WaterEmergency(
                id=MONITORING_WATER_EMERGENCY_ID,
                job_id=MONITORING_WATER_JOB_ID,
                status="DRYING_IN_PROGRESS",
                drying_stage="monitoring",
                next_required_action="Continue synthetic monitoring visibility.",
                equipment_onsite=False,
                moisture_tracking_required=False,
                opened_at=morning_start - timedelta(days=2),
                notes=(
                    "Synthetic Module 36 monitoring Water Emergency example. Not production data."
                ),
            ),
            WaterEmergency(
                id=NEWLY_OPENED_WATER_EMERGENCY_ID,
                job_id=NEWLY_OPENED_WATER_JOB_ID,
                status="NEW",
                drying_stage="initial_response",
                next_required_action="Synthetic newly opened timing visibility.",
                equipment_onsite=False,
                moisture_tracking_required=False,
                opened_at=generated_at - timedelta(hours=6),
                notes=(
                    "Synthetic Module 37 newly opened Water Emergency example. Not production data."
                ),
            ),
            WaterEmergency(
                id=STALE_EVIDENCE_WATER_EMERGENCY_ID,
                job_id=STALE_EVIDENCE_WATER_JOB_ID,
                status="DRYING_IN_PROGRESS",
                drying_stage="monitoring",
                next_required_action="Synthetic stale evidence review visibility.",
                equipment_onsite=False,
                moisture_tracking_required=False,
                opened_at=morning_start - timedelta(days=6),
                notes=(
                    "Synthetic Module 37 stale evidence Water Emergency example. "
                    "Not production data."
                ),
            ),
            OperationalEventRecord(
                id=WATER_EXCEPTION_EVENT_ID,
                occurred_at=scheduled_start - timedelta(hours=2, minutes=30),
                recorded_at=scheduled_start - timedelta(hours=2, minutes=30),
                event_type="water_emergency.review_exception_flagged",
                event_state="review_required",
                entity_type="review_item",
                entity_id=WATER_OPEN_REVIEW_ID,
                route_assignment_id=None,
                visit_id=WATER_FOLLOWUP_VISIT_ID,
                work_order_id=WATER_WORK_ORDER_ID,
                job_id=WATER_JOB_ID,
                technician_id=SECONDARY_TECHNICIAN_ID,
                audit_correlation_id="module34-dashboard-demo-water-critical",
                previous_state=None,
                new_state="manual_review_required",
                event_fingerprint="module34-dashboard-demo-water-review-exception-flagged",
                is_immutable=True,
                event_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "scenario": "water_emergency_review_exception_visibility",
                    "production_data": False,
                    "water_emergency_execution": "not_executed",
                    "alert_visibility_only": True,
                },
            ),
            OperationalEventRecord(
                id=WATER_EMERGENCY_EVENT_ID,
                occurred_at=scheduled_start - timedelta(hours=3, minutes=30),
                recorded_at=scheduled_start - timedelta(hours=3, minutes=30),
                event_type="water_emergency.extraction_started",
                event_state="recorded",
                entity_type="water_emergency",
                entity_id=WATER_EMERGENCY_ID,
                route_assignment_id=None,
                visit_id=WATER_VISIT_ID,
                work_order_id=WATER_WORK_ORDER_ID,
                job_id=WATER_JOB_ID,
                technician_id=SECONDARY_TECHNICIAN_ID,
                audit_correlation_id="module27-dashboard-demo-water",
                previous_state="new",
                new_state="extraction_started",
                event_fingerprint="module32-dashboard-demo-water-extraction-started",
                is_immutable=True,
                event_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "scenario": "water_emergency_separated",
                    "production_data": False,
                },
            ),
            OperationalEventRecord(
                id=WATER_DRYING_CHECK_EVENT_ID,
                occurred_at=scheduled_start - timedelta(hours=2),
                recorded_at=scheduled_start - timedelta(hours=2),
                event_type="water_emergency.drying_check_scheduled",
                event_state="scheduled",
                entity_type="water_emergency",
                entity_id=WATER_EMERGENCY_ID,
                route_assignment_id=None,
                visit_id=WATER_FOLLOWUP_VISIT_ID,
                work_order_id=WATER_WORK_ORDER_ID,
                job_id=WATER_JOB_ID,
                technician_id=SECONDARY_TECHNICIAN_ID,
                audit_correlation_id="module33-dashboard-demo-water-followup",
                previous_state="extraction_started",
                new_state="drying_check_scheduled",
                event_fingerprint="module33-dashboard-demo-water-drying-check-scheduled",
                is_immutable=True,
                event_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "scenario": "water_emergency_visit_chain",
                    "production_data": False,
                    "water_emergency_execution": "not_executed",
                },
            ),
            OperationalEventRecord(
                id=READY_CLOSE_WATER_EVENT_ID,
                occurred_at=morning_start - timedelta(days=1, minutes=30),
                recorded_at=morning_start - timedelta(days=1, minutes=30),
                event_type="water_emergency.ready_for_close_review",
                event_state="ready_for_close_review",
                entity_type="water_emergency",
                entity_id=READY_CLOSE_WATER_EMERGENCY_ID,
                route_assignment_id=None,
                visit_id=READY_CLOSE_WATER_VISIT_ID,
                work_order_id=READY_CLOSE_WATER_WORK_ORDER_ID,
                job_id=READY_CLOSE_WATER_JOB_ID,
                technician_id=SECONDARY_TECHNICIAN_ID,
                audit_correlation_id="module35-dashboard-demo-water-close-review",
                previous_state="drying_complete",
                new_state="ready_for_close_review",
                event_fingerprint="module35-dashboard-demo-water-ready-for-close-review",
                is_immutable=True,
                event_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "scenario": "water_emergency_ready_for_close_review",
                    "production_data": False,
                    "water_emergency_execution": "not_executed",
                    "close_execution": "not_executed",
                },
            ),
            OperationalEventRecord(
                id=FOLLOWUP_WATER_EVENT_ID,
                occurred_at=morning_start - timedelta(hours=3, minutes=45),
                recorded_at=morning_start - timedelta(hours=3, minutes=45),
                event_type="water_emergency.followup_needed",
                event_state="followup_needed",
                entity_type="water_emergency",
                entity_id=FOLLOWUP_WATER_EMERGENCY_ID,
                route_assignment_id=None,
                visit_id=FOLLOWUP_WATER_VISIT_ID,
                work_order_id=FOLLOWUP_WATER_WORK_ORDER_ID,
                job_id=FOLLOWUP_WATER_JOB_ID,
                technician_id=SECONDARY_TECHNICIAN_ID,
                audit_correlation_id="module36-dashboard-demo-water-followup-needed",
                previous_state="visit_completed",
                new_state="followup_needed",
                event_fingerprint="module36-dashboard-demo-water-followup-needed",
                is_immutable=True,
                event_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "scenario": "water_emergency_visit_followup_needed",
                    "production_data": False,
                    "water_emergency_execution": "not_executed",
                },
            ),
            OperationalEventRecord(
                id=EQUIPMENT_REVIEW_WATER_EVENT_ID,
                occurred_at=morning_start - timedelta(hours=3, minutes=30),
                recorded_at=morning_start - timedelta(hours=3, minutes=30),
                event_type="water_emergency.equipment_review_needed",
                event_state="review_needed",
                entity_type="water_emergency",
                entity_id=EQUIPMENT_REVIEW_WATER_EMERGENCY_ID,
                route_assignment_id=None,
                visit_id=EQUIPMENT_REVIEW_WATER_VISIT_ID,
                work_order_id=EQUIPMENT_REVIEW_WATER_WORK_ORDER_ID,
                job_id=EQUIPMENT_REVIEW_WATER_JOB_ID,
                technician_id=SECONDARY_TECHNICIAN_ID,
                audit_correlation_id="module36-dashboard-demo-water-equipment-review",
                previous_state="equipment_recorded",
                new_state="equipment_review_needed",
                event_fingerprint="module36-dashboard-demo-water-equipment-review-needed",
                is_immutable=True,
                event_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "scenario": "water_emergency_equipment_review_needed",
                    "production_data": False,
                    "equipment_execution": "not_executed",
                },
            ),
            OperationalEventRecord(
                id=MONITORING_WATER_EVENT_ID,
                occurred_at=morning_start - timedelta(hours=3, minutes=15),
                recorded_at=morning_start - timedelta(hours=3, minutes=15),
                event_type="water_emergency.monitoring_active",
                event_state="monitoring",
                entity_type="water_emergency",
                entity_id=MONITORING_WATER_EMERGENCY_ID,
                route_assignment_id=None,
                visit_id=MONITORING_WATER_VISIT_ID,
                work_order_id=MONITORING_WATER_WORK_ORDER_ID,
                job_id=MONITORING_WATER_JOB_ID,
                technician_id=SECONDARY_TECHNICIAN_ID,
                audit_correlation_id="module36-dashboard-demo-water-monitoring",
                previous_state="drying_in_progress",
                new_state="monitoring",
                event_fingerprint="module36-dashboard-demo-water-monitoring-active",
                is_immutable=True,
                event_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "scenario": "water_emergency_monitoring",
                    "production_data": False,
                    "water_emergency_execution": "not_executed",
                },
            ),
            OperationalEventRecord(
                id=NEWLY_OPENED_WATER_EVENT_ID,
                occurred_at=generated_at - timedelta(hours=5),
                recorded_at=generated_at - timedelta(hours=5),
                event_type="water_emergency.newly_opened",
                event_state="newly_opened",
                entity_type="water_emergency",
                entity_id=NEWLY_OPENED_WATER_EMERGENCY_ID,
                route_assignment_id=None,
                visit_id=None,
                work_order_id=NEWLY_OPENED_WATER_WORK_ORDER_ID,
                job_id=NEWLY_OPENED_WATER_JOB_ID,
                technician_id=SECONDARY_TECHNICIAN_ID,
                audit_correlation_id="module37-dashboard-demo-water-newly-opened",
                previous_state=None,
                new_state="newly_opened",
                event_fingerprint="module37-dashboard-demo-water-newly-opened",
                is_immutable=True,
                event_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "scenario": "water_emergency_aging_newly_opened",
                    "production_data": False,
                    "water_emergency_execution": "not_executed",
                    "sla_engine": "not_implemented",
                },
            ),
            OperationalEventRecord(
                id=STALE_EVIDENCE_WATER_EVENT_ID,
                occurred_at=morning_start - timedelta(days=4, hours=2),
                recorded_at=morning_start - timedelta(days=4, hours=2),
                event_type="water_emergency.stale_monitoring_evidence",
                event_state="monitoring",
                entity_type="water_emergency",
                entity_id=STALE_EVIDENCE_WATER_EMERGENCY_ID,
                route_assignment_id=None,
                visit_id=STALE_EVIDENCE_WATER_VISIT_ID,
                work_order_id=STALE_EVIDENCE_WATER_WORK_ORDER_ID,
                job_id=STALE_EVIDENCE_WATER_JOB_ID,
                technician_id=SECONDARY_TECHNICIAN_ID,
                audit_correlation_id="module37-dashboard-demo-water-stale",
                previous_state="monitoring",
                new_state="monitoring",
                event_fingerprint="module37-dashboard-demo-water-stale-evidence",
                is_immutable=True,
                event_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "scenario": "water_emergency_stale_evidence",
                    "production_data": False,
                    "water_emergency_execution": "not_executed",
                    "sla_engine": "not_implemented",
                },
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
            OperationalEventRecord(
                id=READY_EVENT_ID,
                occurred_at=morning_start - timedelta(minutes=45),
                recorded_at=morning_start - timedelta(minutes=45),
                event_type="dispatch_authorization.ready",
                event_state="awaiting_dispatch_execution",
                entity_type="route_assignment",
                entity_id=READY_ROUTE_ASSIGNMENT_ID,
                route_assignment_id=READY_ROUTE_ASSIGNMENT_ID,
                visit_id=READY_VISIT_ID,
                work_order_id=READY_WORK_ORDER_ID,
                job_id=READY_JOB_ID,
                technician_id=SECONDARY_TECHNICIAN_ID,
                audit_correlation_id="module29-dashboard-demo-ready",
                previous_state="dispatch_ready",
                new_state="awaiting_dispatch_execution",
                event_fingerprint="module29-dashboard-demo-ready",
                is_immutable=True,
                event_snapshot={"source": SEED_SOURCE_SYSTEM, "production_data": False},
            ),
            OperationalEventRecord(
                id=EXTERNAL_CONFIRMED_EVENT_ID,
                occurred_at=morning_start + timedelta(hours=2),
                recorded_at=morning_start + timedelta(hours=2),
                event_type="external_confirmation.confirmed",
                event_state="confirmed",
                entity_type="route_assignment",
                entity_id=CONFIRMED_ROUTE_ASSIGNMENT_ID,
                route_assignment_id=CONFIRMED_ROUTE_ASSIGNMENT_ID,
                visit_id=CONFIRMED_VISIT_ID,
                work_order_id=CONFIRMED_WORK_ORDER_ID,
                job_id=CONFIRMED_JOB_ID,
                technician_id=TECHNICIAN_ID,
                audit_correlation_id="module29-dashboard-demo-confirmed",
                previous_state="awaiting_external_confirmation",
                new_state="confirmed",
                event_fingerprint="module29-dashboard-demo-external-confirmed",
                is_immutable=True,
                event_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "external_execution": "not_executed",
                    "production_data": False,
                },
            ),
            OperationalEventRecord(
                id=CONFIRMATION_EVENT_ID,
                occurred_at=scheduled_start - timedelta(minutes=45),
                recorded_at=scheduled_start - timedelta(minutes=45),
                event_type="external_confirmation.failed",
                event_state="failed",
                entity_type="route_assignment",
                entity_id=ROUTE_ASSIGNMENT_ID,
                route_assignment_id=ROUTE_ASSIGNMENT_ID,
                visit_id=STANDARD_VISIT_ID,
                work_order_id=WORK_ORDER_ID,
                job_id=STANDARD_JOB_ID,
                technician_id=TECHNICIAN_ID,
                audit_correlation_id=SEED_AUDIT_CORRELATION_ID,
                previous_state="awaiting_external_confirmation",
                new_state="failed",
                event_fingerprint="module29-dashboard-demo-confirmation-failed",
                is_immutable=True,
                event_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "external_execution": "not_executed",
                    "production_data": False,
                },
            ),
            OperationalEventRecord(
                id=RECOVERY_EVENT_ID,
                occurred_at=recovery_start - timedelta(minutes=30),
                recorded_at=recovery_start - timedelta(minutes=30),
                event_type="operational_recovery.rollback_prepared",
                event_state="rollback_prepared",
                entity_type="route_assignment",
                entity_id=RECOVERY_ROUTE_ASSIGNMENT_ID,
                route_assignment_id=RECOVERY_ROUTE_ASSIGNMENT_ID,
                visit_id=RECOVERY_VISIT_ID,
                work_order_id=RECOVERY_WORK_ORDER_ID,
                job_id=RECOVERY_JOB_ID,
                technician_id=SECONDARY_TECHNICIAN_ID,
                audit_correlation_id="module29-dashboard-demo-recovery",
                previous_state="reconciliation_required",
                new_state="rollback_prepared",
                event_fingerprint="module29-dashboard-demo-rollback-prepared",
                is_immutable=True,
                event_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "rollback_execution": "not_executed",
                    "production_data": False,
                },
            ),
            OperationalEventRecord(
                id=GOVERNANCE_EVENT_ID,
                occurred_at=recovery_start - timedelta(minutes=25),
                recorded_at=recovery_start - timedelta(minutes=25),
                event_type="operational_governance.intervention_required",
                event_state="manual_intervention_required",
                entity_type="route_assignment",
                entity_id=RECOVERY_ROUTE_ASSIGNMENT_ID,
                route_assignment_id=RECOVERY_ROUTE_ASSIGNMENT_ID,
                visit_id=RECOVERY_VISIT_ID,
                work_order_id=RECOVERY_WORK_ORDER_ID,
                job_id=RECOVERY_JOB_ID,
                technician_id=SECONDARY_TECHNICIAN_ID,
                audit_correlation_id="module29-dashboard-demo-recovery",
                previous_state="rollback_prepared",
                new_state="manual_intervention_required",
                event_fingerprint="module29-dashboard-demo-governance-required",
                is_immutable=True,
                event_snapshot={"source": SEED_SOURCE_SYSTEM, "production_data": False},
            ),
            OperationalEventRecord(
                id=INCIDENT_EVENT_ID,
                occurred_at=recovery_start - timedelta(minutes=20),
                recorded_at=recovery_start - timedelta(minutes=20),
                event_type="operational_accountability.incident_prepared",
                event_state="incident_prepared",
                entity_type="route_assignment",
                entity_id=RECOVERY_ROUTE_ASSIGNMENT_ID,
                route_assignment_id=RECOVERY_ROUTE_ASSIGNMENT_ID,
                visit_id=RECOVERY_VISIT_ID,
                work_order_id=RECOVERY_WORK_ORDER_ID,
                job_id=RECOVERY_JOB_ID,
                technician_id=SECONDARY_TECHNICIAN_ID,
                audit_correlation_id="module29-dashboard-demo-recovery",
                previous_state="manual_intervention_required",
                new_state="incident_prepared",
                event_fingerprint="module29-dashboard-demo-incident-prepared",
                is_immutable=True,
                event_snapshot={
                    "source": SEED_SOURCE_SYSTEM,
                    "incident_execution": "not_executed",
                    "production_data": False,
                },
            ),
        ),
    )


def seed_dashboard_dev_data(session: Session) -> DashboardDevSeedResult:
    records = build_dashboard_dev_seed_records()
    inserted_count = 0
    updated_count = 0

    for record in records.records:
        with session.no_autoflush:
            existing_record = find_existing_seed_record(session, record)
        if existing_record is None:
            session.add(record)
            inserted_count += 1
        else:
            copy_seed_column_values(record, existing_record)
            updated_count += 1

    return DashboardDevSeedResult(
        inserted=inserted_count > 0,
        record_count=records.record_count,
        inserted_count=inserted_count,
        updated_count=updated_count,
        scenario_count=len(records.scenario_labels),
        scenario_labels=records.scenario_labels,
        source_system=SEED_SOURCE_SYSTEM,
        message="dashboard dev seed data upserted",
    )


def find_existing_seed_record(session: Session, record: object) -> object | None:
    if isinstance(record, IntakeProcessingRecord):
        return session.scalar(
            select(IntakeProcessingRecord)
            .where(IntakeProcessingRecord.source_system == record.source_system)
            .where(IntakeProcessingRecord.source_id == record.source_id)
            .limit(1),
        )
    if isinstance(record, OperationalEventRecord):
        return session.scalar(
            select(OperationalEventRecord)
            .where(OperationalEventRecord.event_fingerprint == record.event_fingerprint)
            .limit(1),
        )

    record_id = getattr(record, "id", None)
    if record_id is None:
        return None
    return session.get(type(record), record_id)


def copy_seed_column_values(source: object, target: object) -> None:
    for column_attr in inspect(type(source)).mapper.column_attrs:
        key = column_attr.key
        if key in {"id", "created_at", "updated_at"}:
            continue
        setattr(target, key, getattr(source, key))


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
