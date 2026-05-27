# ACS-FSM Master System Overview

Date: 2026-05-27
Status: Phase 0 documentation/readiness baseline
Authority: Randall-authorized Phase 0 baseline for technical architecture and workflow documentation

## Purpose

ACS-FSM is the long-term Apple Cleaning Systems field service management platform. It is intended to replace fragile spreadsheet/script-centered workflows with a database-first operational system for dispatch, Manual Review, Water Emergency workflows, technician coordination, future customer/technician portals, integrations, analytics, and advisory AI.

This document is a master overview. It describes the intended complete system and the current Phase 0 state. It does not implement production behavior.

## Business Problem

ACS operations depend on multiple external and semi-manual surfaces: Google Calendar, Google Sheets, FastField, office review, technician communication, Water Emergency tracking, and future routing/GPS inputs. These surfaces are useful, but they should not own workflow truth. The platform needs a durable source of truth, predictable workflow state, traceable review decisions, and safe boundaries before automation can execute real actions.

## Complete Future System Vision

The future ACS Master System should support:

- Dispatch operations for standard jobs.
- First-class Water Emergency case/workflow management.
- Technician assignment, scheduling, routing, and field visibility.
- CRM/customer/property/job history.
- Inventory and equipment lifecycle tracking.
- Billing and management reporting foundations.
- Google Calendar and Google Sheets adapter compatibility during transition.
- FastField adapter compatibility during transition.
- Email/notification workflows after review and approval.
- Possible routing/maps/GPS integration.
- Advisory AI for classification, anomaly detection, summarization, and risk explanation.
- Role-scoped operator dashboards after real auth/RBAC exists.

The system should remain modular. External systems are adapters; PostgreSQL is the operational source of truth.

## Current Phase 0 Architecture

Phase 0 has built read-only foundations, local verification workflows, and safety/readiness metadata. It has not built production deployment, real auth, RBAC enforcement, route protection, user login, action execution, vendor calls, or AI authority.

Core current layers:

- FastAPI backend with modular routes, schemas, services, repositories, adapters, and settings.
- PostgreSQL/Alembic data model foundation.
- Deterministic intake, validation, confidence, Manual Review, dispatch preparation, operational event, governance, accountability, and dashboard read models.
- Next.js/Tailwind dashboard consuming backend read models through GET-only API calls.
- Local PostgreSQL verification and synthetic seed data for read-only dashboard testing.
- Disabled auth/RBAC scaffolding and readiness visibility through Module 60.
- Public ACSSDR stakeholder report source updated only after previous modules are reviewed, committed, and pushed.

## Backend Architecture

Backend stack:

- Python
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Pydantic Settings

Backend boundaries:

- API routes remain thin.
- Domain structures and service modules own workflow rules.
- Repositories are data-access boundaries only.
- External systems sit behind adapters.
- Read models expose dashboard and readiness visibility.
- Mutation/action routes are not implemented in Phase 0.

## Frontend Architecture

Frontend stack:

- Next.js App Router
- TypeScript
- Tailwind CSS
- Vitest render/API contract checks

Frontend boundaries:

- Frontend displays backend read models and local view-state controls only.
- API client remains GET-only for dashboard/auth status surfaces.
- No Authorization header is emitted in Phase 0.
- No login/logout/user-management/role-assignment UI exists.
- No approve/reject/defer/archive/dispatch/close action controls exist.
- Fallback/mock state is labeled and must not be treated as live operational truth.

## Database Source Of Truth Principle

PostgreSQL is the operational source of truth. Google Calendar, Google Sheets, FastField, email, GPS/routing tools, and AI providers are adapters or advisory sources only.

Production future requirements include:

- database provisioning plan
- backup/restore plan
- migration rollout plan
- audit actor linkage
- immutable event writes for real actions
- rollback/replay strategy for controlled recovery

## Manual Review Safety System

Manual Review is the safety system. It exists to stop unsafe automation when data is incomplete, ambiguous, conflicting, duplicated, low-confidence, or Water Emergency-sensitive.

Current Phase 0 provides extensive read-only Manual Review visibility and readiness metadata. It does not execute review actions.

Future action modules must not begin until real auth/RBAC, operator identity, role authorization, audit reason capture, idempotency, immutable events, post-action checks, and review approval workflow are ready.

## Water Emergency Separated Workflow

Water Emergency is first-class workflow data, not a standard dispatch row. Water Emergency work may span multiple visits, equipment lifecycle, drying checks, and legal/insurance-sensitive decisions.

Current Phase 0 provides separated read-only Water Emergency dashboard/detail visibility. It does not close, resolve, dispatch, certify, promise, bill, or finalize Water Emergency policy.

Future Water Emergency action authority may require Alfonso owner review where legal, insurance, warranty, billing, customer-liability, or company-policy consequences exist.

## Dispatch Operations Engine

The Phase 0 dispatch engine is currently preparation and evidence only:

- intake normalization and validation
- Manual Review gating
- operational intake persistence
- job/work-order/visit preparation
- assignment/scheduling/routing readiness
- route assignment authorization boundary
- internal dispatch/external adapter evidence
- confirmation, recovery, reconciliation, replay, governance, accountability evidence

Future production dispatch execution must preserve Manual Review, audit, idempotency, adapter, and database source-of-truth boundaries.

## Auth/RBAC Readiness And Future Implementation

Modules 51-60 completed a disabled Phase 0 auth/RBAC readiness arc:

- operator identity registry planning
- role and permission catalog planning
- provider configuration placeholders
- secret hygiene diagnostics
- claims mapping and dry-run metadata
- route protection matrix and access-decision dry-run
- readiness audit and enforcement-boundary lock
- disabled backend auth core and token verifier
- disabled frontend session and API auth boundary
- backend/frontend auth status bridge
- Phase 0 auth boundary completion audit and future cutover checklist

Current facts:

- auth is not implemented
- auth is disabled
- token verification is disabled
- JWT parsing is disabled
- JWKS fetch is disabled
- RBAC is not enforced
- route guarding is disabled
- current routes require no Authorization header
- Authorization header presence cannot grant authority
- frontend emits no Authorization header
- Manual Review and Water Emergency action authority are not granted
- future auth cutover is not ready

## Audit And Immutable Event Strategy

Auditability is a core design goal. Current Phase 0 has operational event history, audit evidence, dry-run audit-envelope metadata, idempotency planning, and future immutable-event requirements.

Future action modules must write durable actor-linked events before any real workflow mutation is trusted.

## Future Integrations

Google Calendar:

- schedule input adapter
- not source of truth after import

Google Sheets:

- transitional dispatch/report output adapter
- preview before write
- not authoritative workflow state

FastField:

- transitional work-order/dispatch adapter
- Water Emergency must remain separated from standard forms/paths

Email/notifications:

- future operator/customer/technician communication layer
- must not send binding promises or policy decisions without approved workflow rules

Routing/maps/GPS:

- future route optimization and vehicle/technician visibility
- must consume internal state and write evidence back without becoming workflow authority

## AI Advisory-Only Principle

AI may classify, explain, summarize, score, and detect anomalies. AI must not dispatch, approve, reject, close, override operators, bypass Manual Review, mutate workflow state, or become the source of truth.

## ACSSDR Stakeholder Reporting

ACSSDR is the public owner/stakeholder progress report for Luis and Alfonso. It should be updated before each new module only for the previous module after Randall has reviewed, approved, committed, and pushed it.

Module 62 updates the ACSSDR source to mark Module 61 complete after Randall committed and pushed it. Module 62 itself is not complete until reviewed and committed later.

## Codex, ChatGPT, And Review GUI Workflow

Current workflow:

1. Codex implements the module.
2. Codex writes external review files outside the repo.
3. ChatGPT reviews the module.
4. Review GUI / Randall approval happens.
5. Randall commits and pushes manually.
6. ACSSDR is updated for that previous module before the next module starts.

Codex must not commit or push unless explicitly instructed.

## Current Phase 0 Status

Phase 0 has strong read-only foundations but is not production deployment and has no executable operational actions.

Current strengths:

- architecture and business-rule documentation
- backend foundation and domain model
- local database/migration/seed verification
- read-only operational dashboard
- Water Emergency separated visibility
- Manual Review readiness and future action planning
- disabled auth/RBAC scaffolding and cutover checklist
- public stakeholder reporting workflow

Current blockers:

- production infrastructure and deployment plan
- production database, backup, restore, and migration runbook
- real auth provider, credentials, secret management, token verification, and RBAC
- Manual Review action execution design and approval
- Water Emergency action policy and owner review
- real integration execution with Calendar, Sheets, FastField, email, routing/maps
- audit actor/idempotency/immutable-event execution layer

## Future Phase Roadmap

See [[00-Phase-Roadmap]] for detailed phase goals, prerequisites, risks, and transition criteria.
