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
