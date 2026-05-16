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

## Phase 0 Module 14 Dispatch Execution Boundary

The backend now includes the deterministic internal dispatch execution lifecycle boundary:

- `DispatchExecutionState` and dispatch execution blocker-code domain structures
- dispatch execution result, traceability, lifecycle transition, failure reason, and evidence structures
- Route Assignment fields for execution state, execution snapshot, lifecycle snapshot, audit snapshot, dispatched timestamp, and future failure timestamp
- `DispatchExecutionService` for transitioning dispatch-authorized standard Route Assignments into internal `dispatched` state
- audit-log preparation for dispatched Route Assignments

The boundary is intentionally internal-only. It can move an authorized standard Route Assignment and linked Visit to `dispatched`, but it does not sync calendars, export to Sheets/FastField, update technician mobile workflows, call integrations, run background workers, optimize routes, or call AI.

Manual Review and Water Emergency separation remain authoritative. Blocked, review-required, archived, invalid-lifecycle, missing-linkage, Water Emergency, inactive-technician, unassigned, unscheduled, unauthorized, or duplicate-dispatch records cannot use the standard dispatch execution path.

Future external dispatch integration should consume the internal dispatch execution snapshot through isolated adapters and preserve adapter outcomes without letting vendors become the source of truth.

## Phase 0 Module 15 External Dispatch Adapter Boundary

The backend now includes the deterministic preparation boundary between internal dispatch execution and future external integrations:

- `ExternalAdapterLifecycleState` and adapter failure-code domain structures
- adapter execution request, result, evidence, failure reason, and audit evidence structures
- Route Assignment fields for adapter state, request snapshot, payload snapshot, lifecycle snapshot, evidence snapshot, audit snapshot, prepared timestamp, and future failure timestamp
- `ExternalDispatchAdapterPreparationService` for preparing future FastField, Google Sheets, Google Calendar, and technician mobile payload snapshots
- audit-log preparation for adapter-prepared Route Assignments

The boundary is intentionally prepare-only. It can move an internally dispatched standard Route Assignment into `awaiting_external_execution`, but it does not call vendor APIs, sync calendars, write Sheets, update mobile workflows, run background workers, optimize routes, or call AI.

Manual Review and Water Emergency separation remain authoritative. Blocked, review-required, Water Emergency, undispatched, unauthorized, duplicate-prepared, invalid-lifecycle, or missing-linkage records cannot use the standard external adapter preparation path.

Future live integration execution should consume adapter payload snapshots through isolated vendor adapters and write execution outcomes without giving vendors authority over internal ACS workflow state.

## Phase 0 Module 18 External Adapter Execution Boundary

The backend now includes the deterministic controlled execution boundary between adapter preparation and confirmation readiness:

- `ExternalExecutionLifecycleState` and provider execution-state domain structures
- external execution request, provider result, evidence, lifecycle transition, failure reason, and audit evidence structures
- Route Assignment fields for external execution state, request snapshot, provider snapshot, evidence snapshot, failure snapshot, lifecycle snapshot, audit snapshot, and related timestamps
- `ExternalAdapterExecutionService` for processing prepared adapter payloads through simulated controlled provider execution boundaries
- audit-log preparation for completed, failed, or reconciliation-required external execution attempts

The boundary is intentionally controlled and simulation-only. It can move a standard prepared Route Assignment from `awaiting_external_execution` to `awaiting_external_confirmation`, or record failure/reconciliation evidence, but it does not call vendor APIs, execute retries, run background workers, update mobile workflows, optimize routes, or call AI.

Manual Review and Water Emergency separation remain authoritative. Blocked, review-required, Water Emergency, unauthorized, duplicate-attempt, invalid-lifecycle, adapter-unready, or missing-payload records cannot use the standard external execution path.

Future live provider adapters should replace only the provider execution internals while preserving the same lifecycle, evidence, audit, and safety boundaries.

## Phase 0 Module 16 External Confirmation And Recovery Boundary

The backend now includes the deterministic resilience boundary after external adapter preparation:

- `ExternalConfirmationLifecycleState` and simulated confirmation-state domain structures
- confirmation result, evidence, traceability, failure reason, retry, and reconciliation structures
- Route Assignment fields for confirmation state, confirmation evidence snapshot, lifecycle snapshot, audit snapshot, external failure snapshot, retry preparation snapshot, reconciliation snapshot, and related timestamps
- `ExternalExecutionConfirmationService` for processing simulated confirmation outcomes and preparing retry or reconciliation evidence
- audit-log preparation for externally confirmed, failed, retry-prepared, or reconciliation-required Route Assignments

The boundary is intentionally preparation-only. It can record deterministic confirmation, failure, retry-preparation, or reconciliation-preparation evidence for an adapter-prepared standard Route Assignment, but it does not call external APIs, execute retries, run reconciliation engines, update mobile workflows, run background workers, optimize routes, or call AI.

Manual Review and Water Emergency separation remain authoritative. Blocked, review-required, Water Emergency, unauthorized, duplicate-confirmed, invalid-lifecycle, missing-linkage, or adapter-unready records cannot use the standard external confirmation path.

Future live external execution should write vendor outcomes into this boundary through isolated adapters while preserving the ACS database as the workflow source of truth.

## Phase 0 Module 17 Operational Event History Boundary

The backend now includes the append-only operational history and immutable timeline foundation:

- `OperationalEventState` and operational event failure-code domain structures
- lifecycle event, timeline entry, immutable audit, transition, retry/recovery, reconciliation, evidence, and result structures
- `OperationalEventRecord` model for durable event history
- `OperationalEventRecordRepository` for append/query-only event access
- `OperationalEventHistoryService` for recording lifecycle, dispatch execution, adapter preparation, confirmation, retry, and reconciliation evidence
- route-assignment and Visit timeline helpers

The boundary is intentionally evidence-only. It can append immutable operational event records and build ordered timelines, but it does not execute workflows, mutate prior events, run analytics, replay events, run reconciliation engines, call integrations, or call AI.

Manual Review, Water Emergency separation, and deterministic workflow services remain authoritative. Event history records what happened or what was blocked; it does not authorize hidden lifecycle transitions.

Future analytics, replay, operator-forensics, and external-attempt versioning should consume this event history through explicit reporting or investigation services rather than mutating operational records.

## Phase 0 Module 19 Dispatch Reconciliation And Consistency Boundary

The backend now includes deterministic reconciliation preparation and operational consistency verification:

- `ReconciliationLifecycleState`, mismatch-code, and failure-code domain structures
- consistency verification result, divergence evidence, mismatch evidence, blocker, reconciliation result, and audit evidence structures
- Route Assignment fields for reconciliation state, consistency snapshot, divergence snapshot, mismatch snapshot, blocker snapshot, audit snapshot, and related timestamps
- `DispatchReconciliationService` for comparing internal lifecycle, external execution, external confirmation, and immutable event evidence
- audit-log preparation for consistency-verified, reconciliation-required, or blocked reconciliation cases

The boundary is intentionally preparation-only. It can verify consistency or prepare reconciliation evidence, but it does not execute reconciliation, call external APIs, run analytics, replay workflows, mutate operational event history, execute retries, run background workers, or call AI.

Manual Review, Water Emergency separation, immutable event history, and deterministic lifecycle state remain authoritative. Blocked, review-required, Water Emergency, unauthorized, duplicate, invalid-lifecycle, or mutable-history records cannot use the standard reconciliation path.

Future reconciliation execution should consume these snapshots through explicit operator/review workflows rather than hidden state transitions or event replay.

## Phase 0 Module 20 Operational Replay And Recovery Preparation Boundary

The backend now includes deterministic replay-preparation, rollback-preparation, and recovery-coordination evidence:

- `ReplayRecoveryLifecycleState` and replay/recovery failure-code domain structures
- replay eligibility, rollback preparation, recovery coordination, blocker, traceability, evidence, and result structures
- Route Assignment fields for replay/recovery state, replay preparation, rollback preparation, eligibility, blocker, recovery coordination, audit snapshots, and related timestamps
- `OperationalReplayPreparationService` for preparing replay or rollback evidence from reconciliation, retry, or failure context
- audit-log preparation for replay-prepared, rollback-prepared, or blocked recovery cases

The boundary is intentionally preparation-only. It can prepare recovery evidence, but it does not execute replay, execute rollback, call external APIs, execute retries, run workflow engines, mutate operational event history, run background workers, or call AI.

Manual Review, Water Emergency separation, immutable event history, and deterministic lifecycle state remain authoritative. Blocked, review-required, Water Emergency, unauthorized, duplicate, invalid-lifecycle, no-recovery-context, or mutable-history records cannot use the standard replay/recovery path.

Future replay/recovery execution should consume these snapshots through explicit operator/review workflows rather than hidden workflow replay or mutable history changes.

## Phase 0 Module 21 Operational Governance And Approval Control Boundary

The backend now includes deterministic operator governance, approval control, and manual-intervention authorization evidence:

- `GovernanceLifecycleState`, `GovernanceOperation`, and governance failure-code domain structures
- governance approval, intervention authorization, replay authorization, rollback authorization, reconciliation approval, blocker, audit, traceability, and result structures
- Route Assignment fields for governance state, approval, intervention, replay, rollback, reconciliation, blocker, audit snapshots, and related timestamps
- `OperationalGovernanceService` for validating operator approval and intervention authorization without executing the governed action
- audit-log preparation for operator-approved, intervention-required, or governance-blocked cases

The boundary is intentionally approval-only. It can record operator approval or intervention authorization evidence, but it does not execute replay, execute rollback, execute reconciliation, call external APIs, run workflow engines, mutate operational event history, approve automatically, run background workers, or call AI.

Manual Review, Water Emergency separation, immutable event history, and deterministic lifecycle state remain authoritative. Blocked, review-required, Water Emergency, unauthorized-operator, duplicate-approval, invalid-lifecycle, missing-operator, or mutable-history records cannot use the standard governance path.

Future enterprise governance should consume these snapshots through explicit authenticated operator workflows rather than hidden lifecycle transitions.

## Phase 0 Module 22 Operational Accountability And Escalation Boundary

The backend now includes deterministic accountability, escalation-preparation, intervention-escalation, and incident-preparation evidence:

- `AccountabilityLifecycleState`, `AccountabilityEscalationType`, and accountability failure-code domain structures
- escalation result, incident preparation, intervention escalation, operational incident, blocker, audit, traceability, and result structures
- Route Assignment fields for accountability state, escalation, incident, accountability evidence, blocker, intervention escalation, operational incident, audit snapshots, and related timestamps
- `OperationalAccountabilityService` for validating escalation and incident preparation without executing the coordinated action
- audit-log preparation for escalation-required, incident-prepared, critical-intervention-required, or accountability-blocked cases

The boundary is intentionally preparation-only. It can record accountability evidence, but it does not execute escalation, execute incident workflows, execute interventions, call external APIs, run workflow engines, mutate operational event history, approve automatically, run background workers, or call AI.

Manual Review, Water Emergency separation, governance authority, immutable event history, and deterministic lifecycle state remain authoritative. Blocked, review-required, Water Emergency, unauthorized, duplicate-escalation, invalid-lifecycle, missing-operator, missing-governance, no-context, or mutable-history records cannot use the standard accountability path.

Future enterprise coordination should consume these snapshots through explicit authenticated operator workflows rather than automatic incident engines or hidden lifecycle transitions.

## Phase 0 Module 23 Operational Dashboard Read Model Boundary

The backend now includes the first read-only operational dashboard projection boundary:

- dashboard domain read models for operational overview, lifecycle state, Manual Review, dispatch, external execution, reconciliation/recovery, governance/accountability, and operational timelines
- `DashboardReadModelService` for deterministic aggregation over persisted ORM state and immutable event history
- Pydantic API contracts for dashboard responses
- read-only API routes under `/api/v1/dashboard`

The boundary is intentionally projection-only. It summarizes persisted state, blocker evidence, escalation indicators, lifecycle counts, audit-correlation references, and timeline events, but it does not mutate ORM objects, execute dispatch, trigger integrations, run AI, create analytics jobs, resolve Manual Review, or infer hidden lifecycle transitions.

The future admin dashboard should consume these API contracts and display backend state, warnings, review blockers, escalation indicators, and timeline evidence without embedding business workflow logic in frontend components.

Unresolved:

- exact dashboard filtering/pagination contract for production-size event timelines
- which operational counts should be separated by branch, region, technician, or day
- how future authentication should scope dashboard visibility by role
- whether Water Emergency needs a separate dashboard contract once its dedicated workflow path exists
- how to handle stale dashboard data and refresh cadence in the future frontend

## Phase 0 Module 24 Frontend Dashboard Foundation Boundary

The repository now includes the first frontend foundation under `frontend/`:

- Next.js App Router, TypeScript, and Tailwind CSS scaffold
- read-only admin dashboard shell with sidebar, top header, responsive layout, and operational dashboard sections
- TypeScript dashboard API contract types matching the backend Module 23 read-model responses
- server-side dashboard API client using `ACS_DASHBOARD_API_BASE_URL`
- typed local fallback data for layout verification when the backend API is unavailable
- smoke tests for API client behavior and dashboard rendering

The frontend boundary is intentionally display-only. It consumes backend dashboard read models and renders operational state, blocker indicators, Manual Review counts, Water Emergency separation signals, governance/accountability indicators, and timeline evidence without embedding workflow execution or business-rule authority in UI components.

The frontend does not implement authentication, mutation endpoints, dispatch actions, Manual Review resolution, external vendor execution, AI authority, mobile technician UI, or hidden lifecycle inference.

Unresolved:

- authentication and role-scoped dashboard visibility
- production refresh/stale-data behavior
- final filtering, sorting, and pagination behavior for dashboard sections and event timelines
- dedicated Water Emergency dashboard screens and API contracts once that workflow is implemented
- whether future dashboard views should be split by branch, region, route date, technician, or operator role

---

## Phase 0 Module 25 Frontend Visual QA Boundary

The frontend dashboard foundation now includes its first visual QA and polish pass:

- operational health summary panel above the detailed dashboard sections
- stronger status/state communication for Manual Review, blockers, dispatch readiness, and Water Emergency separation
- browser-checked desktop, laptop, and mobile dashboard layouts
- tests confirming dashboard client helpers remain read-only `GET` calls
- tests confirming the rendered dashboard does not expose operational action buttons

This module does not change the workflow architecture. The frontend remains a read-only consumer of backend dashboard read models.

The frontend still does not implement authentication, mutation endpoints, dispatch actions, Manual Review resolution, external vendor execution, AI authority, mobile technician UI, or hidden lifecycle inference.

Unresolved:

- final dashboard information architecture after authentication and role scopes exist
- production refresh cadence and stale-data indicators
- Water Emergency-specific dashboard screens and contracts
- whether future visual QA should introduce a design-system component registry

---

## Phase 0 Module 26 Full-Stack Dashboard Integration Boundary

The dashboard foundation now includes local full-stack integration guidance:

- backend dashboard routes remain read-only API contracts under `/api/v1/dashboard`
- frontend dashboard reads use server-side `ACS_DASHBOARD_API_BASE_URL`
- local development uses separate backend and frontend origins
- fallback data is only a visible local-development continuity state when the backend is unavailable
- frontend verification can run through a single `npm run verify` bundle

This module does not add new workflow authority. The frontend remains a display-only consumer of backend dashboard read models and still does not implement auth, mutation endpoints, dispatch actions, Manual Review resolution, vendor execution, AI authority, mobile technician UI, or hidden lifecycle inference.

Unresolved:

- production Apache reverse-proxy path strategy for backend and frontend
- local PostgreSQL seed-data/demo workflow
- production stale-data, polling, and cache behavior
- role-scoped dashboard visibility after authentication exists

---

## First Module Boundary

The first real implementation module is the Dispatch Operations Engine.

It should not attempt to build the full FSM immediately.

See [[12-Roadmap/MASTER_ROADMAP]] for phased scope.
