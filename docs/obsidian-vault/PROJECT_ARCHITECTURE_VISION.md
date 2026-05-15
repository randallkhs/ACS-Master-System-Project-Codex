# ACS FSM — Project Architecture Vision

# Purpose

This document defines the architectural philosophy, engineering standards, and long-term development mindset for the ACS FSM platform.

This is NOT a temporary automation project.

This is the foundation of a long-term operational platform intended to eventually support most company workflow systems.

All engineering decisions must respect:
- scalability
- maintainability
- operational reliability
- extensibility
- professional software architecture

---

# 1. Core Philosophy

The ACS FSM platform must be:

- modular
- deterministic
- extensible
- auditable
- state-driven
- API-first
- operationally safe

The system must avoid:
- fragile automation
- spaghetti architecture
- hidden side effects
- AI over-dependence
- tightly coupled integrations

---

# 2. Engineering Philosophy

The project must prioritize:

1. Reliability over speed
2. Clarity over cleverness
3. Modularity over shortcuts
4. Explicit workflows over hidden logic
5. Human operational safety over automation convenience

---

# 3. Anti-Hack Rules

The system must NEVER rely on:

- temporary hacks
- silent fallback logic
- fragile regex-only parsing
- hidden operational assumptions
- tightly coupled services
- business logic embedded in UI
- duplicated workflow logic

---

# 4. Architecture Direction

## Backend

Primary backend:
- Python
- FastAPI

Architecture style:
- service-oriented modular architecture

NOT:
- giant monolithic files
- route handlers containing business logic

---

## Frontend

Primary frontend:
- Next.js
- TypeScript
- Tailwind

Dashboard architecture must support:
- modular expansion
- role-based visibility
- future portals
- future technician UI

---

## Database

Primary database:
- PostgreSQL

The database is the operational source of truth.

External systems are adapters only.

---

# 5. Integration Philosophy

External services must be treated as:
- replaceable adapters

Examples:
- Google Calendar
- Google Sheets
- FastField
- Verizon Connect

Core system logic must NEVER depend tightly on vendor-specific behavior.

---

# 6. AI Philosophy

AI is an assistant.

AI is NOT:
- operational authority
- workflow authority
- dispatch authority
- cancellation authority

AI may assist:
- classification
- anomaly detection
- confidence scoring
- recommendations

Human operators always remain authoritative.

---

# 7. State-Driven Design

Operational workflows must use:
- explicit statuses
- explicit transitions
- explicit validation rules

The system must NOT depend on:
- interpreting freeform text titles
- hidden meaning inside strings
- implicit workflow assumptions

---

# 8. Logging Philosophy

Important actions must be:
- logged
- traceable
- reviewable

The system must support:
- operational debugging
- historical tracing
- compliance
- analytics

---

# 9. Modularity Rules

Each major domain should eventually become independently maintainable.

Examples:
- dispatch
- routing
- Water Emergency
- CRM
- inventory
- billing
- technician app

Modules should communicate through:
- service layers
- APIs
- structured events

NOT:
- direct cross-file hacks
- duplicated logic

---

# 10. Water Emergency Philosophy

Water Emergency workflows are FIRST-CLASS operational systems.

They are NOT:
- secondary features
- simple jobs
- spreadsheet rows

The architecture must support:
- multi-visit workflows
- equipment lifecycle
- operational history
- technician continuity

---

# 11. UI Philosophy

The UI must prioritize:
- operational clarity
- speed
- visibility
- error prevention

NOT:
- flashy animation
- over-complicated interaction
- hidden operational states

Operators should immediately understand:
- system state
- warnings
- dispatch status
- review requirements

---

# 12. Manual Review Philosophy

Manual review is a CORE SAFETY SYSTEM.

The platform should intentionally:
- stop unsafe automation
- expose uncertainty
- require human confirmation when necessary

The goal is:
- operational correctness
NOT:
- maximum automation

---

# 13. Scalability Philosophy

The system must be designed so future growth does NOT require:
- architectural rewrites
- database replacement
- workflow redesign

Future support should include:
- multiple branches
- additional regions
- more technicians
- larger dispatch volume
- customer portals
- mobile apps
- inventory systems

---

# 14. Future-Proofing Philosophy

The architecture should assume future expansion into:
- billing
- CRM
- payroll
- inventory
- equipment management
- AI assistants
- analytics
- technician mobile apps
- customer self-service systems

---

# 15. Operational Safety Philosophy

Operational safety always overrides:
- convenience
- automation speed
- AI confidence

If uncertainty exists:
- stop
- warn
- require human review

Never risk:
- bad dispatches
- canceled jobs dispatching
- incorrect Water Emergency handling
- corrupted operational state

---

# 16. Documentation Philosophy

Important architectural decisions must be documented.

Codex and future developers must maintain:
- clear reasoning
- decision history
- workflow explanations

The project documentation is part of the system itself.

---

# 17. Development Philosophy

The platform should evolve iteratively.

Each phase should:
- stabilize operations
- improve structure
- reduce operational friction
- prepare future expansion

The goal is long-term operational excellence, not rapid temporary automation.
