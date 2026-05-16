# ACS FSM — System Architecture

## Purpose

This root-level note is the quick architecture index for the ACS FSM platform.

The detailed architecture baseline is maintained in:

- [[SYSTEM_ARCHITECTURE_V1]]
- [[PROJECT_ARCHITECTURE_VISION]]
- [[09-First-Module-Build-Scope]]

---

## Architecture Baseline

The ACS FSM platform should be:

- database-first
- state-driven
- modular
- auditable
- API-first
- adapter-based
- safe for daily operations

It must avoid:

- business logic in frontend components
- fragile free-text parsing as the main workflow
- hardcoded vendor behavior in the core system
- giant centralized files
- silent automation failures

---

## Preferred Stack

Backend:

- Python
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Pydantic Settings

Frontend:

- Next.js
- TypeScript
- Tailwind

Future background jobs:

- Redis
- Celery or equivalent queue system

---

## Module Boundaries

Core backend structure should separate:

- API routes
- domain models
- schemas
- repositories
- services
- validators
- workflow engines
- integration adapters
- audit logging

Frontend should display state, warnings, review items, route results, and dispatch status from backend APIs.

---

## Phase 0 Module 3 Backend Hardening

The backend foundation now includes production-oriented operating structure without implementing business workflows:

- explicit development, testing, and production settings behavior
- production database URL safety checks
- versioned API docs/OpenAPI URLs under `/api/v1`
- request ID middleware for request-safe logging and future audit correlation
- FastAPI lifespan hooks for startup/shutdown readiness state
- structured JSON logging by default
- Makefile developer commands for install, run, test, lint, format, migrations, compileall, and verification

No deployment scripts, Docker/Kubernetes infrastructure, auth, frontend, external integrations, or dispatch workflow logic were added.

---

## Phase 0 Module 4 Repository Boundary

The backend now includes a thin repository layer and request-scoped session foundation:

- `app/repositories/` contains one repository class per core ACS domain model.
- `BaseRepository` provides minimal `get`, `list`, `add`, and `delete` helpers.
- `app/db/session.py` owns engine/session factory creation, request-scoped session cleanup, rollback-on-error behavior, and explicit transactional `session_scope`.
- `app/db/dependencies.py` exposes a FastAPI dependency alias for future API modules.

The boundary is intentionally narrow. Repositories are for data access only; business workflows belong in services, validators, workflow engines, and Manual Review orchestration.

---

## Phase 0 Module 5 Intake Pipeline Boundary

The backend now includes deterministic intake processing foundations:

- intake domain structures in `app/domain/intake.py`
- normalization service for text cleanup and marker/keyword detection
- validation service for required fields, malformed intake foundations, conflicts, and unsafe dispatch signals
- deterministic confidence scoring service
- Manual Review preparation service

The boundary is intentionally pre-ingestion and pre-dispatch. It transforms raw external-like payloads into normalized internal structures and review recommendations, but it does not connect to Google Calendar, persist jobs, dispatch work, route technicians, export to Sheets/FastField, or call AI.

AI remains a future advisory layer only. Deterministic validation and Manual Review safety must remain authoritative.

---

## Phase 0 Module 6 Manual Review Queue Boundary

The backend now includes the first persistent Manual Review Queue architecture:

- intake processing state enum for raw, normalized, validated, flagged, approved, rejected, deferred, and archived states
- persistent review fields for status, severity, reasons, source references, snapshots, operator notes, timestamps, and audit correlation
- queue creation service for deterministic review items
- classification service for review categories
- escalation service for severity assignment
- transition service for approve, reject, defer, and archive lifecycle steps
- audit trace builder for explainable flagging evidence

The boundary is intentionally pre-dispatch. A review item can be approved, rejected, deferred, or archived, but that transition does not create a job, route a technician, export to Sheets/FastField, call AI, or update live vendor systems.

Future workflow modules should connect approved review outcomes to dispatch orchestration through explicit services and transactions, not hidden side effects inside review-state updates.

---

## Phase 0 Module 7 Dispatch Orchestration Boundary

The backend now includes a deterministic dispatch orchestration preparation layer:

- orchestration domain structures for state, warnings, decision result, evidence, intake processing result, and dispatch eligibility
- `DispatchOrchestrationService` to compose normalization, validation, confidence scoring, Manual Review recommendation, review classification, and eligibility determination
- evidence snapshots for normalization, validation, confidence, review, and deterministic decision output
- tests for valid intake, cancellation, malformed intake, Water Emergency separation, low-confidence cancellation, conflicting state/time markers, unsafe required-field failures, and review-required scheduling failures

The boundary is intentionally pre-persistence and pre-execution. Orchestration prepares a deterministic result; it does not write jobs, visits, review records, route assignments, integration exports, or workflow state.

Future modules should treat orchestration output as an input to explicit transactional workflow services.

---

## Phase 0 Module 8 Operational Intake Persistence Boundary

The backend now includes the first persistent operational transition after orchestration:

- `OperationalLifecycleState` for intake_received, normalized, validated, review_required, approved_for_dispatch, blocked, deferred, and archived states
- `IntakeProcessingRecord` model for durable orchestration outcome storage
- `IntakeProcessingRecordRepository` for thin persistence access
- `OperationalIntakePersistenceService` for storing orchestration outcomes and deterministic evidence
- audit-log builder support for persisted intake records

The boundary is intentionally storage-only. It persists orchestration outputs and lifecycle state, but it does not create jobs, dispatch work, route technicians, export to vendors, call AI, or run background workers.

Future dispatch execution should consume approved intake records through explicit transactional services, with Manual Review and Water Emergency boundaries preserved.

---

## Phase 0 Module 9 Operational Job Creation Boundary

The backend now includes the first controlled operational creation step after intake persistence:

- `JobCreationLifecycleState` and failure-code domain structures for deterministic creation results
- `JobCreationRecord` model for intake-to-job linkage and creation snapshots
- `JobCreationRecordRepository` for thin persistence access
- `OperationalJobCreationService` for creating standard jobs from approved intake records
- creation evidence, failure reasons, traceability references, and audit-log preparation

The boundary is intentionally pre-dispatch. It can create a standard job in `awaiting_dispatch` from an approved intake record, but it does not route technicians, create visits, create work orders, export to vendors, call integrations, run background workers, or call AI.

Manual Review and Water Emergency separation remain authoritative. Review-required, blocked, unsafe, invalid-lifecycle, duplicate, or Water Emergency intake records cannot create standard jobs.

Future dispatch execution should consume created jobs and creation records through explicit workflow services and transactions.

---

## Phase 0 Module 10 Work Order And Visit Generation Boundary

The backend now includes the first scheduling-ready operational execution preparation layer:

- `OperationalGenerationLifecycleState` and failure-code domain structures
- Work Order traceability fields for job creation linkage, review linkage, snapshots, audit correlation, and lifecycle metadata
- Visit traceability fields for Work Order linkage, snapshots, audit correlation, and lifecycle metadata
- repository duplicate lookup helpers for generated Work Orders and Visits
- `OperationalWorkGenerationService` for deterministic Work Order and Visit generation
- audit-log preparation for generated Work Orders and Visits

The boundary is intentionally pre-dispatch and pre-routing. It can create a standard Work Order from an approved standard job and create an unassigned Visit from that Work Order, but it does not assign technicians, schedule exact times, route work, dispatch work, export to vendors, call integrations, run background workers, or call AI.

Manual Review and Water Emergency separation remain authoritative. Blocked, review-required, invalid-lifecycle, duplicate, or Water Emergency jobs cannot use the standard Work Order generation path.

Future dispatch/routing modules should consume generated Work Orders and Visits through explicit workflow services and transactions.

---

## Phase 0 Module 11 Assignment And Scheduling Preparation Boundary

The backend now includes the first technician-facing preparation layer before routing and dispatch:

- `AssignmentPreparationLifecycleState` and blocker-code domain structures
- assignment eligibility, assignment readiness, technician compatibility, scheduling readiness, and operational readiness structures
- Visit readiness snapshot fields for assignment, technician compatibility, scheduling, and operational readiness
- `AssignmentPreparationService` for deterministic Visit readiness preparation
- audit-log preparation for assignment readiness

The boundary is intentionally pre-assignment, pre-routing, and pre-dispatch. It can prepare readiness snapshots and lifecycle state for a generated Visit, but it does not assign technicians, schedule exact times, route work, dispatch work, sync calendars, call integrations, run background workers, or call AI.

Manual Review and Water Emergency separation remain authoritative. Blocked, review-required, archived, invalid-lifecycle, or Water Emergency Visits cannot use the standard assignment preparation path. Inactive technician candidates block compatibility without assigning the technician.

Future routing and dispatch modules should consume readiness snapshots and explicit Visit lifecycle state instead of recomputing assignment blockers from freeform text.

---

## Phase 0 Module 12 Routing And Dispatch Preparation Boundary

The backend now includes the deterministic preparation layer immediately before future route optimization and dispatch execution:

- `RoutingDispatchLifecycleState` and blocker-code domain structures
- routing readiness, technician readiness, Visit dispatch readiness, dispatch eligibility, evidence, and traceability structures
- Visit readiness snapshot fields for routing readiness, dispatch readiness, technician readiness, and Visit dispatch readiness
- `RoutingDispatchPreparationService` for deterministic routing and dispatch preparation
- audit-log preparation for dispatch readiness

The boundary is intentionally pre-routing-engine and pre-dispatch-execution. It can prepare readiness snapshots and move a standard Visit to `routing_ready` or `dispatch_ready`, but it does not optimize routes, create route assignments, assign technicians, schedule Visits, sync calendars, call integrations, run background workers, or call AI.

Manual Review and Water Emergency separation remain authoritative. Blocked, review-required, archived, invalid-lifecycle, missing-linkage, or Water Emergency Visits cannot use the standard routing/dispatch preparation path. Inactive technicians, unassigned Visits, and unscheduled Visits cannot become dispatch-ready.

Future dispatch execution should consume these readiness snapshots and explicit Visit lifecycle state through a separate transactional service.

---

## Phase 0 Module 13 Route Assignment And Dispatch Authorization Boundary

The backend now includes the deterministic boundary between dispatch preparation and future dispatch execution:

- `DispatchExecutionAuthorizationState` and route-assignment blocker-code domain structures
- route grouping, route assignment readiness, technician route compatibility, dispatch authorization readiness, execution authorization, evidence, and traceability structures
- Route Assignment fields for grouping, readiness, technician compatibility, dispatch authorization, execution-boundary, and deterministic evidence snapshots
- `RouteAssignmentPreparationService` for deterministic route assignment preparation and dispatch authorization
- audit-log preparation for dispatch authorization

The boundary is intentionally pre-execution. It can create a prepared `RouteAssignment` and move a standard Visit to `awaiting_dispatch_execution`, but it does not optimize routes, execute dispatch, sync calendars, export to Sheets/FastField, call integrations, run background workers, or call AI.

Manual Review and Water Emergency separation remain authoritative. Blocked, review-required, archived, invalid-lifecycle, missing-linkage, Water Emergency, inactive-technician, unassigned, unscheduled, route-unready, or dispatch-unready Visits cannot become dispatch-authorized.

Future dispatch execution should consume authorized route assignments through a separate transactional service that records operator/system identity and integration outcomes.

---

## First Module Boundary

The first real implementation module is the Dispatch Operations Engine.

It should not attempt to build the full FSM immediately.

See [[12-Roadmap/MASTER_ROADMAP]] for phased scope.
