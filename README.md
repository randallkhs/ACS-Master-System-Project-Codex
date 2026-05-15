# ACS Master System Project

Custom Field Service Management platform for Apple Cleaning Systems.

This repository is the long-term ACS FSM foundation. It is not a temporary script launcher.

## Current Status

- Phase: Phase 0 Module 6
- Current implementation: hardened FastAPI backend foundation with deterministic intake pipeline and persistent Manual Review Queue foundations
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
