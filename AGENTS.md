# AGENTS.md — ACS FSM Platform

# Project Identity

This project is a long-term professional FSM (Field Service Management) platform for Apple Cleaning Systems.

This is NOT:
- a temporary script
- a prototype
- a hacky automation project

This platform is intended to evolve into a complete operational ecosystem supporting:
- dispatch
- Water Emergency workflows
- technician management
- routing
- CRM
- inventory
- billing
- customer portals
- technician apps
- analytics
- operational AI assistance

All engineering decisions must reflect long-term maintainability and scalability.

---

# Core Engineering Philosophy

The project must prioritize:

1. Reliability
2. Deterministic workflows
3. Human operational safety
4. Clear architecture
5. Extensibility
6. Auditability
7. Modular design

The project must NOT prioritize:
- rapid hacks
- fragile automation
- hidden logic
- tightly coupled integrations
- AI over-control

---

# IMPORTANT ARCHITECTURAL RULES

## Rule 1
The database is the operational source of truth.

External systems are integrations only.

Examples:
- Google Calendar
- Google Sheets
- FastField
- Verizon Connect

---

## Rule 2
Business logic must NEVER live inside frontend components.

Frontend should consume:
- APIs
- services
- structured backend responses

---

## Rule 3
Avoid giant files.

Split logic into:
- services
- adapters
- domain modules
- repositories
- validators
- workflow engines

---

## Rule 4
Water Emergency workflows are FIRST-CLASS workflows.

They are NOT:
- standard jobs
- spreadsheet rows
- secondary features

The architecture must support:
- multi-visit workflows
- equipment lifecycle
- operational continuity
- technician history

---

## Rule 5
Manual Review Queue is a CORE SAFETY SYSTEM.

Unsafe automation is worse than slower automation.

If uncertainty exists:
- stop automation
- trigger manual review

---

## Rule 6
AI is an assistant ONLY.

AI may:
- classify
- validate
- score confidence
- detect anomalies

AI must NEVER:
- override operators
- auto-confirm dangerous actions
- auto-dispatch uncertain jobs

---

# Development Standards

## Backend

Preferred stack:
- Python
- FastAPI
- PostgreSQL

Preferred architecture:
- modular service architecture

Avoid:
- giant route handlers
- mixed business logic
- duplicated logic
- hidden side effects

---

## Frontend

Preferred stack:
- Next.js
- TypeScript
- Tailwind

UI philosophy:
- operational clarity
- speed
- safety
- visibility

Avoid:
- overly complex animations
- hidden workflow states
- confusing UI interactions

---

# Operational Workflow Philosophy

The platform must be:
- state-driven
NOT:
- title-string-driven

Avoid:
- hidden operational meaning inside strings
- regex-only business logic
- freeform operational dependence

Prefer:
- explicit statuses
- structured entities
- workflow engines
- validation pipelines

---

# Logging Philosophy

Important operations must be logged.

Examples:
- imports
- dispatches
- cancellations
- technician assignments
- exports
- overrides
- validation failures

Logs should support:
- debugging
- operational tracing
- analytics
- audits

---

# Integration Philosophy

All external integrations should use adapter architecture.

Examples:
- Google APIs
- FastField APIs
- Verizon Connect APIs

The core platform should remain independent from vendors.

---

# Modularity Philosophy

Each future module should be independently extensible.

Examples:
- dispatch
- CRM
- inventory
- technician apps
- billing
- analytics

Avoid architecture decisions that tightly couple unrelated systems.

---

# Documentation Requirements

When making important architectural decisions:
- update documentation
- explain reasoning
- preserve operational clarity

Important files:
- PROJECT_ARCHITECTURE_VISION.md
- 01-Business-Rules.md
- 02-Water-Emergency-Workflow.md
- 03-Dispatch-Pipeline.md
- 07-Codex-Decisions-Log.md

---

# Decision Logging

Important decisions should be added to:
- 07-Codex-Decisions-Log.md

Include:
- what changed
- why
- future implications
- affected systems

---

# Coding Philosophy

Prefer:
- explicit code
- readable code
- maintainable code
- testable code

Avoid:
- magic behavior
- hidden mutations
- implicit side effects
- unnecessary abstractions

---

# Future Expansion Awareness

The architecture must assume future support for:
- customer portals
- technician mobile apps
- inventory
- billing
- CRM
- GPS tracking
- equipment lifecycle
- AI operational assistants

Current decisions must NOT block future growth.

---

# Operational Safety Philosophy

Operational safety overrides:
- convenience
- automation speed
- AI confidence

Never risk:
- dispatching canceled jobs
- incorrect Water Emergency handling
- data corruption
- unsafe automation

When uncertain:
- warn
- stop
- request human review

---

# Research Memory Rule

When researching current technical information from the internet, Context7, API documentation, SDK documentation, or official technical sources, preserve reusable knowledge in the Obsidian vault.

Before researching, check relevant vault notes first.

If stored knowledge exists and is still inside its recheck window, use it.

If stored knowledge is expired, incomplete, or contradicted by current docs, refresh the research and update the note.

Save reusable knowledge in:

- 15-Research/NEW_AI_KNOWLEDGE.md
- 15-Research/RESEARCH_MEMORY_RULES.md
- 16-API-Docs/ when API-specific
- 04-Integrations/ when integration-specific
- 13-Decisions/07-Codex-Decisions-Log.md when it affects architecture

Each saved entry must include:

- Date learned
- Topic
- Category
- Recheck after date
- Source links
- Summary
- Applicable projects
- Confidence level

Do not save one-time debugging noise or obvious general programming knowledge.

---

# Final Directive

This project should be engineered like a professional long-term operational platform, not a temporary automation utility.

Every decision should support:
- future growth
- operational reliability
- maintainability
- extensibility
- architectural clarity
