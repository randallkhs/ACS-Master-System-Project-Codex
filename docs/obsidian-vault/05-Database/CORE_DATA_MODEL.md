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
