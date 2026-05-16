# ACS Master System Project

Custom Field Service Management platform for Apple Cleaning Systems.

This repository is the long-term ACS FSM foundation. It is not a temporary script launcher.

## Current Status

- Phase: Phase 0 Module 20
- Current implementation: hardened FastAPI backend foundation with deterministic intake, Manual Review Queue, dispatch orchestration, operational intake persistence, controlled operational job creation, Work Order/Visit generation, technician assignment/scheduling preparation, routing/dispatch preparation, route-assignment/dispatch-authorization, internal dispatch execution, external adapter preparation, controlled external adapter execution, external confirmation/failure recovery, immutable operational event history, dispatch reconciliation/operational consistency, and operational replay/recovery preparation foundations
- Frontend: deferred for a later Phase 0 module
- Production target: Linux VPS, Apache reverse proxy, HTTPS, FastAPI backend, PostgreSQL database, future Next.js frontend

## Repository Structure

```text
backend/                 FastAPI backend foundation
docs/obsidian-vault/     Project architecture vault and decisions
docs/codex-system/       AI memory/documentation standards
```

## Backend

The backend scaffold includes:

- FastAPI app factory
- `/api/v1/health` endpoint
- Pydantic Settings configuration
- SQLAlchemy 2 model foundation
- Alembic migration environment and initial migration
- PostgreSQL connection setup
- service-layer placeholders and intake pipeline foundations
- integration adapter placeholders
- structured logging and request ID middleware
- lifecycle/readiness foundation
- repository-layer and request-scoped DB session foundation
- deterministic intake normalization, validation, confidence, and Manual Review preparation foundation
- persistent Manual Review Queue fields, lifecycle states, traceability snapshots, and audit-correlation foundation
- deterministic dispatch orchestration preparation and dispatch eligibility result foundation
- operational intake processing record persistence with orchestration snapshots, eligibility snapshots, review linkage, and audit correlation
- controlled job creation from explicitly approved intake records with creation snapshots, intake-to-job linkage, and duplicate prevention foundation
- deterministic Work Order and Visit generation foundations with scheduling-ready lifecycle states and traceability snapshots
- deterministic technician assignment and scheduling preparation with readiness snapshots and lifecycle blockers
- deterministic routing and dispatch preparation with readiness snapshots, dispatch blockers, and no dispatch execution
- deterministic route assignment and dispatch authorization boundary with grouping snapshots
- deterministic internal dispatch execution lifecycle with execution snapshots, audit continuity, and no external integration execution
- deterministic external adapter preparation boundary with FastField, Sheets, Calendar, and technician-mobile payload snapshots but no live API execution
- deterministic controlled external adapter execution boundary with provider execution evidence, audit continuity, and no real vendor API execution
- deterministic external execution confirmation, retry-preparation, and reconciliation-preparation boundary with no live API execution or automatic retries
- append-only operational event history foundation for lifecycle, dispatch, adapter, confirmation, retry, and reconciliation timeline evidence
- deterministic dispatch reconciliation and operational consistency verification foundation with divergence/mismatch evidence and no reconciliation execution
- deterministic operational replay, rollback preparation, and recovery coordination foundation with immutable evidence and no automatic replay execution
- backend Makefile developer commands
- pytest and Ruff configuration

See [backend/README.md](backend/README.md).

## Critical Rules

Before generating implementation code:

1. Read `AGENTS.md`.
2. Read the relevant architecture documents under `docs/obsidian-vault/`.
3. Follow `docs/obsidian-vault/CODEX_PHASE_0_BUILD_PROMPT.md` for Phase 0 boundaries.
4. Never bypass manual review safety rules.
5. Never silently process uncertain jobs.

## Operational Safety

- The database is the operational source of truth.
- External systems are adapters only.
- Manual Review is a core safety system.
- AI is advisory only.
- Water Emergency workflows are first-class workflows.
- Uncertain jobs must never auto-dispatch.
