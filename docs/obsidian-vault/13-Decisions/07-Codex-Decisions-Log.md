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
