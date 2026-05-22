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

## Phase 0 Module 27 Local PostgreSQL Dashboard Verification Boundary

The repository now includes a local PostgreSQL development database workflow for live read-model verification:

- documented `acs_fsm_dev` local database assumptions
- local-only `ACS_FSM_DATABASE_URL` examples
- backend Make targets for local database checks, synthetic dashboard seed data, and read-only dashboard endpoint checks
- a dev-only dashboard seed script that refuses production, non-local hosts, and placeholder credentials
- frontend source labeling for successful backend reads as live backend data

The boundary is still development-only and read-only from the API/UI perspective. The seed script mutates only the explicit local development database when run by a developer; no dashboard endpoint or frontend component can create, update, dispatch, approve, reconcile, execute integrations, or call AI.

Unresolved:

- local PostgreSQL runtime installation remains external to the repository
- whether future integration testing should require a disposable PostgreSQL database
- production database provisioning, migration, backup, and restore workflows
- production dashboard stale-data, polling, and caching strategy

---

## Phase 0 Module 28 Local PostgreSQL Bootstrap And Live Dashboard Verification Boundary

Module 28 verifies the local development loop against a real PostgreSQL-backed dashboard API when the workstation already has a safe local PostgreSQL runtime available:

- local PostgreSQL service detection and readiness checks
- non-destructive creation of the missing `acs_fsm_dev` local role and database
- Alembic migration execution against the local development database
- synthetic dashboard seed insertion for read-model verification only
- read-only backend dashboard endpoint verification
- frontend `/dashboard` smoke verification in live-backend mode

The boundary remains development-only. The repository still does not install PostgreSQL, manage production services, create production secrets, deploy infrastructure, implement auth, expose mutation endpoints, execute dispatch, call vendors, or grant AI operational authority.

Implementation note:

- the local database check script now treats a missing `alembic_version` table as a reachable-but-unmigrated database instead of a connection failure

Unresolved:

- standard local PostgreSQL runtime choice for all future developer workstations
- whether future integration checks should use a dedicated disposable database
- production database provisioning and migration operations
- production frontend/backend routing, stale-data, cache, and authentication strategy

---

## Phase 0 Module 29 Local Live Dashboard Seed Quality Boundary

Module 29 improves the local live-dashboard verification foundation by expanding safe synthetic seed scenarios and validating that dashboard read models represent realistic persisted operational states.

The seed now exercises:

- dispatch-ready standard work
- Manual Review blockers and completed review states
- blocked dispatch and route-assignment states
- external adapter/execution/confirmation states without vendor calls
- retry, reconciliation, rollback, governance, accountability, and incident-preparation evidence without execution
- immutable operational event timelines
- open and closed Water Emergency records that remain separated from standard dispatch

The boundary remains read-model and local-development only. The frontend still displays backend state without business workflow logic, mutation controls, dispatch actions, Manual Review resolution, vendor execution, AI authority, or hidden lifecycle inference.

Unresolved:

- whether seed scenario labels should become formal UI storyboards
- whether seed data should later split into small scenario packs for focused QA
- whether production dashboard filters should mirror these local scenario categories

---

## Phase 0 Module 30 Live Dashboard Scenario Storyboard Boundary

Module 30 improves the read-only frontend dashboard visualization layer for Module 29 live seed scenarios:

- adds a `Scenario Storyboard` section that groups existing backend dashboard read-model counts into local QA scenario families
- improves scanability for dispatch-ready work, Manual Review, blockers, external execution, recovery/reconciliation, governance/accountability, Water Emergency separation, and immutable timeline evidence
- improves timeline interpretation with event-state labels, related record chips, and wrapped audit-correlation text
- improves anchor navigation on mobile and desktop so sticky headers do not cover section headings
- preserves live backend/fallback source labeling and synthetic-data caution text

The boundary remains frontend-only and read-only. The storyboard does not add backend schema fields, mutation routes, dispatch actions, Manual Review resolution, vendor execution, AI controls, or hidden lifecycle inference.

Unresolved:

- whether future production storyboards should be backend-provided formal scenario metadata instead of frontend grouping of existing counts
- whether Water Emergency needs a dedicated storyboard/API contract after its specialized workflow path exists
- how storyboards should interact with future authentication, role scoping, filters, pagination, and refresh cadence

---

## Phase 0 Module 31 Water Emergency Dashboard Read Model Boundary

Module 31 adds a dedicated read-only Water Emergency dashboard projection and frontend view:

- `GET /api/v1/dashboard/water-emergency` exposes a separated Water Emergency dashboard contract
- `DashboardReadModelService` summarizes existing Water Emergency records, status/stage distribution, equipment and moisture-tracking indicators, multi-visit evidence, review/escalation indicators, related references, data gaps, audit correlations, and timeline evidence
- the frontend fetches the dedicated Water Emergency read model separately from the standard operational overview
- the dashboard renders a dedicated Water Emergency section and navigation item so emergency work is not buried inside standard dispatch summaries

The boundary remains projection-only. The endpoint and UI do not create, close, resolve, approve, dispatch, integrate, reconcile, or execute Water Emergency workflows. They also do not call AI or infer hidden lifecycle transitions.

Unresolved:

- exact Water Emergency status and drying-stage taxonomy
- emergency equipment inventory and moisture-reading data models
- production filtering, pagination, and role-scoped Water Emergency visibility
- future authenticated Water Emergency workflow execution modules

---

## Phase 0 Module 32 Water Emergency Detail Read Model Boundary

Module 32 adds read-only Water Emergency detail visibility on top of the Module 31 summary contract:

- `GET /api/v1/dashboard/water-emergency/{water_emergency_id}` exposes one selected Water Emergency record detail
- the backend detail read model returns scoped job, work-order, visit, Manual Review, audit, and timeline evidence
- related Manual Review indicators must be tied to the selected record through job, entity, or visit linkage
- timeline entries are chronological evidence only and do not drive lifecycle transitions
- the frontend renders a dedicated detail/evidence section separated from standard dispatch summaries

The boundary remains projection-only. The endpoint and UI do not create, edit, close, resolve, approve, dispatch, integrate, replay, reconcile, or execute Water Emergency workflows. They also do not call AI or infer hidden lifecycle transitions.

Unresolved:

- user selection model for multiple Water Emergency records
- role-scoped access to emergency detail evidence
- production timeline filtering, pagination, and refresh behavior
- future equipment, moisture-reading, photo, and emergency-specific history models

---

## Phase 0 Module 33 Water Emergency Equipment And Visit Visibility Boundary

Module 33 extends Water Emergency summary/detail visibility with read-only equipment, visit-chain, and drying-stage context:

- backend read models expose equipment flags, required equipment notes, inventory-modeling unknowns, visit-chain counts/timestamps, and drying-stage context from persisted state
- frontend panels display those backend fields without creating workflow logic
- local synthetic seed data now includes a Water Emergency work-order equipment note, multi-visit chain, and drying-check event for live dashboard verification
- standard dispatch-ready counts exclude Water Emergency visits so emergency visit visibility does not become standard dispatch authority

The boundary remains projection-only. The endpoint and UI do not create, edit, close, resolve, approve, dispatch, integrate, replay, reconcile, manage equipment inventory, authorize pickup, or execute Water Emergency workflows. They also do not call AI or infer hidden lifecycle transitions.

Unresolved:

- final Water Emergency drying-stage/status taxonomy
- dedicated equipment inventory, deployment, pickup, and moisture-reading models
- field approval, closure readiness, and revisit scheduling rules
- role-scoped emergency workflow authority after authentication exists

---

## Phase 0 Module 34 Water Emergency Review And Alert Visibility Boundary

Module 34 extends Water Emergency summary/detail visibility with read-only Manual Review, exception, blocker, and critical-alert context:

- backend read models expose review/exception counts, reason buckets, blocker reason buckets, critical unresolved counts, escalation indicators, review IDs, and audit-correlation references from existing `ReviewItem` evidence
- detail read models expose the same context only for reviews scoped to the selected Water Emergency through job, entity, or visit linkage
- frontend panels display review/exception, critical-alert, and blocker/unknown context without creating Manual Review or Water Emergency action controls
- local synthetic seed data now includes Water Emergency open critical, deferred, and archived review examples plus an immutable review-exception evidence event

The boundary remains projection-only. The endpoint and UI do not create, edit, close, resolve, approve, reject, archive, dispatch, integrate, escalate, reconcile, or execute Water Emergency workflows. They also do not call AI or infer hidden lifecycle transitions.

Unresolved:

- final Water Emergency review/escalation taxonomy
- whether future exception and alert visibility should use typed fields instead of reason-code buckets
- production role-scoped Manual Review and Water Emergency authority after authentication exists
- future alert routing, notification, and escalation execution modules

---

## Phase 0 Module 35 Water Emergency Readiness Visibility Boundary

Module 35 extends Water Emergency summary/detail visibility with read-only next-step readiness context:

- backend read models expose readiness labels, explanation text, blocker/reason buckets, attention counts, and evidence references from existing persisted records
- unresolved scoped reviews produce Manual Review/operator-decision readiness labels
- missing work-order, visit, timeline, drying-stage, or next-action evidence produces blocked/missing-data readiness labels
- closed or resolved Water Emergency records produce no-active-next-step visibility
- ready-for-close-review is displayed as read-only evidence only and does not execute closure
- frontend panels display readiness context without creating Water Emergency action controls
- local synthetic seed data now includes readiness examples for Manual Review, equipment review, visit follow-up, missing data, ready-for-close-review, and closed/no-active-action states

The boundary remains projection-only. The endpoint and UI do not create, edit, close, resolve, approve, reject, archive, dispatch, schedule, integrate, escalate, reconcile, or execute Water Emergency workflows. They also do not call AI, define final operations taxonomy, or infer hidden lifecycle transitions.

Unresolved:

- final Water Emergency readiness and closure-review taxonomy
- whether future readiness should become persisted workflow state or remain a derived projection
- role-scoped readiness visibility and authority after authentication exists
- future Water Emergency action modules for operator-controlled visits, equipment pickup, drying confirmation, and closure review

---

## Phase 0 Module 36 Water Emergency Operator Queue Visibility Boundary

Module 36 extends Water Emergency summary visibility with read-only operator queue and attention grouping:

- backend read models expose operator queue items, queue-group counts, attention-label counts, attention ranks, reason codes, evidence references, review counts, critical-alert counts, blocker counts, unknown counts, related references, and audit-correlation IDs from existing persisted evidence
- queue groups are derived from Module 35 readiness evidence and do not introduce workflow execution
- critical-alert records sort ahead of lower-attention records, while closed/resolved records remain separated from active attention items
- frontend panels display queue/triage context without creating Water Emergency action controls
- local synthetic seed data now includes queue examples for critical attention, blocked/missing information, visit follow-up, equipment review, monitoring, close review, and closed/resolved records

The boundary remains projection-only. The endpoint and UI do not create, edit, close, resolve, approve, reject, archive, dispatch, schedule, prioritize as operational authority, integrate, escalate, reconcile, or execute Water Emergency workflows. They also do not call AI, define final operations taxonomy, or infer hidden lifecycle transitions.

Unresolved:

- final Water Emergency triage, priority, and queue taxonomy
- whether future queue labels should become persisted workflow state or remain derived read-model projections
- production filtering, pagination, stale-data behavior, and role-scoped queue visibility
- future authenticated Water Emergency action modules for operator-controlled visits, equipment review, drying confirmation, and closure review

---

## Phase 0 Module 37 Water Emergency Aging And Follow-Up Visibility Boundary

Module 37 extends Water Emergency summary visibility with read-only aging, follow-up risk, stale evidence, and unknown timing context:

- backend read models expose time-sensitivity labels, timing groups, age/follow-up buckets, timestamp references, reason codes, missing timestamp indicators, stale counts, related references, and audit-correlation IDs from existing persisted evidence
- labels are derived from Water Emergency opened/closed timestamps, related Visit timestamps, scoped Review timestamps, and related operational event timestamps
- open Manual Review evidence is shown as waiting-for-review timing context
- closed/resolved records remain separated from active timing risks and are never shown as active overdue work
- frontend panels display timing context without creating Water Emergency action controls
- local synthetic seed data now includes newly opened, active monitoring, follow-up due, follow-up overdue, stale evidence, waiting review, ready-for-close-review, closed/resolved, and unknown timing examples

The boundary remains projection-only. The endpoint and UI do not create, edit, close, resolve, approve, reject, archive, dispatch, schedule, escalate, enforce an SLA, integrate, reconcile, or execute Water Emergency workflows. They also do not call AI, define final operations taxonomy, or infer hidden lifecycle transitions.

Unresolved:

- final Water Emergency aging, follow-up, SLA, and stale-evidence taxonomy
- whether future timing labels should become persisted workflow state or remain derived read-model projections
- production filtering, pagination, refresh cadence, stale-data behavior, and role-scoped timing visibility
- future authenticated Water Emergency action modules for follow-up scheduling, equipment review, drying confirmation, escalation, and closure review

---

## Phase 0 Module 38 Water Emergency Filter/Sort View-State Boundary

Module 38 extends Water Emergency summary visibility with read-only filtering, sorting, grouping, and operator view-state clarity:

- backend read models expose available filter options, sort options, group counts, per-record filter memberships, primary filter groups, sort labels/ranks, last-activity timestamps, queue labels, timing labels, readiness labels, counts, references, and evidence IDs from existing persisted evidence
- filter groups are derived from Module 35 readiness, Module 36 queue/attention, and Module 37 aging/follow-up projections
- critical, review, blocker, follow-up, stale, close-review, unknown, active, and closed/resolved groups are visibility categories only
- frontend controls change only local dashboard display state and do not persist state or call mutation endpoints
- closed/resolved records remain visually separated from active records even when a filter or list limit is active

The boundary remains projection-only. The endpoint and UI do not create, edit, close, resolve, approve, reject, archive, dispatch, schedule, escalate, persist user preferences, integrate, reconcile, or execute Water Emergency workflows. They also do not call AI, define final operations taxonomy, or infer hidden lifecycle transitions.

Unresolved:

- final Water Emergency filtering, sorting, triage, and saved-view taxonomy
- whether filter metadata should remain derived read-model projections or become persisted user/role preferences later
- production pagination, refresh cadence, stale-data behavior, saved view defaults, and role-scoped filter visibility
- future authenticated Water Emergency action modules for follow-up scheduling, equipment review, drying confirmation, escalation, and closure review

---

## First Module Boundary

The first real implementation module is the Dispatch Operations Engine.

It should not attempt to build the full FSM immediately.

See [[12-Roadmap/MASTER_ROADMAP]] for phased scope.
