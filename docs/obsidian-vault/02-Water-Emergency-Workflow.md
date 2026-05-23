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

# Phase 0 Module 34 — Review, Exception, And Critical-Alert Visibility

Module 34 extends the dedicated read-only Water Emergency dashboard and detail views with Manual Review, exception, blocker, and critical-alert visibility.

The read models may show:

- open, deferred, resolved, and archived Water Emergency review counts
- review reason and blocker reason distributions from existing `ReviewItem` evidence
- critical unresolved and escalation indicator counts from existing review status/severity fields
- review item IDs and audit-correlation references
- per-record scoped review context only when a review is tied to the selected Water Emergency through job, entity, or visit linkage
- explicit unknown indicators such as missing scoped review evidence

Boundary:

- this is visibility only
- review visibility is not Manual Review approval, rejection, resolution, or archival authority
- alert visibility is not escalation execution
- blocker visibility is not workflow execution
- no final Water Emergency review or escalation taxonomy is invented
- no Water Emergency create, edit, close, dispatch, approval, vendor, or AI controls are added

Unresolved:

- final Luis-confirmed Water Emergency review/escalation taxonomy
- whether review blockers need dedicated typed fields instead of reason-code buckets
- whether critical alerts need an emergency-specific event taxonomy
- role-scoped authority once authenticated Manual Review and Water Emergency workflows are designed

---

# Phase 0 Module 35 — Next-Step Readiness Visibility

Module 35 extends the dedicated read-only Water Emergency dashboard and detail views with operator-safe next-step readiness visibility.

The read models may show:

- readiness labels such as Manual Review needed, operator decision needed, visit follow-up needed, equipment review needed, drying-stage confirmation needed, blocked by missing data, awaiting more information, ready for close review, or closed with no active next-step action
- short explanations for why each readiness label was selected
- review, critical-alert, blocker, and unknown-data counts that support the readiness label
- related job, work-order, visit, review, event, and audit-correlation evidence references
- synthetic local examples that demonstrate readiness states without using production/customer/vendor data

Boundary:

- next-step readiness is visibility only
- readiness labels are not workflow execution
- readiness labels are not operator authority, approval, close, dispatch, vendor, or AI controls
- `ready_for_close_review` does not close a Water Emergency record and does not define final closure rules
- closed or resolved Water Emergency records must not imply an active workflow action
- missing data must produce safe review/readiness language instead of hidden lifecycle transitions

Unresolved:

- final Luis-confirmed Water Emergency readiness taxonomy
- exact closure-readiness and equipment-pickup requirements
- whether readiness labels should become stored workflow states in a future execution module
- how authenticated roles should see or act on readiness context once Water Emergency operations are implemented

---

# Phase 0 Module 36 — Operator Queue And Attention Visibility

Module 36 extends the dedicated read-only Water Emergency dashboard with operator-safe queue and attention visibility.

The read models may show:

- queue groups such as active attention, Manual Review, blocked or missing information, follow-up readiness, close-review visibility, monitoring, and closed/resolved records
- deterministic attention labels such as critical attention, needs Manual Review, blocked missing data, needs follow-up, equipment review needed, drying-stage review needed, ready for close review, monitoring, and closed or resolved
- why each record appears in a queue group, using existing readiness labels, review counts, critical-alert counts, blocker counts, unknown counts, visit-chain context, equipment/drying context, and evidence references
- closed/resolved Water Emergency records separated from active attention records
- synthetic local examples for queue scanning without production/customer/vendor data

Boundary:

- queue visibility is not workflow execution
- attention labels are not operator authority and do not approve, dispatch, close, or schedule Water Emergency work
- the queue is not a final prioritization engine or final ACS operations taxonomy
- Manual Review remains authoritative when review evidence exists
- unknown or incomplete evidence must remain visible as blocked/review context instead of hidden lifecycle progress

Unresolved:

- final Luis-confirmed Water Emergency triage and priority taxonomy
- whether future queue labels should remain derived read models or become persisted workflow states
- authenticated role-scoped queue visibility and operator authority
- future execution modules for visits, equipment review, drying confirmation, and closure review

---

# Phase 0 Module 37 — Aging, Follow-Up Risk, And Time-Sensitive Visibility

Module 37 extends the dedicated read-only Water Emergency dashboard with timing awareness based on existing timestamps and persisted evidence.

The read models may show:

- time-sensitivity labels such as newly opened, active monitoring, follow-up due, follow-up overdue, stale evidence, waiting for review, ready for close review, closed or resolved, and unknown timing
- created/opened, last visit, last review, last event, and closed timestamps when existing records provide them
- age buckets, follow-up buckets, stale/missing evidence indicators, and reason codes explaining why a label appears
- closed/resolved Water Emergency records separated from active timing risks
- synthetic local examples for timing visibility without production/customer/vendor data

Boundary:

- aging visibility is not an SLA engine
- follow-up visibility is not workflow execution, auto-escalation, scheduling, dispatch, closure, or approval
- timing labels are conservative Phase 0 projections from persisted evidence only
- missing timestamp evidence must show unknown timing rather than inventing an SLA or hidden lifecycle transition
- closed/resolved Water Emergency records must not appear as active overdue work

Unresolved:

- final Luis-confirmed Water Emergency SLA, aging, and follow-up taxonomy
- whether timing labels should remain read-model projections or become stored workflow states later
- authenticated role-scoped timing visibility and operator authority
- future execution modules for follow-up scheduling, drying confirmation, equipment pickup, escalation, and closure review

---

# Phase 0 Module 38 — Filtering, Sorting, And Operator View-State Visibility

Module 38 extends the dedicated read-only Water Emergency dashboard with operator-safe filtering, sorting, grouping, and view-state clarity.

The read models may show:

- available filter groups such as all, active, critical attention, needs Manual Review, blocked or missing data, follow-up due, follow-up overdue, stale evidence, ready for close review, unknown timing, and closed/resolved
- deterministic sort options for attention priority, last activity, and status/stage scanning
- per-record filter group membership, primary filter group, sort label/rank, queue group, timing label, readiness label, review counts, critical counts, blocker counts, unknown counts, related references, audit references, and evidence references
- active Water Emergency records separated from closed/resolved records
- empty filter states without implying hidden lifecycle progress or operator authority
- synthetic local examples using existing Module 29-37 seed coverage without production/customer/vendor data

Boundary:

- filtering and sorting are visibility only
- frontend view state is not backend operational state
- filters do not approve, dispatch, close, escalate, schedule, mutate, or execute Water Emergency work
- filter labels are not final ACS operations taxonomy
- Manual Review remains authoritative when review evidence exists
- closed/resolved records must remain separate from active attention and timing views

Unresolved:

- final Luis-confirmed Water Emergency filter, triage, and queue taxonomy
- whether future filter metadata should remain derived read-model projections or become persisted user preferences
- production pagination, role-scoped visibility, saved views, refresh cadence, and stale-data behavior
- future authenticated Water Emergency action modules for follow-up scheduling, equipment review, drying confirmation, escalation, and closure review

---

# Phase 0 Module 39 — Governance, View Preferences, And Scalability Readiness

Module 39 formalizes the Water Emergency visibility categories created in Modules 35-38 so they are no longer loose notes.

Decision authority baseline:

- Randall Rodriguez is the delegated technical manager, software owner, implementation approver, and Phase 0 software decision authority for ACS-FSM.
- Internal software-visible labels, filters, readiness groups, timing heuristics, dashboard behavior, and conservative UI defaults are marked as a Randall-authorized Phase 0 visibility baseline.
- Older notes that say final non-legal Water Emergency taxonomy requires Luis or operations confirmation are now interpreted as: record the assumption, choose a conservative Phase 0 software baseline, document it, and continue.
- Luis and Alfonso remain business stakeholders and operational reviewers.

Legal and owner-review boundary:

- Phase 0 visibility labels are not final legal, insurance, compliance, warranty, customer-facing, or company-liability policy.
- Final SLA enforcement, drying certification language, insurance documentation, warranty language, customer promises, or formal company policy require Alfonso owner review.
- The system may display owner-review boundaries, but it must not silently finalize those policies.

Read-only dashboard behavior:

- backend governance metadata identifies provisional filter groups, attention labels, timing labels, readiness labels, and future role-visibility roles
- result-window metadata prepares future pagination/query scaling by reporting total count, visible count, result limit, `has_more`, sort key, and generation time
- frontend saved view preferences may persist selected Water Emergency filter and sort values locally in the browser only
- saved view preferences do not store secrets, tokens, PII, customer data, backend records, or operational workflow state
- saved view preferences do not approve, close, dispatch, schedule, escalate, or mutate Water Emergency records

Future role planning:

- provisional future roles include office_admin, operations_manager, dispatcher, reviewer, technician, and owner
- current Phase 0 does not implement auth, RBAC, fake login, fake role hiding, or role enforcement
- role-scoped visibility must be designed in a future authenticated module

Unresolved:

- Alfonso owner review for any final SLA, insurance, warranty, drying certification, customer-facing promise, or company-liability policy
- future authenticated role-scoped visibility and authority
- future production saved views that synchronize to backend user accounts
- future backend pagination/query limits once real Water Emergency volume requires them

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

---

# 14. Phase 0 Module 46 Manual Review Command-Contract Separation

Water Emergency-related Manual Review items may now expose read-only future command-contract metadata when they are specifically linked to Water Emergency evidence.

Separation rules:

- Water Emergency command-contract metadata is visibility only and does not execute Water Emergency actions
- Water Emergency-related reviews require a future Water Emergency scope check before any future Manual Review command could be implemented
- Water Emergency command-contract blockers must not be merged into standard dispatch action preparation
- resolved or archived Water Emergency-related review items remain historical visibility, not active action needs
- no Water Emergency close, resolve, dispatch, vendor, AI, auth, RBAC, or workflow execution behavior is added

Future work:

- authenticated Manual Review action workflows
- role-scoped Water Emergency review authority
- owner-reviewed legal, insurance, warranty, or company-liability language if future actions affect formal policy
