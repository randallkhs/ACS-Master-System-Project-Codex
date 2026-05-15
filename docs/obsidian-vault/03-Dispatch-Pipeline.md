# ACS FSM — Dispatch Pipeline

# Purpose

This document defines the official dispatch pipeline workflow for the ACS FSM platform.

The dispatch pipeline is responsible for:

- importing operational jobs
- validating operational data
- detecting problems
- routing technicians
- generating dispatch-ready output
- supporting FastField transitional workflows

This document describes BOTH:
- current operational behavior
- future architectural direction

---

# 1. High-Level Pipeline

```text
Google Calendar
    ↓
Calendar Import
    ↓
Normalization
    ↓
Classification
    ↓
Validation
    ↓
Confidence Scoring
    ↓
Manual Review Queue (if needed)
    ↓
Routing Engine
    ↓
Dispatch Generation
    ↓
Spreadsheet / FastField Export
    ↓
Audit Logging

2. Calendar Import Stage

Current Behavior

The system imports:

* NEXT DAY jobs only

Example:

* current date = 2026-05-14
* imported jobs = 2026-05-15

---

Future Behavior

Future versions may support:

* same-day dispatch
* live updates
* recurring synchronization
* customer portal requests

---

3. Import Sources

Current import sources:

* Google Calendar

Future sources:

* customer portal
* technician requests
* emergency intake forms
* CRM system
* API integrations

---

4. Normalization Stage

Imported events must be normalized into structured internal data.

Examples:

* customer name
* address
* state
* AM/PM markers
* cancellation indicators
* water emergency detection
* technician requirements

---

5. Classification Stage

Jobs must be classified into operational categories.

Examples:

* standard cleaning
* water emergency
* canceled
* manual review required

---

6. Cancellation Detection

The system must detect cancellation indicators using:

* fuzzy matching
* spelling tolerance
* confidence scoring

Examples:

* canceled
* cancelled
* canseled
* cancelld
* canneled

Low-confidence results must trigger:

* manual review

---

7. AM/PM Detection

The system must detect:

* AM jobs
* PM jobs

Examples:

* AM/DE
* DE/AM
* PM/NJ
* NJ/PM

These affect:

* routing
* technician scheduling
* dispatch grouping

---

8. State Detection

The system must detect:

* DE
* MD
* PA
* NJ

Future versions may support:

* expanded service regions

---

9. Address Validation

Addresses should be validated before dispatch.

Potential validation:

* malformed addresses
* missing street numbers
* incomplete ZIP codes
* duplicate addresses

Invalid addresses trigger:

* manual review

---

10. Water Emergency Detection

The system must identify Water Emergency workflows separately from standard jobs.

Examples:

* extraction
* flood
* water damage
* drying
* moisture
* dehumidifier

Water Emergency jobs follow different operational workflows.

---

11. Confidence Scoring

Each imported job should receive:

* operational confidence score

Examples:

High confidence

* valid address
* clear job type
* valid state marker
* no conflicting indicators

Low confidence

* malformed title
* unclear cancellation
* missing address
* conflicting states

---

12. Manual Review Queue

Jobs requiring human review must be isolated before dispatch.

Examples:

* unclear cancellation
* invalid address
* duplicate jobs
* missing data
* low confidence parsing

The system must NEVER auto-dispatch uncertain jobs.

---

## Phase 0 Module 5 Intake Pipeline Foundation

Module 5 establishes the deterministic intake foundation for future dispatch ingestion.

Current internal pipeline:

```text
RawIntakePayload
    ↓
Normalization
    ↓
Validation
    ↓
Deterministic Confidence Scoring
    ↓
Manual Review Preparation
```

Implemented foundations:

* raw intake payload structure
* normalized intake structure
* detection result structure
* validation issue and result structures
* deterministic confidence score structure
* Manual Review recommendation structure
* whitespace cleanup
* AM/PM marker extraction
* supported state marker extraction
* cancellation keyword detection, including known misspellings
* Water Emergency keyword detection
* required-field validation
* malformed-address foundation
* conflicting state and time-window detection
* unsafe dispatch detection foundation
* warning/error aggregation
* review reason generation

Safety boundary:

* no live Google Calendar ingestion
* no route generation
* no Sheets/FastField export
* no AI orchestration
* no dispatch execution

Deterministic rules run before any future AI support. AI may later assist with ambiguous parsing, but it must not become the source of truth or bypass Manual Review.

Unresolved normalization questions:

* exact ACS service taxonomy and keyword list
* whether `AM` and `PM` should be detected from human time phrases such as `9 AM` or only from route markers such as `AM/DE`
* whether state markers should be trusted from title text, address text, or both when they conflict
* exact cancellation fuzzy-match thresholds for auto-cancel versus Manual Review
* full Water Emergency keyword taxonomy and stage mapping
* whether missing scheduled date should always block dispatch in every future intake source

---

Phase 0 Module 6 Manual Review Persistence

The dispatch pipeline now has a persistent Manual Review Queue foundation for intake that cannot safely continue.

Current intake processing states:

* raw
* normalized
* validated
* flagged_for_review
* approved
* rejected
* deferred
* archived

Persistent review items store deterministic traceability:

* why the item was flagged
* validation evidence
* normalization evidence
* confidence explanation
* warning snapshot
* source system/source ID
* operator notes and decision timestamps
* audit correlation ID

Review generation remains deterministic. It can classify cancellation review, Water Emergency review, malformed address review, missing field review, conflicting state review, low confidence review, and unsafe dispatch review.

Review approval means an operator has resolved the review item. It does not automatically dispatch, route, export, or complete workflow execution.

Unresolved review questions:

* exact operator roles and permission boundaries
* whether deferred review items need SLA timers or scheduled reminders
* exact severity escalation thresholds once ACS confirms operational urgency categories
* how review decisions should attach to future created jobs, visits, and Water Emergency records
* whether some review categories should require a second operator confirmation

---

Phase 0 Module 7 Dispatch Orchestration Preparation

The dispatch pipeline now has a deterministic orchestration preparation layer.

Current orchestration flow:

```text
Raw Intake
    ↓
Normalization
    ↓
Validation
    ↓
Confidence Scoring
    ↓
Manual Review Recommendation
    ↓
Dispatch Eligibility Decision
```

The orchestration result preserves:

* normalized intake
* validation result
* confidence score
* Manual Review recommendation
* review reasons
* orchestration warnings
* dispatch eligibility
* normalization evidence
* validation evidence
* confidence evidence
* review evidence
* deterministic decision evidence

Dispatch eligibility is a preparation result only. It can mark intake as eligible, review-required, blocked, deferred, unsafe, or Water Emergency-separated, but it does not dispatch work.

Safety boundary:

* no live Google Calendar ingestion
* no job persistence
* no Manual Review persistence from orchestration
* no route generation
* no Sheets/FastField export
* no AI orchestration
* no dispatch execution
* no hidden state transitions

Unresolved orchestration questions:

* exact rule for warning-only intake that is technically dispatch-safe but still operationally sensitive
* whether dispatch eligibility should later include date-window policy such as next-day only
* how approved review outcomes become persisted jobs, visits, and Water Emergency records
* exact point where duplicate detection enters the deterministic orchestration flow
* whether future AI advisory context should be attached before or after Manual Review recommendation

---

Phase 0 Module 8 Operational Intake Persistence

The dispatch pipeline now has a durable operational intake persistence boundary.

Current persistence flow:

```text
Orchestration Result
    ↓
Operational Intake Persistence
    ↓
Intake Processing Record
```

The persisted intake processing record stores:

* source system/source ID
* lifecycle state
* orchestration state
* dispatch eligibility snapshot
* orchestration result snapshot
* raw payload snapshot
* normalized evidence
* validation evidence
* confidence evidence
* review evidence
* warning evidence
* deterministic decision evidence
* review item linkage
* audit correlation ID

Current operational lifecycle states:

* intake_received
* normalized
* validated
* review_required
* approved_for_dispatch
* blocked
* deferred
* archived

Safety boundary:

* persistence does not execute dispatch
* persistence does not create jobs, visits, work orders, or route assignments
* persistence does not call integrations
* persistence does not run background workers
* unsafe intake cannot be marked approved for dispatch
* Water Emergency intake remains separated from standard dispatch approval
* review-required intake remains review-required until explicitly resolved

Unresolved persistence questions:

* whether imported intake records need deduplication keys before persistence
* when approved intake becomes a real job/work order/visit
* whether review resolution should create a second immutable lifecycle event record
* exact retention/archive policy for intake processing records
* how future operator identity should be stored on lifecycle transitions

---

Phase 0 Module 9 Operational Job Creation Foundation

The dispatch pipeline now has a controlled intake-to-job transition boundary.

Current creation flow:

```text
Approved Intake Processing Record
    ↓
Operational Job Creation
    ↓
Standard Job
    ↓
Job Creation Record
```

The job creation service only creates standard operational jobs from intake records that have already been explicitly approved for dispatch by deterministic orchestration or a future explicit review-resolution path.

Creation evidence preserves:

* intake processing record ID
* created job ID
* job creation record ID
* review item linkage when present
* audit correlation ID
* orchestration snapshot
* dispatch eligibility snapshot
* deterministic evidence snapshot
* creation snapshot
* lifecycle metadata

Creation safety rules:

* blocked intake cannot create jobs
* review-required intake cannot create jobs
* unsafe intake cannot create jobs
* Water Emergency intake cannot create standard jobs
* invalid lifecycle states cannot create jobs
* duplicate job creation from the same intake record is blocked
* created standard jobs start at `awaiting_dispatch`, not dispatched

Safety boundary:

* job creation does not execute dispatch
* job creation does not route technicians
* job creation does not create visits or work orders
* job creation does not export to Sheets/FastField
* job creation does not call integrations
* job creation does not run background workers
* job creation does not call AI

Unresolved creation questions:

* exact future mapping from approved intake to customer/property/job records
* whether standard job creation should also create a work order in a later module
* how review-resolution approvals should be represented before job creation
* whether duplicate prevention should use source-system/source-ID in addition to intake record ID
* how Water Emergency intake becomes a separate Water Emergency workflow record

---

Phase 0 Module 10 Work Order And Visit Generation Foundation

The dispatch pipeline now has a scheduling-ready operational generation boundary.

Current generation flow:

```text
Standard Job
    ↓
Work Order Generation
    ↓
Work Order
    ↓
Visit Generation
    ↓
Visit
```

The Work Order generation service creates standard Work Orders only from approved standard jobs that came through the explicit intake-to-job creation boundary.

Work Order evidence preserves:

* job ID
* work order ID
* job creation record ID
* review item linkage when present
* audit correlation ID
* intake snapshot
* orchestration snapshot
* dispatch eligibility snapshot
* deterministic evidence snapshot
* generation snapshot
* lifecycle metadata

Visit evidence preserves:

* job ID
* work order ID
* visit ID
* audit correlation ID
* work order snapshot
* deterministic evidence snapshot
* review linkage snapshot
* generation snapshot
* lifecycle metadata

Generation safety rules:

* blocked jobs cannot create Work Orders
* review-required jobs cannot create Work Orders
* Water Emergency jobs cannot use the standard Work Order path
* invalid lifecycle states cannot create Work Orders or Visits
* duplicate Work Order generation for the same job is blocked
* duplicate Visit generation for the same Work Order is blocked
* generated Work Orders are not dispatched
* generated Visits are not assigned, scheduled, routed, or dispatched

Safety boundary:

* generation does not execute dispatch
* generation does not route technicians
* generation does not assign technicians
* generation does not run a scheduling engine
* generation does not export to Sheets/FastField
* generation does not call integrations
* generation does not run background workers
* generation does not call AI

Unresolved generation questions:

* exact Work Order numbering policy for production operations
* exact default required forms and equipment notes by service type
* whether one standard job should always create exactly one Work Order and one Visit
* whether future reviewed jobs need a second operator confirmation before Work Order generation
* how standard Work Order generation differs from the future Water Emergency operational path
* when technician assignment, schedule time windows, and routing should become durable workflow steps

---

13. Routing Engine

Current Routing

Current strategy:

* North group
* South group

based on:

* depot location

---

Future Routing

Future routing should support:

* AM/PM windows
* technician skills
* live traffic
* GPS integration
* Water Emergency priority
* technician availability
* equipment constraints

---

14. Technician Assignment

Dispatch generation should eventually support:

* technician specialization
* workload balancing
* regional familiarity
* emergency prioritization

---

15. Spreadsheet Generation

Current workflow generates:

* Google Sheets operational spreadsheet

Separate sections:

* standard jobs
* AM/PM jobs
* Water Emergency jobs

---

16. FastField Export

Current system exports operational data to FastField.

Different forms:

* standard jobs
* Water Emergency jobs

Future system must support:

* adapter-based export architecture

The core system should NOT depend tightly on FastField.

---

17. Audit Logging

All major pipeline stages must be logged.

Examples:

* imported jobs
* normalized records
* validation warnings
* routing results
* dispatch exports
* manual review decisions

Logs must support:

* debugging
* operational auditing
* future analytics

---

18. Future Customer Portal Integration

Future workflow:

Customer Portal
    ↓
Structured Request Form
    ↓
Internal Validation
    ↓
Dispatch Pipeline

This reduces:

* human spelling errors
* malformed requests
* ambiguous operational text

---

19. AI Usage

AI may assist:

* classification
* validation
* anomaly detection
* operational recommendations

AI must NOT:

* override human review
* auto-confirm cancellations
* auto-close Water Emergency workflows

---

20. Long-Term Goal

The dispatch pipeline should evolve into:

* deterministic
* state-driven
* scalable
* modular
* auditable
* API-first

The future platform must eventually replace:

* spreadsheet dependency
* fragmented workflows
* manual coordination
* fragile calendar parsing
```
