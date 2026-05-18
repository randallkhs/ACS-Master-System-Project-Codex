# ACS FSM — Water Emergency Workflow

# Purpose

This document defines the official operational lifecycle of Water Emergency jobs inside the ACS FSM platform.

Water Emergency jobs are NOT normal jobs.

They are long-lived operational workflows with:
- multiple visits
- multiple technicians
- equipment tracking
- moisture monitoring
- staged completion logic

---

# 1. Water Emergency Philosophy

Water Emergency jobs behave more like:
- operational cases
or
- projects

than traditional same-day work orders.

The system must support:
- continuity
- history
- visit tracking
- technician notes
- equipment lifecycle
- staged completion

---

# 2. Core Operational Lifecycle

## Phase 1 — Emergency Intake

Typical trigger:
- burst pipe
- flooding
- water intrusion
- sewage backup
- storm damage

Initial information is received from:
- customer
- apartment complex
- property manager
- insurance-related contact

---

## Phase 2 — Initial Dispatch

The first technician visit typically includes:
- water extraction
- initial inspection
- equipment setup
- moisture measurements
- emergency stabilization

Typical equipment:
- air movers
- dehumidifiers
- extraction machines
- air scrubbers

The job remains OPEN.

---

## Phase 3 — Drying Monitoring

Additional technician visits may include:
- moisture checks
- equipment repositioning
- progress verification
- contamination monitoring

Multiple technicians may participate.

The job remains OPEN.

---

## Phase 4 — Cleaning / Treatment

After drying:
- carpet cleaning
- antimicrobial treatment
- deodorization
- floor treatment
- structural cleaning

The job may still remain OPEN.

---

## Phase 5 — Equipment Pickup

Final technician visit:
- remove equipment
- final moisture verification
- confirm completion
- customer signoff (future)

Only after this phase:
- the job may CLOSE

---

# 3. Water Emergency Job Structure

A Water Emergency job may contain:

- one customer
- one property
- multiple visits
- multiple technicians
- multiple equipment assignments
- multiple notes
- multiple status changes

---

# 4. Visits

Visits are separate operational records.

A visit represents:
- one technician interaction
- one scheduled service occurrence

Examples:
- extraction visit
- drying check
- cleaning visit
- pickup visit

---

# 5. Equipment Lifecycle

Equipment tracking is critical.

Equipment examples:
- dehumidifiers
- air movers
- extraction machines
- HEPA systems

Future system requirements:
- assignment tracking
- deployment timestamps
- pickup timestamps
- location tracking
- technician accountability

---

# 6. Water Emergency Status States

Suggested initial statuses:

## Intake
- NEW
- PENDING_REVIEW

## Active
- DISPATCHED
- EXTRACTION_IN_PROGRESS
- DRYING_IN_PROGRESS
- CLEANING_IN_PROGRESS
- WAITING_FOR_NEXT_VISIT

## Completion
- READY_FOR_PICKUP
- PICKUP_SCHEDULED
- COMPLETED

## Exception States
- ON_HOLD
- CUSTOMER_DELAY
- CANCELLED
- MANUAL_REVIEW_REQUIRED

---

# 7. Technician Notes

Each visit may include:
- work performed
- moisture readings
- equipment updates
- contamination notes
- customer communication
- recommendations

Notes must be:
- timestamped
- tied to technician
- immutable in audit logs

---

# 8. Scheduling Rules

Water Emergency jobs:
- may overlap multiple days
- may require recurring visits
- may require priority dispatching
- may interrupt standard scheduling

Future versions should support:
- dynamic reprioritization
- emergency escalation
- technician reassignment

---

# 9. FastField Compatibility

Current workflow uses:
- separate FastField forms

Examples:
- standard work order form
- water emergency form

Water Emergency forms remain open until:
- final equipment pickup
- operational completion

The future ACS FSM platform must replicate this behavior internally.

---

# 10. Manual Review Requirements

Water Emergency jobs require higher operational scrutiny.

Examples:
- missing drying visit
- missing equipment
- invalid pickup state
- incomplete moisture tracking
- technician conflict
- duplicate dispatch

These conditions should trigger:
- operational warnings
- manual review queue
- escalation states

---

# 11. Future Expansion

Future Water Emergency functionality may include:

- moisture graphs
- equipment QR tracking
- technician mobile uploads
- insurance exports
- customer signatures
- before/after photos
- GPS technician verification
- automated revisit scheduling
- billing integration
- inventory consumption tracking

---

# Phase 0 Module 31 — Dedicated Dashboard Visibility

Module 31 adds a dedicated read-only Water Emergency dashboard contract and frontend section.

The dashboard read model may show:

- open and closed Water Emergency counts
- Water Emergency status and drying-stage distribution
- multi-visit indicators based on related Visit records
- equipment onsite and moisture-tracking indicators from existing fields
- related job, work-order, visit, review, audit, and timeline references where persisted state supports them
- data-gap indicators such as missing stage, missing next action, missing visit history, or missing timeline evidence

Boundary:

- this is visibility only
- it does not create Water Emergency records
- it does not close or resolve Water Emergency work
- it does not dispatch Water Emergency work
- it does not call FastField, Sheets, Calendar, Verizon Connect, or AI
- it does not infer hidden lifecycle transitions
- it does not bypass Manual Review

Unresolved:

- exact Water Emergency stage taxonomy
- exact closure and pickup requirements
- dedicated equipment inventory/entities
- whether emergency timeline events need a separate event taxonomy
- how future authenticated roles should scope Water Emergency visibility and authority

---

# Phase 0 Module 32 — Detail And Timeline Visibility

Module 32 extends the dedicated Water Emergency dashboard with a read-only per-record detail contract and frontend detail section.

The detail read model may show:

- one selected Water Emergency record
- related Job, Work Order, and Visit references where available
- Manual Review indicators only when specifically tied to that Water Emergency record through job, entity, or visit linkage
- chronological operational event timeline evidence
- audit correlation references
- explicit data gaps such as missing job reference, no work order reference, no visit history, no timeline evidence, missing drying stage, or missing next action

Boundary:

- this is detail visibility only
- it does not create or edit Water Emergency records
- it does not close or resolve Water Emergency work
- it does not dispatch Water Emergency work
- it does not approve or reject Manual Review items
- it does not call FastField, Sheets, Calendar, Verizon Connect, or AI
- it does not infer hidden lifecycle transitions from timeline events

Unresolved:

- exact operator selection/navigation model for multiple Water Emergency records
- whether future detail screens should use dedicated equipment and moisture-reading entities
- production timeline pagination and filtering
- role-scoped access to emergency detail evidence once authentication exists

---

# Phase 0 Module 33 — Equipment, Visit Chain, And Drying-Stage Visibility

Module 33 extends the dedicated read-only Water Emergency dashboard and detail views with equipment context, visit-chain context, and drying-stage context where existing persisted data supports it.

The read models may show:

- equipment onsite and moisture-tracking flags from `WaterEmergency`
- required equipment notes from related `WorkOrder` records
- explicit unknown indicators when dedicated equipment inventory entities are not modeled yet
- related Water Emergency visit-chain counts and visit status buckets
- first/latest/next scheduled visit timestamps when related `Visit` records provide them
- current Water Emergency status, drying stage, next required action, and missing-stage indicators

Boundary:

- this is visibility only
- equipment visibility is not inventory management
- visit-chain visibility is not dispatch execution
- drying-stage visibility is not field approval or closure authority
- no final Water Emergency taxonomy is invented
- no Water Emergency create, edit, close, dispatch, approval, vendor, or AI controls are added

Unresolved:

- final Luis-confirmed Water Emergency status/stage taxonomy
- dedicated equipment inventory and equipment lifecycle records
- dedicated moisture reading/history records
- formal rules for equipment pickup, closure readiness, and revisit scheduling
- role-scoped authority once authenticated Water Emergency workflows are designed

---

# 12. Critical Architectural Rules

## Rule 1
Water Emergency jobs are NOT simple jobs.

---

## Rule 2
A Water Emergency job may contain MANY visits.

---

## Rule 3
Visits must be independently tracked.

---

## Rule 4
Equipment must become first-class data entities.

---

## Rule 5
The system must preserve complete operational history.

---

## Rule 6
The workflow must support future mobile technician apps.

---

## Rule 7
Operational continuity is more important than automation speed.

---

# 13. Operational Goal

The final system should allow ACS to completely replace:
- FastField water emergency workflows
- fragmented tracking
- manual coordination
- spreadsheet dependency

with one integrated operational workflow system.
