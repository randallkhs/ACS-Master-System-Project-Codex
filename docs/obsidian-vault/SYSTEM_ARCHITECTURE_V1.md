# ACS FSM — SYSTEM_ARCHITECTURE_V1.md

## Purpose

This document defines the first official system architecture for the Apple Cleaning Systems FSM platform.

This system is not a script launcher.  
It is a long-term operational platform designed to eventually replace fragmented external tools such as FastField, Google Sheets workflows, manual dispatch processes, and other disconnected systems.

---

# 1. Architecture Philosophy

The ACS FSM must be:

- database-first
- state-driven
- modular
- auditable
- API-first
- integration-adapter based
- safe for daily operations
- ready for future expansion

The system must avoid:

- business logic hidden in frontend components
- fragile free-text parsing as the main workflow
- hardcoded vendor logic inside the core system
- giant centralized files
- temporary hacks
- silent automation failures

---

# 2. Source of Truth

The internal database is the operational source of truth.

External systems are adapters only:

- Google Calendar = input adapter
- Google Sheets = transitional output adapter
- FastField = transitional dispatch adapter
- Verizon Connect = future tracking adapter
- AI models = assistant/validation adapter

No external system should control the internal workflow state.

---

# 3. Recommended Stack

## Backend

- Python
- FastAPI
- SQLAlchemy
- Alembic migrations
- Pydantic schemas
- PostgreSQL

## Frontend

- Next.js
- TypeScript
- TailwindCSS
- Professional dashboard UI

## Future Background Jobs

- Redis
- Celery or equivalent queue system

## Infrastructure

- GoDaddy VPS initially
- future scalable deployment path
- HTTPS required
- environment variables for secrets

---

# 4. High-Level System Flow

```text
External Inputs
    ↓
Adapters
    ↓
Normalization Layer
    ↓
Validation Layer
    ↓
Internal Database
    ↓
Workflow Engine
    ↓
Manual Review / Approval
    ↓
Routing Engine
    ↓
Dispatch Outputs
    ↓
Audit Logs

---

5. First Module: Dispatch Operations Engine

The first module focuses on replacing the current CleaningWorkflow system.

It includes:

* Google Calendar import
* job normalization
* cancellation detection
* AM/PM detection
* state detection
* water emergency detection
* manual review queue
* routing preparation
* Google Sheets compatibility
* FastField transitional export
* admin dashboard
* audit logging

It does NOT include yet:

* billing
* inventory
* full CRM
* full customer portal
* technician mobile app
* payroll
* full Verizon Connect integration

---

6. Core Domains

6.1 Customers

Represents people, businesses, property managers, apartment complexes, or organizations requesting service.

Future role:

* CRM
* customer portal
* billing
* service history

---

6.2 Properties

Represents physical service locations.

Important distinction:

* customer/account address
* apartment complex/property address
* exact physical unit/location address

Properties must support:

* unit numbers
* building numbers
* access notes
* gate codes
* parking notes
* service history

---

6.3 Jobs

Represents the work requested.

A job is not always equal to a visit.

Examples:

* standard carpet cleaning = usually one job and one visit
* water emergency = one job with multiple visits

---

6.4 Work Orders

Represents operational instructions sent to technicians.

A work order belongs to a job and contains:

* service instructions
* technician assignment
* required forms
* job notes
* dispatch status

---

6.5 Visits

Represents a technician visit to a property.

Water Emergency jobs may have many visits:

* extraction
* moisture check
* treatment
* pickup

Visits must support:

* notes
* technician assignment
* photos in future
* equipment actions in future
* status tracking

---

6.6 Technicians

Represents field workers.

Must support:

* regular employees
* temporary employees
* part-time temporary employees
* skills/specialties
* FastField user mapping
* future GPS/Verizon mapping
* active/inactive status

---

6.7 Route Assignments

Represents routing decisions.

Must support:

* route date
* technician
* route order
* region
* AM/PM designation
* route status
* future estimated arrival times

---

6.8 Water Emergency

Water Emergency is a first-class workflow.

It is NOT merely a job type.

Must support:

* open/closed lifecycle
* wet/dry stages
* multiple visits
* equipment left onsite
* daily notes
* photos in future
* future IICRC S500 documentation

---

6.9 Manual Review Items

Represents anything requiring human attention.

Examples:

* possible cancellation
* invalid address
* low confidence classification
* duplicate job
* missing required information
* conflicting AM/PM/state tags

Manual review is a core safety system.

---

6.10 Audit Logs

Every important system action must be logged.

Examples:

* import
* normalization
* validation
* manual override
* dispatch export
* route generation
* FastField send
* status change

---

7. Backend Module Structure

Recommended backend structure:

backend/
  app/
    main.py
    core/
      config.py
      lifecycle.py
      logging.py
      middleware.py
      security.py
    db/
      session.py
      base.py
      migrations/
    models/
      customer.py
      property.py
      job.py
      work_order.py
      visit.py
      technician.py
      route_assignment.py
      review_item.py
      audit_log.py
      water_emergency.py
    schemas/
      customer.py
      property.py
      job.py
      work_order.py
      visit.py
      technician.py
      routing.py
      review.py
    services/
      normalization/
      validation/
      classification/
      routing/
      dispatch/
      review/
      water_emergency/
    adapters/
      google_calendar/
      google_sheets/
      fastfield/
      verizon_connect/
      ai/
    api/
      v1/
        routes/
          jobs.py
          dispatch.py
          review.py
          technicians.py
          routes.py
          water_emergency.py
    tests/

8. Frontend Module Structure

Recommended frontend structure:

frontend/
  app/
    dashboard/
    dispatch/
    review/
    routing/
    water-emergency/
    technicians/
    settings/
  components/
    layout/
    tables/
    forms/
    status/
    review/
    routing/
  lib/
    api.ts
    types.ts
    utils.ts
  styles/

The frontend must not contain business logic.

The frontend consumes backend APIs and displays:

* state
* warnings
* review items
* route results
* dispatch status

---

9. Adapter Philosophy

External integrations must live in adapters.

Examples:

adapters/google_calendar
adapters/google_sheets
adapters/fastfield
adapters/verizon_connect
adapters/ai

Adapters should translate between:

external vendor data
↔
internal ACS data models

The core system should not depend directly on vendor-specific structures.

---

10. Workflow Engine Philosophy

Workflow state must be explicit.

Examples:

Water Emergency may have additional states:

OPEN
MONITORING
DRYING_IN_PROGRESS
READY_FOR_PICKUP
CLOSED

No workflow should depend only on free-text calendar titles.

---

11. AI Usage Philosophy

AI may help with:

* classification suggestions
* anomaly detection
* unclear text interpretation
* summarization
* confidence scoring support

AI must never:

* silently dispatch jobs
* override human operators
* auto-confirm dangerous state transitions
* replace deterministic validation rules

---

12. Manual Review Philosophy

Manual review is required when:

* cancellation is uncertain
* address is invalid
* job type is unclear
* Water Emergency state is unclear
* AM/PM markers conflict
* technician assignment is invalid
* FastField export may be unsafe

Manual review must show:

* issue detected
* reason
* confidence score
* recommended action
* operator decision

---

13. Security Philosophy

The system must eventually support:

* role-based access control
* admin users
* office users
* technicians
* future customers
* audit logs
* secure secrets handling

No passwords or API keys may be hardcoded.

Secrets must live in environment variables or secure secret storage.

---

14. Deployment Philosophy

Initial deployment may use the existing VPS.

The deployment must support:

* environment configuration
* database migrations
* logging
* HTTPS
* backup strategy
* rollback strategy

Future deployment may use:

* Docker

Phase 0 backend hardening prepares for VPS deployment through environment-based settings, structured logs, request IDs, health readiness state, and migration/developer commands. It does not implement production deployment infrastructure yet.
* managed database
* cloud object storage
* background workers

---

15. Documentation Philosophy

Codex and future developers must keep documentation updated.

Important docs:

* AGENTS.md
* 00-Project-Index.md
* 01-Business-Rules.md
* 02-Water-Emergency-Workflow.md
* 03-Dispatch-Pipeline.md
* 09-First-Module-Build-Scope.md
* SYSTEM_ARCHITECTURE_V1.md
* 13-Decisions/07-Codex-Decisions-Log.md

Major architecture decisions must be logged.

---

16. Build Strategy

Phase 0 — Foundation

Create:

* repo structure
* FastAPI backend skeleton
* PostgreSQL connection
* Alembic migrations
* base models
* service folders
* adapter folders
* Next.js dashboard skeleton
* basic health endpoints
* audit log foundation

No full business workflow yet.

---

Phase 1 — Core Dispatch Engine

Build:

* Google Calendar import adapter
* normalization pipeline
* validation pipeline
* classification pipeline
* manual review queue
* job database persistence

---

Phase 2 — Routing and Output

Build:

* route assignment model
* routing engine
* Google Sheets output adapter
* FastField preview/export adapter

---

Phase 3 — Water Emergency Foundation

Build:

* water emergency lifecycle
* visit tracking
* equipment notes
* water-specific statuses
* water-specific dispatch support

---

17. Final Directive

Build this system as a professional operational platform.

Every design decision should support:

* long-term maintainability
* operational safety
* future expansion
* clean architecture
* clear business rules
* human review where uncertainty exists
```
