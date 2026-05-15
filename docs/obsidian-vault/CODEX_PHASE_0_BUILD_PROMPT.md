# ACS FSM — CODEX_PHASE_0_BUILD_PROMPT.md

## Objective

Build the foundational architecture for the ACS FSM platform.

This phase does NOT build the complete business workflow yet.

The goal is to create a professional, scalable, maintainable system foundation that future phases can safely build on.

This project is intended to become the long-term operational platform for Apple Cleaning Systems.

---

# Required Pre-Read

Before generating code:

1. Read:
   - AGENTS.md
   - SYSTEM_ARCHITECTURE_V1.md
   - 00-Project-Index.md
   - 01-Business-Rules.md
   - 02-Water-Emergency-Workflow.md
   - 03-Dispatch-Pipeline.md
   - 09-First-Module-Build-Scope.md

2. Inspect the Obsidian vault structure.

3. Follow all architecture rules defined in the vault.

---

# Phase 0 Goals

Build ONLY the foundational system.

Do NOT build:
- full dispatch workflows
- full routing engine
- full FastField integration
- billing
- inventory
- customer portal
- technician mobile app
- AI workflow logic

This phase is infrastructure and architecture only.

---

# Required Stack

## Backend

- Python
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Pydantic Settings

## Frontend

- Next.js
- TypeScript
- TailwindCSS

---

# Required Repository Structure

Create a professional monorepo structure:

```text
acs-fsm/
  backend/
  frontend/
  infrastructure/
  docs/
  scripts/
  tests/

Backend Requirements

Create:

backend/app/

with:

core/
db/
models/
schemas/
services/
adapters/
api/
tests/

Database Foundation

Configure:

* PostgreSQL connection
* SQLAlchemy setup
* Alembic migrations
* base declarative model
* session management

Create initial foundational models only:

* Customer
* Property
* Job
* WorkOrder
* Visit
* Technician
* RouteAssignment
* WaterEmergency
* ReviewItem
* AuditLog

Models may initially be minimal.

Focus on:

* clean relationships
* timestamps
* UUIDs
* future expandability

---

API Foundation

Create:

/api/v1/

with starter routes:

* health
* jobs
* technicians
* review
* dispatch

Routes may initially return placeholders.

Goal:

* architecture
* typing
* structure

---

Service Layer Foundation

Create service folders:

services/
  normalization/
  validation/
  classification/
  routing/
  dispatch/
  review/
  water_emergency/

No heavy logic yet.

Only architectural scaffolding.

---

Adapter Layer Foundation

Create adapters:

adapters/
  google_calendar/
  google_sheets/
  fastfield/
  verizon_connect/
  ai/

No full implementations yet.

Only:

* clean structure
* interfaces
* placeholders
* typed clients

---

Frontend Foundation

Create:

frontend/

using:

* Next.js
* App Router
* TypeScript
* Tailwind

Create starter pages:

* Dashboard
* Dispatch
* Review Queue
* Routing
* Water Emergency
* Technicians
* Settings

Pages may initially contain placeholder content.

Focus on:

* layout
* architecture
* scalability
* reusable components

---

Dashboard Requirements

The dashboard should look professional.

Requirements:

* dark/light professional UI
* modular cards
* sidebar navigation
* scalable admin layout
* responsive design
* no giant component files

Avoid:

* overengineering
* unnecessary animations
* hardcoded business logic

---

Security Foundation

Implement:

* environment-based config
* secrets handling structure
* future RBAC-ready structure
* CORS setup
* logging foundation

Do NOT hardcode:

* passwords
* API keys
* secrets

---

Audit Logging Foundation

Create:

* audit log model
* audit service placeholder
* logging utilities

Future workflows must be able to write:

* user actions
* dispatch events
* workflow transitions
* review actions

---

Documentation Requirements

Create/update:

* README.md
* architecture overview
* backend setup instructions
* frontend setup instructions
* environment variable examples

Do NOT create excessive documentation noise.

Keep documentation concise and professional.

---

Code Quality Rules

Required:

* modular architecture
* strong typing
* clean separation of concerns
* no business logic in frontend
* no giant centralized files
* future-safe structure
* scalable organization

Avoid:

* premature optimization
* temporary hacks
* deeply coupled modules
* hidden side effects

---

Important Operational Philosophy

This system is intended for real operational dispatch workflows.

Architecture must prioritize:

* safety
* maintainability
* auditability
* human review
* operational reliability

AI is an assistant layer.
Not the operational source of truth.

---

Final Deliverable

At the end of Phase 0 the system should provide:

* runnable backend
* runnable frontend
* database migrations
* clean architecture
* foundational domain models
* scalable repo structure
* starter dashboard
* health endpoints
* adapter scaffolding
* service scaffolding

But NOT full operational workflows yet.

---

Final Instruction

Build this as if it were the foundation of a long-term professional FSM platform, not a temporary automation script.
```
