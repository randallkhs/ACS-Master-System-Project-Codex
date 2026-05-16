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
