# ACS FSM — Core Data Model

## Purpose

This note captures the pre-implementation domain model understanding for the first ACS FSM module.

The model should support the Dispatch Operations Engine now and future FSM modules later.

---

## Core Principle

A job is not always the same thing as a visit.

Standard cleaning work is usually one job with one visit. Water Emergency work is usually one long-lived job with many visits, multiple technician actions, and equipment lifecycle concerns.

---

## Initial Entities

## Customers

Represents the person, business, property manager, apartment complex, insurance contact, or organization requesting service.

Prepare for:

- customer name
- company name
- phone and email
- billing or property manager contact
- tags such as commercial, VIP, recurring, insurance, or do-not-service
- future service history

## Properties

Represents the physical service location.

Prepare for:

- street address
- unit or apartment number
- building number
- city, state, ZIP
- property name
- access notes
- gate code
- parking notes
- service history

Keep customer/account identity separate from physical service location.

## Jobs

Represents requested work.

Prepare for:

- job type
- job status
- requested date
- scheduled date
- customer
- property
- source system
- source event ID
- priority
- review status
- operational notes

Jobs created from intake must preserve traceability to the approved intake processing record through a job creation record. Standard jobs created by the Phase 0 foundation start as `awaiting_dispatch`; creation does not mean routing or dispatch has happened.

## Work Orders

Represents operational instructions sent to technicians.

Prepare for:

- work order number
- related job
- assigned technician or technicians
- required forms
- required equipment or notes
- dispatch status
- completion status
- technician-facing notes

Work Orders generated from standard jobs must preserve intake/job creation traceability and start as scheduling-ready records. Work Order generation does not assign technicians, schedule exact times, route work, or dispatch work.

## Visits

Represents one technician interaction at a property on a date/time.

Prepare for:

- related job
- visit date
- visit type
- technician or technicians
- arrival and completion times
- visit notes
- photos in future
- moisture readings in future
- equipment actions in future
- visit status

Visits generated from Work Orders must preserve Work Order linkage and generation evidence. A generated Visit starts awaiting assignment; technician assignment, exact scheduling, routing, and dispatch remain future workflow steps.

Visit assignment and scheduling preparation should persist readiness snapshots before future dispatch execution. These snapshots should record eligibility, assignment blockers, technician compatibility context, AM/PM scheduling preference, service-state markers, and operational readiness without assigning a technician or setting exact schedule times.

Visit routing and dispatch preparation should persist readiness snapshots before future dispatch execution. These snapshots should record routing blockers, technician readiness, assignment evidence, scheduling evidence, dispatch eligibility, dispatch blockers, and lifecycle state without creating route assignments, optimizing routes, or executing dispatch.

## Technicians

Represents field workers and future technician app users.

Prepare for:

- name
- phone and email
- active/inactive status
- skills and specialties
- service areas
- vehicle or truck
- FastField user mapping
- future GPS/Verizon mapping

## Route Assignments

Represents routing decisions for a route date.

Prepare for:

- route date
- technician
- route order
- job or visit reference
- estimated drive time
- estimated arrival time
- region
- AM/PM designation
- route status
- route grouping key
- dispatch authorization readiness
- dispatch execution boundary
- dispatch execution state
- dispatch lifecycle snapshot
- dispatch audit snapshot
- dispatched timestamp
- external adapter state
- external adapter payload and evidence snapshots
- external adapter prepared timestamp
- external execution state
- external execution provider, evidence, failure, lifecycle, and audit snapshots
- external execution started, completed, and failed timestamps
- external confirmation state
- external confirmation, failure, retry, and reconciliation snapshots
- external confirmation and recovery timestamps
- dispatch reconciliation state
- consistency, divergence, mismatch, blocker, and reconciliation audit snapshots
- reconciliation prepared, consistency verified, and reconciliation blocked timestamps
- replay/recovery state
- replay preparation, rollback preparation, replay eligibility, replay blocker, recovery coordination, and replay audit snapshots
- replay prepared, rollback prepared, and replay blocked timestamps
- governance state
- governance approval, intervention authorization, replay authorization, rollback authorization, reconciliation approval, blocker, and audit snapshots
- governance approved, rejected, intervention-required, and blocked timestamps
- accountability state
- escalation preparation, incident preparation, accountability evidence, escalation blocker, intervention escalation, operational incident, and accountability audit snapshots
- escalation-required, incident-prepared, critical-intervention-required, and accountability-blocked timestamps
- deterministic route assignment evidence

Route assignments created by the authorization foundation represent prepared, authorized operational boundaries only. Module 14 dispatch execution can move authorized standard route assignments to `dispatched` internally. Module 15 adapter preparation can create external payload evidence. Module 18 controlled external adapter execution can record provider execution evidence without calling live vendor APIs. Module 16 confirmation and recovery preparation can record simulated confirmation, failure, retry-preparation, and reconciliation evidence. Module 19 reconciliation preparation can verify consistency and classify divergence without executing reconciliation. Module 20 replay/recovery preparation can prepare replay, rollback, and recovery-coordination evidence without executing replay or rollback. Module 21 governance can record operator approval and intervention authorization evidence without executing the governed action. Module 22 accountability can record escalation and incident-preparation evidence without executing escalation or incident workflows. This still does not mean route optimization has run or production external systems have been updated.

## Water Emergency Records

Water Emergency is first-class workflow data, not just a job type.

Prepare for:

- related job
- lifecycle status
- drying stage
- next required action
- equipment onsite flag
- moisture tracking readiness
- visit history
- open/closed status

## Equipment

Detailed inventory can come later, but the model should not block it.

Prepare for future:

- extractors
- air movers
- dehumidifiers
- moisture meters
- truckmounts
- air duct equipment
- dryer vent equipment
- LVT equipment
- equipment left onsite

## Manual Review Items

Represents a blocked or risky operational item needing human review.

Prepare for:

- related job, visit, route, or export action
- reason code
- confidence score
- source data snapshot
- recommended action
- operator decision
- resolution timestamp

## Audit Logs

Represents durable trace history.

Log important actions:

- imports
- normalization
- validation warnings
- classification decisions
- review decisions
- route generation
- spreadsheet export
- FastField preview/send
- status changes
- operator overrides

## Operational Event History

Represents immutable operational lifecycle and execution history.

Prepare for:

- lifecycle transition events
- dispatch execution events
- external adapter preparation events
- confirmation and failure recovery events
- retry-preparation events
- reconciliation-preparation events
- route-assignment timelines
- Visit timelines
- audit-correlation continuity
- deterministic duplicate event prevention
- future forensic/debugging workflows

Operational event history is append-only evidence. It must not execute workflows, replace Manual Review, mutate lifecycle state, call integrations, run analytics/replay engines, or call AI.

## Job Creation Records

Represents the controlled transition from an approved intake processing record into a standard operational job.

Prepare for:

- related intake processing record
- related created job
- review item linkage when present
- creation lifecycle state
- audit correlation ID
- intake snapshot
- orchestration snapshot
- dispatch eligibility snapshot
- review linkage snapshot
- deterministic evidence snapshot
- creation snapshot
- duplicate creation prevention

Job creation records should make intake-to-job transitions traceable without executing dispatch, routing technicians, creating visits/work orders, or bypassing Manual Review.

## Work Order And Visit Generation

Represents the controlled transition from a standard operational job into technician-facing execution structures.

Prepare for:

- job-to-work-order linkage
- job creation record linkage
- work-order-to-visit linkage
- audit correlation continuity
- intake/orchestration/dispatch eligibility evidence on Work Orders
- deterministic evidence snapshots
- review linkage snapshots
- generation snapshots
- scheduling-ready lifecycle states
- duplicate generation prevention

The standard path is intentionally separated from Water Emergency. Water Emergency work will need its own generation rules because it may require multiple visits, equipment lifecycle actions, and long-lived workflow state.

## Assignment And Scheduling Preparation

Represents the deterministic readiness layer between generated Visits and future routing/dispatch.

Prepare for:

- assignment eligibility
- assignment-required state
- technician active/inactive validation
- technician skills, service areas, vehicle, and availability context
- scheduling readiness
- AM/PM schedule-window preference
- lifecycle blockers
- review blockers
- Water Emergency assignment separation
- future multi-technician compatibility
- future vehicle/routing compatibility

This layer must not assign technicians, set scheduled times, route work, dispatch work, sync calendars, or call integrations.

## Routing And Dispatch Preparation

Represents the deterministic readiness layer between prepared Visits and future dispatch execution.

Prepare for:

- routing readiness
- routing blockers
- technician readiness snapshots
- Visit dispatch readiness
- dispatch eligibility
- dispatch blockers
- assignment readiness evidence
- scheduling readiness evidence
- audit correlation continuity
- future route optimization evidence

This layer must not optimize routes, create route assignments, execute dispatch, sync calendars, update technician mobile workflows, call integrations, or call AI.

## Route Assignment And Dispatch Authorization

Represents the deterministic boundary between dispatch-ready Visits and future dispatch execution.

Prepare for:

- route grouping foundation
- route assignment readiness
- technician route compatibility
- dispatch authorization readiness
- execution authorization state
- route blockers and dispatch blockers
- audit correlation continuity
- future route optimization handoff

This layer may create a prepared `RouteAssignment` in `awaiting_dispatch_execution`, but it must not execute dispatch, optimize routes, call integrations, sync calendars, update technician mobile workflows, or call AI.

## Dispatch Execution

Represents the deterministic internal lifecycle transition from dispatch-authorized route assignment to dispatched standard work.

Prepare for:

- dispatch execution state
- execution blocker reasons
- lifecycle transition evidence
- Route Assignment, Visit, Work Order, Job, technician, and audit-correlation traceability
- duplicate dispatch prevention
- future confirmation and failure timestamps
- future external adapter outcome linkage

This layer may update internal ACS records to `dispatched` after deterministic blockers pass. It must not call FastField, sync Google Calendar, write Sheets, update technician mobile workflows, run background workers, execute external APIs, optimize routes, or call AI.

## External Dispatch Adapter Preparation

Represents the deterministic boundary between internal dispatch execution and future vendor/mobile integration execution.

Prepare for:

- adapter execution request snapshots
- adapter lifecycle state
- FastField standard dispatch payload preparation
- Google Sheets dispatch export payload preparation
- Google Calendar dispatch sync payload preparation
- technician mobile sync payload preparation
- external adapter audit evidence
- duplicate adapter preparation prevention
- future external execution failure and confirmation evidence

This layer may prepare payload snapshots after internal dispatch execution completes. It must not call FastField, sync Google Calendar, write Sheets, update technician mobile workflows, run background workers, execute external APIs, optimize routes, or call AI.

## External Adapter Execution

Represents the deterministic boundary between prepared external payloads and future live provider execution.

Prepare for:

- external execution request snapshots
- provider execution result snapshots
- FastField execution preparation
- Google Sheets execution preparation
- Google Calendar execution preparation
- technician mobile sync preparation
- provider correlation continuity
- external execution failure evidence
- external execution audit evidence
- duplicate execution prevention

This layer may process prepared payloads and store controlled provider execution evidence. It must not call FastField, sync Google Calendar, write Sheets, update technician mobile workflows, run background workers, execute real vendor APIs, execute retries, optimize routes, or call AI.

## External Execution Confirmation And Recovery

Represents the deterministic boundary between prepared external adapter payloads and future external execution outcomes.

Prepare for:

- external confirmation lifecycle state
- external confirmation evidence snapshots
- external failure evidence snapshots
- retry preparation snapshots
- reconciliation-required snapshots
- confirmation audit evidence
- duplicate confirmation prevention
- future vendor confirmation status mapping

This layer may process simulated external confirmation states and store confirmation, failure, retry-preparation, or reconciliation-preparation evidence. It must not call external APIs, execute retries, run reconciliation engines, update technician mobile workflows, run background workers, optimize routes, or call AI.

## Dispatch Reconciliation And Operational Consistency

Represents deterministic consistency verification across internal lifecycle, external execution, external confirmation, and immutable event history evidence.

Prepare for:

- consistency verification results
- operational divergence tracking
- mismatch classification evidence
- reconciliation blocker evidence
- reconciliation audit evidence
- manual-resolution preparation
- duplicate reconciliation prevention
- immutable event history protection

This layer may verify consistency and prepare reconciliation evidence. It must not execute reconciliation, mutate operational event history, replay workflows, call external APIs, execute retries, run analytics engines, update technician mobile workflows, run background workers, optimize routes, or call AI.

## Operational Replay And Recovery Preparation

Represents deterministic replay-preparation, rollback-preparation, and recovery-coordination evidence after reconciliation, retry, or failure context exists.

Prepare for:

- replay eligibility evidence
- replay blocker evidence
- rollback preparation snapshots
- recovery coordination snapshots
- reconciliation replay preparation
- retry replay preparation
- immutable replay evidence
- replay/recovery audit evidence
- duplicate replay preparation prevention

This layer may prepare replay and rollback evidence for later operator-controlled recovery workflows. It must not execute replay, execute rollback, mutate operational event history, call external APIs, execute retries, run reconciliation engines, update technician mobile workflows, run background workers, optimize routes, or call AI.

## Operational Governance And Approval Control

Represents deterministic operator approval, manual intervention authorization, and governance evidence for future enterprise workflows.

Prepare for:

- governance approval result evidence
- intervention authorization evidence
- replay authorization evidence
- rollback authorization evidence
- reconciliation approval evidence
- governance blocker reasons
- operator decision traceability
- immutable governance audit evidence
- duplicate approval prevention

This layer may record operator approval or intervention authorization for later controlled execution. It must not execute replay, execute rollback, execute reconciliation, mutate operational event history, call external APIs, run workflow engines, update technician mobile workflows, run background workers, optimize routes, or call AI.

## Operational Accountability, Escalation, And Incident Coordination

Represents deterministic escalation preparation, incident preparation, intervention escalation, and accountability evidence for future enterprise coordination workflows.

Prepare for:

- escalation result evidence
- incident preparation result evidence
- accountability evidence
- escalation blocker evidence
- intervention escalation evidence
- operational incident evidence
- immutable accountability audit evidence
- duplicate escalation prevention

This layer may record accountability, escalation, or incident-preparation evidence for later operator-controlled coordination. It must not execute escalations, execute incident workflows, execute interventions, mutate operational event history, call external APIs, run workflow engines, update technician mobile workflows, run background workers, optimize routes, or call AI.

---

## Phase 0 Module 2 Model Refinements

The Module 2 backend model pass refined only fields and relationships already supported by the documented ACS domain model.

Decisions:

- Customers include flexible billing and property manager contact fields plus tags. Full CRM contact records are deferred.
- Work orders and visits support multiple assigned technicians through association tables. The existing single technician reference remains available for primary assignment compatibility until operations confirms the exact assignment semantics.
- Technicians include vehicle/truck context and a flexible availability status. No fixed availability state machine has been implemented yet.
- Route assignments include estimated drive time minutes in addition to estimated arrival time.
- Manual Review items keep direct job, visit, and route links and also include a generic entity target for future export actions or other reviewable operations.
- Audit logs timestamp events by default so trace records are durable even before full workflow services exist.

No workflow logic, CRUD behavior, auth behavior, integration behavior, or Water Emergency stage automation was added in Module 2.

---

## Initial Status Concepts

Suggested statuses to refine with operations:

- NEW
- SCHEDULED
- NEEDS_MANUAL_REVIEW
- POSSIBLE_CANCELLATION
- CANCELLED
- READY_TO_ROUTE
- ROUTED
- READY_FOR_SHEET
- WRITTEN_TO_SHEET
- READY_FOR_FASTFIELD
- SENT_TO_FASTFIELD
- IN_PROGRESS
- ON_HOLD
- FOLLOW_UP_REQUIRED
- COMPLETED
- FAILED

Water Emergency-specific statuses may include:

- NEW_WATER_EMERGENCY
- INITIAL_VISIT_DISPATCHED
- DRYING_IN_PROGRESS
- MOISTURE_CHECK_NEEDED
- TREATMENT_NEEDED
- READY_FOR_PICKUP
- PICKUP_SCHEDULED
- READY_TO_CLOSE
- CLOSED

---

## Constraints To Confirm With Operations

- complete ACS job/service taxonomy
- exact Water Emergency stages and closure rules
- which jobs require different forms or technician skills
- whether Water Emergency routing is mixed or separate
- exact Google Sheet layout compatibility requirements
- exact FastField forms and approval requirements
- cancellation confidence behavior
- next-day vs next-business-day processing rules
- whether customer billing and property manager contacts need structured person records or flexible text fields are sufficient for the first dispatch module
- how ACS wants to distinguish primary technician, helper technician, crew lead, and reassigned technician on work orders and visits
- whether route drive-time estimates should come from Verizon Connect, a mapping provider, operator entry, or internal calculation
