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
