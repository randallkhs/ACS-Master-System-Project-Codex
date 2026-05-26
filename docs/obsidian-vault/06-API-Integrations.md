# ACS FSM — API Integrations

## Purpose

This file records the integration philosophy and known adapter boundaries for ACS FSM.

---

## Adapter Rule

All external systems must be isolated behind adapters.

The core ACS FSM platform should use internal domain models and services, not vendor-specific data structures.

---

## Initial Integrations

## Google Calendar

Role: schedule input adapter.

Initial use:

- import target-date jobs
- preserve source event IDs
- normalize freeform event data into structured internal records

Google Calendar is not the source of truth after import.

## Google Sheets

Role: transitional dispatch output adapter.

Initial use:

- preserve existing operational sheet compatibility
- preview before write
- support AppleJobs and Water Emergency output separation

Long-term goal: replace spreadsheet dependence with database-driven UI.

## FastField

Role: transitional work-order/dispatch adapter.

Initial use:

- support current standard-job dispatch
- support separate Water Emergency workflow/form requirements
- preview before send

Critical rule: never send Water Emergency jobs through the regular FastField work-order path.

Long-term goal: replace FastField with native ACS technician workflows.

## Verizon Connect

Role: future vehicle/GPS adapter.

Future use:

- technician/vehicle location
- route visibility
- dynamic reassignment support

## AI Providers

Role: assistant and validation adapter.

Allowed use:

- classification suggestions
- anomaly detection
- confidence scoring support
- summarization

Forbidden use:

- operational authority
- silent dispatch
- auto-confirmed cancellation
- auto-closed Water Emergency workflows

See [[08-AI-Systems/AI_AUTOMATION_RULES]].

---

## Integration Safety Requirements

- Use environment variables or secure secret storage for credentials.
- Do not hardcode API keys or passwords.
- Log imports, exports, sends, failures, and operator approvals.
- Support preview/dry-run for risky outputs.
- Send uncertain records to Manual Review before external write/send.

## Phase 0 Module 15 External Adapter Boundary

External dispatch adapter preparation is deterministic and prepare-only.

Current payload foundations:

- FastField standard dispatch payload snapshot
- Google Sheets standard-job dispatch row snapshot
- Google Calendar dispatch-status sync snapshot
- technician mobile standard-visit sync snapshot

Rules:

- prepared payloads are evidence, not live sends
- external API calls remain `not_executed`
- Water Emergency work cannot use the standard adapter path
- blocked, review-required, unauthorized, undispatched, or duplicate-prepared records cannot reach adapter preparation
- future live adapters must write execution outcomes back to the database without becoming workflow authority

## Phase 0 Module 18 External Adapter Execution Boundary

External adapter execution is deterministic and controlled-execution-only.

Current provider foundations:

- FastField execution evidence snapshot
- Google Sheets execution evidence snapshot
- Google Calendar execution evidence snapshot
- technician mobile sync execution evidence snapshot
- provider correlation IDs and audit continuity

Rules:

- execution consumes prepared payloads awaiting external execution
- real provider API calls remain `not_executed`
- provider failures record failure evidence without automatic retry
- Water Emergency work cannot use the standard external execution path
- blocked, review-required, unauthorized, duplicate-attempt, adapter-unready, invalid-lifecycle, or missing-payload records cannot execute externally
- future live adapters must preserve these lifecycle and audit boundaries when replacing simulated provider execution internals

## Phase 0 Module 16 External Confirmation And Recovery Boundary

External confirmation and recovery preparation is deterministic and simulation-only.

Current outcome foundations:

- external confirmation success evidence
- external confirmation failure evidence
- retry preparation evidence
- reconciliation-required evidence
- confirmation audit evidence

Rules:

- confirmation processing consumes adapter-prepared records awaiting external confirmation
- external API calls remain `not_executed`
- retries are prepared only, not executed automatically
- reconciliation is prepared only, not executed automatically
- Water Emergency work cannot use the standard external confirmation path
- blocked, review-required, unauthorized, duplicate-confirmed, adapter-unready, or invalid-lifecycle records cannot reach confirmation
- future live adapters must write confirmation outcomes back to the database without becoming workflow authority

## Phase 0 Module 17 Operational Event History Boundary

Operational event history is deterministic and append-only.

Current event foundations:

- dispatch execution timeline events
- external adapter preparation timeline events
- external confirmation and failure timeline events
- retry-preparation timeline events
- reconciliation-required timeline events
- immutable audit evidence snapshots

Rules:

- event history records evidence only
- duplicate event fingerprints are blocked
- no live external API calls are made by event history
- event history does not execute retries or reconciliation
- event history does not become a workflow engine or analytics engine
- future live adapters should append confirmation/failure events while preserving database workflow authority

## Phase 0 Module 19 Dispatch Reconciliation Boundary

Dispatch reconciliation preparation is deterministic and evidence-only.

Current consistency foundations:

- internal dispatch lifecycle comparison
- external execution state comparison
- external confirmation state comparison
- retry/recovery mismatch classification
- immutable event-history protection
- reconciliation audit evidence

Rules:

- reconciliation preparation does not call external APIs
- reconciliation preparation does not execute reconciliation
- reconciliation preparation does not execute retries
- reconciliation preparation does not mutate operational event history
- Water Emergency work cannot use the standard reconciliation path
- blocked, review-required, unauthorized, duplicate, invalid-lifecycle, or mutable-history records cannot prepare standard reconciliation
- future live adapters and reconciliation workflows must preserve database workflow authority

## Phase 0 Module 20 Operational Replay And Recovery Boundary

Operational replay and recovery preparation is deterministic and evidence-only.

Current recovery foundations:

- replay eligibility evidence
- rollback preparation evidence
- recovery coordination evidence
- replay blocker evidence
- immutable replay audit evidence

Rules:

- replay preparation does not execute replay
- rollback preparation does not execute rollback
- external API calls remain `not_executed`
- automatic retries remain `not_executed`
- Water Emergency work cannot use the standard replay/recovery path
- blocked, review-required, unauthorized, duplicate, invalid-lifecycle, no-recovery-context, or mutable-history records cannot prepare standard replay/recovery
- future live recovery workflows must preserve database workflow authority and immutable event-history boundaries

## Phase 0 Module 21 Operational Governance Boundary

Operational governance and approval control are deterministic and evidence-only.

Current governance foundations:

- operator approval evidence
- manual intervention authorization evidence
- replay authorization evidence
- rollback authorization evidence
- reconciliation approval evidence
- governance audit evidence

Rules:

- governance approval does not execute replay, rollback, or reconciliation
- external API calls remain `not_executed`
- automatic approvals remain `not_executed`
- Water Emergency work cannot use the standard governance path
- blocked, review-required, unauthorized-operator, duplicate-approval, invalid-lifecycle, missing-operator, or mutable-history records cannot prepare standard governance
- future live enterprise workflows must preserve database workflow authority and immutable event-history boundaries

## Phase 0 Module 22 Operational Accountability Boundary

Operational accountability, escalation preparation, and incident preparation are deterministic and evidence-only.

Current accountability foundations:

- escalation preparation evidence
- incident preparation evidence
- intervention escalation evidence
- operational incident evidence
- accountability blocker evidence
- accountability audit evidence

Rules:

- accountability preparation does not execute escalation, incident workflows, or interventions
- external API calls remain `not_executed`
- automatic escalation and incident workflows remain `not_executed`
- replay/recovery escalation cannot bypass governance approval
- Water Emergency work cannot use the standard accountability path
- blocked, review-required, unauthorized, duplicate-escalation, invalid-lifecycle, missing-operator, missing-governance, no-context, or mutable-history records cannot prepare standard accountability
- future live enterprise coordination workflows must preserve database workflow authority and immutable event-history boundaries

## Phase 0 Module 23 Dashboard API Contract Boundary

The dashboard API foundation is read-only and backend-owned.

Current route contracts:

- `/api/v1/dashboard/overview`
- `/api/v1/dashboard/lifecycle`
- `/api/v1/dashboard/review`
- `/api/v1/dashboard/dispatch`

Rules:

- dashboard APIs expose read models only
- dashboard APIs do not mutate operational records
- dashboard APIs do not execute dispatch, replay, rollback, reconciliation, escalation, or incident workflows
- dashboard APIs do not call vendor integrations
- dashboard APIs do not call AI
- future frontend/admin dashboard code must consume these contracts instead of duplicating lifecycle or blocker logic

Open API concerns:

- filtering, sorting, and pagination have not been finalized
- authentication and role-scoped visibility are not implemented yet
- high-volume dashboard projections may later need explicit query optimization or materialized read models
- Water Emergency may need dedicated dashboard endpoints once its separated workflow path is implemented

## Phase 0 Module 24 Frontend Dashboard API Consumption Boundary

The frontend foundation consumes dashboard API contracts as read-only display data.

Current frontend API behavior:

- `ACS_DASHBOARD_API_BASE_URL` configures the backend origin for server-side dashboard reads
- the API client only defines `GET` helpers for `/api/v1/dashboard/overview`, `/api/v1/dashboard/lifecycle`, `/api/v1/dashboard/review`, and `/api/v1/dashboard/dispatch`
- local fallback data is typed against the backend dashboard contracts and clearly marked in the UI as mock/fallback state
- frontend components render response fields without performing lifecycle transitions, blocker decisions, dispatch execution, reconciliation execution, vendor calls, or AI calls

Frontend API constraints:

- no mutation calls
- no operational execution calls
- no vendor integration calls
- no Manual Review resolution calls
- no hidden lifecycle inference in UI components
- no frontend-owned workflow logic

Open API/frontend concerns:

- production authentication and role-scoped API visibility
- dashboard refresh cadence and stale-data indicators
- event timeline filtering, pagination, and sorting
- Water Emergency-specific dashboard API needs
- deployment path and reverse-proxy routing between the future Next.js frontend and FastAPI backend

## Phase 0 Module 25 Frontend Dashboard Contract Polish

The frontend polish pass preserved the Module 23 dashboard API boundary.

Confirmed frontend API behavior:

- dashboard client helpers remain read-only `GET` requests
- no `POST`, `PUT`, `PATCH`, or `DELETE` helpers were added
- fallback data remains typed local development data and is visibly marked in the UI
- production data still depends on environment-configured backend origin through `ACS_DASHBOARD_API_BASE_URL`
- visual polish does not add dispatch, review-resolution, reconciliation, integration, or AI execution calls

Open API/frontend concerns:

- role-scoped dashboard API access after authentication exists
- stale-data and refresh signaling
- timeline pagination and filtering
- Water Emergency-specific dashboard endpoints

## Phase 0 Module 26 Full-Stack Dashboard Integration Boundary

The frontend-to-backend dashboard integration remains read-only and environment-driven.

Local development behavior:

- backend expected origin: `http://127.0.0.1:8000`
- frontend expected origin: `http://127.0.0.1:3000`
- frontend server-side dashboard reads use `ACS_DASHBOARD_API_BASE_URL`
- frontend falls back to visibly labeled typed mock data when the backend is unavailable
- production must set an environment-specific HTTPS backend origin

Contract constraints:

- only dashboard `GET` requests are used
- no mutation methods are added
- no dispatch, review-resolution, reconciliation, integration, or AI execution calls are added
- backend dashboard routes remain the source of dashboard read-model truth

Open API/frontend concerns:

- production reverse-proxy routing and path prefixes
- role-scoped dashboard API access after auth exists
- dashboard refresh/stale-data behavior
- future CORS configuration if browser-side dashboard fetches are introduced

## Phase 0 Module 27 Local Live Dashboard API Verification

The local PostgreSQL workflow verifies dashboard APIs against persisted backend state without changing integration authority.

Local verification behavior:

- `make db-check` confirms the configured local database is reachable and migrated
- `make seed-dashboard` inserts synthetic local read-model data only after explicit developer confirmation
- `make dashboard-check` calls only health and dashboard `GET` endpoints
- frontend live mode remains driven by `ACS_DASHBOARD_API_BASE_URL`

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` dashboard calls are added
- no dispatch execution, vendor execution, replay, rollback, reconciliation, governance, escalation, or AI calls are added
- synthetic seed records must not be treated as provider/vendor execution evidence

Open API/local concerns:

- whether future live API verification should become a dedicated integration-test profile
- production API base URL and reverse-proxy path strategy
- production authentication and role-scoped dashboard visibility

## Phase 0 Module 30 Dashboard Storyboard API Consumption Boundary

The frontend scenario storyboard consumes the existing dashboard overview read model only.

Confirmed behavior:

- no backend dashboard API routes were added or changed
- the storyboard derives display groups from existing `GET /api/v1/dashboard/overview` response fields
- the API client remains read-only and environment-driven through `ACS_DASHBOARD_API_BASE_URL`
- live backend and mock fallback source indicators remain visually distinct
- synthetic local seed context is labeled as local verification context, not production data

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` dashboard calls are added
- no dispatch, review-resolution, replay, rollback, reconciliation, governance, escalation, vendor, or AI execution calls are added
- frontend grouping must not become lifecycle authority or infer hidden workflow transitions

Open API/frontend concerns:

- formal production scenario filtering may need backend-owned metadata rather than frontend grouping
- Water Emergency may need dedicated dashboard/storyboard contracts once its workflow path is implemented
- role-scoped dashboard visibility and refresh behavior remain future authentication/deployment decisions

## Phase 0 Module 31 Water Emergency Dashboard API Contract Boundary

The dashboard API now includes a dedicated Water Emergency read model:

- `/api/v1/dashboard/water-emergency`

Contract behavior:

- read-only `GET` endpoint only
- summarizes existing Water Emergency records and related persisted evidence
- exposes status/stage counts, open/closed counts, multi-visit indicators, equipment indicators, review/escalation indicators, related references, data gaps, audit correlations, and timeline entries
- remains separate from `/api/v1/dashboard/dispatch` so Water Emergency visibility is not treated as standard dispatch workflow authority

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` Water Emergency dashboard calls are added
- no Water Emergency creation, closure, resolution, approval, dispatch, vendor, or AI execution calls are added
- no FastField, Sheets, Calendar, Verizon Connect, or AI adapters are invoked
- frontend display must consume this backend contract instead of duplicating emergency lifecycle logic

Open API/frontend concerns:

- production Water Emergency filters, pagination, sorting, and timeline volume controls
- role-scoped visibility after authentication exists
- final emergency status/stage taxonomy and equipment/moisture data contracts

## Phase 0 Module 32 Water Emergency Detail API Contract Boundary

The dashboard API now includes a read-only Water Emergency detail read model:

- `/api/v1/dashboard/water-emergency/{water_emergency_id}`

Contract behavior:

- read-only `GET` endpoint only
- returns 404 when the selected Water Emergency record does not exist
- returns one selected record with related job, work-order, visit, Manual Review, audit, data-gap, and timeline evidence
- scopes Manual Review indicators to the selected record through persisted job, entity, or visit references
- keeps timeline entries as evidence, not executable workflow state

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` detail calls are added
- no Water Emergency edit, closure, resolution, approval, dispatch, vendor, or AI execution calls are added
- no hidden lifecycle transition is inferred from event evidence
- frontend detail display must consume the backend contract instead of creating emergency business logic

Open API/frontend concerns:

- production detail selection/navigation
- timeline pagination and filtering
- role-scoped evidence visibility
- future equipment, moisture, photo, and technician-note data contracts

## Phase 0 Module 33 Water Emergency Equipment And Visit Visibility Contract Boundary

The existing Water Emergency dashboard API contracts now include read-only equipment, visit-chain, and drying-stage visibility fields.

Contract behavior:

- `GET /api/v1/dashboard/water-emergency` exposes summary-level equipment context, visit-chain summary, and drying-stage summary
- `GET /api/v1/dashboard/water-emergency/{water_emergency_id}` exposes detail-level equipment notes/unknowns, visit-chain timing/status counts, and drying-stage context
- fields are derived only from persisted Water Emergency, Work Order, Visit, Review, and event evidence
- unknown indicators are explicit when equipment inventory or moisture-reading entities are not modeled
- Water Emergency visit-chain data remains separate from standard dispatch API authority

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` dashboard calls are added
- no Water Emergency equipment management, drying approval, closure, dispatch, vendor, or AI execution calls are added
- frontend display must consume the backend contract instead of deriving hidden emergency lifecycle state

Open API/frontend concerns:

- final Water Emergency status/stage taxonomy
- dedicated equipment inventory and moisture-reading API contracts
- production filtering, pagination, refresh cadence, and role-scoped detail visibility

## Phase 0 Module 34 Water Emergency Review And Alert Visibility Contract Boundary

The existing Water Emergency dashboard API contracts now include read-only review, exception, blocker, and critical-alert visibility fields.

Contract behavior:

- `GET /api/v1/dashboard/water-emergency` exposes summary-level review/exception counts, review reason buckets, blocker reason buckets, critical unresolved counts, escalation indicators, review IDs, and audit references
- `GET /api/v1/dashboard/water-emergency/{water_emergency_id}` exposes detail-level review/exception context scoped to the selected Water Emergency record
- fields are derived only from persisted Water Emergency, Visit, Review, and event evidence
- generic Water Emergency review labels may inform dashboard-level counts, but detail-level context depends on concrete job, entity, or visit linkage

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` dashboard calls are added
- no Manual Review approve/reject/resolve/archive calls are added
- no Water Emergency closure, dispatch, escalation execution, vendor, or AI execution calls are added
- frontend display must consume the backend contract instead of deriving hidden emergency review authority

Open API/frontend concerns:

- final Water Emergency review and escalation taxonomy
- typed exception/alert API contracts after operations confirms categories
- production filtering, pagination, refresh cadence, notification routing, and role-scoped review visibility

## Phase 0 Module 35 Water Emergency Readiness Contract Boundary

The existing Water Emergency dashboard API contracts now include read-only next-step readiness visibility fields.

Contract behavior:

- `GET /api/v1/dashboard/water-emergency` exposes summary-level readiness counts, label buckets, blocker/reason buckets, and per-record readiness previews
- `GET /api/v1/dashboard/water-emergency/{water_emergency_id}` exposes detail-level readiness labels, explanation text, review/critical/blocker/unknown counts, and evidence references
- fields are derived only from persisted Water Emergency, Work Order, Visit, Review, and event evidence
- closed/resolved records are represented as no-active-next-step visibility
- ready-for-close-review is represented as readiness evidence only and not as an execution instruction

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` dashboard calls are added
- no Manual Review approve/reject/resolve/archive calls are added
- no Water Emergency closure, dispatch, visit scheduling, drying approval, equipment pickup, vendor, or AI execution calls are added
- frontend display must consume the backend contract instead of deriving hidden emergency workflow state

Open API/frontend concerns:

- final Water Emergency readiness and closure taxonomy
- whether readiness should later become persisted workflow state or remain a read-model projection
- production filtering, pagination, refresh cadence, and role-scoped readiness visibility

## Phase 0 Module 36 Water Emergency Queue Contract Boundary

The existing Water Emergency dashboard API contract now includes read-only operator queue and attention visibility fields.

Contract behavior:

- `GET /api/v1/dashboard/water-emergency` exposes summary-level queue-group counts, attention-label counts, and per-record queue items
- queue items include Water Emergency ID, attention label, queue group, attention rank, readiness labels, reason codes, evidence references, review/critical/blocker/unknown counts, related job/work-order/visit IDs, and audit references
- fields are derived only from persisted Water Emergency, Work Order, Visit, Review, and event evidence through the existing readiness read model
- closed/resolved records are separated from active attention items
- critical-alert evidence sorts above lower-attention queue items

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` dashboard calls are added
- no Manual Review approve/reject/resolve/archive calls are added
- no Water Emergency closure, dispatch, visit scheduling, drying approval, equipment pickup, vendor, priority-engine, or AI execution calls are added
- frontend display must consume the backend queue contract instead of deriving hidden triage authority

Open API/frontend concerns:

- final Water Emergency triage, priority, and queue taxonomy
- whether queue labels should remain derived read-model projections or become persisted workflow state later
- production filtering, pagination, refresh cadence, stale-data handling, and role-scoped queue visibility

## Phase 0 Module 37 Water Emergency Aging Contract Boundary

The existing Water Emergency dashboard API contract now includes read-only aging, follow-up risk, stale evidence, and unknown timing visibility fields.

Contract behavior:

- `GET /api/v1/dashboard/water-emergency` exposes summary-level time-sensitivity label counts, age bucket counts, follow-up bucket counts, active timing risk counts, closed/resolved timing counts, stale-evidence counts, and per-record timing items
- timing items include Water Emergency ID, time-sensitivity label, timing group/rank, age and follow-up buckets, opened/closed/latest evidence timestamps, reason codes, missing timestamp indicators, stale indicator count, related job/work-order/visit IDs, audit references, and evidence references
- fields are derived only from persisted Water Emergency, Work Order, Visit, Review, and operational event evidence
- closed/resolved records are separated from active timing risks and must not appear as active overdue work
- missing timestamp evidence returns unknown timing rather than an invented SLA state

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` dashboard calls are added
- no Manual Review approve/reject/resolve/archive calls are added
- no Water Emergency closure, dispatch, visit scheduling, drying approval, equipment pickup, escalation execution, SLA engine, vendor, priority-engine, or AI execution calls are added
- frontend display must consume the backend timing contract instead of deriving hidden time-sensitive authority

Open API/frontend concerns:

- final Water Emergency aging, follow-up, stale-evidence, and SLA taxonomy
- whether timing labels should remain derived read-model projections or become persisted workflow state later
- production filtering, pagination, refresh cadence, stale-data handling, and role-scoped timing visibility

## Phase 0 Module 38 Water Emergency Filter/Sort Contract Boundary

The existing Water Emergency dashboard API contract now includes read-only filtering, sorting, grouping, and operator view-state metadata.

Contract behavior:

- `GET /api/v1/dashboard/water-emergency` exposes available filter options, sort options, group counts, and per-record view-state items
- view-state items include Water Emergency ID, filter groups, primary filter group, sort rank/label, queue group, attention label, time-sensitivity label, readiness label, active/closed state, current status/stage, review/critical/blocker/unknown counts, last-activity timestamp, related job/work-order/visit IDs, audit references, and evidence references
- fields are derived only from persisted Water Emergency, Work Order, Visit, Review, and operational event evidence through existing readiness, queue, and timing projections
- closed/resolved records are separated from active records in the contract so the frontend can keep them visible even when active lists are limited
- frontend filter and sort controls change only local display state

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` dashboard calls are added
- no Manual Review approve/reject/resolve/archive calls are added
- no Water Emergency closure, dispatch, visit scheduling, drying approval, equipment pickup, escalation execution, SLA engine, vendor, priority-engine, saved-view persistence, or AI execution calls are added
- frontend display must consume the backend view-state contract instead of deriving hidden workflow authority

Open API/frontend concerns:

- final Water Emergency filter, triage, and saved-view taxonomy
- whether filter metadata should remain derived read-model projections or become persisted user/role preferences later
- production pagination, refresh cadence, stale-data handling, role-scoped filter visibility, and saved default views

## Phase 0 Module 39 Water Emergency Governance And View Preference Contract Boundary

The existing Water Emergency dashboard API contract now includes read-only governance and result-window metadata.

Contract behavior:

- `GET /api/v1/dashboard/water-emergency` exposes Randall-authorized Phase 0 visibility baseline metadata
- governance metadata lists provisional filter groups, attention labels, timing labels, readiness labels, owner-review policy boundaries, and future role-visibility role names
- timing and follow-up labels are explicitly marked as conservative Phase 0 visibility heuristics, not final SLA enforcement
- legal, insurance, warranty, drying certification, customer-facing, compliance, or company-liability policy boundaries are marked as requiring Alfonso owner review
- result-window metadata exposes total count, visible count, result limit, `has_more`, sort key, and generated timestamp for future pagination/query scaling readiness
- frontend saved view preferences are local browser state only and are not sent to this API

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` dashboard calls are added
- no auth, RBAC, saved-view backend persistence, workflow execution, SLA enforcement, vendor execution, or AI execution is added
- no final legal, insurance, compliance, warranty, drying certification, or customer-facing policy is finalized in the API contract
- frontend display must consume backend governance metadata without turning view-state into workflow authority

Open API/frontend concerns:

- future authenticated saved view preference API, if ACS needs account-level preferences
- production pagination/query parameters once Water Emergency volume requires them
- role-scoped visibility and evidence restrictions after authentication exists
- Alfonso owner-review checklist for formal policy language that may create company liability

## Phase 0 Module 40 Manual Review Queue Contract Boundary

The dashboard API now includes a dedicated read-only Manual Review queue detail contract.

Contract behavior:

- `GET /api/v1/dashboard/manual-review/queue` exposes detailed Manual Review queue visibility.
- queue items include Review Item ID, status, severity, reason code, visibility groups, primary group, entity type/ID, job/work-order/visit/route-assignment IDs, Water Emergency ID when specifically linked, timestamps, age bucket, blocker/attention indicators, confidence score, recommended action, audit-correlation ID, and evidence references.
- summary fields include status, reason, severity, visibility group, and age-bucket counts.
- Water Emergency-related reviews are separated from standard dispatch and other review items through concrete persisted linkage, not generic attachment.
- taxonomy metadata marks Manual Review queue groups as a Randall-authorized Phase 0 visibility baseline.

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` Manual Review queue calls are added
- no approve, reject, defer, archive, resolve, dispatch, vendor, or AI calls are added
- queue labels are internal software visibility groups only, not final Manual Review workflow action authority
- no legal, insurance, compliance, or company-liability policy is finalized in this contract

## Phase 0 Module 41 Manual Review Detail Contract Boundary

The dashboard API now includes a read-only Manual Review detail contract.

Contract behavior:

- `GET /api/v1/dashboard/manual-review/queue/{review_item_id}` exposes one selected Manual Review item.
- detail responses include the review queue item, reason/evidence context, linked entity context, data-gap counts, audit-correlation IDs, taxonomy metadata, and related operational timeline evidence.
- linked entity context may include job, work order, visit, route assignment, and Water Emergency references when those references exist in persisted backend data.
- Water Emergency-related Manual Review details remain separated from standard dispatch review details.
- missing review items return `404` from the live backend; the frontend does not replace live 404 responses with mock detail data.

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` Manual Review detail calls are added
- no approve, reject, defer, archive, resolve, dispatch, vendor, or AI calls are added
- detail visibility is internal Phase 0 investigation context only, not action authority or final business policy

Open API/frontend concerns:

- future authenticated Manual Review action endpoints
- final Manual Review reason/action taxonomy
- role-scoped review visibility after auth/RBAC exists
- production pagination/query parameters once review queue volume requires them

## Phase 0 Module 42 Manual Review Filter/Sort And View Preference Contract Boundary

The Manual Review queue API contract now includes read-only filter/sort metadata and result-window metadata for frontend view-state.

Contract behavior:

- `GET /api/v1/dashboard/manual-review/queue` exposes available filter options, sort options, and result-window metadata alongside queue items.
- filter options include all, open, deferred, resolved, archived, active attention, Water Emergency-related, dispatch-related, missing data, duplicate/conflict, cancellation/status uncertainty, and needs operator review.
- sort options are informational read-only choices for frontend view-state: attention priority, newest first, and status/reason ordering.
- result-window metadata exposes total count, visible count, result limit, `has_more`, sort key, and generated timestamp for future pagination/query scaling readiness.
- frontend saved view preferences are browser-local state only and are not sent to the backend API.

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` Manual Review calls are added
- no approve, reject, defer, archive, resolve, dispatch, vendor, AI, auth, RBAC, backend preference persistence, or workflow execution calls are added
- filter/sort metadata changes only dashboard visibility and must not imply operational approval, closure, rejection, dispatch, or escalation

Open API/frontend concerns:

- future authenticated Manual Review action endpoints
- final Manual Review filter/action taxonomy
- role-scoped review visibility after auth/RBAC exists
- future backend-persisted saved preferences if ACS needs account-level saved views
- production pagination/query parameters once review queue volume requires them

## Phase 0 Module 43 Manual Review Decision-Readiness Contract Boundary

The Manual Review queue and detail API contracts now include read-only decision-readiness metadata for operator-safe investigation context.

Contract behavior:

- `GET /api/v1/dashboard/manual-review/queue` exposes decision-readiness counts and each queue item's readiness label, summary, reason codes, evidence references, active-decision flag, and resolution-candidate flag.
- `GET /api/v1/dashboard/manual-review/queue/{review_item_id}` exposes the selected review item's same decision-readiness context alongside reason/evidence, linked entity, and timeline evidence.
- readiness labels include needs operator review, needs missing information, needs entity context, needs Water Emergency review, needs dispatch review, ready for operator decision, ready for resolution review, blocked by conflict, blocked by missing data, resolved or archived, and unknown readiness where deterministically supported.
- Water Emergency-related readiness remains separated through persisted entity/job/visit/Water Emergency links.
- resolved and archived review records return historical readiness instead of active action needs.

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` Manual Review calls are added
- no approve, reject, defer, archive, resolve, dispatch, vendor, AI, auth, RBAC, backend preference persistence, or workflow execution calls are added
- readiness labels are Randall-authorized Phase 0 visibility baselines only and must not imply operational approval, closure, rejection, dispatch, escalation, legal policy, or company-liability policy

Open API/frontend concerns:

- future authenticated Manual Review action endpoints
- final Manual Review readiness/action taxonomy
- role-scoped review visibility after auth/RBAC exists
- future action history, resolution outcome, and audit identity requirements

## Phase 0 Module 44 Manual Review Action-Preflight Contract Boundary

The Manual Review queue and detail API contracts now include read-only action-preflight metadata for future action module preparation.

Contract behavior:

- `GET /api/v1/dashboard/manual-review/queue` exposes action-preflight counts and each queue item's preflight label, summary, blocker codes, future requirement labels, evidence references, non-executable flag, operator-identity requirement flag, and audit-reason requirement flag.
- `GET /api/v1/dashboard/manual-review/queue/{review_item_id}` exposes the selected review item's same action-preflight context alongside decision-readiness, reason/evidence, linked entity, and timeline evidence.
- preflight labels include blocked by missing entity context, blocked by missing data, blocked by conflict, blocked by Water Emergency context, blocked by resolved or archived status, eligible for future operator decision, eligible for future resolution review, and unknown action eligibility where deterministically supported.
- future requirements such as auth, operator identity, and audit reason are informational only and are not implemented as controls.
- Water Emergency-related action preflight remains separated through persisted entity/job/visit/Water Emergency links.

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` Manual Review calls are added
- no approve, reject, defer, archive, resolve, dispatch, vendor, AI, auth, RBAC, backend preference persistence, or workflow execution calls are added
- action-preflight labels are Randall-authorized Phase 0 visibility baselines only and must not imply current action authority, legal policy, company-liability policy, or executable workflow state

Open API/frontend concerns:

- future authenticated Manual Review action endpoints
- final Manual Review action-preflight/action eligibility taxonomy
- operator identity, audit reason, action history, and outcome reason contracts
- role-scoped action visibility after auth/RBAC exists

## Phase 0 Module 45 Manual Review Future-Action Preview Contract Boundary

The Manual Review queue and detail API contracts now include read-only future-action preview metadata for later action module preparation.

Contract behavior:

- `GET /api/v1/dashboard/manual-review/queue` exposes future-action preview counts and each queue item's preview label, description, expected non-binding outcome summary, impacted entity references, blocker codes, future requirement labels, evidence references, non-executable flag, operator-identity requirement flag, and audit-reason requirement flag.
- `GET /api/v1/dashboard/manual-review/queue/{review_item_id}` exposes the selected review item's same future-action preview context alongside decision-readiness, action-preflight, reason/evidence, linked entity, and timeline evidence.
- preview labels include future approve, reject, defer, archive, resolve, request-information, operator-decision, missing-entity no-action, conflict-blocked no-action, Water Emergency no-action, resolved/archived no-action, and unknown preview states where deterministically supported.
- every preview is informational only and remains `is_currently_executable = false`.
- Water Emergency-related future-action preview remains separated through persisted entity/job/visit/Water Emergency links.

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` Manual Review calls are added
- no approve, reject, defer, archive, resolve, dispatch, vendor, AI, auth, RBAC, backend preference persistence, audit-action persistence, or workflow execution calls are added
- future-action preview labels are Randall-authorized Phase 0 visibility baselines only and must not imply current action authority, legal policy, company-liability policy, or executable workflow state

Open API/frontend concerns:

- future authenticated Manual Review action endpoints
- final Manual Review future-action preview/action taxonomy
- operator identity, audit reason, action history, impacted-entity audit, and outcome reason contracts
- role-scoped action visibility after auth/RBAC exists

## Phase 0 Module 46 Manual Review Command-Contract Boundary

The Manual Review queue and detail API contracts now include read-only future command-contract and audit-envelope metadata for later action module preparation.

Contract behavior:

- `GET /api/v1/dashboard/manual-review/queue` exposes command-contract counts and each queue item's command-contract label, summary, future command candidates, required contract labels, impacted entity references, blocker codes, evidence references, non-executable flag, not-executable reason, and future audit-envelope requirement flags.
- `GET /api/v1/dashboard/manual-review/queue/{review_item_id}` exposes the selected review item's same command-contract context alongside decision-readiness, action-preflight, future-action preview, reason/evidence, linked entity, and timeline evidence.
- command-contract labels include command-contract read-only phase, requires future auth, operator identity, role authorization, audit reason, idempotency key, preflight pass, entity context, no conflict blocker, Water Emergency scope check, immutable event recording, post-action consistency check, and command not executable Phase 0 where deterministically supported.
- every command contract is informational only and remains `is_currently_executable = false`.
- Water Emergency-related command contracts remain separated through persisted entity/job/visit/Water Emergency links.

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` Manual Review calls are added
- no approve, reject, defer, archive, resolve, dispatch, vendor, AI, auth, RBAC, backend preference persistence, audit-action persistence, idempotency persistence, or workflow execution calls are added
- command-contract labels are Randall-authorized Phase 0 visibility baselines only and must not imply current action authority, legal policy, company-liability policy, or executable workflow state

Open API/frontend concerns:

- future authenticated Manual Review command endpoints
- final Manual Review command/action taxonomy
- operator identity, role authorization, audit reason, idempotency, immutable event, post-action consistency, action history, impacted-entity audit, and outcome reason contracts
- role-scoped action visibility after auth/RBAC exists

## Phase 0 Module 47 Manual Review Audit-Ledger Dry-Run Boundary

The Manual Review queue and detail API contracts now include read-only audit-ledger dry-run metadata for later action module preparation.

Contract behavior:

- `GET /api/v1/dashboard/manual-review/queue` exposes audit-ledger dry-run counts and each queue item's dry-run label, summary, future command candidates, required labels, proposed future event type/state, proposed audit envelope fields, proposed idempotency scope, proposed consistency-check summary, evidence references, non-executable flag, Phase 0 execution-blocked flag, and future audit-envelope requirement flags.
- `GET /api/v1/dashboard/manual-review/queue/{review_item_id}` exposes the selected review item's same dry-run context alongside decision-readiness, action-preflight, future-action preview, command-contract, reason/evidence, linked entity, and timeline evidence.
- dry-run labels include dry-run only Phase 0, audit envelope required, operator identity required, role authorization required, idempotency key required, immutable event required, consistency check required, command execution blocked by read-only phase, missing entity, conflict, Water Emergency scope, resolved/archived status, and unknown dry-run readiness where deterministically supported.
- every dry-run record is informational only and remains `is_currently_executable = false` and `phase_allows_execution = false`.
- Water Emergency-related dry-runs remain separated through persisted entity/job/visit/Water Emergency links.

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` Manual Review calls are added
- no approve, reject, defer, archive, resolve, dispatch, vendor, AI, auth, RBAC, backend preference persistence, audit-action persistence, idempotency persistence, immutable event write, or workflow execution calls are added
- dry-run labels are Randall-authorized Phase 0 visibility baselines only and must not imply current action authority, legal policy, company-liability policy, audit-write behavior, or executable workflow state

Open API/frontend concerns:

- future authenticated Manual Review command endpoints
- final Manual Review dry-run/action taxonomy
- operator identity, role authorization, audit reason, idempotency, immutable event, post-action consistency, audit-ledger/action history, impacted-entity audit, and outcome reason contracts
- role-scoped action visibility after auth/RBAC exists

## Phase 0 Module 48 Manual Review Command-Validation Boundary

The Manual Review queue and detail API contracts now include read-only command-validation and safety-gate matrix metadata for later action module preparation.

Contract behavior:

- `GET /api/v1/dashboard/manual-review/queue` exposes command-validation counts and each queue item's validation label, validation status, candidate future command type, validation blockers, validation warnings, safety gates, evidence references, non-executable flag, Phase 0 execution-blocked flag, and future audit-envelope requirement flags.
- `GET /api/v1/dashboard/manual-review/queue/{review_item_id}` exposes the selected review item's same validation context alongside decision-readiness, action-preflight, future-action preview, command-contract, audit-ledger dry-run, reason/evidence, linked entity, and timeline evidence.
- validation labels include validation read-only phase, validation passes future requirements, missing entity, missing audit reason, missing operator identity, missing role authorization, missing idempotency key, missing immutable-event plan, missing consistency check, Water Emergency scope, resolved/archived status, conflict, warning requires review, and unknown validation state where deterministically supported.
- safety gates include entity context present, status allows future action, review not resolved/archived, Water Emergency scope checked, no conflict blocker, missing data reviewed, operator identity required, role authorization required, audit reason required, idempotency key required, immutable event required, post-action consistency check required, and phase allows execution.
- every validation record is informational only and remains `is_currently_executable = false`; the `phase_allows_execution` gate remains false in Phase 0.
- Water Emergency-related validation remains separated through persisted entity/job/visit/Water Emergency links.

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` Manual Review calls are added
- no approve, reject, defer, archive, resolve, dispatch, vendor, AI, auth, RBAC, backend preference persistence, audit-action persistence, idempotency persistence, immutable event write, command validation execution, or workflow execution calls are added
- validation labels and safety gates are Randall-authorized Phase 0 visibility baselines only and must not imply current action authority, legal policy, company-liability policy, audit-write behavior, or executable workflow state

Open API/frontend concerns:

- future authenticated Manual Review command endpoints
- final Manual Review validation/action taxonomy
- operator identity, role authorization, audit reason, idempotency, immutable event, post-action consistency, safety-gate persistence, audit-ledger/action history, impacted-entity audit, and outcome reason contracts
- role-scoped action visibility after auth/RBAC exists

## Phase 0 Module 49 Manual Review Operator-Identity And Permission-Readiness Boundary

The Manual Review queue and detail API contracts now include read-only operator-identity, role-authorization, and permission-readiness metadata for later auth/RBAC and action module preparation.

Contract behavior:

- `GET /api/v1/dashboard/manual-review/queue` exposes permission-readiness counts and each queue item's permission-readiness label, future command candidate, future required roles, future forbidden roles, future permission set, identity requirement labels, evidence references, non-executable flag, Phase 0 execution-blocked flag, and future audit/identity/RBAC requirement flags.
- `GET /api/v1/dashboard/manual-review/queue/{review_item_id}` exposes the selected review item's same permission-readiness context alongside decision-readiness, action-preflight, future-action preview, command-contract, audit-ledger dry-run, command validation, reason/evidence, linked entity, and timeline evidence.
- permission-readiness labels include permission read-only phase, requires future auth, requires operator identity, requires role authorization, reviewer/dispatcher/operations-manager/owner future role requirements, service account not allowed, technician action not allowed, unknown operator blocked, Water Emergency scope blocked, resolved/archived blocked, and ready-for-future-auth-phase where deterministically supported.
- every permission-readiness record is informational only and remains `is_currently_executable = false` and `phase_allows_execution = false`.
- Water Emergency-related authorization requirements remain separated through persisted entity/job/visit/Water Emergency links.

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` Manual Review calls are added
- no approve, reject, defer, archive, resolve, dispatch, vendor, AI, auth/RBAC enforcement, login/session/token behavior, auth headers, backend preference persistence, audit-action persistence, idempotency persistence, immutable event write, command validation execution, or workflow execution calls are added
- permission-readiness labels are Randall-authorized Phase 0 visibility baselines only and must not imply current action authority, legal policy, company-liability policy, audit-write behavior, role enforcement, or executable workflow state

Open API/frontend concerns:

- future authenticated Manual Review command endpoints
- final ACS-FSM auth provider, operator identity schema, role model, and permission taxonomy
- operator identity, role authorization, audit actor, audit reason, idempotency, immutable event, post-action consistency, safety-gate persistence, audit-ledger/action history, impacted-entity audit, and outcome reason contracts
- role-scoped action visibility after auth/RBAC exists

## Phase 0 Module 50 Manual Review Execution-Readiness Audit Boundary

The Manual Review queue API contract now includes a read-only execution-readiness audit, mutation-boundary lock, future transition prerequisite checklist, and owner-review guardrails for later action module preparation.

Contract behavior:

- `GET /api/v1/dashboard/manual-review/queue` exposes execution-readiness counts for active, resolved/archived, Water Emergency-related, dispatch-related, missing entity, conflict, missing data, future-preview, command-contract, dry-run, safety-gate, permission-readiness, Phase 0 blocked, and future auth/RBAC/audit/idempotency/immutable-event/consistency requirements.
- The queue response exposes mutation-boundary metadata: `manual_review_mutations_enabled = false`, `action_execution_phase = read_only_phase_0`, `currently_executable_count = 0`, `mutation_endpoints_available = false`, and future auth/RBAC/audit/idempotency/immutable-event/consistency requirements.
- The queue response exposes future transition prerequisites for auth provider selection, operator identity, role/permission approval, audit envelope approval, idempotency strategy, immutable event writing, rollback/replay, post-action consistency checks, Manual Review action contracts, frontend action UI review, ACSSDR report workflow, Review GUI/ChatGPT review, and Alfonso owner review where liability-sensitive actions are involved.
- Water Emergency-related execution-readiness remains separated through persisted entity/job/visit/Water Emergency links.

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` Manual Review calls are added
- no approve, reject, defer, archive, resolve, dispatch, vendor, AI, auth/RBAC enforcement, login/session/token behavior, auth headers, backend preference persistence, audit-action persistence, idempotency persistence, immutable event write, command validation execution, mutation boundary enforcement, or workflow execution calls are added
- execution-readiness labels are Randall-authorized Phase 0 visibility baselines only and must not imply current action authority, legal policy, company-liability policy, audit-write behavior, role enforcement, or executable workflow state

Open API/frontend concerns:

- future authenticated Manual Review command endpoints
- final ACS-FSM auth provider, operator identity schema, role model, and permission taxonomy
- approved audit envelope, idempotency, immutable event, rollback/replay, and post-action consistency strategies
- owner-reviewed legal, insurance, warranty, drying certification, formal policy, and financial action boundaries

## Phase 0 Module 51 Manual Review Auth-Boundary Readiness Boundary

The Manual Review queue and detail API contracts now include read-only auth-boundary readiness metadata for future operator identity, role catalog, and permission catalog preparation.

Contract behavior:

- `GET /api/v1/dashboard/manual-review/queue` exposes `auth_boundary_readiness` metadata with `auth_implemented = false`, `rbac_enforced = false`, `login_ui_available = false`, `action_execution_available = false`, `operator_identity_registry_available = false`, metadata-only operator registry mode, role catalog availability, permission catalog availability, service-account prohibition, and future auth/RBAC/audit-actor requirements.
- `GET /api/v1/dashboard/manual-review/queue/{review_item_id}` exposes the same auth-boundary readiness metadata alongside the selected review item's existing decision-readiness, preflight, preview, command-contract, dry-run, validation, permission-readiness, linked-entity, and timeline context.
- The operator identity registry fields, provisional role catalog, and future permission catalog are planning metadata only. They are not persisted identities, enforced roles, action grants, or authenticated user data.
- Service accounts, technicians, and unknown operators remain blocked for future Manual Review operator actions unless a later reviewed module explicitly changes the boundary.

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` Manual Review calls are added
- no auth/RBAC enforcement, login/session/token behavior, auth headers, fake user identity, fake role enforcement, approve, reject, defer, archive, resolve, dispatch, vendor, AI, audit write, idempotency persistence, immutable event write, or workflow execution calls are added
- role and permission labels are Randall-authorized Phase 0 planning baselines only and must not imply current access authority, current action authority, legal policy, company-liability policy, or executable workflow state

Open API/frontend concerns:

- final ACS-FSM authentication provider
- durable operator identity registry schema and lifecycle policy
- approved RBAC role model and permission taxonomy
- role-scoped Manual Review visibility and action authority after authentication exists

## Phase 0 Module 52 Auth Provider Configuration Readiness Boundary

The Manual Review queue and detail API contracts now include read-only auth configuration readiness metadata for future provider setup, environment safety, and local development auth planning.

Contract behavior:

- `GET /api/v1/dashboard/manual-review/queue` exposes `auth_boundary_readiness.auth_configuration_readiness` metadata with provider configured false, provider disabled, token verification disabled, RBAC enforcement disabled, sign-in UI unavailable, frontend auth config unavailable, real credentials required later, committed credentials disallowed, local dev auth mode disabled, and future provider selection required.
- `GET /api/v1/dashboard/manual-review/queue/{review_item_id}` exposes the same auth configuration readiness metadata alongside the selected review item's existing auth-boundary, permission-readiness, command-validation, dry-run, command-contract, preview, preflight, decision-readiness, linked-entity, and timeline context.
- Backend environment placeholder labels use `ACS_FSM_AUTH_*` names in the existing backend settings namespace.
- Frontend environment placeholder labels use `NEXT_PUBLIC_ACS_AUTH_*` names for future public UI configuration only.
- Safe placeholders may appear in `.env.example` files. Real credentials, service account JSON, private keys, tokens, `.env`, and `.env.local` remain forbidden from source control.

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` Manual Review calls are added
- no auth/RBAC enforcement, token verification, login/logout/session behavior, auth headers, fake authenticated user data, fake role enforcement, approve, reject, defer, archive, resolve, dispatch, vendor, AI, audit write, idempotency persistence, immutable event write, or workflow execution calls are added
- auth provider labels and environment placeholder labels are Randall-authorized Phase 0 planning baselines only and must not imply current access authority, current action authority, legal policy, company-liability policy, or executable workflow state

Open API/frontend concerns:

- final ACS-FSM authentication provider and production credential ownership
- secure VPS secret configuration and local development auth mode
- token verification middleware, RBAC enforcement, role-scoped visibility, and authenticated Manual Review action authority after a future reviewed auth module exists

## Phase 0 Module 56 Auth/RBAC Readiness Audit Boundary

The Manual Review queue and detail API contracts now include a read-only Auth/RBAC readiness audit and enforcement-boundary lock for future auth/RBAC transition planning.

Contract behavior:

- `GET /api/v1/dashboard/manual-review/queue` exposes `auth_boundary_readiness.auth_rbac_readiness_audit` metadata with auth implementation/enabled false, token verification false, real token parsing false, JWKS fetch false, RBAC enforcement false, route guarding false, auth headers required/emitted false, role and permission catalogs available, claims mapping available, route protection matrix available, access decision dry-run available, secret hygiene helper available, committed credentials disallowed, service-account Manual Review action allowed false, technician Manual Review action allowed false, future auth/RBAC/audit actor requirements true, route protection enforcement required before actions true, and Manual Review/Water Emergency action execution false.
- the audit includes `enforcement_boundary_lock` metadata with auth enforcement, token verification, real token parsing, JWKS fetch, RBAC enforcement, route guarding, sign-in UI, user management, action execution, mutation endpoints, and Phase 0 enforcement allowances all false.
- the audit includes future transition prerequisites grouped by provider selection, real credentials/secret hygiene, token verification, claims mapping, operator identity, RBAC/role policy, route protection, Manual Review action permissions, Water Emergency action permissions, audit actor/idempotency, legal/owner review, and review workflow.
- `GET /api/v1/dashboard/manual-review/queue/{review_item_id}` exposes the same auth-boundary audit metadata alongside the selected review item's existing read-only context.

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` Manual Review calls are added
- no auth/RBAC enforcement, route guards, route denial, section hiding, real token parsing, JWT validation, token verification, JWKS fetch, login/logout/session behavior, auth headers, fake authenticated user data, fake role enforcement, approve, reject, defer, archive, resolve, dispatch, vendor, AI, audit write, idempotency persistence, immutable event write, or workflow execution calls are added
- auth/RBAC readiness labels and enforcement-boundary labels are Randall-authorized Phase 0 planning baselines only and must not imply current access authority, current action authority, legal policy, company-liability policy, credential provisioning, or executable workflow state

Open API/frontend concerns:

- final ACS-FSM authentication provider and production credential ownership
- secure VPS secret configuration, token verification middleware, JWKS strategy, RBAC enforcement, route guard architecture, role-scoped visibility, authenticated Manual Review action authority, Water Emergency action authority, and owner-reviewed legal/company policy after future reviewed modules exist

## Phase 0 Module 57 Backend Auth Core Disabled Scaffold Boundary

The backend now includes disabled auth core interfaces and optional auth-context helpers for future API modules.

Contract behavior:

- current API routes still do not require Authorization headers
- disabled token verification returns not-verified metadata and never parses token contents, validates signatures, fetches JWKS, contacts providers, or treats any token as valid
- optional auth context is anonymous, non-authenticated, non-RBAC, and non-enforcing
- Manual Review queue/detail auth-boundary metadata reports auth core scaffold available, disabled token verifier available, optional auth context available, current routes require auth false, route protection enforced false, and Manual Review/Water Emergency action authority false

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` Manual Review calls are added
- no auth/RBAC enforcement, route guards, route denial, section hiding, real token parsing, JWT validation, token verification, JWKS fetch, login/logout/session behavior, auth headers, fake authenticated user data, fake role enforcement, approve, reject, defer, archive, resolve, dispatch, vendor, AI, audit write, idempotency persistence, immutable event write, or workflow execution calls are added
- disabled auth-core labels are Randall-authorized Phase 0 planning baselines only and must not imply current access authority, current action authority, legal policy, company-liability policy, credential provisioning, or executable workflow state

Open API/frontend concerns:

- final ACS-FSM authentication provider, production credential ownership, secure VPS secret configuration, token verification middleware, JWKS strategy, RBAC enforcement, route guard architecture, role-scoped visibility, authenticated Manual Review action authority, Water Emergency action authority, and owner-reviewed legal/company policy after future reviewed modules exist

## Phase 0 Module 54 Auth Claims Mapping And Token Dry-Run Boundary

The Manual Review queue and detail API contracts now include read-only auth claims mapping, token-verification dry-run, and role-resolution readiness metadata for future auth/RBAC planning.

Contract behavior:

- `GET /api/v1/dashboard/manual-review/queue` exposes `auth_boundary_readiness.auth_claims_mapping_readiness` metadata with token dry-run visibility, token verification disabled, real token parsing disabled, JWKS fetch disabled, required auth headers false, frontend-emitted auth headers false, claim mapping not configured, role claim not configured, permission claim not configured, required claims documented, safe example fixtures available, and service-account/technician block rules documented.
- `GET /api/v1/dashboard/manual-review/queue/{review_item_id}` exposes the same auth claims mapping metadata alongside the selected review item's existing auth-boundary, auth-configuration, auth-diagnostics, permission-readiness, command-validation, dry-run, command-contract, preview, preflight, decision-readiness, linked-entity, and timeline context.
- Claim contract labels document future subject, email, email verification, display name, role, permission, provider, issuer, audience, tenant/domain, expiration, issued-at, and auth-time expectations.
- Role-resolution labels document unknown-role mapping to `unknown_operator`, service-account/system-service blocking for Manual Review actions, and technician blocking unless a future reviewed module authorizes it.
- Safe claim fixtures are placeholder examples only and must not include real user data, real tokens, private keys, service account JSON, credentials, or JWT-like strings.

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` Manual Review calls are added
- no auth/RBAC enforcement, real token parsing, token verification, JWKS fetch, login/logout/session behavior, auth headers, fake authenticated user data, fake role enforcement, approve, reject, defer, archive, resolve, dispatch, vendor, AI, audit write, idempotency persistence, immutable event write, or workflow execution calls are added
- auth claim labels, dry-run labels, and role-resolution labels are Randall-authorized Phase 0 planning baselines only and must not imply current access authority, current action authority, legal policy, company-liability policy, credential provisioning, or executable workflow state

Open API/frontend concerns:

- final ACS-FSM authentication provider claim names and production credential ownership
- secure VPS secret configuration and local development auth mode
- token verification middleware, JWKS strategy, RBAC enforcement, role-to-permission expansion, role-scoped visibility, and authenticated Manual Review action authority after a future reviewed auth module exists

## Phase 0 Module 55 Route Protection Matrix And Access Decision Dry-Run Boundary

The Manual Review queue and detail API contracts now include read-only route protection matrix and access decision dry-run metadata for future auth/RBAC planning.

Contract behavior:

- `GET /api/v1/dashboard/manual-review/queue` exposes `auth_boundary_readiness.route_protection_readiness` metadata with route protection matrix availability, access decision dry-run enabled, enforcement disabled, Phase 0 enforcement allowance false, token verification disabled, RBAC enforcement disabled, route guarding disabled, simulated decisions only, current auth/RBAC denial false, future protected-surface counts, and unknown mapping counts.
- `GET /api/v1/dashboard/manual-review/queue/{review_item_id}` exposes the same route protection matrix metadata alongside the selected review item's existing auth-boundary, auth-configuration, auth-diagnostics, auth-claims, permission-readiness, command-validation, dry-run, command-contract, preview, preflight, decision-readiness, linked-entity, and timeline context.
- Matrix items document current dashboard API routes, frontend dashboard sections, and future action surfaces with future roles, future permissions, denied future roles, Manual Review sensitivity, Water Emergency sensitivity, mutation sensitivity, and Alfonso owner-review flags where legal/insurance/company-liability implications may exist.
- Manual Review routes map to future Manual Review view/detail permissions only and do not create action authority.
- Water Emergency routes map to future Water Emergency read/review permissions and remain separated from standard Manual Review and dispatch visibility.

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` Manual Review calls are added
- no auth/RBAC enforcement, route guards, route denial, section hiding, real token parsing, JWT validation, token verification, JWKS fetch, login/logout/session behavior, auth headers, fake authenticated user data, fake role enforcement, approve, reject, defer, archive, resolve, dispatch, vendor, AI, audit write, idempotency persistence, immutable event write, or workflow execution calls are added
- route protection labels and access decision dry-run labels are Randall-authorized Phase 0 planning baselines only and must not imply current access authority, current action authority, legal policy, company-liability policy, credential provisioning, or executable workflow state

Open API/frontend concerns:

- final ACS-FSM route guard architecture, frontend section-hiding policy, token verification middleware, JWKS strategy, RBAC enforcement, role-to-permission expansion, role-scoped visibility, and authenticated Manual Review action authority after a future reviewed auth module exists

## Phase 0 Module 53 Auth Diagnostics And Secret Hygiene Boundary

The Manual Review queue and detail API contracts now include read-only auth diagnostics and runtime safety metadata for future auth configuration checks.

Contract behavior:

- `GET /api/v1/dashboard/manual-review/queue` exposes `auth_boundary_readiness.auth_configuration_readiness.runtime_safety_diagnostics` metadata with auth disabled, provider disabled, provider configured false, token verification disabled, RBAC enforcement disabled, sign-in UI unavailable, auth headers not required, frontend auth headers not emitted, real credentials required later, committed credentials disallowed, tracked `.env` false, tracked `.env.local` false, service account JSON tracked false, private key detected false, placeholder values only true, and runtime auth mode `read_only_phase_0`.
- `GET /api/v1/dashboard/manual-review/queue/{review_item_id}` exposes the same diagnostics metadata alongside the selected review item's existing auth-boundary, auth-configuration, permission-readiness, command-validation, dry-run, command-contract, preview, preflight, decision-readiness, linked-entity, and timeline context.
- Diagnostic check labels are visibility metadata only. They explain why auth remains disabled and why secret hygiene must remain safe before future provider setup.
- The `backend/scripts/check_auth_config_safety.py` helper verifies tracked/example files without printing secret values, contacting external services, mutating files, or providing credential management.

Contract constraints:

- no `POST`, `PUT`, `PATCH`, or `DELETE` Manual Review calls are added
- no auth/RBAC enforcement, token verification, login/logout/session behavior, auth headers, fake authenticated user data, fake role enforcement, approve, reject, defer, archive, resolve, dispatch, vendor, AI, audit write, idempotency persistence, immutable event write, or workflow execution calls are added
- auth diagnostic labels, secret-hygiene labels, and helper output are Randall-authorized Phase 0 planning baselines only and must not imply current access authority, current action authority, legal policy, company-liability policy, credential provisioning, or executable workflow state

Open API/frontend concerns:

- final ACS-FSM authentication provider and production credential ownership
- secure VPS secret configuration and local development auth mode
- token verification middleware, RBAC enforcement, role-scoped visibility, and authenticated Manual Review action authority after a future reviewed auth module exists
