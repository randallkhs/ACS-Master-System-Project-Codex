# Apple Cleaning Systems
# NEW_SYSTEM_REQUIREMENTS.md

Version: 1.0
Status: Planning / Architecture Phase
Prepared By: Randall Rodríguez + AI-assisted development workflow
Primary AI Development Stack: Codex + MCP + AGENT.md system

---

# 1. PROJECT OVERVIEW

This project is the beginning of a long-term custom FSM (Field Service Management) platform for Apple Cleaning Systems.

The first module replaces the current temporary CleaningWorkflow system and focuses on:

- Dispatch operations
- Calendar job processing
- Route preparation
- Google Sheets generation
- FastField workflow preparation
- Water emergency workflow handling
- Manual review and validation
- Internal office workflow optimization

This new system MUST be designed as a modular foundation for the future complete FSM platform.

The system is NOT a temporary script launcher.
It is the first production-grade module of a larger enterprise workflow system.

---

# 2. PRIMARY GOALS

The new system must:

- Reduce human error
- Reduce dependency on manually written emails
- Eliminate unreliable AI-only parsing workflows
- Increase dispatch reliability
- Improve operational visibility
- Prepare the architecture for future FSM expansion
- Replace manual office workflows progressively
- Support long-term scalability

---

# 3. CURRENT SYSTEM PROBLEMS

The old system has the following major issues:

## 3.1 Unreliable AI interpretation

The old workflow depended heavily on Gemini interpreting human-written emails and calendar titles.

Problems:
- spelling mistakes
- inconsistent formatting
- unpredictable wording
- missing information
- false positives
- false negatives

This caused:
- canceled jobs accidentally dispatched
- jobs not sent to technicians
- invalid routing
- incorrect sheet entries

The new system MUST minimize dependence on AI interpretation for mission-critical logic.

AI may assist workflows but MUST NOT be the primary decision engine for critical dispatch logic.

---

# 4. FIRST MODULE SCOPE

This first module is:

# Dispatch Operations Engine

The module will process next-day operational scheduling.

---

# 5. CORE WORKFLOW

## 5.1 Next-Day Processing

The system processes jobs scheduled for the NEXT DAY.

Example:
- Current date: 2026-05-14
- System processes jobs for: 2026-05-15

The system DOES NOT process the current day by default.

---

# 6. JOB SOURCES

Initial source:
- Google Calendar

Future sources:
- Customer portal
- Internal office dashboard
- API integrations
- Technician-created follow-ups
- Water emergency continuation workflows

---

# 7. JOB TYPES

The system must support:

## 7.1 Standard Jobs

Examples:
- carpet cleaning
- upholstery
- air duct cleaning
- deep cleaning

Characteristics:
- usually opened and closed same day
- sent using standard FastField workflow
- routed normally

---

## 7.2 Water Emergency Jobs

Examples:
- pipe burst
- flooding
- water mitigation
- extraction
- drying
- restoration

Characteristics:
- multi-day lifecycle
- multiple technician visits
- open workflow
- drying process tracking
- equipment tracking
- daily updates
- delayed closure

These jobs MUST be treated differently from standard jobs.

---

# 8. WATER EMERGENCY REQUIREMENTS

Water emergency jobs:

- remain open across multiple days
- require technician notes each visit
- require future restoration compatibility
- require equipment tracking compatibility
- require future moisture-log compatibility

The architecture MUST support future:
- IICRC S500 workflows
- psychrometric tracking
- drying reports
- insurance documentation

Even if not implemented yet.

---

# 9. CANCELLATION DETECTION

The current company workflow uses human-written cancellation markers inside calendar titles.

Examples:
- CANCELED
- Cancelled
- canceled
- CANCELLD
- CANSELED
- Canneled

The old system failed to reliably detect misspellings.

The new system MUST include:

- fuzzy cancellation detection
- confidence scoring
- validation rules
- manual review escalation
- safe fail behavior

If uncertainty exists:
- DO NOT dispatch automatically
- send to manual review queue

Safety is more important than automation.

---

# 10. AM / PM JOB DETECTION

Certain jobs contain scheduling markers inside calendar titles.

Examples:
- AM/DE
- DE/AM
- PM/DE
- DE/PM

States include:
- DE
- MD
- PA
- NJ

These markers indicate:
- preferred scheduling window
- geographic region

The system must:
- parse these reliably
- separate them visually
- prioritize routing accordingly

---

# 11. ROUTING REQUIREMENTS

The system currently:

- uses depot as origin
- optimizes all next-day jobs
- separates jobs north/south of depot
- reorganizes jobs into dispatch-friendly structure

New system requirements:

- maintain routing optimization
- improve routing visibility
- support future live re-optimization
- support future emergency insertion
- support future technician reassignment

Google Route Optimization API may continue initially.

Architecture must remain provider-agnostic when possible.

---

# 12. GOOGLE SHEETS OUTPUT

Initial versions may still generate Google Sheets outputs.

Sheets currently include:
- AppleJobs
- Water Emergency sheets
- routing sections
- AM/PM separated jobs

The new system should:
- continue compatibility temporarily
- progressively reduce dependence on Sheets
- eventually replace Sheets entirely with internal database-driven UI

---

# 13. FASTFIELD COMPATIBILITY

The company currently still uses FastField.

The new system must:
- support FastField workflows initially
- support standard jobs
- support water emergency jobs
- support different forms/workflows per job type

Future goal:
- replace FastField completely

The architecture MUST prepare for internal work-order replacement.

---

# 14. MANUAL REVIEW SYSTEM

Critical requirement.

The system MUST include:
- review queue
- warnings
- confidence indicators
- unresolved parsing flags
- dispatch hold states
- audit visibility

If the system is uncertain:
- human review is required

No uncertain job should auto-dispatch.

---

# 15. CUSTOMER PORTAL (FUTURE)

Future customer dashboard goals:

- submit service requests
- structured forms
- eliminate freeform email dependency
- upload photos
- service-specific workflows
- appointment requests
- customer history

This future system is a major reason why the backend architecture must be modular.

---

# 16. OFFICE STAFF DASHBOARD

Future office workflows should reduce manual typing.

Preferred workflow:
- dropdowns
- structured selections
- guided forms
- validation
- templates
- operational workflows

Goal:
reduce human formatting errors.

---

# 17. SYSTEM ARCHITECTURE

Recommended stack:

## Backend
- FastAPI (Python)

## Frontend
- Next.js
- React
- TailwindCSS

## Database
- PostgreSQL

## Queue / async
- Redis (future)

## Hosting
- GoDaddy VPS initially

---

# 18. FRONTEND STRUCTURE

## Public Website
applecleaningsystems.net

Purpose:
- marketing
- SEO
- customer acquisition
- customer entry point

---

## Internal Operations Dashboard
app.applecleaningsystems.net

Purpose:
- dispatch
- scheduling
- review
- operations
- routing
- workflow management

---

## Future Customer Portal
portal.applecleaningsystems.net

Purpose:
- customer requests
- history
- invoices
- uploads
- approvals

---

## Future Technician App
tech.applecleaningsystems.net

Purpose:
- field workflows
- photos
- signatures
- notes
- work completion

---

# 19. DESIGN REQUIREMENTS

The system must:
- look modern
- look enterprise-grade
- be highly visual
- be mobile-friendly
- support dark mode
- support scalable dashboards
- support operational speed

The Admindek template may be used as:
- inspiration
- component source
- UI acceleration framework

Not necessarily as final architecture.

---

# 20. DEVELOPMENT PRINCIPLES

The system must prioritize:

1. Reliability
2. Validation
3. Safety
4. Auditability
5. Scalability
6. Human override capability
7. Clear operational visibility

Automation must NEVER be prioritized over operational safety.

---

# 21. AI USAGE RULES

AI may:
- assist classification
- assist suggestions
- assist summaries
- assist fuzzy matching
- assist descriptions

AI must NOT:
- silently make critical dispatch decisions
- auto-send uncertain jobs
- bypass validation rules
- bypass review queues

Human review always overrides AI.

---

# 22. LONG-TERM GOAL

This module is the foundation of a complete custom FSM platform replacing:

- FastField
- Google Sheets
- Google Calendar workflows
- manual dispatch
- fragmented office workflows

The final platform will unify:
- scheduling
- dispatch
- CRM
- water restoration
- inventory
- technician workflows
- invoicing
- reporting
- customer communication

into one centralized system.