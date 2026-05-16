# ACS FSM — Database Architecture

## Purpose

This file records the database architecture baseline for the ACS FSM platform.

Detailed entity notes are maintained in [[05-Database/CORE_DATA_MODEL]].

---

## Source Of Truth

The internal database is the operational source of truth.

External systems are integrations only:

- Google Calendar provides schedule input.
- Google Sheets is transitional output.
- FastField is transitional dispatch/work-order output.
- Verizon Connect is future vehicle/GPS input.
- AI providers are assistant/validation adapters.

No external system should own ACS workflow state.

---

## Initial Database Direction

Preferred database:

- PostgreSQL

Backend data layer:

- SQLAlchemy models
- Alembic migrations
- Pydantic schemas
- repository/service boundaries

---

## Foundational Models

Initial architecture should prepare:

- Customer
- Property
- Job
- WorkOrder
- Visit
- Technician
- RouteAssignment
- WaterEmergency
- ReviewItem
- IntakeProcessingRecord
- JobCreationRecord
- AuditLog

The first implementation may keep models minimal, but relationships should not block future CRM, technician app, inventory, billing, or customer portal work.

---

## Phase 0 Module 2 Foundation Decisions

The domain model foundation now includes:

- flexible customer contact and tag fields without introducing full CRM contact tables yet
- many-to-many technician assignment support for work orders and visits
- technician vehicle and availability context
- route drive-time estimate storage
- generic Manual Review entity targeting for future export or integration actions
- default audit timestamps for traceability

These additions are schema foundation only. They do not implement dispatch workflows, Water Emergency workflow transitions, CRUD APIs, authentication, or external integrations.

---

## Data Safety Rules

- Use UUIDs for durable identifiers where appropriate.
- Use timestamps for important entities.
- Log important workflow transitions.
- Avoid hidden state in JSON files except debug/export snapshots.
- Never store secrets in source or plain documentation.
- Persist Manual Review reasons and operator decisions.

## Environment And Migration Safety

- Database configuration must come from environment-based settings.
- Production must not use local database hosts, placeholder example hosts, placeholder passwords, or SQL echo logging.
- Alembic must read the same settings layer as the application.
- New migrations should be added as forward revisions after committed migrations; do not rewrite committed migrations unless explicitly instructed.
- Local Phase 0 tests and health checks must not require connecting to a real PostgreSQL database.

## Repository And Session Boundary

Phase 0 Module 4 adds the first database access boundary:

```text
API routes -> services/workflow modules -> repositories -> SQLAlchemy session -> PostgreSQL
```

Repository rules:

- Repositories are thin data-access wrappers.
- Repositories may build SQLAlchemy queries and persist models.
- Repositories must not contain dispatch workflow logic, routing decisions, integration calls, AI orchestration, or operator-safety decisions.
- Domain-specific repositories should exist for core ACS entities so future services do not query directly from API routes.

Session rules:

- Request-scoped DB access should use the FastAPI dependency wrapper around `get_db_session`.
- `get_db_session` closes sessions and rolls back when request handling raises an exception.
- `session_scope` is the explicit transaction foundation for future non-request workflows and service-level units of work.
- Automatic commits should remain outside generic repositories; future services or unit-of-work orchestration should decide transaction boundaries.

Unresolved:

- whether future workflow services should use a formal Unit of Work class or explicit `session_scope` blocks
- whether read-only request dependencies should be separated from write transaction dependencies
- how long-running background workers should manage transactional boundaries once workers exist

## Manual Review Queue Persistence

Phase 0 Module 6 expands `ReviewItem` from a lightweight safety placeholder into the persistent Manual Review Queue foundation.

The queue stores:

- review status
- intake processing state
- severity
- deterministic review reasons
- source system and source ID
- confidence, warning, normalization, and validation snapshots
- review metadata
- operator notes
- reviewed, deferred, and resolved timestamps
- audit correlation IDs

Review persistence rules:

- Manual Review items are durable operational records, not temporary validation messages.
- Review items must explain why automation stopped.
- Queue state transitions require an operator decision.
- Approval, rejection, deferral, and archival are review lifecycle actions only; they do not execute dispatch.
- Audit records can reference the same queryable correlation ID and evidence snapshots.

Unresolved:

- whether Manual Review items should eventually have a dedicated state-transition history table
- exact retention/archive policy for completed review items
- exact relationship between intake review items and future persisted job/visit records created after approval
- operator identity/auth fields once authentication exists

## Dispatch Orchestration Persistence Boundary

Phase 0 Module 7 adds dispatch orchestration preparation without adding new database tables.

The orchestration result is currently an in-memory deterministic decision structure. It composes normalized intake, validation, confidence, review recommendation, dispatch eligibility, warnings, and decision evidence.

Persistence boundary:

- orchestration does not create jobs
- orchestration does not create visits or work orders
- orchestration does not create route assignments
- orchestration does not persist Manual Review items
- orchestration does not call integrations
- orchestration does not mutate workflow state

Future workflow modules should persist orchestration outcomes through explicit service transactions after the storage model for imported intake and approved review outcomes is confirmed.

## Intake Processing Records

Phase 0 Module 8 adds `intake_processing_records` as the first persistent operational intake boundary.

The table stores:

- source references
- lifecycle state
- orchestration state
- review item linkage
- audit correlation ID
- dispatch eligibility flags
- raw payload snapshot
- orchestration result snapshot
- dispatch eligibility snapshot
- normalized, validation, confidence, review, warning, and deterministic evidence snapshots

Persistence philosophy:

- Orchestration remains in-memory decision preparation.
- Persistence stores the orchestration outcome and evidence.
- Persistence does not create jobs, visits, work orders, route assignments, exports, or integration calls.
- `approved_for_dispatch` means the intake record is eligible for a future dispatch workflow step, not that dispatch has executed.
- Review-required records must remain review-required unless a future explicit review-resolution transaction moves them forward.

Unresolved:

- whether intake processing records need immutable transition history rows
- whether source-system/source-ID uniqueness should be enforced per import source
- exact relationship between intake records and future persisted job/work-order records
- how operator identity and authorization should be captured on lifecycle transitions

## Operational Job Creation Records

Phase 0 Module 9 adds `job_creation_records` as the durable linkage between an approved intake processing record and the standard job created from it.

The table stores:

- intake processing record ID
- created job ID
- review item ID when present
- lifecycle state
- audit correlation ID
- creation snapshot
- intake snapshot
- orchestration snapshot
- dispatch eligibility snapshot
- review linkage snapshot
- deterministic evidence snapshot
- lifecycle metadata
- created-from-intake timestamp

Persistence philosophy:

- Intake persistence stores orchestration outcomes.
- Job creation consumes only explicitly approved intake records.
- Job creation records preserve why and how a job was created.
- A unique intake-processing-record link prevents duplicate standard job creation from the same intake record.
- Standard job creation sets the created job to `awaiting_dispatch`; it does not route or dispatch work.
- Water Emergency intake remains separated from standard job creation.

Unresolved:

- whether future job creation should materialize customer/property records at the same boundary
- whether future standard job creation should also create a work order or wait for a dispatch module
- whether duplicate protection should also be enforced on source-system/source-ID
- how Water Emergency intake should link to dedicated Water Emergency records instead of standard jobs
- whether creation attempts that fail should eventually be persisted as separate audit/history records

## Work Order And Visit Generation Traceability

Phase 0 Module 10 expands `work_orders` and `visits` with scheduling-ready generation traceability.

Work Orders store:

- job creation record ID
- review item ID when present
- audit correlation ID
- generation snapshot
- intake snapshot
- orchestration snapshot
- dispatch eligibility snapshot
- review linkage snapshot
- deterministic evidence snapshot
- lifecycle metadata
- generated-from-job timestamp

Visits store:

- work order ID
- audit correlation ID
- generation snapshot
- work order snapshot
- review linkage snapshot
- deterministic evidence snapshot
- lifecycle metadata
- generated-from-work-order timestamp

Persistence philosophy:

- Job creation and Work Order generation are separate boundaries.
- Work Order generation prepares technician-facing operational structure.
- Visit generation prepares assignment/scheduling/routing input.
- Generation does not assign technicians, run routing, schedule exact times, dispatch work, export to vendors, or call AI.
- Standard Work Order/Visit generation blocks Water Emergency jobs because Water Emergency requires a separated operational path.

Unresolved:

- whether production Work Order numbers should use date, branch, service type, or operator-visible sequence
- whether source-level duplicate protection should extend from intake into Work Order generation
- which service types require multiple visits or multiple Work Orders
- where future schedule-window persistence should live
- how Water Emergency Work Orders and Visits should differ from the standard path

## Assignment And Scheduling Preparation Snapshots

Phase 0 Module 11 expands `visits` with deterministic assignment and scheduling readiness snapshots.

Visits store:

- assignment readiness snapshot
- technician compatibility snapshot
- scheduling readiness snapshot
- operational readiness snapshot
- assignment-prepared timestamp
- scheduling-prepared timestamp

Persistence philosophy:

- Assignment preparation records readiness and blockers; it does not assign a technician.
- Scheduling preparation records AM/PM and service-state evidence; it does not set scheduled times.
- Technician compatibility currently validates active/inactive state and preserves future compatibility context.
- Water Emergency Visits are blocked from the standard assignment path.
- Readiness snapshots keep future routing/dispatch modules from recalculating hidden state from freeform strings.

Unresolved:

- exact technician availability statuses and which values should block assignment
- exact technician skill/service matching rules
- how service-area matching should interact with routing
- how multi-technician readiness should be represented for standard jobs
- when schedule-window readiness becomes an actual scheduled timestamp

## Routing And Dispatch Preparation Snapshots

Phase 0 Module 12 expands `visits` with deterministic routing and dispatch preparation snapshots.

Visits store:

- routing readiness snapshot
- dispatch readiness snapshot
- technician readiness snapshot
- Visit dispatch readiness snapshot
- routing-prepared timestamp
- dispatch-prepared timestamp

Persistence philosophy:

- Routing preparation records readiness and blockers; it does not optimize routes.
- Dispatch preparation records eligibility and blockers; it does not execute dispatch.
- Standard dispatch readiness requires explicit technician assignment and a scheduled start time.
- Inactive technicians, unassigned Visits, unscheduled Visits, blocked lifecycle, review-required lifecycle, and Water Emergency Visits block dispatch readiness.
- Readiness snapshots preserve deterministic evidence so future route optimization and dispatch execution do not infer safety from freeform text.

Unresolved:

- whether a future persisted `RouteAssignment` should be required before `dispatch_ready`
- exact route zone/region model for ACS production routing
- whether assigned technician readiness must always be revalidated from the database before dispatch
- how future route optimization results should attach to these preparation snapshots
- how Water Emergency routing/dispatch persistence should differ from the standard path

## Route Assignment And Dispatch Authorization Snapshots

Phase 0 Module 13 expands `route_assignments` into the first durable dispatch authorization boundary.

Route assignments store:

- route grouping key
- audit correlation ID
- route grouping snapshot
- route assignment readiness snapshot
- technician route compatibility snapshot
- dispatch authorization snapshot
- dispatch execution boundary snapshot
- deterministic evidence snapshot
- authorization-prepared timestamp
- authorized-for-dispatch timestamp

Persistence philosophy:

- Route assignment preparation records deterministic grouping and authorization evidence; it does not run route optimization.
- Dispatch authorization records whether a Visit is allowed to wait for future dispatch execution; it does not execute dispatch.
- Authorized route assignments move to `awaiting_dispatch_execution`.
- Blocked, review-required, Water Emergency, inactive-technician, unassigned, unscheduled, or route-unready Visits cannot become dispatch-authorized.
- Authorization evidence lives on `RouteAssignment` so future execution can consume one explicit boundary record rather than infer from Visit strings.

Unresolved:

- exact operator identity and approval semantics for dispatch authorization once auth exists
- whether future route optimization creates a new revision or updates the prepared route assignment
- exact production route grouping beyond state and AM/PM preparation
- whether warning-heavy but valid jobs need a second authorization step
- how the Water Emergency dispatch authorization record should differ from the standard route assignment path

## Dispatch Execution Snapshots

Phase 0 Module 14 expands `route_assignments` into the first durable internal dispatch execution boundary.

Route assignments store:

- dispatch execution state
- dispatch execution snapshot
- dispatch lifecycle snapshot
- dispatch audit snapshot
- dispatched timestamp
- future dispatch-failed timestamp

Persistence philosophy:

- Dispatch execution consumes an already authorized Route Assignment; it does not infer authorization from freeform Visit text.
- Internal dispatch execution moves standard records to `dispatched` only after deterministic blockers pass.
- External integration outcomes remain explicitly not executed in the execution snapshot.
- Duplicate dispatch attempts are blocked by lifecycle and timestamp evidence.
- Blocked, review-required, Water Emergency, inactive-technician, unassigned, unscheduled, unauthorized, or invalid-lifecycle records cannot dispatch through the standard path.

Unresolved:

- exact operator/system identity and actor model once authentication exists
- whether `awaiting_confirmation` should become a durable state before external adapter completion
- how failed external adapter execution should attach to the internal dispatch record
- whether dispatch retries create revisions or update the current Route Assignment
- how Water Emergency dispatch execution persistence should differ from the standard path

## External Dispatch Adapter Snapshots

Phase 0 Module 15 expands `route_assignments` with the first durable external adapter preparation boundary.

Route assignments store:

- external adapter state
- external adapter request snapshot
- external adapter payload snapshot
- external adapter lifecycle snapshot
- external adapter evidence snapshot
- external adapter audit snapshot
- external-adapter prepared timestamp
- future external-adapter failed timestamp

Persistence philosophy:

- Adapter preparation consumes an internally dispatched Route Assignment; it does not perform dispatch execution itself.
- Adapter payloads are prepared as deterministic snapshots for future FastField, Google Sheets, Google Calendar, and technician mobile workflows.
- External API calls remain explicitly not executed in this module.
- Duplicate adapter preparation attempts are blocked by adapter state and preparation timestamp.
- Blocked, review-required, Water Emergency, unauthorized, undispatched, invalid-lifecycle, or missing-linkage records cannot enter the standard external adapter path.

Unresolved:

- exact vendor payload schemas and field mappings
- whether external execution attempts need a dedicated immutable attempt table
- how retries, partial failures, and confirmations should be versioned
- how operator approval and credential scoping should be recorded once auth exists
- how Water Emergency external adapter persistence should differ from the standard path

## External Adapter Execution Snapshots

Phase 0 Module 18 expands `route_assignments` with the controlled external execution boundary.

Route assignments store:

- external execution state
- external execution request snapshot
- provider execution snapshot
- external execution evidence snapshot
- external execution failure snapshot
- external execution lifecycle snapshot
- external execution audit snapshot
- external execution started, completed, and failed timestamps

Persistence philosophy:

- External execution consumes prepared adapter payloads in `awaiting_external_execution`; it does not prepare payloads itself.
- Provider execution snapshots preserve FastField, Google Sheets, Google Calendar, and technician mobile evidence without calling live provider APIs.
- Successful controlled execution moves records to `awaiting_external_confirmation` for the confirmation/recovery boundary.
- Provider failure records failure evidence and blocks silent replay; retry execution remains a future explicit workflow.
- Blocked, review-required, Water Emergency, unauthorized, invalid-lifecycle, duplicate-attempt, or missing-payload records cannot enter the standard external execution path.

Unresolved:

- exact provider execution request and response contracts
- whether provider attempts need a dedicated immutable attempt table separate from Route Assignment snapshots
- how retry attempt limits and operator approval should be represented
- how credential scoping should attach to provider execution once auth exists
- how Water Emergency external execution persistence should differ from the standard path

## External Confirmation And Recovery Snapshots

Phase 0 Module 16 expands `route_assignments` with the first durable confirmation, failure recovery, retry-preparation, and reconciliation-preparation boundary.

Route assignments store:

- external confirmation state
- external confirmation evidence snapshot
- external confirmation lifecycle snapshot
- external confirmation audit snapshot
- external failure snapshot
- retry preparation snapshot
- reconciliation-required snapshot
- confirmation, failure, retry-prepared, and reconciliation-required timestamps

Persistence philosophy:

- Confirmation processing consumes adapter-prepared Route Assignments in `awaiting_external_confirmation`; it does not execute external APIs.
- Confirmation, failure, retry, and reconciliation evidence remain deterministic snapshots attached to the internal Route Assignment record.
- Retry preparation is not retry execution, and reconciliation preparation is not a reconciliation engine.
- Duplicate confirmations are blocked by confirmation state and timestamp evidence.
- Blocked, review-required, Water Emergency, unauthorized, invalid-lifecycle, or missing-linkage records cannot enter the standard external confirmation path.

Unresolved:

- exact vendor confirmation status mapping
- whether external confirmation attempts need a dedicated immutable attempt table
- how retry attempt limits and operator approval should be modeled once live execution exists
- how reconciliation cases should become Manual Review or operator tasks
- how Water Emergency confirmation persistence should differ from the standard path

## Operational Event History

Phase 0 Module 17 adds `operational_event_records` as the append-only operational history and timeline foundation.

Operational event records store:

- occurred and recorded timestamps
- event type and event state
- generic entity type and entity ID
- Route Assignment, Visit, Work Order, Job, and technician references when available
- audit correlation ID
- previous and new lifecycle states
- deterministic event fingerprint
- immutable marker
- event, transition, immutable evidence, retry/recovery, reconciliation, and audit snapshots

Persistence philosophy:

- Event history is append-only and exists beside current audit logs and lifecycle snapshots.
- Services may append timeline evidence, but they must not mutate existing event records.
- Event records are evidence, not workflow commands.
- Duplicate event fingerprints are blocked before persistence.
- No-op lifecycle transitions and missing audit correlation are blocked.
- Timeline queries sort by event occurrence time and recorded time.

Unresolved:

- whether external execution attempts should become a separate immutable attempt table
- whether authentication should add actor identity to the event fingerprint
- retention, archive, and legal hold policy for immutable operational events
- whether analytics should query event history directly or consume derived reporting tables
- how Water Emergency timelines should differ from the standard operational execution timeline

## Dispatch Reconciliation And Consistency Snapshots

Phase 0 Module 19 expands `route_assignments` with deterministic reconciliation and operational consistency snapshots.

Route assignments store:

- dispatch reconciliation state
- dispatch consistency snapshot
- dispatch divergence snapshot
- dispatch mismatch snapshot
- dispatch reconciliation blocker snapshot
- dispatch reconciliation audit snapshot
- reconciliation prepared timestamp
- consistency verified timestamp
- reconciliation blocked timestamp

Persistence philosophy:

- Reconciliation preparation reads internal lifecycle, external execution, external confirmation, and immutable event evidence.
- Consistency verification records deterministic evidence but does not execute reconciliation.
- Divergence detection classifies mismatches and prepares manual-resolution evidence.
- Immutable event history is read-only input; reconciliation cannot mutate or replay it.
- Blocked, review-required, Water Emergency, unauthorized, duplicate, invalid-lifecycle, or mutable-history records cannot enter the standard reconciliation path.

Unresolved:

- whether reconciliation attempts need a separate immutable attempt table
- whether future reconciliation should create Manual Review items automatically
- how provider-specific mismatch classifications should evolve once live APIs exist
- how operator ownership and approvals should be modeled
- how Water Emergency reconciliation persistence should differ from the standard path
