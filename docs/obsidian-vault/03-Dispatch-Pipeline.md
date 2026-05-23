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

Phase 0 Module 11 Technician Assignment And Scheduling Preparation

The dispatch pipeline now has a deterministic technician assignment and scheduling readiness boundary.

Current preparation flow:

```text
Generated Visit
    ↓
Assignment Preparation
    ↓
Technician Compatibility Check
    ↓
Scheduling Readiness Preparation
```

Assignment preparation evidence preserves:

* visit ID
* work order ID
* job ID
* candidate technician ID when provided
* audit correlation ID
* assignment eligibility
* assignment-required state
* technician active/inactive readiness
* technician skills, service areas, vehicle label, and availability context
* AM/PM scheduling preference
* service-state markers
* lifecycle blockers
* operational readiness metadata

Preparation safety rules:

* blocked Visits cannot be prepared for assignment
* review-required Visits cannot be prepared for assignment
* Water Emergency Visits cannot use the standard assignment path
* archived lifecycle cannot be scheduled
* invalid lifecycle transitions are blocked
* inactive technician candidates block compatibility
* unassigned Visits without a candidate remain assignment-required
* preparation does not set the technician ID or scheduled time

Safety boundary:

* assignment preparation does not execute dispatch
* assignment preparation does not run routing
* assignment preparation does not assign technicians
* assignment preparation does not sync calendars
* assignment preparation does not update technician mobile workflows
* assignment preparation does not call integrations
* assignment preparation does not run background workers
* assignment preparation does not call AI

Unresolved assignment and scheduling questions:

* exact technician availability states and which values block assignment
* exact skill-to-service compatibility rules
* whether service areas should block assignment before routing exists
* how multi-technician assignments should be represented in the assignment preparation result
* how AM/PM windows should translate into exact schedule windows
* when prepared scheduling should become a durable scheduled time

---

Phase 0 Module 12 Routing And Dispatch Preparation

The dispatch pipeline now has a deterministic routing and dispatch preparation boundary.

Current preparation flow:

```text
Prepared Visit
    ↓
Routing Readiness Preparation
    ↓
Technician Readiness Snapshot
    ↓
Dispatch Eligibility Preparation
```

Routing and dispatch preparation evidence preserves:

* Visit, Work Order, Job, technician, and audit-correlation references
* routing readiness
* routing blockers
* technician readiness snapshots
* assignment readiness evidence
* scheduling readiness evidence
* Visit dispatch readiness
* dispatch eligibility
* dispatch blockers
* deterministic lifecycle state

Preparation safety rules:

* blocked Visits cannot become dispatch-ready
* review-required lifecycle blocks dispatch
* Water Emergency Visits cannot use the standard routing/dispatch path
* inactive technicians block dispatch readiness
* unassigned Visits cannot become dispatch-ready
* unscheduled Visits cannot become dispatch-ready
* `routing_ready` and `dispatch_ready` are preparation states only

Safety boundary:

* routing preparation does not optimize routes
* routing preparation does not create route assignments
* dispatch preparation does not execute dispatch
* dispatch preparation does not call integrations
* dispatch preparation does not sync calendars
* dispatch preparation does not update technician mobile workflows
* dispatch preparation does not call AI

Unresolved routing and dispatch preparation questions:

* exact route grouping model for North/South regions and future route zones
* whether dispatch readiness should require a persisted `RouteAssignment`
* exact technician availability statuses that block dispatch
* whether assigned-but-not-evaluated technicians should block dispatch in production
* how route optimization evidence should later be stored without overwriting deterministic readiness
* how Water Emergency routing/dispatch should diverge from the standard path

---

Phase 0 Module 13 Route Assignment And Dispatch Authorization

The dispatch pipeline now has a deterministic route assignment and dispatch authorization boundary.

Current authorization flow:

```text
Dispatch-ready Visit
    ↓
Route Grouping Preparation
    ↓
Route Assignment Preparation
    ↓
Dispatch Authorization
    ↓
Awaiting Dispatch Execution
```

Authorization evidence preserves:

* route grouping key, route date, region, and AM/PM window
* Visit, Work Order, Job, technician, and audit-correlation references
* route assignment readiness
* technician route compatibility
* dispatch authorization readiness
* dispatch execution boundary state
* deterministic blocker reasons

Authorization safety rules:

* blocked Visits cannot become dispatch-authorized
* review-required lifecycle blocks dispatch authorization
* Water Emergency Visits cannot use the standard dispatch authorization path
* inactive technicians block dispatch authorization
* unassigned Visits cannot become dispatch-authorized
* unscheduled Visits cannot become dispatch-authorized
* route-unready Visits cannot become dispatch-authorized
* `awaiting_dispatch_execution` is an authorization boundary only

Safety boundary:

* route grouping preparation does not optimize routes
* route assignment preparation does not run a routing engine
* dispatch authorization does not execute dispatch
* dispatch authorization does not sync calendars
* dispatch authorization does not export to Sheets/FastField
* dispatch authorization does not call integrations
* dispatch authorization does not call AI

Unresolved route assignment and dispatch authorization questions:

* exact ACS route grouping model beyond deterministic state/time-window grouping
* whether route assignment authorization should require operator identity once auth exists
* how future route optimization results should update or supersede prepared route assignments
* whether dispatch authorization should require second approval for warning-heavy but valid jobs
* how Water Emergency dispatch authorization should be modeled separately from the standard path

---

Phase 0 Module 14 Dispatch Execution Foundation

The dispatch pipeline now has a deterministic internal dispatch execution boundary.

Current execution flow:

```text
Awaiting Dispatch Execution Route Assignment
    ↓
Dispatch Execution Validation
    ↓
Dispatch Execution Evidence
    ↓
Dispatched
```

Execution evidence preserves:

* Route Assignment, Visit, Work Order, Job, technician, and audit-correlation references
* previous and new lifecycle state
* dispatch timestamp
* dispatch execution blockers when execution is blocked
* explicit `not_executed` markers for external integrations
* deterministic audit evidence

Execution safety rules:

* only dispatch-authorized Route Assignments may dispatch
* blocked Visits cannot dispatch
* review-required lifecycle blocks dispatch execution
* Water Emergency Visits cannot use the standard dispatch execution path
* inactive technicians block dispatch execution
* unassigned Visits cannot dispatch
* unscheduled Visits cannot dispatch
* duplicate dispatch attempts are blocked
* unauthorized Route Assignments cannot dispatch

Safety boundary:

* dispatch execution updates internal ACS lifecycle state only
* dispatch execution does not call FastField
* dispatch execution does not sync Google Calendar
* dispatch execution does not write Sheets
* dispatch execution does not update technician mobile workflows
* dispatch execution does not run background workers
* dispatch execution does not call AI

Unresolved dispatch execution questions:

* exact operator or system identity to record once auth exists
* whether `awaiting_confirmation` should be used before external adapters are added
* how external integration outcomes should attach to internal dispatch execution records
* whether failed external execution should create a new dispatch execution revision
* how Water Emergency dispatch execution should be modeled separately from the standard path

---

Phase 0 Module 15 External Dispatch Adapter Foundation

The dispatch pipeline now has a deterministic external adapter preparation boundary.

Current adapter preparation flow:

```text
Dispatched Route Assignment
    ↓
Adapter Preparation Validation
    ↓
External Payload Evidence
    ↓
Awaiting External Execution
```

Adapter evidence preserves:

* Route Assignment, Visit, Work Order, Job, technician, and audit-correlation references
* adapter execution request snapshot
* FastField payload preparation snapshot
* Google Sheets payload preparation snapshot
* Google Calendar payload preparation snapshot
* technician mobile payload preparation snapshot
* lifecycle evidence and deterministic blocker reasons
* explicit `not_executed` markers for all external API calls

Adapter safety rules:

* only internally dispatched Visits may prepare external adapter payloads
* blocked Visits cannot prepare external adapter payloads
* review-required lifecycle blocks adapter preparation
* Water Emergency Visits cannot use the standard external adapter path
* unauthorized Route Assignments cannot prepare external adapter payloads
* duplicate adapter preparation attempts are blocked
* invalid lifecycle transitions are blocked

Safety boundary:

* adapter preparation does not call FastField
* adapter preparation does not sync Google Calendar
* adapter preparation does not write Google Sheets
* adapter preparation does not update technician mobile workflows
* adapter preparation does not run background workers
* adapter preparation does not call AI

Unresolved external adapter questions:

* exact payload schema for FastField standard dispatch forms
* exact transitional Google Sheets row format after database-first dispatch
* whether Calendar sync should create events, update existing events, or record status only
* how external adapter retry/failure attempts should be versioned
* how operator approval and credential scoping should work once auth and secrets exist
* how Water Emergency external adapter payloads should differ from the standard path

---

Phase 0 Module 18 Real External Adapter Execution Foundation

The dispatch pipeline now has a deterministic controlled external execution boundary.

Current external execution flow:

```text
Awaiting External Execution
    ↓
Controlled Provider Execution Boundary
    ↓
Provider Execution Evidence
    ↓
Awaiting External Confirmation or External Execution Failed
```

External execution evidence preserves:

* Route Assignment, Visit, Work Order, Job, technician, and audit-correlation references
* external execution request snapshot
* provider execution snapshots for FastField, Google Sheets, Google Calendar, and technician mobile sync
* provider correlation IDs
* lifecycle transition evidence
* deterministic blocker reasons
* explicit `not_executed` markers for real vendor API calls, automatic retries, and background execution

External execution safety rules:

* only prepared Route Assignments awaiting external execution may execute
* duplicate external execution attempts are blocked
* invalid lifecycle transitions are blocked
* blocked Visits cannot execute externally
* review-required lifecycle blocks external execution
* Water Emergency Visits cannot use the standard external execution path
* unauthorized Route Assignments cannot execute externally
* provider failure records failure evidence but does not run automatic retry

Safety boundary:

* external execution does not call FastField
* external execution does not sync Google Calendar
* external execution does not write Google Sheets
* external execution does not update technician mobile workflows
* external execution does not run background workers
* external execution does not call AI

Unresolved external execution questions:

* exact live provider execution contracts and response schemas
* whether external execution attempts need dedicated immutable attempt records
* retry limits and operator approval before re-execution
* credential scoping and provider-specific authorization once auth exists
* how Water Emergency external execution should differ from the standard path

---

Phase 0 Module 16 External Confirmation And Failure Recovery Foundation

The dispatch pipeline now has a deterministic external confirmation and recovery preparation boundary after controlled external execution reaches confirmation readiness.

Current confirmation flow:

```text
Awaiting External Confirmation
    ↓
Simulated External Confirmation Processing
    ↓
Confirmation / Failure / Reconciliation Evidence
    ↓
Externally Confirmed, Awaiting Retry, or Reconciliation Required
```

Confirmation and recovery evidence preserves:

* Route Assignment, Visit, Work Order, Job, technician, and audit-correlation references
* simulated external confirmation state
* confirmation success evidence
* external failure evidence
* retry preparation evidence
* reconciliation-required evidence
* deterministic blocker reasons
* explicit `not_executed` markers for external API calls, automatic retries, and reconciliation engines

Confirmation safety rules:

* only adapter-prepared Route Assignments awaiting external confirmation may confirm
* duplicate confirmations are blocked
* invalid lifecycle transitions are blocked
* blocked Visits cannot confirm
* review-required lifecycle blocks confirmation
* Water Emergency Visits cannot use the standard external confirmation path
* unauthorized Route Assignments cannot confirm
* retry preparation is allowed only after failed confirmation

Safety boundary:

* confirmation processing does not call external APIs
* retry preparation does not execute retries
* reconciliation preparation does not run a reconciliation engine
* confirmation processing does not update technician mobile workflows
* confirmation processing does not run background workers
* confirmation processing does not call AI

Unresolved confirmation and recovery questions:

* exact vendor confirmation payload formats and statuses
* whether external confirmation attempts need a dedicated immutable attempt table
* how many retry attempts should be permitted once execution exists
* how operator approval should be captured before retry or reconciliation
* how Water Emergency confirmation and recovery should differ from the standard path

---

Phase 0 Module 17 Operational Event History And Immutable Audit Timeline

The dispatch pipeline now has an append-only operational event history boundary.

Current event-history flow:

```text
Lifecycle / Dispatch / Adapter / Confirmation Evidence
    ↓
Operational Event History Validation
    ↓
Immutable Event Record
    ↓
Operational Timeline
```

Event history preserves:

* event type and event lifecycle state
* occurred and recorded timestamps
* Route Assignment, Visit, Work Order, Job, technician, and audit-correlation references
* previous and new lifecycle states
* transition evidence
* dispatch execution evidence
* external adapter preparation evidence
* confirmation, retry, recovery, and reconciliation evidence
* deterministic event fingerprint for duplicate prevention
* immutable audit evidence with explicit append-only markers

Event-history safety rules:

* event history is append-only
* duplicate event fingerprints are blocked
* hidden no-op transitions are blocked
* audit correlation continuity is required
* chronological timeline ordering is deterministic
* event history records evidence only

Safety boundary:

* event history does not execute workflows
* event history does not run route optimization
* event history does not call external APIs
* event history does not run reconciliation
* event history does not run analytics or replay engines
* event history does not call AI

Unresolved event-history questions:

* whether future external execution attempts need dedicated attempt records separate from the general event table
* retention and archive policy for immutable operational events
* whether event fingerprints should include actor identity after authentication exists
* whether production analytics should read directly from event history or from derived reporting tables
* how Water Emergency event timelines should diverge from standard route-assignment timelines

---

Phase 0 Module 19 Dispatch Reconciliation And Operational Consistency Foundation

The dispatch pipeline now has a deterministic operational consistency verification and reconciliation preparation boundary.

Current reconciliation flow:

```text
Internal Dispatch / External Execution / Confirmation Evidence
    ↓
Consistency Verification
    ↓
Divergence And Mismatch Classification
    ↓
Consistency Verified or Reconciliation Required
```

Reconciliation evidence preserves:

* Route Assignment, Visit, Work Order, Job, technician, and audit-correlation references
* internal dispatch lifecycle state
* external execution state
* external confirmation state
* mismatch classification evidence
* divergence evidence and manual-resolution requirement
* immutable operational event history count
* explicit `not_executed` markers for external API calls, retry execution, reconciliation execution, replay, and AI

Reconciliation safety rules:

* immutable event history cannot mutate
* reconciliation preparation cannot bypass Manual Review
* Water Emergency Visits cannot use the standard reconciliation path
* unauthorized Route Assignments cannot reconcile
* duplicate reconciliation preparation is blocked
* invalid lifecycle reconciliation is blocked

Safety boundary:

* reconciliation preparation does not execute reconciliation
* reconciliation preparation does not call external APIs
* reconciliation preparation does not run analytics
* reconciliation preparation does not replay workflows
* reconciliation preparation does not mutate operational history
* reconciliation preparation does not call AI

Unresolved reconciliation questions:

* exact operator ownership for manual reconciliation cases
* whether reconciliation attempts need a dedicated immutable attempt table
* how provider-specific mismatch codes should evolve once live APIs exist
* whether reconciliation should create Manual Review items automatically in a later module
* how Water Emergency reconciliation should diverge from the standard path

---

Phase 0 Module 20 Operational Replay And Recovery Preparation

The dispatch pipeline now has a deterministic replay-preparation and recovery-coordination boundary.

Current recovery preparation flow:

```text
Reconciliation / retry / failure evidence
    ↓
Replay Eligibility Evaluation
    ↓
Rollback Preparation Evaluation
    ↓
Recovery Coordination Evidence
    ↓
Replay Prepared / Rollback Prepared / Replay Blocked
```

Replay/recovery evidence preserves:

* replay eligibility
* rollback preparation status
* recovery coordination requirements
* replay blocker reasons
* immutable event-history evidence
* audit correlation continuity
* explicit `not_executed` markers for replay execution, rollback execution, retry execution, external API calls, and AI

Replay/recovery safety rules:

* immutable operational history cannot mutate
* replay preparation cannot bypass Manual Review
* Water Emergency Visits cannot use the standard replay/recovery path
* unauthorized Route Assignments cannot prepare replay or rollback
* duplicate replay preparation is blocked
* invalid lifecycle replay preparation is blocked
* replay requires reconciliation, retry, or failure context

Safety boundary:

* replay preparation does not execute replay
* rollback preparation does not execute rollback
* recovery coordination does not run a workflow engine
* replay preparation does not call external APIs
* replay preparation does not execute retries
* replay preparation does not mutate operational history
* replay preparation does not call AI

Unresolved replay/recovery questions:

* exact operator approval model before replay or rollback execution
* whether replay attempts need a dedicated immutable attempt table
* how rollback scope should be limited for production recovery
* whether future recovery coordination should create Manual Review items automatically
* how Water Emergency replay/recovery should diverge from the standard path

---

Phase 0 Module 21 Operational Governance And Approval Control

The dispatch pipeline now has a deterministic operational governance and manual-intervention authorization boundary.

Current governance flow:

```text
Replay / rollback / reconciliation preparation
    ↓
Operator Governance Validation
    ↓
Manual Intervention Authorization
    ↓
Replay / Rollback / Reconciliation Approval Evidence
    ↓
Operator Approved / Intervention Required / Governance Blocked
```

Governance evidence preserves:

* operator identity and role evidence
* replay authorization evidence
* rollback authorization evidence
* reconciliation approval evidence
* intervention authorization evidence
* governance blocker reasons
* immutable event-history evidence
* audit correlation continuity
* explicit `not_executed` markers for replay execution, rollback execution, reconciliation execution, external API calls, workflow engines, and AI

Governance safety rules:

* replay cannot execute without governance approval
* rollback cannot execute without governance approval
* reconciliation cannot bypass Manual Review
* Water Emergency Visits cannot use the standard governance path
* unauthorized operator actions are blocked
* duplicate approval is blocked
* invalid lifecycle governance is blocked
* immutable operational history cannot mutate

Safety boundary:

* governance does not execute replay
* governance does not execute rollback
* governance does not execute reconciliation
* governance does not run a workflow engine
* governance does not call external APIs
* governance does not mutate operational history
* governance does not call AI

Unresolved governance questions:

* exact operator role and permission model once authentication exists
* whether high-risk recovery actions require two-person approval
* whether approvals expire or can be revoked
* whether governance decisions need a dedicated immutable approval table
* how Water Emergency governance should diverge from the standard path

---

Phase 0 Module 22 Operational Accountability, Escalation, And Incident Coordination

The dispatch pipeline now has a deterministic accountability and escalation-preparation boundary after governance approval.

Current accountability flow:

```text
Governed Replay / Rollback / Reconciliation / Divergence Context
    ↓
Operational Accountability Validation
    ↓
Escalation / Intervention Escalation / Incident Preparation Evidence
    ↓
Escalation Required / Incident Prepared / Critical Intervention Required / Accountability Blocked
```

Accountability evidence preserves:

* governance approval evidence
* replay/recovery source state
* reconciliation and divergence context
* escalation blocker reasons
* intervention escalation evidence
* operational incident evidence
* immutable event-history evidence
* audit correlation continuity
* explicit `not_executed` markers for escalation execution, incident execution, intervention execution, external API calls, workflow engines, and AI

Accountability safety rules:

* replay and recovery escalation cannot bypass governance approval
* critical divergence requires escalation preparation
* Water Emergency Visits cannot use the standard accountability path
* unauthorized intervention escalation is blocked
* duplicate escalation or incident preparation is blocked
* invalid lifecycle accountability preparation is blocked
* immutable operational history cannot mutate

Safety boundary:

* accountability does not execute escalation
* accountability does not execute incident workflows
* accountability does not execute interventions
* accountability does not run a workflow engine
* accountability does not call external APIs
* accountability does not mutate operational history
* accountability does not call AI

Unresolved accountability questions:

* exact operator role and permission model once authentication exists
* whether critical escalations require two-person approval or supervisor acknowledgement
* whether escalation/incident records need dedicated immutable tables
* how accountability records should surface in the future office UI
* how Water Emergency accountability should diverge from the standard path

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

---

Phase 0 Module 23 Operational Dashboard Read Models

The dispatch pipeline now has a read-only dashboard projection boundary for future admin/API consumption.

Current dashboard read models summarize:

* operational overview counts
* dispatch lifecycle counts
* Manual Review blocker and escalation indicators
* Route Assignment state
* external adapter/execution/confirmation state
* reconciliation and recovery-preparation state
* governance and accountability state
* immutable operational event timeline entries
* audit correlation references

Safety boundary:

* dashboard read models do not mutate ORM objects
* dashboard read models do not execute dispatch
* dashboard read models do not trigger integrations
* dashboard read models do not run AI
* dashboard read models do not resolve Manual Review
* dashboard read models do not infer hidden lifecycle transitions
* dashboard API routes are read-only and expose contracts for future UI work only

Unresolved dashboard questions:

* exact filtering and pagination requirements for office dashboard views
* whether lifecycle counts should default to target date, route date, or all visible records
* how Water Emergency dashboard views should differ from standard dispatch views
* exact operator role visibility once authentication exists
* whether dashboard snapshots need caching or materialized views in production

---

Phase 0 Module 24 Frontend Dashboard Consumer

The dispatch pipeline now has an initial read-only admin dashboard frontend consumer.

Frontend display scope:

* operational overview counts
* lifecycle summary counts
* Manual Review safety indicators
* route assignment summary
* external execution evidence
* reconciliation and recovery-preparation indicators
* governance and accountability indicators
* operational event timeline preview
* Water Emergency separation signals exposed by the backend read model

Safety boundary:

* frontend components do not own workflow logic
* frontend components do not infer hidden lifecycle transitions
* frontend components do not execute dispatch
* frontend components do not resolve Manual Review
* frontend components do not call integrations
* frontend components do not call AI
* frontend fallback data is only for local layout verification and is visibly marked as fallback state

Unresolved frontend/pipeline questions:

* whether office users need separate dispatch, review, recovery, and governance pages or one consolidated dashboard
* exact refresh cadence for active dispatch operations
* role-scoped visibility once authentication exists
* dedicated Water Emergency dashboard workflow design
* production filters for route date, region, technician, and branch

---

Phase 0 Module 25 Frontend Dashboard Visual QA Pass

The frontend dashboard consumer received its first visual QA and polish pass without changing dispatch workflow authority.

Polish scope:

* operational health summary added before detailed dashboard sections
* read-only and fallback notices balanced for desktop and mobile layouts
* safety, blocker, dispatch-ready, and Water Emergency signals made easier to scan
* responsive navigation verified at desktop, laptop, and mobile widths
* dashboard tests expanded to confirm no operational action controls are rendered
* API client tests expanded to confirm dashboard helpers remain `GET`-only

Safety boundary:

* no dispatch actions
* no Manual Review approve/reject actions
* no integration execution controls
* no AI action controls
* no hidden lifecycle inference
* no mutation API calls from the frontend

Unresolved frontend/pipeline questions:

* final office dashboard navigation model once more pages exist
* whether the operational health summary should become role-specific after authentication
* exact stale-data and refresh behavior for active office use
* dedicated Water Emergency dashboard screen design

---

Phase 0 Module 26 Full-Stack Dashboard Integration Verification

The dashboard consumer now has a documented local full-stack integration path.

Integration scope:

* backend dashboard endpoints verified through read-only contract tests
* frontend dashboard API base URL documented for local development
* frontend fallback behavior tested for unavailable backend state
* frontend verification script added for lint, typecheck, test, and build bundle
* local workflow documented for running FastAPI and Next.js together

Safety boundary:

* frontend still performs only read-only dashboard `GET` calls
* frontend still does not execute dispatch
* frontend still does not resolve Manual Review
* frontend still does not call integrations
* frontend still does not call AI
* fallback data remains visibly marked and cannot become operational authority

Unresolved integration questions:

* local PostgreSQL seed-data workflow for dashboard demos
* production reverse-proxy route shape between Apache, Next.js, and FastAPI
* future CORS rules if dashboard reads move from server-side Next.js to browser/client components
* dashboard stale-data and refresh behavior

---

Phase 0 Module 27 Local PostgreSQL Live Dashboard Verification

The dashboard integration now has a local PostgreSQL-backed verification path.

Verification scope:

* local development database documented as `acs_fsm_dev`
* Alembic migration workflow documented before live dashboard endpoint checks
* optional synthetic dashboard seed data added for read-model demo state
* backend endpoint checker added for health and dashboard `GET` endpoints
* frontend live-backend label clarified for successful backend reads

Safety boundary:

* dashboard endpoints remain read-only
* seed data is local-development-only and source-labeled
* seed data does not execute dispatch or imply production state
* no vendor adapters are executed
* no replay, rollback, reconciliation, governance, or escalation action is executed
* no AI controls or AI-generated authority are introduced

Unresolved integration questions:

* local PostgreSQL installation is still outside the repository
* whether future integration tests should use a disposable PostgreSQL database
* production database provisioning and migration rollout strategy
* dashboard refresh and stale-data rules for office use

---

Phase 0 Module 46 Manual Review Command Contract Boundary

Manual Review command-contract metadata is intentionally outside the dispatch execution path.

Dispatch boundary:

* command-contract labels do not authorize dispatch
* future Manual Review commands remain currently non-executable
* Water Emergency-related command contracts require Water Emergency scope checks and do not enter standard dispatch action preparation
* audit-envelope requirements are future action prerequisites, not dispatch instructions
* no dispatch execution, vendor call, approval action, auth/RBAC, or workflow engine behavior is added

Future dispatch-facing work may consume reviewed Manual Review outcomes only after authenticated action modules exist and preserve Manual Review authority.

---

Phase 0 Module 47 Manual Review Audit-Ledger Dry-Run Boundary

Manual Review audit-ledger dry-run metadata is intentionally outside the dispatch execution path.

Dispatch boundary:

* dry-run labels do not authorize dispatch
* future Manual Review commands remain currently non-executable and Phase 0 blocks execution
* Water Emergency-related dry-runs require Water Emergency scope checks and do not enter standard dispatch action preparation
* proposed future event type/state, audit envelope fields, idempotency scope, immutable-event requirements, and consistency checks are preparation metadata only
* no dispatch execution, vendor call, approval action, audit write, auth/RBAC, or workflow engine behavior is added

Future dispatch-facing work may consume reviewed Manual Review outcomes only after authenticated action modules and durable audit/event persistence exist.
