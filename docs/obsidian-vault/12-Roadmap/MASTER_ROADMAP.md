# ACS FSM — Master Roadmap

## Purpose

This roadmap captures the pre-implementation project direction. It should stay compact and be updated when major scope or sequence decisions change.

---

## Current State

Status: Pre-implementation architecture and planning.

The repository currently contains:

- project-level engineering rules
- Obsidian architecture vault
- AI memory/documentation standards
- Phase 0 build prompt
- first-module scope
- operational planning documents

The repository does not yet contain production backend or frontend implementation.

---

## Phase 0 — Foundation

Goal: create the professional system foundation without full business workflow automation.

Expected foundation:

- monorepo structure
- FastAPI backend skeleton
- PostgreSQL configuration
- SQLAlchemy base and Alembic migrations
- foundational domain models
- service layer folders
- adapter layer folders
- audit logging foundation
- health endpoints
- Next.js dashboard skeleton
- admin layout and starter pages
- concise setup documentation

Do not build full routing, full FastField integration, billing, inventory, customer portal, technician mobile app, or AI workflow logic in Phase 0.

---

## Phase 1 — Dispatch Operations Engine

Goal: replace the fragile CleaningWorkflow process with a state-driven dispatch pipeline.

Expected capabilities:

- Google Calendar import adapter
- target date selection
- job normalization
- cancellation detection
- AM/PM and state detection
- Water Emergency detection
- validation pipeline
- confidence scoring
- Manual Review Queue
- job persistence
- audit logs

---

## Phase 2 — Routing And Transitional Outputs

Goal: support dispatch-ready route planning and preserve required transitional outputs.

Expected capabilities:

- route assignment model
- North/South grouping
- route optimization provider adapter
- fallback routing behavior
- route preview
- Google Sheets preview/write adapter
- FastField preview/export adapter
- approval gates before final write/send

---

## Phase 3 — Water Emergency Foundation

Goal: make Water Emergency workflows operationally durable inside ACS FSM.

Expected capabilities:

- Water Emergency lifecycle states
- multi-visit tracking
- technician notes per visit
- equipment notes and future equipment model compatibility
- open Water Emergency dashboard
- next-action visibility
- manual review triggers for unsafe water workflow states

---

## Later Modules

Prepare architecture for, but do not build prematurely:

- CRM
- customer portal
- technician mobile app
- inventory
- billing and invoicing
- payroll support
- Verizon Connect/GPS integration
- equipment lifecycle
- reporting and analytics
- AI operational assistant

---

## Persistent Safety Rules

- Database is the source of truth.
- External systems are adapters.
- Manual Review Queue is a core safety system.
- AI is advisory only.
- Water Emergency is a first-class workflow.
- Business logic does not belong in frontend components.
- Major decisions must be recorded in the vault.
