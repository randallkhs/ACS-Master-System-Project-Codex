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

## First Module Boundary

The first real implementation module is the Dispatch Operations Engine.

It should not attempt to build the full FSM immediately.

See [[12-Roadmap/MASTER_ROADMAP]] for phased scope.
