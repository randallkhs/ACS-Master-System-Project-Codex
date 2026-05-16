# ACS FSM — Codex Decisions Log

This log records major architecture, workflow, implementation, and documentation decisions for the ACS FSM platform.

Use this file for durable decisions that affect future development. Do not record trivial edits or one-time debugging noise.

---

## 2026-05-15 — Pre-Implementation Architecture Ingestion Baseline

- Decision type: Architecture / workflow / AI operating policy
- Status: Accepted planning baseline
- Context:
  - The project is in pre-implementation planning for the long-term ACS Field Service Management platform.
  - The repository currently contains documentation and vault structure, not production backend/frontend implementation.
  - External folders are references only unless explicitly authorized.
- Decision:
  - Treat `docs/obsidian-vault/` as the primary project architecture vault.
  - Treat `docs/codex-system/AI_MEMORY_SYSTEM/` as the project AI memory and documentation-standard reference.
  - All production implementation must occur inside `ACS-Workflow-Master-System`.
  - `ACS-Home-Page-Project` is a public website/template reference only.
  - `ACS-dashboardpack-admindek` is dashboard/UI inspiration and possible component reference only; do not copy blindly.
- Rationale:
  - The ACS FSM is intended as a long-term operational platform, not a temporary automation script.
  - Project continuity depends on preserving business rules, architecture decisions, and AI safety constraints in established documentation locations.
- Future implications:
  - Before implementation prompts, Codex should re-read `AGENTS.md`, `SYSTEM_ARCHITECTURE_V1.md`, `PROJECT_ARCHITECTURE_VISION.md`, `01-Business-Rules.md`, `02-Water-Emergency-Workflow.md`, `03-Dispatch-Pipeline.md`, and `09-First-Module-Build-Scope.md`.
  - Major architecture decisions, workflow changes, implementation decisions, important fixes, and discovered constraints must be recorded in the vault.
  - Documentation should remain compact and high-signal.
- Affected systems:
  - Documentation workflow
  - Future backend architecture
  - Future frontend architecture
  - AI-assisted development workflow

---

## 2026-05-15 — Source of Truth and Integration Boundary

- Decision type: Architecture
- Status: Accepted planning baseline
- Decision:
  - PostgreSQL will be the operational source of truth for the ACS FSM.
  - Google Calendar, Google Sheets, FastField, Verizon Connect, and AI providers are integration adapters only.
  - No external vendor system should own internal workflow state.
- Rationale:
  - Vendor lock-in and fragmented state caused operational fragility in the old workflow.
  - A database-first model supports auditability, future portals, technician apps, CRM, billing, inventory, and analytics.
- Future implications:
  - Adapter modules translate vendor data into internal ACS domain models.
  - Core business rules must live in backend services/domain modules, not frontend components or vendor-specific adapter code.
- Affected systems:
  - Database
  - Integration adapters
  - Dispatch pipeline
  - Water Emergency workflow

---

## 2026-05-15 — Manual Review Queue as Safety System

- Decision type: Workflow / operational safety
- Status: Accepted planning baseline
- Decision:
  - Manual Review Queue is a core safety system, not a secondary UI feature.
  - Any uncertain cancellation, malformed address, low-confidence classification, duplicate, conflicting tag, unclear Water Emergency state, or unsafe dispatch/export condition must stop automation and require human review.
- Rationale:
  - Unsafe automation is worse than slower automation for ACS operations.
  - The old system risked dispatching canceled or malformed jobs due to weak interpretation of human-written text.
- Future implications:
  - Review items need durable persistence, reason codes, confidence scores, operator decisions, and audit logs.
  - Dispatch, sheet export, and FastField send actions should require explicit approval when warnings exist.
- Affected systems:
  - Dispatch pipeline
  - Review service
  - Admin dashboard
  - Audit logs

---

## 2026-05-15 — AI Assistant Boundary

- Decision type: AI rule / operational safety
- Status: Accepted planning baseline
- Decision:
  - AI may assist with classification, anomaly detection, confidence scoring, summarization, and recommendations.
  - AI must never override operators, silently dispatch jobs, auto-confirm cancellations, auto-close Water Emergency workflows, or bypass manual review.
- Rationale:
  - ACS workflows require deterministic, auditable, human-controlled operations.
  - AI interpretation of messy human-written text is useful as support, but unsafe as operational authority.
- Future implications:
  - AI outputs should be treated as advisory signals with confidence and explanation.
  - Deterministic validation rules should run before and after AI assistance.
- Affected systems:
  - AI adapters
  - Classification services
  - Validation services
  - Manual review queue

---

## 2026-05-15 — First Implementation Boundary

- Decision type: Scope
- Status: Accepted planning baseline
- Decision:
  - The first implementation module will be the Dispatch Operations Engine foundation.
  - It should replace the current Google Calendar to Google Sheets to FastField workflow over time, while preserving transitional compatibility.
  - It must not attempt to build billing, full CRM, full customer portal, technician mobile app, payroll, inventory, or full Verizon Connect integration in the first module.
- Rationale:
  - The first module must be small enough to build safely but structured as the foundation of the full FSM.
- Future implications:
  - Initial architecture should include clean placeholders and extensible model boundaries for future modules without implementing their full behavior prematurely.
- Affected systems:
  - Backend scaffold
  - Frontend scaffold
  - Database models
  - Integration adapters
  - Documentation roadmap

---

## 2026-05-15 — Phase 0 Module 1 Backend Foundation

- Decision type: Implementation / architecture
- Status: Implemented
- Decision:
  - Build Phase 0 Module 1 as the backend foundation only.
  - Create a production-oriented FastAPI backend under `backend/`.
  - Use Pydantic Settings for environment-driven configuration.
  - Use SQLAlchemy 2 typed declarative models and Alembic for PostgreSQL migrations.
  - Add adapter placeholders for Google Calendar, Google Sheets, FastField, Verizon Connect, and AI without implementing live vendor integrations.
  - Add service placeholders for dispatch pipeline layers and core domains without implementing business workflow logic.
  - Defer frontend creation to a later Phase 0 module unless explicitly directed.
- Rationale:
  - The user directive for Module 1 listed backend foundation requirements and explicitly prohibited full FSM workflow implementation.
  - Production VPS and Apache reverse-proxy deployment require environment-based configuration and no localhost-hardcoded assumptions.
  - Clean backend/frontend separation is better preserved by finishing the backend foundation before adding Next.js structure.
- Future implications:
  - Future backend work should add repositories, validators, workflow engines, and route handlers inside the existing module boundaries.
  - Future frontend work should consume API responses and avoid business logic in components.
  - Live integrations must be implemented inside adapters and guarded by manual-review safety rules.
- Affected systems:
  - Backend package
  - Database models
  - Alembic migrations
  - API routing
  - Service layer
  - Adapter layer
  - Documentation

---

## 2026-05-15 — Phase 0 Module 2 Domain Model Refinement

- Decision type: Implementation / data model
- Status: Implemented
- Decision:
  - Refine the Module 1 SQLAlchemy model foundation only where supported by the documented ACS core data model.
  - Add flexible customer billing/property-manager contact fields and tags without creating full CRM contact tables yet.
  - Add many-to-many technician assignment tables for work orders and visits so Water Emergency and larger jobs are not limited to one technician.
  - Keep the existing single technician reference available as a primary assignment field until ACS confirms exact crew semantics.
  - Add technician vehicle and availability context, route drive-time estimates, generic Manual Review target fields, and audit-log default timestamps.
  - Add a new Alembic revision for these changes instead of rewriting the committed initial migration.
- Rationale:
  - The documented model explicitly calls for assigned technician(s), multiple technicians on Water Emergency visits, vehicle/truck context, estimated drive time, export-action review targets, and durable traceability.
  - The build directive prohibited workflow logic, CRUD endpoints, auth, real integrations, and invented business rules, so the changes stay at schema and relationship level.
- Future implications:
  - Operations still needs to confirm structured contact requirements, crew/primary technician semantics, route drive-time source, and exact Water Emergency stages.
  - Future workflow modules can build on multi-technician assignments and Manual Review targets without changing core table identity.
- Affected systems:
  - SQLAlchemy models
  - Alembic migrations
  - Model metadata tests
  - Database documentation
  - Manual Review foundation
  - Water Emergency foundation

---

## 2026-05-15 — Phase 0 Module 3 Backend Hardening

- Decision type: Implementation / backend operations
- Status: Implemented
- Decision:
  - Harden backend settings, logging, lifecycle, API metadata, and developer workflow without adding business workflow logic.
  - Keep environment behavior explicit for development, testing, and production, including production database URL safety checks.
  - Version OpenAPI and documentation routes under `/api/v1`, with environment control to disable docs when needed.
  - Add request ID middleware and structured JSON logging using request-safe fields only.
  - Add FastAPI lifespan readiness state for future service initialization and shutdown hooks.
  - Add backend Makefile commands for install, startup, testing, linting, formatting, migrations, Alembic history, compileall, and full verification.
- Rationale:
  - The production target is a Linux VPS behind Apache with environment-based configuration, so the backend needs safe runtime boundaries before workflow modules are added.
  - Request IDs, structured logs, and lifecycle readiness prepare future audit correlation and operational troubleshooting without implementing audit workflow behavior yet.
  - Makefile commands reduce command drift across future modules.
- Future implications:
  - Production deployment still needs a real process manager, Apache reverse-proxy configuration, HTTPS setup, secret management, database backup/rollback strategy, and migration runbook.
  - Future workflow modules can attach service initialization, background workers, and audit correlation to the lifecycle/logging foundations.
- Affected systems:
  - Backend settings
  - FastAPI application factory
  - Health endpoint
  - Structured logging
  - Developer workflow
  - Backend documentation

---

## 2026-05-15 — Phase 0 Module 4 Repository And Session Boundary

- Decision type: Implementation / database access architecture
- Status: Implemented
- Decision:
  - Add a thin repository layer under `backend/app/repositories/`.
  - Add one repository class for each core ACS domain model.
  - Keep the base repository limited to simple data access helpers: `get`, `list`, `add`, and `delete`.
  - Add request-scoped DB session handling with rollback-on-error and close-on-exit behavior.
  - Add an explicit `session_scope` context manager for future service-level transaction boundaries.
  - Add a FastAPI DB session dependency alias in `app/db/dependencies.py`.
- Rationale:
  - The long-term FSM architecture needs a stable data access boundary before workflow modules are added.
  - API routes should not accumulate SQLAlchemy query logic.
  - Repositories should isolate persistence without owning dispatch, Manual Review, integration, or AI behavior.
- Future implications:
  - Future workflow modules should coordinate transactions at the service/workflow level, not inside generic repositories.
  - A formal Unit of Work may be useful once multi-repository dispatch workflows begin.
  - Background workers will need their own session lifecycle policy when introduced.
- Affected systems:
  - Database session handling
  - Repository layer
  - Future service layer
  - Future workflow engines
  - Backend documentation

---

## 2026-05-15 — Phase 0 Module 5 Intake Normalization And Validation Foundation

- Decision type: Implementation / dispatch pipeline foundation
- Status: Implemented
- Decision:
  - Add intake domain structures for raw intake payloads, normalized intake, detection results, validation issues, validation results, confidence scores, and review recommendations.
  - Replace placeholder normalization and validation services with deterministic pipeline foundations.
  - Add a deterministic confidence scoring service separate from validation.
  - Add Manual Review preparation that turns validation and confidence results into review-ready reason codes and actions.
  - Keep cancellation and Water Emergency detections as dispatch-safety blockers until future workflows define persistence and execution behavior.
- Rationale:
  - External intake data will be messy, but dispatch safety requires normalized, validated, explainable internal structures before routing or export.
  - Manual Review must receive structured reasons instead of relying on freeform text.
  - AI may later assist, but deterministic validation must be the first authority.
- Future implications:
  - Google Calendar ingestion can later adapt vendor events into `RawIntakePayload` without owning core workflow state.
  - Future AI services should consume normalized/validated structures and return advisory context only.
  - Future persistence should map review recommendations into Manual Review records after transaction boundaries are confirmed.
- Affected systems:
  - Intake domain structures
  - Normalization service
  - Validation service
  - Confidence scoring service
  - Manual Review preparation service
  - Dispatch pipeline documentation

---

## 2026-05-15 — Phase 0 Module 6 Persistent Manual Review Queue Foundation

- Decision type: Implementation / operational safety
- Status: Implemented
- Decision:
  - Add explicit intake processing states for raw, normalized, validated, flagged for review, approved, rejected, deferred, and archived intake.
  - Expand `ReviewItem` into the persistent Manual Review Queue foundation with status, severity, deterministic reasons, source references, confidence snapshots, warning snapshots, normalization snapshots, validation snapshots, operator notes, timestamps, and audit correlation.
  - Add a queryable audit correlation field to audit logs so future review/audit joins do not depend only on JSON details.
  - Add deterministic services for review queue creation, review classification, severity escalation, state transitions, and audit-trace preparation.
  - Keep review state transitions operator-driven and side-effect-free with respect to dispatch execution.
- Rationale:
  - Manual Review is a core ACS safety system and must be durable, explainable, and auditable before dispatch workflows are introduced.
  - Unsafe, canceled, Water Emergency, conflicting, malformed, missing-field, or low-confidence intake must stop automation and preserve evidence.
  - Review approval should resolve review uncertainty, but it should not silently dispatch, route, export, or call external systems.
- Future implications:
  - Future dispatch modules should consume approved review outcomes through explicit workflow services and transactions.
  - Authentication will need to add operator identity to review decisions.
  - A dedicated review transition history table may be needed once multi-operator review workflows are defined.
  - Background reminders or SLA timers for deferred review items remain undecided.
- Affected systems:
  - ReviewItem model
  - AuditLog model
  - Alembic migrations
  - Manual Review services
  - Intake processing domain
  - Audit traceability foundation
  - Backend documentation

---

## 2026-05-15 — Phase 0 Module 7 Dispatch Orchestration Preparation

- Decision type: Implementation / dispatch pipeline foundation
- Status: Implemented
- Decision:
  - Add orchestration domain structures for orchestration state, warnings, dispatch eligibility, evidence, decision result, and intake processing result.
  - Replace the dispatch service placeholder with `DispatchOrchestrationService`.
  - Compose the existing deterministic normalization, validation, confidence scoring, Manual Review preparation, review classification, and review escalation services into one orchestration result.
  - Keep orchestration output in-memory and side-effect-free.
  - Represent dispatch eligibility separately from dispatch execution.
- Rationale:
  - Future dispatch workflows need one explainable preparation result before persistence, routing, exports, integrations, or AI assistance are introduced.
  - Unsafe intake, cancellations, malformed data, conflicts, low-confidence intake, and Water Emergency intake must stop before dispatch execution and preserve deterministic evidence.
  - Eligibility should make safety decisions visible without creating hidden workflow transitions.
- Future implications:
  - Future modules can persist orchestration outcomes through explicit transactions once intake/job/review persistence decisions are finalized.
  - Duplicate detection, next-day import policy, and warning-only intake behavior still need operational decisions.
  - Future AI orchestration must consume this deterministic evidence and remain advisory only.
- Affected systems:
  - Dispatch service layer
  - Orchestration domain structures
  - Intake pipeline services
  - Manual Review preparation/classification/escalation
  - Dispatch pipeline documentation

---

## 2026-05-15 — Phase 0 Module 8 Operational Intake Persistence

- Decision type: Implementation / persistence boundary
- Status: Implemented
- Decision:
  - Add `OperationalLifecycleState` for intake_received, normalized, validated, review_required, approved_for_dispatch, blocked, deferred, and archived records.
  - Add `IntakeProcessingRecord` as the durable operational intake record for orchestration outcomes.
  - Add `IntakeProcessingRecordRepository` and `OperationalIntakePersistenceService`.
  - Persist raw payload, orchestration, dispatch eligibility, normalized, validation, confidence, review, warning, and deterministic evidence snapshots.
  - Preserve review item linkage and audit correlation on the intake processing record.
  - Keep persistence separate from orchestration and dispatch execution.
- Rationale:
  - The platform needs a durable, auditable handoff between deterministic orchestration and future operational workflow creation.
  - Evidence must persist before dispatch execution exists so operators can inspect why a record is approved, blocked, or review-required.
  - Unsafe and Water Emergency intake must remain blocked from standard dispatch approval at the persistence boundary.
- Future implications:
  - Future dispatch execution should consume `approved_for_dispatch` intake records through explicit transactions.
  - Intake-to-job/work-order/visit creation remains unresolved and should not be hidden inside persistence.
  - Future review resolution, operator identity, deduplication, and immutable lifecycle history need separate design decisions.
- Affected systems:
  - Intake processing model
  - Alembic migrations
  - Repository layer
  - Operational intake persistence service
  - Audit traceability foundation
  - Dispatch pipeline documentation

---

## 2026-05-15 — Phase 0 Module 9 Operational Job Creation Foundation

- Decision type: Implementation / operational workflow boundary
- Status: Implemented
- Decision:
  - Add a deterministic operational job creation boundary after operational intake persistence.
  - Create `JobCreationRecord` as the durable intake-to-job linkage and creation evidence record.
  - Add `OperationalJobCreationService` to create standard jobs only from explicitly approved intake records.
  - Preserve orchestration, dispatch eligibility, review linkage, deterministic evidence, audit correlation, and lifecycle metadata snapshots when a job is created.
  - Block job creation for review-required, blocked, unsafe, invalid-lifecycle, duplicate, missing-linkage, and Water Emergency-separated intake.
  - Set created standard jobs to `awaiting_dispatch` only, preserving the boundary that job creation is not dispatch execution.
- Rationale:
  - The platform needs a controlled transition from approved intake into operational entities before routing or dispatch modules are added.
  - Intake persistence should not hide job creation side effects, and dispatch orchestration should remain side-effect-free.
  - Water Emergency and Manual Review safety boundaries must remain enforceable before any future dispatch execution exists.
- Future implications:
  - Future dispatch execution should consume created jobs and job creation records through explicit workflow services and transactions.
  - Customer/property materialization, standard work-order creation, review-resolution approval semantics, source-level duplicate keys, and Water Emergency workflow creation remain unresolved.
  - Creation failures may eventually need separate persisted attempt history if operations requires audit visibility for failed creation attempts.
- Affected systems:
  - Job model lifecycle usage
  - JobCreationRecord model
  - Alembic migrations
  - Repository layer
  - Operational job creation service
  - Operational intake lifecycle
  - Audit traceability foundation
  - Dispatch pipeline documentation

---

## 2026-05-15 — Phase 0 Module 10 Work Order And Visit Generation Foundation

- Decision type: Implementation / operational execution preparation
- Status: Implemented
- Decision:
  - Add a deterministic Work Order and Visit generation boundary after operational job creation.
  - Add `OperationalGenerationLifecycleState`, failure reasons, traceability, evidence, and result structures for Work Order and Visit generation.
  - Expand Work Orders with job creation linkage, review linkage, audit correlation, snapshots, lifecycle metadata, and generated-from-job timestamp.
  - Expand Visits with Work Order linkage, audit correlation, snapshots, lifecycle metadata, and generated-from-work-order timestamp.
  - Add repository lookup helpers for duplicate Work Order generation by job and duplicate Visit generation by Work Order.
  - Add `OperationalWorkGenerationService` to create scheduling-ready standard Work Orders and unassigned standard Visits.
  - Block Work Order generation for blocked, review-required, invalid-lifecycle, duplicate, or Water Emergency jobs.
- Rationale:
  - The platform needs technician-facing operational structures before dispatch/routing modules can consume jobs.
  - Work Order generation should preserve the intake/orchestration/job creation evidence chain instead of relying on transient service context.
  - Visits must become durable before future technician assignment, scheduling, routing, and dispatch can operate safely.
  - Water Emergency requires a separated path because it can involve multi-day, multi-visit, equipment-tracked workflows.
- Future implications:
  - Future dispatch/routing should consume generated Work Orders and Visits through explicit workflow services.
  - Production Work Order numbering, service-specific form/equipment defaults, one-job-to-one-work-order assumptions, and schedule-window persistence still need operational decisions.
  - Water Emergency Work Order/Visit generation needs a separate module rather than reuse of the standard path.
- Affected systems:
  - WorkOrder model
  - Visit model
  - JobCreationRecord relationships
  - Alembic migrations
  - Repository layer
  - Operational work generation service
  - Audit traceability foundation
  - Dispatch pipeline documentation

---

## 2026-05-15 — Phase 0 Module 11 Assignment And Scheduling Preparation Foundation

- Decision type: Implementation / technician-facing preparation
- Status: Implemented
- Decision:
  - Add a deterministic technician assignment and scheduling readiness boundary after Visit generation.
  - Add domain structures for assignment eligibility, assignment readiness, technician compatibility, scheduling readiness, operational readiness, lifecycle state, and blocker codes.
  - Expand Visits with assignment readiness, technician compatibility, scheduling readiness, and operational readiness snapshots plus preparation timestamps.
  - Add `AssignmentPreparationService` to prepare standard generated Visits for future assignment and scheduling without assigning technicians or scheduling times.
  - Preserve AM/PM time-window and service-state evidence from deterministic normalization snapshots.
  - Block standard assignment preparation for blocked, review-required, archived, invalid-lifecycle, and Water Emergency Visits.
  - Treat inactive technician candidates as incompatible without mutating `technician_id`.
- Rationale:
  - Future routing and dispatch need explicit readiness evidence before technician assignment and schedule execution exist.
  - Visit lifecycle should remain deterministic and auditable; future modules should not infer assignment readiness from freeform strings.
  - Manual Review and Water Emergency boundaries must remain authoritative before any technician-facing execution is introduced.
- Future implications:
  - Future routing should consume Visit readiness snapshots and lifecycle state.
  - Technician assignment will need explicit operator/system authority and possibly multi-technician semantics.
  - Exact technician availability states, skill matching, service-area matching, vehicle/routing compatibility, and schedule-window conversion remain unresolved.
- Affected systems:
  - Assignment preparation domain structures
  - Visit model
  - Alembic migrations
  - Assignment preparation service
  - Audit traceability foundation
  - Dispatch pipeline documentation

---

## 2026-05-15 — Phase 0 Module 12 Routing And Dispatch Preparation Foundation

- Decision type: Implementation / routing and dispatch preparation
- Status: Implemented
- Decision:
  - Add a deterministic routing and dispatch preparation boundary after assignment/scheduling preparation.
  - Add domain structures for routing readiness, technician readiness, Visit dispatch readiness, dispatch eligibility, lifecycle state, blocker codes, traceability, and deterministic evidence.
  - Expand Visits with routing readiness, dispatch readiness, technician readiness, Visit dispatch readiness snapshots, and preparation timestamps.
  - Add `RoutingDispatchPreparationService` to prepare standard Visits for future routing and dispatch execution without optimizing routes or executing dispatch.
  - Preserve assignment readiness and scheduling readiness evidence from the Module 11 preparation boundary.
  - Block dispatch readiness for blocked Visits, review-required lifecycle, Water Emergency Visits, inactive technicians, unassigned Visits, unscheduled Visits, invalid lifecycle, and missing linkage.
- Rationale:
  - Future route optimization and dispatch execution need explicit readiness evidence before any live operational action can run.
  - Dispatch-ready must mean deterministic prerequisites are present, not that dispatch has executed.
  - Manual Review and Water Emergency boundaries must remain enforceable immediately before technician-facing execution.
- Future implications:
  - Future dispatch execution should consume `dispatch_ready` Visits through a separate transactional workflow service.
  - Route optimization, persisted route assignments, technician availability revalidation, calendar sync, vendor exports, and mobile technician workflows remain separate modules.
  - Exact route grouping, whether dispatch readiness should require a persisted route assignment, and Water Emergency routing semantics remain unresolved.
- Affected systems:
  - Routing/dispatch preparation domain structures
  - Visit model
  - Alembic migrations
  - Routing/dispatch preparation service
  - Audit traceability foundation
  - Dispatch pipeline documentation

---

## 2026-05-15 — Phase 0 Module 13 Route Assignment And Dispatch Authorization Foundation

- Decision type: Implementation / dispatch authorization boundary
- Status: Implemented
- Decision:
  - Add a deterministic route assignment preparation and dispatch authorization boundary after routing/dispatch preparation.
  - Add domain structures for route grouping, route assignment readiness, technician route compatibility, dispatch authorization readiness, execution authorization state, blocker codes, traceability, and evidence.
  - Expand Route Assignments with route grouping, readiness, technician compatibility, dispatch authorization, execution-boundary, deterministic evidence, route group key, audit correlation, and authorization timestamps.
  - Add `RouteAssignmentPreparationService` to create prepared route assignments for standard dispatch-ready Visits without optimizing routes or executing dispatch.
  - Move authorized standard Visits to `awaiting_dispatch_execution`, preserving the boundary that dispatch has not run.
  - Block dispatch authorization for blocked, review-required, Water Emergency, inactive-technician, unassigned, unscheduled, route-unready, dispatch-unready, invalid-lifecycle, archived, and missing-linkage Visits.
- Rationale:
  - Future dispatch execution needs one explicit durable authorization record instead of inferring execution readiness from Visit status text.
  - Route grouping evidence should be preserved before optimization exists, without pretending that optimization has run.
  - Manual Review and Water Emergency boundaries must remain authoritative at the final pre-execution gate.
- Future implications:
  - Future dispatch execution should consume authorized Route Assignments through a separate transactional execution service.
  - Operator identity, route optimization revisioning, warning-heavy second approval, integration export outcomes, and Water Emergency dispatch authorization remain separate decisions.
- Affected systems:
  - Route assignment authorization domain structures
  - RouteAssignment model
  - Alembic migrations
  - Route assignment preparation service
  - Audit traceability foundation
  - Dispatch pipeline documentation

---

## 2026-05-15 — Phase 0 Module 14 Dispatch Execution Foundation

- Decision type: Implementation / internal dispatch execution boundary
- Status: Implemented
- Decision:
  - Add a deterministic internal dispatch execution boundary after route assignment authorization.
  - Add domain structures for dispatch execution state, blocker codes, failure reasons, traceability, lifecycle transitions, evidence, and execution results.
  - Expand Route Assignments with dispatch execution state, execution snapshot, lifecycle snapshot, audit snapshot, dispatched timestamp, and future failure timestamp.
  - Add `DispatchExecutionService` to transition authorized standard Route Assignments and linked Visits into internal `dispatched` state.
  - Preserve explicit `not_executed` evidence for FastField, Calendar, Sheets, mobile workflow, background worker, and other external integration paths.
  - Block dispatch execution for blocked, review-required, Water Emergency, inactive-technician, unassigned, unscheduled, unauthorized, duplicate-dispatch, invalid-lifecycle, archived, and missing-linkage records.
- Rationale:
  - Dispatch execution needs one explicit internal lifecycle boundary before external adapters can safely consume work.
  - Manual Review and Water Emergency separation must remain authoritative at the first true execution gate.
  - Internal ACS state must remain the source of truth while external systems remain adapters.
- Future implications:
  - Future external dispatch adapters should consume the execution snapshot and write adapter outcomes without owning lifecycle truth.
  - Operator/system identity, dispatch confirmation semantics, adapter failure/retry handling, route optimization revisioning, and Water Emergency dispatch execution remain separate decisions.
- Affected systems:
  - Dispatch execution domain structures
  - RouteAssignment model
  - Alembic migrations
  - Dispatch execution service
  - Audit traceability foundation
  - Dispatch pipeline documentation

---

## 2026-05-15 — Phase 0 Module 15 External Dispatch Adapter Foundation

- Decision type: Implementation / external adapter preparation boundary
- Status: Implemented
- Decision:
  - Add a deterministic external adapter preparation boundary after internal dispatch execution.
  - Add domain structures for adapter lifecycle state, failure codes, execution request, execution result, evidence, failure reasons, and audit evidence.
  - Expand Route Assignments with external adapter state, request snapshot, payload snapshot, lifecycle snapshot, evidence snapshot, audit snapshot, prepared timestamp, and future failure timestamp.
  - Add `ExternalDispatchAdapterPreparationService` to prepare FastField, Google Sheets, Google Calendar, and technician mobile payload snapshots without calling external APIs.
  - Move standard internally dispatched Route Assignments to `awaiting_external_execution` only after deterministic adapter-preparation blockers pass.
  - Block adapter preparation for blocked, review-required, Water Emergency, undispatched, unauthorized, duplicate-prepared, invalid-lifecycle, and missing-linkage records.
- Rationale:
  - Future vendor/mobile execution needs a clean handoff from internal dispatch execution without letting vendors own ACS workflow state.
  - Payload preparation should be auditable before any external write/send occurs.
  - Manual Review and Water Emergency separation must remain authoritative before external systems receive work.
- Future implications:
  - Future live adapters should consume payload snapshots and record execution outcomes separately from internal lifecycle truth.
  - Vendor schemas, retry/failure versioning, confirmation semantics, operator approval, credential scoping, and Water Emergency adapter payloads remain separate decisions.
- Affected systems:
  - External adapter domain structures
  - RouteAssignment model
  - Alembic migrations
  - External dispatch adapter preparation service
  - Audit traceability foundation
  - Integration and dispatch pipeline documentation

---

## 2026-05-16 — Phase 0 Module 16 External Confirmation And Failure Recovery Foundation

- Decision type: Implementation / external confirmation and recovery boundary
- Status: Implemented
- Decision:
  - Add a deterministic external confirmation and failure recovery preparation boundary after external adapter preparation.
  - Add domain structures for confirmation lifecycle state, simulated confirmation state, failure codes, confirmation result, evidence, traceability, and failure reasons.
  - Expand Route Assignments with external confirmation state, confirmation snapshot, lifecycle snapshot, audit snapshot, external failure snapshot, retry preparation snapshot, reconciliation snapshot, and related timestamps.
  - Add `ExternalExecutionConfirmationService` to process simulated confirmation success, simulated failure, reconciliation-required outcomes, and retry-preparation requests without calling external APIs.
  - Block confirmation for blocked, review-required, Water Emergency, unauthorized, duplicate-confirmed, adapter-unready, invalid-lifecycle, and missing-linkage records.
- Rationale:
  - Future live vendor execution needs a durable outcome boundary that can preserve confirmation, failure, retry, and reconciliation evidence without giving external systems workflow authority.
  - Failure recovery should be explicit and auditable before automatic retry or reconciliation behavior exists.
  - Manual Review and Water Emergency separation must remain authoritative when external outcomes are uncertain or failed.
- Future implications:
  - Future live adapters should write vendor outcomes into these snapshots and may later introduce immutable attempt records if retry/versioning requirements grow.
  - Retry attempt limits, operator approval before retry, reconciliation task ownership, vendor status mapping, credential scoping, and Water Emergency confirmation paths remain separate decisions.
- Affected systems:
  - External confirmation domain structures
  - RouteAssignment model
  - Alembic migrations
  - External execution confirmation service
  - Audit traceability foundation
  - Integration and dispatch pipeline documentation

---

## 2026-05-16 — Phase 0 Module 17 Operational Event History And Immutable Audit Timeline

- Decision type: Implementation / immutable operational history boundary
- Status: Implemented
- Decision:
  - Add an append-only operational event history boundary after confirmation/recovery preparation.
  - Add domain structures for operational event state, timeline entries, immutable audit evidence, transition evidence, retry/recovery evidence, reconciliation evidence, event results, and failure reasons.
  - Add `OperationalEventRecord` as the durable timeline table for lifecycle, dispatch, adapter, confirmation, retry, and reconciliation events.
  - Add `OperationalEventRecordRepository` with append/query behavior and repository-level deletion blocking.
  - Add `OperationalEventHistoryService` to record deterministic lifecycle transitions, dispatch execution events, adapter preparation events, confirmation/recovery events, and ordered route-assignment or Visit timelines.
  - Block duplicate event fingerprints, missing entity linkage, missing audit correlation, missing transition states, and hidden no-op transitions.
- Rationale:
  - ACS needs forensic operational traceability across lifecycle transitions and external execution preparation without turning history into a workflow engine.
  - Immutable event history should preserve why transitions happened, what was blocked, and what evidence existed at the time.
  - Audit logs and lifecycle snapshots remain useful, but a dedicated event table gives future debugging, reporting, and operator review a chronological operational timeline.
- Future implications:
  - Future live integrations should append execution/confirmation/failure events without mutating prior history.
  - Analytics, event replay, retention/legal hold, actor identity, and external attempt versioning remain separate decisions.
  - Water Emergency timelines may need a separated event taxonomy instead of reusing the standard dispatch path.
- Affected systems:
  - Operational event history domain structures
  - OperationalEventRecord model
  - Alembic migrations
  - Repository layer
  - Operational event history service
  - Audit traceability and dispatch pipeline documentation

---

## 2026-05-16 — Phase 0 Module 18 Real External Adapter Execution Foundation

- Decision type: Implementation / controlled external execution boundary
- Status: Implemented
- Decision:
  - Add a deterministic controlled external adapter execution boundary between adapter preparation and confirmation readiness.
  - Add domain structures for external execution lifecycle state, provider execution state, execution request, provider result, lifecycle transition, evidence, failure reasons, and execution result.
  - Expand Route Assignments with external execution state, request snapshot, provider snapshot, evidence snapshot, failure snapshot, lifecycle snapshot, audit snapshot, and started/completed/failed timestamps.
  - Add `ExternalAdapterExecutionService` to process prepared adapter payloads through simulated provider execution boundaries for FastField, Google Sheets, Google Calendar, and technician mobile sync without calling live APIs.
  - Move successful controlled execution to `awaiting_external_confirmation`; record provider failures as explicit failure evidence without automatic retry.
  - Block external execution for blocked, review-required, Water Emergency, unauthorized, duplicate-attempt, adapter-unready, invalid-lifecycle, missing-linkage, and missing-payload records.
- Rationale:
  - Future live provider execution needs a durable boundary that can be tested and audited before real credentials, background workers, or vendor APIs exist.
  - Provider execution evidence should preserve correlation and failure context without letting external systems become workflow authority.
  - Manual Review, Water Emergency separation, and no-automatic-retry behavior must remain authoritative when external execution is uncertain or failed.
- Future implications:
  - Future live adapters should replace simulated provider internals while preserving the same service boundary, lifecycle states, audit snapshots, and blocker rules.
  - Provider-specific request/response schemas, immutable attempt tables, retry limits, operator approvals, credential scoping, and Water Emergency execution paths remain separate decisions.
- Affected systems:
  - External adapter execution domain structures
  - RouteAssignment model
  - Alembic migrations
  - External adapter execution service
  - Audit traceability foundation
  - Integration and dispatch pipeline documentation

---

## 2026-05-16 — Phase 0 Module 19 Dispatch Reconciliation And Operational Consistency Foundation

- Decision type: Implementation / reconciliation preparation and consistency boundary
- Status: Implemented
- Decision:
  - Add a deterministic dispatch reconciliation and operational consistency boundary after external execution, confirmation/recovery, and event-history evidence exist.
  - Add domain structures for reconciliation lifecycle state, mismatch codes, failure codes, consistency verification result, divergence evidence, mismatch evidence, blockers, traceability, and reconciliation result.
  - Expand Route Assignments with dispatch reconciliation state, consistency snapshot, divergence snapshot, mismatch snapshot, blocker snapshot, audit snapshot, and reconciliation/verification/block timestamps.
  - Add `DispatchReconciliationService` to compare internal dispatch lifecycle, external execution state, external confirmation state, retry/recovery evidence, and immutable event history.
  - Record consistency-verified or reconciliation-required evidence without executing reconciliation.
  - Block reconciliation preparation for review-required, Water Emergency, unauthorized, duplicate, invalid-lifecycle, missing-linkage, missing-audit-correlation, and mutable-history records.
- Rationale:
  - ACS needs deterministic consistency checks before future reconciliation execution can safely exist.
  - Divergence and mismatch evidence should be explicit, auditable, and operator-reviewable.
  - Immutable operational history must remain read-only evidence and must not become a replay or mutation mechanism.
- Future implications:
  - Future reconciliation execution should consume these snapshots through explicit operator/review workflows.
  - Manual Review item creation, provider-specific mismatch taxonomies, reconciliation attempt tables, operator approvals, and Water Emergency reconciliation paths remain separate decisions.
- Affected systems:
  - Dispatch reconciliation domain structures
  - RouteAssignment model
  - Alembic migrations
  - Dispatch reconciliation service
  - Operational event history evidence boundary
  - Audit traceability and dispatch pipeline documentation

---

## 2026-05-16 — Phase 0 Module 20 Operational Replay And Recovery Preparation Foundation

- Decision type: Implementation / replay preparation and recovery coordination boundary
- Status: Implemented
- Decision:
  - Add a deterministic operational replay and recovery preparation boundary after reconciliation, retry, or failure context exists.
  - Add domain structures for replay/recovery lifecycle state, replay blockers, replay eligibility, rollback preparation, recovery coordination, traceability, evidence, and replay preparation results.
  - Expand Route Assignments with replay/recovery state, replay preparation, rollback preparation, replay eligibility, replay blocker, recovery coordination, audit snapshots, and replay/rollback/block timestamps.
  - Add `OperationalReplayPreparationService` to prepare replay or rollback evidence without executing replay, rollback, retries, external APIs, workflow engines, or AI.
  - Block replay preparation for review-required, Water Emergency, unauthorized, duplicate, invalid-lifecycle, missing-linkage, missing-audit-correlation, no-recovery-context, and mutable-history records.
- Rationale:
  - ACS needs recovery coordination evidence before any future replay or rollback execution can safely exist.
  - Replay preparation must preserve immutable event history as read-only evidence and avoid turning history into a mutable workflow replay engine.
  - Manual Review, Water Emergency separation, and deterministic lifecycle state must remain authoritative when recovery is required.
- Future implications:
  - Future replay/recovery execution should consume these snapshots through explicit operator/review workflows.
  - Replay attempt tables, rollback scope, operator approval, Manual Review item creation, retry limits, and Water Emergency replay/recovery paths remain separate decisions.
- Affected systems:
  - Operational replay/recovery domain structures
  - RouteAssignment model
  - Alembic migrations
  - Operational replay preparation service
  - Operational event history evidence boundary
  - Audit traceability and dispatch pipeline documentation

---

## 2026-05-16 — Phase 0 Module 21 Operational Governance And Approval Control Foundation

- Decision type: Implementation / governance and operator approval boundary
- Status: Implemented
- Decision:
  - Add a deterministic operational governance and approval-control boundary after replay/recovery preparation.
  - Add domain structures for governance lifecycle state, governance operation, governance blockers, approval results, intervention authorization, replay authorization, rollback authorization, reconciliation approval, audit evidence, and traceability.
  - Expand Route Assignments with governance state, governance approval, intervention authorization, replay authorization, rollback authorization, reconciliation approval, governance blocker, governance audit snapshots, and governance timestamps.
  - Add `OperationalGovernanceService` to validate operator approval and manual intervention authorization without executing replay, rollback, reconciliation, external APIs, workflow engines, or AI.
  - Block governance for review-required, Water Emergency, unauthorized-operator, duplicate-approval, invalid-lifecycle, missing-operator, missing-linkage, missing-audit-correlation, operation-not-prepared, and mutable-history records.
- Rationale:
  - ACS needs explicit operator authority evidence before future replay, rollback, reconciliation, or manual intervention execution can safely exist.
  - Governance must not become a workflow engine or automatic approval mechanism.
  - Manual Review, Water Emergency separation, deterministic lifecycle state, and immutable event history must remain authoritative.
- Future implications:
  - Future enterprise governance should consume these snapshots through authenticated operator workflows.
  - Operator roles, two-person approval, approval expiration/revocation, immutable approval tables, and Water Emergency governance paths remain separate decisions.
- Affected systems:
  - Operational governance domain structures
  - RouteAssignment model
  - Alembic migrations
  - Operational governance service
  - Operational event history evidence boundary
  - Audit traceability and dispatch pipeline documentation

---

## 2026-05-16 — Phase 0 Module 22 Operational Accountability, Escalation, And Incident Coordination Foundation

- Decision type: Implementation / accountability and escalation preparation boundary
- Status: Implemented
- Decision:
  - Add a deterministic operational accountability and escalation-preparation boundary after governance approval.
  - Add domain structures for accountability lifecycle state, escalation type, accountability blockers, escalation results, incident preparation, intervention escalation, operational incident evidence, audit evidence, and traceability.
  - Expand Route Assignments with accountability state, escalation preparation, incident preparation, accountability evidence, escalation blocker, intervention escalation, operational incident, accountability audit snapshots, and accountability timestamps.
  - Add `OperationalAccountabilityService` to validate escalation and incident preparation without executing escalations, incidents, interventions, external APIs, workflow engines, or AI.
  - Block accountability preparation for review-required, Water Emergency, unauthorized, duplicate-escalation, invalid-lifecycle, missing-operator, missing-linkage, missing-audit-correlation, missing-governance, no-context, and mutable-history records.
- Rationale:
  - ACS needs explicit accountability evidence before future enterprise escalation, incident coordination, or critical intervention workflows can safely exist.
  - Accountability must not become an automatic incident engine or workflow executor.
  - Manual Review, governance authority, Water Emergency separation, deterministic lifecycle state, and immutable event history must remain authoritative.
- Future implications:
  - Future enterprise coordination should consume these snapshots through authenticated operator workflows.
  - Operator roles, two-person escalation approval, escalation acknowledgement, incident closure, immutable accountability tables, and Water Emergency accountability paths remain separate decisions.
- Affected systems:
  - Operational accountability domain structures
  - RouteAssignment model
  - Alembic migrations
  - Operational accountability service
  - Operational event history evidence boundary
  - Audit traceability and dispatch pipeline documentation

---

## 2026-05-16 — Phase 0 Module 23 Operational Dashboard Read Model And API Contract Foundation

- Decision type: Implementation / read model / API contract
- Status: Implemented
- Decision:
  - Add a read-only dashboard projection boundary for future admin dashboard consumption.
  - Add dashboard domain read models for operational overview, lifecycle, Manual Review, route assignment, external execution, reconciliation/recovery, governance/accountability, and operational timelines.
  - Add `DashboardReadModelService` to aggregate persisted ORM state and immutable event evidence without mutating objects or triggering workflow execution.
  - Add Pydantic dashboard response schemas and read-only routes under `/api/v1/dashboard`.
  - Keep dashboard routes contract-only; do not add mutation, execution, integration, frontend, analytics-engine, or AI behavior.
- Rationale:
  - Future office/admin dashboard work needs stable backend-owned contracts before frontend implementation begins.
  - Lifecycle counts, blocker counts, Manual Review indicators, and timeline evidence should come from persisted backend state, not frontend inference.
  - Manual Review, Water Emergency separation, audit correlation, and immutable event history must remain authoritative and visible.
- Future implications:
  - Frontend dashboard work should consume these contracts and avoid embedding workflow rules in UI components.
  - Filtering, pagination, role-scoped visibility, stale-data handling, and Water Emergency-specific dashboard contracts remain unresolved.
  - Large production datasets may require optimized queries or materialized projections later, but Module 23 intentionally avoids analytics-engine complexity.
- Affected systems:
  - Dashboard domain read models
  - Dashboard service layer
  - Dashboard API schemas
  - Dashboard API routes
  - Operational event history read consumption
  - Backend documentation

---

## 2026-05-16 — Phase 0 Module 24 Frontend Admin Dashboard Foundation

- Decision type: Implementation / frontend foundation / dashboard consumer
- Status: Implemented
- Decision:
  - Add the first frontend foundation under `frontend/` using Next.js, TypeScript, and Tailwind CSS.
  - Build a read-only admin dashboard shell that consumes backend Module 23 dashboard read-model contracts.
  - Add TypeScript dashboard contract types, a server-side read-only dashboard API client, and typed fallback data for local development when the backend is unavailable.
  - Build display-only sections for operational overview, lifecycle counts, Manual Review, dispatch, external execution, reconciliation/recovery, governance/accountability, and operational event timeline preview.
  - Keep the frontend free of operational mutations, dispatch actions, Manual Review resolution, vendor execution, AI authority, authentication, and mobile app behavior.
- Rationale:
  - ACS office/admin dashboard work needs a maintainable visual foundation, but workflow authority must remain in backend services and persisted read models.
  - The frontend should validate the Module 23 API contract shape without duplicating lifecycle, blocker, Manual Review, Water Emergency, or governance logic.
  - Local development needs a safe fallback state so UI layout can be verified before a live backend is running.
- Future implications:
  - Future frontend modules can add authenticated role-scoped screens after backend auth and permissions are defined.
  - Dashboard filtering, pagination, refresh cadence, stale-data indicators, and Water Emergency-specific screens remain separate decisions.
  - Production deployment must define reverse-proxy routing between the future Next.js frontend and FastAPI backend without hardcoded localhost assumptions.
- Affected systems:
  - Frontend application scaffold
  - Dashboard API client
  - Dashboard UI component foundation
  - Dashboard contract documentation
  - AI/dashboard safety boundary
  - Future deployment architecture
