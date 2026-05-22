# ACS FSM — Business Rules

# Purpose

This document defines the official operational rules of the Apple Cleaning Systems FSM platform.

These rules override assumptions, AI interpretation, or inferred logic.

All workflows must follow these rules strictly.

---

# 1. Operational Philosophy

The system must prioritize:

1. Operational reliability
2. Human verification
3. Deterministic workflows
4. Structured data
5. Auditability
6. Extensibility

The system must NOT depend heavily on AI interpretation of unpredictable human-written text.

---

# 2. Source of Truth Rules

## Official Source of Truth

The internal PostgreSQL database is the primary operational source of truth.

External systems are integrations only.

Examples:
- Google Calendar
- Google Sheets
- FastField
- Email
- Verizon Connect

These systems may provide input/output data, but they are NOT authoritative.

---

# 3. Job Categories

## 3.1 Standard Jobs

Examples:
- carpet cleaning
- upholstery
- air duct cleaning
- deep cleaning
- dryer vents
- LVT cleaning

Characteristics:
- usually single-day
- usually single-visit
- normally closed same day
- assigned to technicians for completion

---

## 3.2 Water Emergency Jobs

Water Emergency jobs are NOT treated as normal jobs.

They are long-lived operational workflows.

Characteristics:
- multi-visit
- multi-day
- may involve multiple technicians
- equipment lifecycle tracking required
- drying progress required
- moisture checks required
- completion state controlled separately
- may remain open for multiple days

Water Emergency workflows are first-class operational entities.

---

# 4. Calendar Import Rules

## Import Window

The system normally processes:
- NEXT DAY schedule
not:
- current day schedule

Example:
- today = 2026-05-14
- system processes = 2026-05-15

---

## Calendar Events

Calendar events are considered:
- operational input
NOT:
- operational truth

Imported calendar data must be normalized before use.

---

# 5. Cancellation Rules

## Cancellation Detection

Cancellation detection must NEVER rely only on exact spelling.

Examples of valid cancellation indicators:
- CANCELED
- CANCELLED
- canceled
- cancelled
- canseled
- cancelld
- canneled

The system must use:
- fuzzy matching
- confidence scoring
- manual review triggers

---

## Cancellation Confidence

If confidence is low:
- DO NOT auto-dispatch
- send to manual review queue

Operational safety is more important than automation speed.

---

# 6. AM/PM Time Window Rules

Jobs may contain operational time windows.

Examples:
- AM/DE
- DE/AM
- PM/NJ
- NJ/PM

States currently used:
- DE = Delaware
- MD = Maryland
- PA = Pennsylvania
- NJ = New Jersey

Rules:
- AM jobs require morning scheduling priority
- PM jobs require afternoon scheduling priority
- time windows affect routing decisions
- time windows affect technician assignment

---

# 7. Routing Rules

## Routing Objective

Routing exists to:
- reduce drive time
- optimize technician allocation
- improve operational efficiency

---

## Geographic Grouping

Current routing strategy:
- North group
- South group

based on:
- depot location

This routing system may evolve in future versions.

---

## Routing Constraints

Routing must eventually support:
- AM/PM windows
- technician skills
- water emergency priority
- technician availability
- equipment requirements
- geographic efficiency

---

# 8. Technician Rules

Technicians may have:
- skill specializations
- certifications
- equipment limitations
- geographic preferences
- availability states

Future versions will support:
- live GPS
- dynamic reassignment
- mobile technician workflows

---

# 9. Manual Review Queue

The manual review queue is a core operational safety system.

The queue exists to prevent:
- bad dispatches
- incorrect cancellations
- incomplete jobs
- malformed addresses
- AI uncertainty failures

---

## Manual Review Triggers

Examples:
- low confidence parsing
- unclear cancellation
- invalid address
- missing customer info
- conflicting state markers
- malformed dates
- duplicate jobs
- uncertain AI classification

## Phase 0 Module 40 Manual Review Visibility

The Manual Review Queue now has a read-only dashboard detail view. It groups review items by persisted status, reason, severity, entity links, Water Emergency relation, age bucket, blocker/attention signals, and audit evidence.

This visibility does not approve, reject, defer, archive, resolve, dispatch, or otherwise execute review actions. Manual Review remains authoritative until future authenticated action workflows are explicitly designed.

## Phase 0 Module 41 Manual Review Detail Visibility

Manual Review now has a read-only single-item detail view for operator investigation context. The detail view shows the selected review item, reason and evidence context, linked job/work-order/visit/route-assignment context, Water Emergency context when specifically linked, audit references, and chronological timeline evidence.

This detail visibility is a Randall-authorized Phase 0 baseline for internal review investigation only. It does not approve, reject, defer, archive, resolve, dispatch, escalate, call AI, call vendors, or create final company policy.

## Phase 0 Module 42 Manual Review Filter, Sort, And Saved-View Visibility

Manual Review now has read-only queue filter and sort visibility for operator scanability. The queue can expose internal view groups such as open, deferred, resolved, archived, active attention, Water Emergency-related, dispatch-related, missing data, duplicate/conflict, cancellation/status uncertainty, and needs operator review.

These groups are Randall-authorized Phase 0 visibility baselines only. They do not approve, reject, defer, archive, resolve, dispatch, escalate, enforce SLA rules, create legal/company policy, or replace future authenticated Manual Review action workflows.

Frontend saved view preferences are browser-only UI preferences. They may remember the selected Manual Review filter and sort option, but they must not store tokens, secrets, customer data, PII, backend operational state, or Manual Review decisions.

---

# 10. Confidence Scoring

The system should assign operational confidence scores.

Example:

- 95–100 → safe automation
- 75–94 → warning state
- below 75 → manual review required

---

# 11. AI Usage Rules

AI is an ASSISTANT.

AI is NOT:
- operational authority
- dispatch authority
- cancellation authority

Humans always override AI decisions.

---

# 12. FastField Rules

FastField is transitional infrastructure.

The system must NOT tightly couple internal architecture to FastField.

Future versions will replace FastField with:
- ACS technician workflows
- ACS mobile app
- internal work order management

---

# 13. Audit Logging Rules

Important actions must be logged.

Examples:
- imports
- dispatches
- cancellations
- technician assignments
- overrides
- manual reviews
- route generation
- exports

Logs must support:
- debugging
- compliance
- operational tracing

---

# 14. Future Expansion Rules

The system must be designed for future modules:

- billing
- inventory
- CRM
- payroll support
- customer portal
- technician app
- equipment lifecycle
- analytics
- AI operational assistant
- Verizon Connect integration

Architecture decisions today must NOT block future expansion.

---

# 15. Safety Rules

Operational safety always overrides automation convenience.

When uncertainty exists:
- stop automation
- request human review

Never risk:
- dispatching canceled jobs
- losing water emergency tracking
- assigning wrong technicians
- corrupting operational data
