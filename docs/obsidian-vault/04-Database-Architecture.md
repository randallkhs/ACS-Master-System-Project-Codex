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

## Phase 0 Module 27 Local PostgreSQL Development Database

Module 27 establishes the local development database workflow for live dashboard read-model verification.

Default local development assumptions:

- database: `acs_fsm_dev`
- user: `acs_fsm_dev`
- host: `127.0.0.1`
- SQLAlchemy URL shape: `postgresql+psycopg://acs_fsm_dev:acs_fsm_dev@127.0.0.1:5432/acs_fsm_dev`

Rules:

- This is local-development-only and not production deployment.
- Production credentials must remain outside source control and documentation.
- Alembic migrations remain the schema setup mechanism.
- Synthetic dashboard seed data is allowed only for local read-model verification.
- Seed data must be clearly source-labeled, contain no customer-sensitive data, call no vendors, and imply no real production state.
- Automated unit tests must continue to run without a live local database unless a future integration-test profile explicitly opts in.

Unresolved:

- whether future integration tests should use a dedicated `acs_fsm_test` PostgreSQL database
- whether local database lifecycle should remain manual or gain optional non-production tooling
- exact production database backup, restore, and migration rollout procedures

## Phase 0 Module 28 Local PostgreSQL Bootstrap Verification

Module 28 moves the local database workflow from documented readiness to an actual workstation bootstrap when PostgreSQL is safely available.

Verified local bootstrap actions:

- detected Homebrew PostgreSQL client tools: `psql`, `pg_isready`, and `createdb`
- detected a stopped local `postgresql@18` Homebrew service
- started only the local development PostgreSQL service with the normal Homebrew service command
- created the missing local-only `acs_fsm_dev` role and `acs_fsm_dev` database
- ran Alembic migrations to `20260515_0018`
- inserted synthetic dashboard seed records labeled `module27_dev_seed`
- verified read-only dashboard endpoints against the local PostgreSQL database

Safety rules:

- repository scripts must not install PostgreSQL or Homebrew packages automatically
- database bootstrap remains local-development-only and must not target remote or production hosts
- destructive reset commands require explicit developer intent and must remain scoped to `acs_fsm_dev`
- seed data remains synthetic and must not imply real production state
- dashboard endpoint checks remain GET-only and read-only

Implementation note:

- the local database checker now distinguishes a reachable but unmigrated database from a failed connection by reporting `connected=true` and `migrated=false` when the `alembic_version` table is not present yet

Unresolved:

- whether ACS wants local PostgreSQL managed through Homebrew, Postgres.app, Docker, or a separate standard for each developer workstation
- whether future integration tests should bootstrap a separate disposable `acs_fsm_test` database
- production database provisioning, backup, restore, and migration rollout procedures

## Phase 0 Module 29 Local Dashboard Seed Scenario Expansion

Module 29 expands local development seed data so dashboard read models can be verified against more realistic synthetic operational states.

Seed scenario coverage:

- standard dispatch-ready work awaiting execution
- Manual Review open, deferred, approved, and archived examples
- blocked route and blocked intake examples
- external confirmation failure with retry-preparation evidence
- successful external confirmation evidence
- reconciliation-required and consistency-verified examples
- rollback-preparation and recovery evidence
- governance manual-intervention and operator-approved examples
- accountability escalation, incident-preparation, and blocked examples
- ordered immutable operational event timeline entries
- open and closed Water Emergency records, separated from standard dispatch

Seed behavior:

- seed execution remains dev/test-only and local-database-only
- seed records are synthetic, fake, source-labeled, and contain no customer-sensitive data
- the seed script upserts seed-owned records by deterministic IDs or natural seed keys
- rerunning the seed updates/inserts seed-owned examples without resetting the database or deleting non-seed data
- external/vendor execution fields remain evidence-only and explicitly not executed

Unresolved:

- whether future demo data should move into named scenario packs
- whether UI storyboards should map to seed scenario labels
- whether local integration tests should run against a disposable database rather than persistent `acs_fsm_dev`

## Phase 0 Module 31 Water Emergency Dashboard Read Model

Module 31 adds a dedicated Water Emergency dashboard read model without changing the database schema.

Read-model behavior:

- consumes existing `WaterEmergency`, `Job`, `WorkOrder`, `Visit`, `ReviewItem`, and `OperationalEventRecord` rows
- summarizes open/closed counts, status/stage distribution, multi-visit indicators, equipment flags, review/escalation indicators, related references, data gaps, and timeline evidence
- remains read-only and does not mutate ORM objects or infer lifecycle transitions

Unresolved:

- future Water Emergency execution modules may require dedicated equipment, moisture reading, visit-stage, and immutable emergency-history tables
- production filtering and pagination for Water Emergency dashboard records remain undecided
- exact Water Emergency closure and pickup data requirements still need operations confirmation

## Phase 0 Module 32 Water Emergency Detail Read Model

Module 32 adds a read-only Water Emergency detail projection without changing the database schema.

Read-model behavior:

- consumes existing `WaterEmergency`, `Job`, `WorkOrder`, `Visit`, `ReviewItem`, and `OperationalEventRecord` rows
- returns one Water Emergency record by UUID
- includes related job/work-order/visit references when available
- includes Manual Review indicators only when specifically linked to the selected record through job, entity, or visit linkage
- includes chronological operational event timeline evidence scoped to the selected record
- returns data-gap buckets for missing detail evidence instead of inventing lifecycle state
- returns 404 for missing records through the API detail route

Unresolved:

- whether future detail read models need separate query optimization or materialized projections
- whether Water Emergency equipment, moisture readings, and visit-stage history should become dedicated tables
- production timeline filtering, pagination, retention, and role-scoped visibility

## Phase 0 Module 33 Water Emergency Visibility Read Models

Module 33 extends the Water Emergency dashboard/detail projections without changing the database schema.

Read-model behavior:

- derives equipment context from existing `WaterEmergency.equipment_onsite`, `WaterEmergency.moisture_tracking_required`, and related `WorkOrder.required_equipment_notes`
- derives visit-chain context from related `Visit` rows and existing visit timestamps/statuses
- derives drying-stage visibility from existing `WaterEmergency.status`, `drying_stage`, and `next_required_action`
- exposes explicit unknown indicators, including `equipment_inventory_not_modeled`, where dedicated inventory or moisture-reading tables do not yet exist
- excludes Water Emergency visits from standard dispatch-ready action counts while still preserving persisted visit status buckets

Unresolved:

- future schema may require dedicated equipment inventory, deployment/pickup, moisture readings, photo evidence, and emergency history tables
- final Water Emergency stage taxonomy remains an operations decision
- production read-model query optimization remains future work

## Phase 0 Module 34 Water Emergency Review And Exception Read Models

Module 34 extends the Water Emergency dashboard/detail projections without changing the database schema.

Read-model behavior:

- derives review/exception counts from existing `ReviewItem` status, severity, reason-code, ID, and audit-correlation fields
- derives blocker reason buckets from persisted reason-code evidence without defining a final operations taxonomy
- exposes critical unresolved and escalation indicators as read-only alert visibility
- scopes detail-level review context to concrete Water Emergency job, entity, or visit links
- exposes unknown indicators when a selected Water Emergency record has no specifically scoped review evidence
- adds synthetic local seed examples for open critical, deferred, and archived Water Emergency review states

Unresolved:

- future schema may require typed Water Emergency exception categories, dedicated alert history, and review-state transition history
- final review/escalation taxonomy remains an operations decision
- production read-model query optimization, pagination, and role-scoped review visibility remain future work

## Phase 0 Module 35 Water Emergency Next-Step Readiness Read Models

Module 35 extends the Water Emergency dashboard/detail projections without changing the database schema.

Read-model behavior:

- derives next-step readiness labels from persisted `WaterEmergency`, `Job`, `WorkOrder`, `Visit`, `ReviewItem`, and `OperationalEventRecord` evidence
- treats unresolved scoped review evidence as Manual Review/operator-decision readiness context
- treats missing work-order, visit, timeline, drying-stage, or next-action evidence as missing-data readiness context
- treats closed/resolved Water Emergency records as no-active-next-step visibility
- exposes ready-for-close-review as read-only evidence only; no close action or final closure rule is implemented
- expands synthetic local seed examples for missing data, visit follow-up, equipment review, ready-for-close-review, and closed/no-active-action visibility

Unresolved:

- future schema may require stored Water Emergency readiness states, typed blocker categories, equipment deployment/pickup tables, moisture readings, and closure-review history
- final Water Emergency readiness/closure taxonomy remains an operations decision
- production read-model query optimization, pagination, and role-scoped readiness visibility remain future work

## Phase 0 Module 37 Water Emergency Aging And Follow-Up Read Models

Module 37 extends the Water Emergency dashboard projection without changing the database schema.

Read-model behavior:

- derives aging and follow-up labels from persisted `WaterEmergency` opened/closed timestamps, related `Visit` timestamps, scoped `ReviewItem` timestamps, and `OperationalEventRecord` timestamps
- exposes time-sensitivity labels, timing groups, age buckets, follow-up buckets, stale/missing evidence indicators, reason codes, related IDs, audit IDs, and evidence references
- treats unresolved scoped review evidence as waiting-for-review timing context
- treats missing timestamp evidence as unknown timing instead of inventing an SLA state
- treats closed/resolved Water Emergency records as separated timing history, not active overdue work
- expands synthetic local seed examples for newly opened, active monitoring, follow-up due, follow-up overdue, stale evidence, waiting review, ready-for-close-review, closed/resolved, and unknown timing visibility

Unresolved:

- future schema may require stored Water Emergency SLA windows, follow-up checkpoints, stale-evidence acknowledgement history, and typed timing/review categories
- final Water Emergency aging, SLA, and follow-up taxonomy remains an operations decision
- production read-model query optimization, pagination, stale-data behavior, and role-scoped timing visibility remain future work

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

## Operational Replay And Recovery Preparation Snapshots

Phase 0 Module 20 expands `route_assignments` with deterministic replay, rollback-preparation, and recovery-coordination snapshots.

Route assignments store:

- replay/recovery state
- replay preparation snapshot
- rollback preparation snapshot
- replay eligibility snapshot
- replay blocker snapshot
- recovery coordination snapshot
- replay/recovery audit snapshot
- replay prepared, rollback prepared, and replay blocked timestamps

Persistence philosophy:

- Replay preparation consumes reconciliation, retry, or failure context; it does not execute replay.
- Rollback preparation records rollback evidence only; it does not mutate operational state or event history.
- Recovery coordination preserves manual-recovery requirements and audit continuity for future operator workflows.
- Immutable event history is read-only input; replay preparation cannot mutate or replay it.
- Blocked, review-required, Water Emergency, unauthorized, duplicate, invalid-lifecycle, no-recovery-context, or mutable-history records cannot enter the standard replay/recovery path.

Unresolved:

- whether replay attempts need a separate immutable attempt table
- exact operator approval semantics before any future replay or rollback execution
- how rollback scope should be constrained for production data recovery
- whether recovery coordination should create Manual Review items automatically
- how Water Emergency replay/recovery persistence should differ from the standard path

## Operational Governance And Approval Control Snapshots

Phase 0 Module 21 expands `route_assignments` with deterministic governance, approval-control, and manual-intervention snapshots.

Route assignments store:

- governance state
- governance approval snapshot
- intervention authorization snapshot
- replay authorization snapshot
- rollback authorization snapshot
- reconciliation approval snapshot
- governance blocker snapshot
- governance audit snapshot
- governance approved, rejected, intervention-required, and blocked timestamps

Persistence philosophy:

- Governance records operator approval evidence; it does not execute the governed operation.
- Replay, rollback, and reconciliation remain blocked from future execution unless a governance approval snapshot exists.
- Manual intervention authorization is evidence for future operator workflows, not a workflow engine.
- Immutable event history is read-only input; governance cannot mutate or replay it.
- Blocked, review-required, Water Emergency, unauthorized-operator, duplicate-approval, invalid-lifecycle, missing-operator, or mutable-history records cannot enter the standard governance path.

Unresolved:

- exact operator identity and role model once authentication exists
- whether governance approvals need a dedicated immutable approval table
- whether high-risk actions require two-person approval
- how approval expiration and revocation should work
- how Water Emergency governance persistence should differ from the standard path

## Operational Accountability, Escalation, And Incident Snapshots

Phase 0 Module 22 expands `route_assignments` with deterministic accountability, escalation-preparation, intervention-escalation, and incident-preparation snapshots.

Route assignments store:

- accountability state
- escalation preparation snapshot
- incident preparation snapshot
- accountability evidence snapshot
- escalation blocker snapshot
- intervention escalation snapshot
- operational incident snapshot
- accountability audit snapshot
- escalation-required, incident-prepared, critical-intervention-required, and blocked timestamps

Persistence philosophy:

- Accountability records escalation and incident-preparation evidence; it does not execute escalation or incident workflows.
- Replay/recovery escalation cannot bypass governance approval.
- Critical divergence context is preserved as escalation evidence for future operator coordination.
- Immutable event history is read-only input; accountability cannot mutate or replay it.
- Blocked, review-required, Water Emergency, unauthorized, duplicate-escalation, invalid-lifecycle, missing-operator, missing-governance, no-context, or mutable-history records cannot enter the standard accountability path.

Unresolved:

- whether escalation and incident records need dedicated immutable tables
- whether critical accountability actions require two-person approval
- how escalation acknowledgement and closure should work once auth exists
- how accountability should create or link Manual Review items in future modules
- how Water Emergency accountability persistence should differ from the standard path

## Water Emergency Filter/Sort View-State Projection

Phase 0 Module 38 adds read-only filter, sort, grouping, and view-state metadata to the Water Emergency dashboard contract without adding database tables or columns.

Persistence philosophy:

- filter options, sort options, primary view groups, and sort ranks are derived read-model projections
- frontend filter selection is display state only and is not persisted as operational state
- view-state items combine existing Water Emergency, Work Order, Visit, Review, and operational event evidence through the existing readiness, queue, and aging projections
- closed/resolved records remain separated from active records in the read model
- missing or ambiguous evidence remains visible as blocked, unknown, or needs-operator-review context instead of hidden lifecycle progress

Unresolved:

- whether production saved views or role-specific filters need dedicated persistence later
- final Luis-confirmed filter, triage, queue, SLA, and Water Emergency operations taxonomy
- production pagination/query optimization for larger Water Emergency record sets
- how future authenticated actions should interact with filter state without making the frontend the source of truth

## Water Emergency Governance And Saved-View Readiness

Phase 0 Module 39 adds read-only governance and result-window metadata to the Water Emergency dashboard contract without adding database tables or columns.

Persistence philosophy:

- provisional Water Emergency filters, attention labels, timing labels, and readiness labels remain derived read-model metadata
- the metadata is marked as a Randall-authorized Phase 0 visibility baseline for internal software behavior
- timing/follow-up labels remain conservative visibility heuristics and are not final SLA enforcement
- legal, insurance, compliance, warranty, drying certification, customer-facing, or company-liability policy remains outside the database model until Alfonso owner review
- frontend saved view preferences are browser-local only and do not become backend operational state
- no authentication, RBAC, user-preference table, or backend saved-view persistence is added in Module 39
- result-window metadata reports current counts and sort context only; it does not implement production pagination yet

Unresolved:

- whether future authenticated saved views need a dedicated user-preferences table
- whether future pagination should use cursor-based read models or materialized dashboard projections
- exact role-scoped visibility rules after auth exists
- final owner-reviewed SLA, insurance, drying certification, warranty, and customer-facing policy language

## Manual Review Filter/Sort View-State Projection

Phase 0 Module 42 adds read-only filter, sort, and result-window metadata to the Manual Review queue contract without adding database tables or columns.

Persistence philosophy:

- Manual Review filter groups and sort options are derived read-model metadata from existing ReviewItem evidence
- frontend filter selection and sort selection are display state only and are not persisted as backend operational state
- browser-local saved preferences may remember only the selected Manual Review filter and sort option
- saved preferences must not store tokens, secrets, PII, customer data, backend records, or Manual Review decisions
- Water Emergency-related reviews remain separated through concrete persisted linkage, not frontend inference
- no authentication, RBAC, user-preference table, backend saved-view persistence, or Manual Review action execution is added in Module 42

Unresolved:

- whether future authenticated saved views need a dedicated user-preferences table
- whether production review queues should use cursor-based pagination, result windows, or materialized projections
- exact role-scoped Manual Review visibility rules after auth exists
- final Manual Review action taxonomy and operator authority model

## Manual Review Decision-Readiness Projection

Phase 0 Module 43 adds read-only decision-readiness and resolution-preparation metadata to Manual Review queue and detail contracts without adding database tables or columns.

Projection philosophy:

- readiness labels are derived from existing ReviewItem status, reason, severity, blocker, entity-link, Water Emergency-link, dispatch-link, and evidence-reference data
- labels such as needs-missing-information, needs-entity-context, needs-Water-Emergency-review, needs-dispatch-review, ready-for-operator-decision, ready-for-resolution-review, blocked-by-conflict, blocked-by-missing-data, and resolved-or-archived are Randall-authorized Phase 0 visibility baselines only
- Water Emergency-related readiness remains separated through persisted linkage instead of generic entity labels
- resolved and archived review items are projected as historical visibility rather than active decision needs
- no review action state, operator authority, auth/RBAC table, user-preference table, vendor execution, AI authority, or workflow engine is added in Module 43

Unresolved:

- final Manual Review action taxonomy and authenticated operator authority model
- whether future resolution workflows need dedicated transition history or decision outcome tables
- exact role-scoped Manual Review visibility rules after auth exists

## Manual Review Command-Contract Projection

Phase 0 Module 46 adds read-only future command-contract and audit-envelope metadata to Manual Review queue and detail contracts without adding database tables or columns.

Projection philosophy:

- command-contract labels are derived from existing ReviewItem status, reason, recommended action, entity-link, Water Emergency-link, decision-readiness, action-preflight, future-action preview, and evidence-reference data
- every projected command contract is currently non-executable
- every future command contract requires future auth, operator identity, role authorization, audit reason, idempotency key, immutable event recording, and post-action consistency checks
- missing entity context, conflict evidence, Water Emergency scope, and resolved/archived status remain blockers or historical visibility states
- no command table, audit-envelope persistence, operator identity table, RBAC table, action history table, vendor execution record, AI authority, or workflow engine is added in Module 46

Unresolved:

- future authenticated Manual Review command execution schema
- operator identity, role authorization, idempotency, audit reason, immutable event, and consistency-check persistence
- final command taxonomy and role-scoped action authority

## Manual Review Audit-Ledger Dry-Run Projection

Phase 0 Module 47 adds read-only audit-ledger and command dry-run metadata to Manual Review queue and detail contracts without adding database tables or columns.

Persistence philosophy:

- audit-ledger dry-run labels are derived from existing ReviewItem status, reason, recommended action, entity-link, Water Emergency-link, action-preflight labels, command-contract labels, and evidence-reference data
- every projected dry-run record is currently non-executable and Phase 0 blocks execution
- every future dry-run requires audit reason, operator identity, role authorization, idempotency key, immutable event recording, and post-action consistency checks
- proposed future event type/state, audit envelope fields, idempotency scope, and consistency-check summaries are deterministic read-model metadata only
- existing OperationalEventRecord evidence remains the read source for timeline/audit references; this module does not write audit events
- missing entity context, conflict evidence, Water Emergency scope, and resolved/archived status remain blockers or historical visibility states
- no audit-ledger table, command table, audit-envelope persistence, operator identity table, RBAC table, action history table, vendor execution record, AI authority, or workflow engine is added in Module 47

Unresolved:

- future authenticated Manual Review command execution schema
- durable audit ledger or immutable event write model for executed actions
- operator identity, role authorization, audit reason, idempotency, immutable event, and consistency-check persistence
- final dry-run/action taxonomy and role-scoped action authority

## Manual Review Command-Validation Projection

Phase 0 Module 48 adds read-only command-validation and safety-gate matrix metadata to Manual Review queue and detail contracts without adding database tables or columns.

Projection philosophy:

- command-validation labels are derived from existing ReviewItem status, reason, recommended action, entity-link, Water Emergency-link, decision-readiness, action-preflight, future-action preview, command-contract, audit-ledger dry-run, and evidence-reference data
- every projected validation record is currently non-executable and Phase 0 blocks execution
- every safety gate is read-only and reports whether a future prerequisite is present, required, or blocked; no gate writes state or executes a workflow
- every future validation record exposes required audit reason, operator identity, role authorization, idempotency key, immutable event recording, post-action consistency check, entity context, and Phase 0 execution-blocked gates
- missing entity context, conflict evidence, Water Emergency scope, and resolved/archived status remain blockers or historical visibility states
- no validation table, safety-gate table, command table, audit-envelope persistence, operator identity table, RBAC table, action history table, vendor execution record, AI authority, or workflow engine is added in Module 48

Unresolved:

- future authenticated Manual Review command validation/execution schema
- durable safety-gate/audit-ledger persistence requirements for executed actions
- operator identity, role authorization, audit reason, idempotency, immutable event, and consistency-check persistence
- final validation/action taxonomy and role-scoped action authority

## Manual Review Permission-Readiness Projection

Phase 0 Module 49 adds read-only operator-identity, role-authorization, and permission-readiness metadata to Manual Review queue and detail contracts without adding database tables or columns.

Projection philosophy:

- permission-readiness labels are derived from existing ReviewItem status, reason, recommended action, entity-link, Water Emergency-link, command-validation labels, command-contract labels, and evidence-reference data
- every projected permission-readiness record is currently non-executable and Phase 0 blocks execution
- every future permission-readiness record exposes required future auth, operator identity, role authorization, audit actor, audit reason, idempotency key, immutable event recording, post-action consistency check, and permission-set requirements
- service accounts, technicians, and unknown operators are future forbidden Manual Review operator-action actors
- Water Emergency scope, missing entity context, resolved/archived status, and unknown operator context remain blockers or historical visibility states
- no operator identity table, RBAC table, permission table, command table, audit-envelope persistence, action history table, vendor execution record, AI authority, or workflow engine is added in Module 49

Unresolved:

- future authenticated Manual Review command validation/execution schema
- final ACS-FSM auth provider and operator identity schema
- durable RBAC/permission model and role-scoped action authority
- operator identity, role authorization, audit actor, audit reason, idempotency, immutable event, and consistency-check persistence

## Manual Review Execution-Readiness Audit Projection

Phase 0 Module 50 adds read-only execution-readiness audit, mutation-boundary lock, and future transition prerequisite metadata to the Manual Review queue contract without adding database tables or columns.

Projection philosophy:

- execution-readiness counts are derived from already-built Manual Review queue items and their existing decision-readiness, preflight, preview, command-contract, dry-run, command-validation, safety-gate, and permission-readiness metadata
- `manual_review_mutations_enabled` is false, `action_execution_phase` is `read_only_phase_0`, `currently_executable_count` is zero, and mutation endpoints are unavailable
- future auth, RBAC, operator identity, audit envelope, audit reason, idempotency, immutable event, post-action consistency, action-contract, action-UI, ACSSDR report, and Review GUI/ChatGPT review prerequisites are transition-plan metadata only
- Water Emergency-related readiness remains counted and separated from standard dispatch-related readiness
- liability-sensitive customer-facing, insurance, warranty, drying certification, formal policy, and billing/financial actions are flagged for Alfonso owner review before becoming binding policy or action authority
- no execution-readiness table, mutation table, operator identity table, RBAC table, permission table, command table, audit-envelope persistence, action history table, vendor execution record, AI authority, or workflow engine is added in Module 50

Unresolved:

- future authenticated Manual Review command validation/execution schema
- final ACS-FSM auth provider and operator identity schema
- durable RBAC/permission model and role-scoped action authority
- approved audit envelope, idempotency, immutable event, rollback/replay, and post-action consistency strategies
- owner-reviewed legal, insurance, warranty, certification, policy, and financial action boundaries

## Manual Review Auth Diagnostics Projection

Phase 0 Module 53 adds read-only auth diagnostics, runtime safety, and secret-hygiene metadata to the Manual Review auth-boundary read model without adding database tables or columns.

Projection philosophy:

- auth diagnostics are deterministic metadata layered on the existing auth configuration readiness projection
- `auth_enabled`, token verification, RBAC enforcement, login UI, required auth headers, and frontend-emitted auth headers remain false in Phase 0
- tracked `.env`, tracked `.env.local`, tracked service account JSON, private key detection, and placeholder-only status are reported as safe booleans only
- the secret-hygiene helper inspects tracked/example files and must not read or print real credential values as dashboard data
- no auth diagnostics table, credential table, operator identity table, RBAC table, session table, token table, mutation endpoint, vendor execution record, AI authority, or workflow engine is added in Module 53

Unresolved:

- final ACS-FSM auth provider and production credential ownership
- secure VPS secret configuration and local development auth mode
- token verification, auth middleware, RBAC enforcement, role-scoped visibility, and authenticated Manual Review action authority

## Manual Review Auth Claims Mapping Projection

Phase 0 Module 54 adds read-only auth claims mapping, token-verification dry-run, and role-resolution metadata to the Manual Review auth-boundary read model without adding database tables or columns.

Projection philosophy:

- auth claims mapping is deterministic planning metadata layered on the existing auth boundary, auth configuration readiness, and auth diagnostics projections
- `token_verification_enabled`, `real_token_parsing_enabled`, `jwks_fetch_enabled`, required auth headers, and frontend-emitted auth headers remain false in Phase 0
- future subject, email, email verification, display name, role, permission, provider, issuer, audience, tenant/domain, expiration, issued-at, and auth-time claims are documented as future contract labels only
- role resolution metadata maps unknown roles to `unknown_operator`, blocks `system_service` and service-account subjects for Manual Review operator actions, and keeps technician Manual Review action authority blocked unless a future reviewed module authorizes it
- example claim fixtures use placeholder scope only and do not contain real user data, real tokens, private keys, service account JSON, credentials, or JWT-like strings
- no auth claims table, token/session table, credential table, JWKS cache table, operator identity table, RBAC table, mutation endpoint, vendor execution record, AI authority, or workflow engine is added in Module 54

Unresolved:

- final provider claim names and production credential ownership
- token verification middleware, JWKS strategy, RBAC enforcement, role-to-permission expansion, role-scoped visibility, and authenticated Manual Review action authority

## Manual Review Route Protection Matrix Projection

Phase 0 Module 55 adds read-only route protection matrix and access decision dry-run metadata to the Manual Review auth-boundary read model without adding database tables or columns.

Projection philosophy:

- route protection metadata is deterministic planning metadata layered on the existing auth boundary, auth configuration, auth diagnostics, and claims mapping projections
- API routes, frontend sections, and future action surfaces are mapped to future roles and permissions as labels only
- `enforcement_enabled`, `phase_allows_enforcement`, `route_guarding_enabled`, token verification, and RBAC enforcement remain false in Phase 0
- access decision dry-run metadata simulates readiness only and never denies requests, hides UI, requires headers, parses tokens, validates JWTs, or creates route guards
- Water Emergency-related route and section metadata remains separated from standard Manual Review and dispatch visibility
- legal, insurance, warranty, drying certification, billing, customer-promise, and formal policy surfaces are flagged for Alfonso owner review before executable behavior or binding policy exists
- no route protection table, route guard table, RBAC table, token/session table, JWT/JWKS table, operator identity table, mutation endpoint, vendor execution record, AI authority, or workflow engine is added in Module 55

Unresolved:

- final route guard architecture, token verification middleware, RBAC enforcement, role-to-permission expansion, role-scoped visibility, frontend section hiding policy, and authenticated Manual Review action authority

## Auth/RBAC Readiness Audit Projection

Phase 0 Module 56 adds a read-only Auth/RBAC readiness audit, enforcement-boundary lock, and future transition prerequisite checklist to the Manual Review auth-boundary read model without adding database tables or columns.

Projection philosophy:

- Auth/RBAC readiness audit metadata is computed from existing read-model/catalog layers and static Phase 0 contract definitions
- enforcement-boundary lock metadata explicitly keeps auth enforcement, token verification, real token parsing, JWKS fetch, RBAC enforcement, route guarding, sign-in UI, user management, action execution, mutation endpoints, and Phase 0 enforcement allowances false
- future prerequisites describe provider selection, real credentials, token verification, claims mapping, operator identity, RBAC policy, route guarding, Manual Review action permissions, Water Emergency action permissions, audit actor/idempotency, owner review, and review workflow as planning states only
- Water Emergency action authorization remains separated from standard Manual Review and dispatch projections
- no operator identity table, RBAC table, route protection table, token/session table, JWT/JWKS table, audit-action table, mutation endpoint, vendor execution record, AI authority, or workflow engine is added in Module 56

Unresolved:

- final auth provider, production secret provisioning, token verification middleware, route guard architecture, RBAC enforcement, role-to-permission expansion, role-scoped visibility, audit actor/idempotency persistence, and authenticated action authority remain future schema/design work
