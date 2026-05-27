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

## Phase 0 Module 61 Master Documentation Baseline

Module 61 adds the durable master documentation package for the current architecture and phase transition plan:

- [[00-ACS-FSM-Master-System-Overview]]
- [[00-Phase-0-Module-Inventory]]
- [[00-Phase-Roadmap]]
- [[00-Phase-0-Completion-Checklist]]
- [[00-ACS-FSM-Risk-Register]]

This is a documentation/readiness baseline only. It does not change backend APIs, frontend behavior, auth enforcement, token verification, RBAC, route guarding, Manual Review action authority, Water Emergency action authority, dispatch execution, vendor calls, AI authority, or workflow execution.

The package records that Phase 0 has produced read-only foundations and safety boundaries, while production deployment, real auth/RBAC, controlled actions, dispatch execution, Water Emergency execution, and live external integrations remain future phases with explicit transition criteria.

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

## Phase 0 Module 39 Water Emergency Governance, View Preferences, And Scalability Boundary

Module 39 converts open Water Emergency taxonomy, saved-view, role-scope, and scalability concerns into explicit read-only architecture boundaries:

- Randall-authorized Phase 0 visibility baseline metadata is exposed through the Water Emergency dashboard read model.
- provisional filter groups, attention labels, timing labels, and readiness labels remain internal software visibility metadata.
- timing/follow-up labels remain conservative heuristics, not final SLA enforcement.
- Alfonso owner review is required for formal legal, insurance, compliance, warranty, drying certification, customer-facing, or company-liability policy.
- frontend saved view preferences are limited to selected filter and sort order in browser localStorage.
- saved preferences do not store secrets, tokens, PII, customer data, backend records, or workflow state.
- result-window metadata prepares future pagination/query scaling without changing current query semantics.
- future roles are documented as office_admin, operations_manager, dispatcher, reviewer, technician, and owner, but no auth or RBAC is implemented.

The boundary remains visibility-only. The endpoint and UI do not create, edit, close, resolve, approve, reject, archive, dispatch, schedule, escalate, enforce SLA rules, implement auth, implement RBAC, integrate with vendors, or execute Water Emergency workflows. They also do not call AI, define final legal policy, or infer hidden lifecycle transitions.

Unresolved:

- Alfonso owner review for final legal, insurance, warranty, drying certification, SLA, or customer-facing policy
- future authenticated role-scoped visibility and authority
- future backend-persisted saved views for named users or roles
- future production pagination, query optimization, refresh cadence, and stale-data rules

---

## Phase 0 Module 40 Manual Review Queue Visibility Boundary

Module 40 extends dashboard visibility with a dedicated read-only Manual Review queue detail contract:

- backend read models expose queue items, status counts, reason counts, severity counts, visibility group counts, age buckets, active-attention counts, blocker counts, entity links, Water Emergency links when specifically tied to the item, audit-correlation IDs, and evidence references from existing persisted ReviewItem evidence
- queue groups are Randall-authorized Phase 0 visibility labels only
- Water Emergency-related review items are separated from standard dispatch and other review items
- resolved and archived review items remain historical visibility and are not counted as active attention records
- frontend panels display Manual Review queue context without creating approve, reject, defer, archive, resolve, dispatch, vendor, or AI controls

The boundary remains projection-only. The endpoint and UI do not execute Manual Review actions, mutate review records, dispatch work, call external integrations, add AI authority, implement auth/RBAC, or infer hidden workflow transitions.

Unresolved:

- future authenticated Manual Review action workflow
- final Manual Review reason/action taxonomy
- role-scoped review visibility and authority after authentication exists
- production pagination, query optimization, refresh cadence, and stale-data rules for large review queues

---

## Phase 0 Module 41 Manual Review Detail Visibility Boundary

Module 41 extends Manual Review dashboard visibility with a read-only single-item detail contract:

- backend read models return one selected ReviewItem as a queue item plus reason/evidence context, linked entity context, data-gap counts, audit-correlation IDs, taxonomy metadata, and related timeline evidence
- linked entity context is derived only from persisted ReviewItem links and existing job, work-order, visit, route-assignment, and Water Emergency records
- Water Emergency-related review details remain visually and architecturally separated from standard dispatch review details
- timeline entries are ordered by the backend read model and preserve audit/correlation references
- missing review IDs return a safe not-found response instead of mock success

The boundary remains projection-only. The detail endpoint and UI do not execute Manual Review actions, mutate review records, dispatch work, call external integrations, add AI authority, implement auth/RBAC, or infer hidden workflow transitions.

Unresolved:

- future authenticated Manual Review approve/reject/defer/archive workflows
- final Manual Review action taxonomy and role authority
- production review detail pagination or event-window limits for very large timelines
- formal legal, insurance, compliance, or company-liability policy if future detail language becomes customer-facing

---

## Phase 0 Module 42 Manual Review Filter/Sort View-State Boundary

Module 42 extends Manual Review queue visibility with read-only filtering, sorting, frontend saved view preferences, and queue result metadata:

- backend read models expose available Manual Review filter options, sort options, result-window metadata, and counts from existing ReviewItem evidence
- filter groups include all, open, deferred, resolved, archived, active attention, Water Emergency-related, dispatch-related, missing data, duplicate/conflict, cancellation/status uncertainty, and needs operator review
- frontend controls change only local dashboard view state and preserve Water Emergency-related review separation
- frontend saved preferences are limited to selected Manual Review filter and sort order in browser storage, with safe in-memory fallback when storage is unavailable
- open/active Manual Review items remain visible unless the operator explicitly chooses a narrower local view filter

The boundary remains projection and view-state only. The endpoint and UI do not execute Manual Review actions, mutate review records, persist backend preferences, dispatch work, call external integrations, add AI authority, implement auth/RBAC, or infer hidden workflow transitions.

Unresolved:

- future authenticated Manual Review approve/reject/defer/archive workflows
- final Manual Review filter/action taxonomy and role authority
- whether saved view preferences should later move from browser-only storage to backend user preferences
- production query parameters, pagination, refresh cadence, stale-data behavior, and role-scoped visibility for large review queues

---

## Phase 0 Module 43 Manual Review Decision-Readiness Boundary

Module 43 extends Manual Review queue and detail visibility with read-only decision-readiness and resolution-preparation context:

- backend read models expose deterministic readiness labels, summaries, reason codes, evidence references, active-decision flags, and resolution-candidate flags from existing ReviewItem evidence
- Water Emergency-related readiness is separated from standard dispatch readiness through persisted job, visit, entity, and Water Emergency links
- missing-data, conflict, unknown entity context, dispatch-related, Water Emergency-related, active decision, resolution review, and resolved/archived states are visible without becoming action authority
- frontend queue and detail panels display readiness context as read-only evidence and do not add workflow controls
- resolved and archived review items remain historical visibility rather than active decision needs

The boundary remains projection-only. The endpoint and UI do not execute Manual Review actions, mutate review records, dispatch work, call external integrations, add AI authority, implement auth/RBAC, or infer hidden workflow transitions.

Unresolved:

- future authenticated Manual Review approve/reject/defer/archive/resolve workflows
- final Manual Review readiness/action taxonomy and role authority
- whether future action workflows need dedicated review transition history tables
- production role-scoped visibility and refresh cadence for review detail views

---

## Phase 0 Module 44 Manual Review Action-Preflight Boundary

Module 44 extends Manual Review queue and detail visibility with read-only action authorization readiness and preflight context:

- backend read models expose deterministic action-preflight labels, summaries, blocker codes, future requirement labels, evidence references, and explicit non-executable flags from existing ReviewItem evidence
- future-only requirements identify that real actions will need auth, operator identity, and audit reason capture later
- Water Emergency-related action preflight is separated from standard dispatch review preparation through persisted job, visit, entity, and Water Emergency links
- missing entity context, missing data, duplicate/conflict evidence, Water Emergency context, resolved/archived status, and unknown eligibility remain blockers or visibility states instead of executable actions
- frontend queue and detail panels display preflight context as read-only evidence and do not add workflow controls

The boundary remains projection-only. The endpoint and UI do not execute Manual Review actions, mutate review records, implement auth/RBAC, dispatch work, call external integrations, add AI authority, or infer hidden workflow transitions.

Unresolved:

- future authenticated Manual Review approve/reject/defer/archive/resolve workflows
- final Manual Review action eligibility taxonomy and role authority
- operator identity capture, audit reason requirements, and action-history persistence
- production role-scoped action visibility and permission design

---

## Phase 0 Module 45 Manual Review Future-Action Preview Boundary

Module 45 extends Manual Review queue and detail visibility with read-only future-action preview and expected outcome preparation context:

- backend read models expose deterministic future-action preview labels, descriptions, expected non-binding outcome summaries, impacted entity references, blocker codes, future requirement labels, evidence references, and explicit non-executable flags from existing ReviewItem evidence
- every future-action preview remains `is_currently_executable = false`
- future-only requirements continue to identify that real actions will need auth, operator identity, and audit reason capture later
- Water Emergency-related future-action preview is separated from standard dispatch review preparation through persisted job, visit, entity, and Water Emergency links
- missing entity context, missing data, duplicate/conflict evidence, Water Emergency context, resolved/archived status, and unknown preview evidence remain blockers or visibility states instead of executable actions
- frontend queue and detail panels display preview context as read-only evidence and do not add workflow controls or button-styled preview labels

The boundary remains projection-only. The endpoint and UI do not execute Manual Review actions, mutate review records, implement auth/RBAC, dispatch work, call external integrations, add AI authority, create audit/action history, or infer hidden workflow transitions.

Unresolved:

- future authenticated Manual Review approve/reject/defer/archive/resolve workflows
- final Manual Review future-action preview taxonomy and role authority
- operator identity capture, audit reason requirements, action-history persistence, and impacted-entity audit writes
- production role-scoped action visibility and permission design

---

## Phase 0 Module 46 Manual Review Command-Contract Boundary

Module 46 extends Manual Review queue and detail visibility with read-only future command-contract and audit-envelope preparation context:

- backend read models expose deterministic command-contract labels, summaries, future command candidates, required contract labels, impacted entity references, blocker codes, evidence references, explicit non-executable flags, and future audit-envelope requirement flags from existing ReviewItem evidence
- every command contract remains `is_currently_executable = false`
- every future command contract requires future auth, operator identity, role authorization, audit reason, idempotency key, immutable event recording, and post-action consistency checks
- Water Emergency-related command contracts require Water Emergency scope checks and remain separated from standard dispatch review preparation through persisted job, visit, entity, and Water Emergency links
- missing entity context, missing data, duplicate/conflict evidence, Water Emergency context, resolved/archived status, and unknown command evidence remain blockers or visibility states instead of executable actions
- frontend queue and detail panels display command-contract context as read-only evidence and do not add forms, inputs, workflow controls, or button-styled command labels

The boundary remains projection-only. The endpoint and UI do not execute Manual Review commands, mutate review records, create POST/PUT/PATCH/DELETE endpoints, implement auth/RBAC, dispatch work, call external integrations, add AI authority, create audit/action history, persist idempotency keys, or infer hidden workflow transitions.

Unresolved:

- future authenticated Manual Review command execution workflows
- final Manual Review command taxonomy and role authority
- operator identity capture, role authorization, audit reason requirements, idempotency persistence, immutable event writes, post-action consistency checks, and action-history persistence
- production role-scoped action visibility and permission design

---

## Phase 0 Module 47 Manual Review Audit-Ledger Dry-Run Boundary

Module 47 extends Manual Review queue and detail visibility with read-only audit-ledger preparation, command dry-run, immutable-event, and idempotency-readiness context:

- backend read models expose deterministic dry-run labels, proposed future event type/state, proposed audit envelope fields, idempotency scope, consistency-check summary, evidence references, explicit non-executable flags, and Phase 0 execution-blocked flags from existing ReviewItem evidence
- every dry-run record remains `is_currently_executable = false` and `phase_allows_execution = false`
- every future dry-run requires audit reason, operator identity, role authorization, idempotency key, immutable event recording, and post-action consistency checks
- Water Emergency-related dry-runs require Water Emergency scope checks and remain separated from standard dispatch review preparation through persisted job, visit, entity, and Water Emergency links
- missing entity context, duplicate/conflict evidence, Water Emergency context, resolved/archived status, and unknown dry-run evidence remain blockers or visibility states instead of executable actions
- frontend queue and detail panels display dry-run context as read-only evidence and do not add forms, inputs, workflow controls, audit-write controls, or button-styled dry-run labels

The boundary remains projection-only. The endpoint and UI do not execute Manual Review commands, mutate review records, write audit events, create POST/PUT/PATCH/DELETE endpoints, implement auth/RBAC, persist idempotency keys, dispatch work, call external integrations, add AI authority, create action history, or infer hidden workflow transitions.

Unresolved:

- future authenticated Manual Review command execution workflows
- final Manual Review dry-run/action taxonomy and role authority
- operator identity capture, role authorization, audit reason requirements, idempotency persistence, immutable event writes, post-action consistency checks, audit-ledger persistence, and action-history persistence
- production role-scoped action visibility and permission design

---

## Phase 0 Module 48 Manual Review Command-Validation Boundary

Module 48 extends Manual Review queue and detail visibility with read-only command validation and safety-gate matrix context:

- backend read models expose deterministic validation labels, validation status, validation blockers, validation warnings, candidate future command type, safety gates, evidence references, explicit non-executable flags, and Phase 0 execution-blocked flags from existing ReviewItem evidence
- every validation record remains `is_currently_executable = false` and `phase_allows_execution = false`
- every future validation record requires audit reason, operator identity, role authorization, idempotency key, immutable event recording, post-action consistency checks, and linked entity context
- the `phase_allows_execution` safety gate is always false in Phase 0
- Water Emergency-related validation requires Water Emergency scope checks and remains separated from standard dispatch review preparation through persisted job, visit, entity, and Water Emergency links
- missing entity context, duplicate/conflict evidence, Water Emergency context, resolved/archived status, and unknown validation evidence remain blockers or visibility states instead of executable actions
- frontend queue and detail panels display validation and safety gates as read-only evidence and do not add forms, inputs, workflow controls, validation execution controls, audit-write controls, or button-styled gate labels

The boundary remains projection-only. The endpoint and UI do not execute Manual Review commands, mutate review records, validate commands for current execution, write audit events, create POST/PUT/PATCH/DELETE endpoints, implement auth/RBAC, persist idempotency keys, dispatch work, call external integrations, add AI authority, create action history, or infer hidden workflow transitions.

Unresolved:

- future authenticated Manual Review command validation/execution workflows
- final Manual Review validation/action taxonomy and role authority
- operator identity capture, role authorization, audit reason requirements, idempotency persistence, immutable event writes, post-action consistency checks, audit-ledger persistence, safety-gate persistence, and action-history persistence
- production role-scoped action visibility and permission design

---

## Phase 0 Module 49 Manual Review Operator-Identity And Permission Boundary

Module 49 extends Manual Review queue and detail visibility with read-only operator-identity, role-authorization, and permission-readiness context:

- backend read models expose deterministic permission-readiness labels, future command candidate, future required roles, forbidden roles, future permission set, identity requirement labels, evidence references, explicit non-executable flags, and Phase 0 execution-blocked flags from existing ReviewItem evidence
- every permission-readiness record remains `is_currently_executable = false` and `phase_allows_execution = false`
- every future permission-readiness record requires future auth, operator identity, role authorization, audit actor, audit reason, idempotency key, immutable event recording, and post-action consistency checks
- service accounts, technicians, and unknown operators are not future Manual Review operator-action actors
- Water Emergency-related authorization requirements require Water Emergency scope checks and remain separated from standard dispatch review preparation through persisted job, visit, entity, and Water Emergency links
- missing entity context, Water Emergency context, resolved/archived status, and unknown operator context remain blockers or visibility states instead of executable actions
- frontend queue and detail panels display future authorization boundary context as read-only evidence and do not add login UI, user-management UI, forms, inputs, workflow controls, auth/RBAC controls, or button-styled permission labels

The boundary remains projection-only. The endpoint and UI do not execute Manual Review commands, mutate review records, validate commands for current execution, write audit events, create POST/PUT/PATCH/DELETE endpoints, implement auth/RBAC, create login/session/token behavior, persist idempotency keys, dispatch work, call external integrations, add AI authority, create action history, or infer hidden workflow transitions.

Unresolved:

- future authenticated Manual Review command validation/execution workflows
- final ACS-FSM auth provider and operator identity schema
- durable RBAC/permission model and role-scoped action authority
- operator identity capture, role authorization, audit actor, audit reason, idempotency, immutable event, post-action consistency, audit-ledger persistence, safety-gate persistence, and action-history persistence

---

## Phase 0 Module 50 Manual Review Execution-Readiness And Mutation-Boundary

Module 50 consolidates the Manual Review readiness layers from Modules 40-49 into a read-only execution-readiness audit and transition-plan boundary:

- backend read models expose queue-level counts for active, resolved/archived, Water Emergency-related, dispatch-related, missing-entity, conflict, missing-data, preview, command-contract, dry-run, safety-gate, permission-readiness, Phase 0 blocked, and future auth/RBAC/audit/idempotency/immutable-event/consistency requirements
- the mutation-boundary lock reports `manual_review_mutations_enabled = false`, `action_execution_phase = read_only_phase_0`, `currently_executable_count = 0`, and `mutation_endpoints_available = false`
- future transition prerequisites remain planned or blocked until real auth, RBAC, audit envelope, idempotency, immutable event writing, rollback/replay, consistency checks, action contracts, action UI review, stakeholder reporting, and Review GUI/ChatGPT review are satisfied
- liability-sensitive Manual Review actions require Alfonso owner review before any binding legal, insurance, warranty, drying certification, formal policy, customer-facing, or billing/financial behavior exists
- Water Emergency-related readiness remains separated from standard Manual Review readiness through persisted job, visit, entity, and Water Emergency links
- frontend queue panels display the audit and mutation boundary as read-only evidence and do not add login UI, user-management UI, forms, inputs, workflow controls, auth/RBAC controls, mutation controls, or button-styled readiness labels

The boundary remains projection-only. The endpoint and UI do not execute Manual Review commands, mutate review records, validate commands for current execution, write audit events, create POST/PUT/PATCH/DELETE endpoints, implement auth/RBAC, create login/session/token behavior, persist idempotency keys, dispatch work, call external integrations, add AI authority, create action history, or infer hidden workflow transitions.

Unresolved:

- future authenticated Manual Review command validation/execution workflows
- final ACS-FSM auth provider and operator identity schema
- durable RBAC/permission model and role-scoped action authority
- approved audit envelope, idempotency, immutable event, rollback/replay, and post-action consistency strategies
- owner-reviewed legal, insurance, warranty, certification, policy, and financial action boundaries

---

## Phase 0 Module 51 Manual Review Auth-Boundary Readiness

Module 51 starts the controlled transition toward future auth/RBAC modules by adding read-only auth-boundary readiness metadata without implementing auth:

- backend read models expose future operator identity registry fields, metadata-only registry mode, provisional role catalog, future permission catalog, service-account prohibition, and explicit auth/RBAC/action-execution false flags
- `auth_implemented`, `rbac_enforced`, `login_ui_available`, and `action_execution_available` remain false
- `operator_identity_registry_available` remains false because no operator identities are persisted in Phase 0
- service accounts, technicians, and unknown operators are not future Manual Review operator-action actors under the current baseline
- frontend queue and detail panels display the catalog metadata as read-only evidence and do not add login/signup/user-management UI, role assignment UI, auth headers, token/session behavior, role enforcement, action controls, or button-styled role/permission labels
- Water Emergency-related authorization and future action scope remain separated from standard Manual Review readiness

The boundary remains projection-only. The endpoint and UI do not authenticate users, enforce RBAC, persist identities, create fake users, hide UI based on fake roles, execute Manual Review commands, mutate review records, write audit events, create POST/PUT/PATCH/DELETE endpoints, persist idempotency keys, dispatch work, call external integrations, add AI authority, create action history, or infer hidden workflow transitions.

Unresolved:

- final ACS-FSM auth provider and credential ownership
- durable operator identity registry schema
- approved RBAC role model and permission taxonomy
- role-scoped Manual Review visibility and action authority after authentication exists
- future authenticated Manual Review command validation/execution workflows

---

## Phase 0 Module 52 Auth Provider Configuration And Environment Safety

Module 52 extends the read-only auth boundary with a future provider configuration contract and environment safety baseline:

- backend read models expose auth configuration readiness metadata as deterministic planning visibility
- `auth_provider_configured`, `token_verification_enabled`, `rbac_enforcement_enabled`, `login_ui_available`, and `frontend_auth_config_available` remain false
- the current provider and local dev auth mode are `disabled`
- backend placeholder names use the existing `ACS_FSM_` settings namespace and include `ACS_FSM_AUTH_PROVIDER`, `ACS_FSM_AUTH_ENABLED`, issuer, audience, JWKS, allowed-domain, verified-email, local-dev-mode, role-claim, and permission-claim placeholders
- frontend placeholder names use public `NEXT_PUBLIC_ACS_AUTH_*` labels for future UI configuration only
- safe placeholders are committed in example files, but real credentials, `.env`, `.env.local`, service account JSON, private keys, and tokens remain forbidden from source control
- Randall controls future provider technical configuration; Alfonso owner review remains required only for legal, insurance, compliance, contractual, financial-liability, customer-liability, or formal company-policy consequences
- frontend queue and detail panels display auth configuration readiness as read-only evidence and do not add login/logout UI, auth headers, token/session behavior, fake authenticated users, forms, inputs, role assignment, or button-styled auth labels

The boundary remains projection-only. The endpoint and UI do not authenticate users, verify tokens, enforce RBAC, persist identities, create fake users, hide UI based on roles, execute Manual Review commands, mutate review records, write audit events, create POST/PUT/PATCH/DELETE endpoints, dispatch work, call external integrations, add AI authority, create action history, or infer hidden workflow transitions.

Unresolved:

- final ACS-FSM auth provider selection and production credential ownership
- secure VPS secret configuration and local development auth mode
- token verification dependencies, auth middleware, RBAC enforcement, role-scoped visibility, and authenticated Manual Review action authority

---

## Phase 0 Module 53 Auth Diagnostics, Secret Hygiene, And Runtime Safety

Module 53 extends the read-only auth boundary with diagnostics and secret-hygiene visibility without implementing auth:

- backend read models expose runtime auth diagnostics as deterministic planning visibility
- `auth_enabled`, `token_verification_enabled`, `rbac_enforcement_enabled`, `login_ui_available`, `auth_headers_required`, and `auth_headers_emitted_by_frontend` remain false
- `runtime_auth_mode` remains `read_only_phase_0`
- secret-hygiene status is exposed as booleans only for tracked `.env`, `.env.local`, service account JSON, private key detection, and placeholder-only examples
- `backend/scripts/check_auth_config_safety.py` can inspect tracked/example files and report safe JSON without printing credential values, contacting services, or mutating files
- frontend queue and detail panels display auth diagnostics as read-only evidence and do not add login/logout UI, auth headers, token/session behavior, fake authenticated users, forms, inputs, role assignment, or button-styled auth labels

The boundary remains projection-only. The endpoint, helper, and UI do not authenticate users, verify tokens, enforce RBAC, persist identities, create fake users, hide UI based on roles, execute Manual Review commands, mutate review records, write audit events, create POST/PUT/PATCH/DELETE endpoints, dispatch work, call external integrations, add AI authority, create action history, print secrets, or infer hidden workflow transitions.

Unresolved:

- final ACS-FSM auth provider selection and production credential ownership
- secure VPS secret configuration and local development auth mode
- token verification dependencies, auth middleware, RBAC enforcement, role-scoped visibility, and authenticated Manual Review action authority

---

## Phase 0 Module 54 Auth Claims Mapping, Token Dry-Run, And Role Resolution

Module 54 extends the read-only auth boundary with future claims mapping and role-resolution planning metadata without implementing auth:

- backend read models expose future subject, email, email verification, display name, role, permission, provider, issuer, audience, tenant/domain, expiration, issued-at, and auth-time claim labels as deterministic planning metadata
- token-verification dry-run visibility is available as metadata, but `token_verification_enabled`, `real_token_parsing_enabled`, `jwks_fetch_enabled`, `auth_headers_required`, and `auth_headers_emitted_by_frontend` remain false
- role-resolution metadata maps unknown roles to `unknown_operator`, blocks service-account/system-service roles for Manual Review operator actions, and keeps technician Manual Review action authority blocked unless a future reviewed module authorizes it
- safe example claim fixtures use placeholder-only `example.com` scope and do not include real user data, real tokens, private keys, service account JSON, credentials, or JWT-like strings
- frontend queue and detail panels display claims mapping, dry-run, and role-resolution readiness as read-only evidence and do not add login/logout UI, auth headers, token/session behavior, fake authenticated users, forms, inputs, role assignment, or button-styled auth labels

The boundary remains projection-only. The endpoint and UI do not authenticate users, parse request tokens, verify tokens, fetch JWKS, enforce RBAC, persist identities, create fake users, hide UI based on roles, execute Manual Review commands, mutate review records, write audit events, create POST/PUT/PATCH/DELETE endpoints, dispatch work, call external integrations, add AI authority, create action history, or infer hidden workflow transitions.

Unresolved:

- final ACS-FSM provider claim names and production credential ownership
- token verification middleware, JWKS strategy, RBAC enforcement, role-to-permission expansion, role-scoped visibility, and authenticated Manual Review action authority

---

## Phase 0 Module 55 Route Protection Matrix And Access Decision Dry-Run

Module 55 extends the read-only auth boundary with future route protection, access decision dry-run, and UI permission-boundary planning metadata without implementing auth or route protection:

- backend read models expose current dashboard API routes, frontend sections, and future action surfaces as deterministic planning metadata
- route items expose future auth requirements, future RBAC requirements, future roles, future permissions, denied future roles, Manual Review sensitivity, Water Emergency sensitivity, mutation sensitivity, and owner-review flags
- access decision dry-run metadata reports simulated readiness counts only; `enforcement_enabled`, `phase_allows_enforcement`, `route_guarding_enabled`, `token_verification_enabled`, and `rbac_enforcement_enabled` remain false
- Manual Review queue/detail mappings use future `manual_review.view` and `manual_review.detail.view` permission labels without granting action authority
- Water Emergency dashboard/detail mappings use future Water Emergency read labels and remain separated from standard Manual Review and dispatch visibility
- future mutation surfaces remain non-executable and continue to require auth, RBAC, audit envelope, idempotency, immutable events, post-action consistency checks, and review workflow before implementation
- frontend queue and detail panels display route protection and access decision readiness as read-only evidence and do not add login/logout UI, auth headers, token/session behavior, fake authenticated users, forms, inputs, route guards, role assignment, section hiding, or button-styled access labels

The boundary remains projection-only. The endpoint and UI do not authenticate users, parse or validate JWTs, fetch JWKS, enforce route protection, enforce RBAC, hide UI based on roles, execute Manual Review commands, mutate review records, write audit events, create POST/PUT/PATCH/DELETE endpoints, dispatch work, call external integrations, add AI authority, create action history, or infer hidden workflow transitions.

Unresolved:

- final ACS-FSM route guard architecture, frontend section-hiding policy, token verification middleware, JWKS strategy, RBAC enforcement, role-to-permission expansion, role-scoped visibility, and authenticated Manual Review action authority

## Phase 0 Module 56 Auth/RBAC Readiness Audit And Enforcement Boundary

Module 56 consolidates the read-only auth/RBAC readiness layers from Modules 51-55 into a final Phase 0 readiness checkpoint without implementing auth, RBAC, route protection, or actions:

- backend read models expose an Auth/RBAC readiness audit that summarizes auth disabled, token verification disabled, real token parsing disabled, JWKS fetch disabled, RBAC disabled, route guarding disabled, auth headers not required/emitted, operator identity metadata-only, role/permission catalogs available, claims mapping available, route protection matrix available, access dry-run available, secret hygiene helper available, committed credentials disallowed, service accounts blocked, technicians blocked, and action execution unavailable
- an enforcement-boundary lock explicitly reports auth enforcement, token verification, real token parsing, JWKS fetch, RBAC enforcement, route guarding, sign-in UI, user management, action execution, mutation endpoints, and Phase 0 enforcement allowances as false
- future transition prerequisites are grouped for provider selection, real credentials/secret hygiene, token verification, claims mapping, operator identity, RBAC/role policy, route protection, Manual Review action permissions, Water Emergency action permissions, audit actor/idempotency, owner review, and review workflow
- frontend Manual Review queue panels display the audit, lock, and prerequisite groups as read-only evidence and do not add login/logout UI, user management UI, forms, inputs, auth headers, token/session behavior, route guards, role assignment, section hiding, or button-styled gate labels
- Water Emergency action permissions remain separated from standard Manual Review action readiness and owner-review flags remain visible where legal, insurance, warranty, billing, customer promise, or company-liability policy could be affected

The boundary remains projection-only. The endpoint and UI do not authenticate users, parse or validate JWTs, fetch JWKS, enforce route protection, enforce RBAC, hide UI based on roles, execute Manual Review commands, mutate review records, write audit events, create POST/PUT/PATCH/DELETE endpoints, dispatch work, call external integrations, add AI authority, create action history, or infer hidden workflow transitions.

Unresolved:

- final ACS-FSM auth provider, real secret provisioning, token verification middleware, JWKS strategy, route guard architecture, RBAC enforcement, role-to-permission expansion, role-scoped visibility, audit actor/idempotency integration, authenticated Manual Review action authority, Water Emergency action authority, and owner-reviewed legal/company policy

## Phase 0 Module 57 Backend Auth Core Disabled Scaffold

Module 57 adds backend auth core scaffolding without implementing auth, token verification, RBAC, route protection, or actions:

- backend `app/auth/` defines typed auth mode/provider/status, principal/context, disabled auth context, anonymous Phase 0 principal, and token verification result structures
- the disabled token verifier returns deterministic not-verified results, records only redacted header presence, and never parses token content, validates signatures, fetches JWKS, contacts providers, or treats any token as valid
- optional auth context helpers remain anonymous, non-authenticated, non-RBAC, non-enforcing, and grant no Manual Review or Water Emergency action authority
- strict future-auth helper behavior is not wired to current routes and only reports that auth enforcement is not implemented
- dashboard readiness metadata reports the auth core scaffold, disabled token verifier, optional auth context, current route auth requirement, route protection enforcement, and action authority boundaries as read-only evidence
- frontend queue panels display this disabled-auth-core visibility without login/logout UI, user management UI, role assignment, auth headers, token/session behavior, JWT parsing, route guards, section hiding, action buttons, forms, or mutation controls

The boundary remains non-enforcing. Current routes remain public read-only routes. Authorization header presence does not authenticate a user, grant RBAC, hide or unlock UI, execute Manual Review commands, mutate records, write audit events, dispatch work, call external integrations, add AI authority, create action history, or infer hidden workflow transitions.

Unresolved:

- final ACS-FSM auth provider, token verification middleware, JWKS strategy, route guard architecture, RBAC enforcement, role-to-permission expansion, role-scoped visibility, audit actor/idempotency integration, authenticated Manual Review action authority, Water Emergency action authority, and owner-reviewed legal/company policy

## Phase 0 Module 58 Frontend Auth Core Disabled Session Scaffold

Module 58 adds frontend auth core scaffolding without implementing login, sessions, token behavior, auth header emission, RBAC, route protection, or actions:

- frontend `src/lib/auth/` defines typed frontend auth mode/provider/status, principal/session/token-state, disabled session, and anonymous Phase 0 principal structures
- the disabled session adapter returns deterministic unauthenticated state with auth disabled, session unavailable, token unavailable, token verification disabled, RBAC unenforced, route protection unenforced, and Phase 0 enforcement disabled
- the API auth-boundary helper returns an empty header object and the dashboard API client remains GET-only with no Authorization header emission
- Manual Review queue panels display disabled frontend auth/session/API boundary visibility without sign-in/sign-out UI, user management UI, role assignment, token storage, JWT parsing, section hiding, action buttons, forms, or mutation controls

The boundary remains non-enforcing. Frontend auth labels do not authenticate a user, grant RBAC, hide or unlock UI, execute Manual Review commands, mutate records, write audit events, dispatch work, call external integrations, add AI authority, create action history, or infer hidden workflow transitions.

Unresolved:

- final ACS-FSM frontend login/session UX, backend token verification middleware, route guard architecture, RBAC enforcement, role-scoped visibility, audit actor/idempotency integration, authenticated Manual Review action authority, Water Emergency action authority, and owner-reviewed legal/company policy

## Phase 0 Module 59 Backend/Frontend Auth Status Bridge

Module 59 adds a cross-layer disabled auth status bridge without implementing auth, token verification, RBAC, route protection, login/session behavior, or actions:

- backend `GET /api/v1/auth/status` returns disabled Phase 0 auth status with auth disabled, provider disabled, token verification disabled, RBAC disabled, route protection not enforced, current routes not requiring auth, Authorization headers not required or parsed, and action authority unavailable
- frontend dashboard API contracts and client helper consume the status with a GET-only call and no Authorization header emission
- Manual Review queue panels display backend/frontend disabled auth alignment without sign-in/sign-out UI, user management UI, role assignment, token storage, JWT parsing, section hiding, action buttons, forms, or mutation controls
- fallback auth status remains disabled if the endpoint is unavailable and does not become a fake login/status success path

The boundary remains non-enforcing. Current routes remain public read-only routes. Authorization header presence does not authenticate a user, grant RBAC, hide or unlock UI, execute Manual Review commands, mutate records, write audit events, dispatch work, call external integrations, add AI authority, create action history, or infer hidden workflow transitions.

Unresolved:

- final ACS-FSM frontend login/session UX, backend token verification middleware, JWKS strategy, route guard architecture, RBAC enforcement, role-scoped visibility, audit actor/idempotency integration, authenticated Manual Review action authority, Water Emergency action authority, and owner-reviewed legal/company policy

## Phase 0 Module 60 Auth Boundary Completion Audit And Future Cutover Plan

Module 60 consolidates Modules 51-59 into a final read-only Phase 0 auth boundary completion checkpoint without implementing auth, token verification, RBAC, route protection, login/session behavior, or actions:

- backend `GET /api/v1/auth/status` now reports `phase0_auth_boundary_complete = true`, while auth implementation, auth enabled state, token verification, real token parsing, JWKS fetch, RBAC, route guarding, login UI, user management, mutation endpoints, and action authority remain false
- the status contract includes a future auth cutover checklist and blocker list; real cutover remains unavailable until provider selection, credentials outside Git, secret management, token verification, RBAC, route guarding, audit/idempotency/event controls, action workflows, staging tests, ACSSDR reporting, and Review GUI/ChatGPT review are completed in future reviewed modules
- the status contract includes a current route accessibility audit for the health, auth status, dashboard, Manual Review, dispatch, and Water Emergency read-only GET surfaces; current routes do not require auth and enforcement remains disabled
- frontend Manual Review queue panels display auth boundary completion, future cutover-not-ready state, current route accessibility, and prerequisite visibility without sign-in/sign-out UI, user management UI, role assignment, token storage, JWT parsing, section hiding, action buttons, forms, or mutation controls

The boundary remains non-enforcing. Authorization header presence does not authenticate a user, grant RBAC, guard routes, hide or unlock UI, execute Manual Review commands, mutate records, write audit events, dispatch work, call external integrations, add AI authority, create action history, or infer hidden workflow transitions.

Unresolved:

- final ACS-FSM provider selection, production secret storage, frontend login/session UX, backend token verification middleware, JWKS strategy, route guard architecture, RBAC enforcement, role-scoped visibility, audit actor/idempotency integration, immutable action events, authenticated Manual Review action authority, Water Emergency action authority, and owner-reviewed legal/company policy

---

## First Module Boundary

The first real implementation module is the Dispatch Operations Engine.

It should not attempt to build the full FSM immediately.

See [[12-Roadmap/MASTER_ROADMAP]] for phased scope.
