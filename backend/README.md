# ACS FSM Backend

FastAPI backend foundation for the Apple Cleaning Systems FSM platform.

This module is Phase 0 scaffolding only. It does not implement live Calendar, Sheets, FastField, Verizon Connect, AI, route optimization, or production external dispatch integration workflows yet.

## Module 55 Route Protection Matrix Notes

Module 55 adds read-only route protection matrix and access decision dry-run metadata to the Manual Review auth-boundary read model. It maps current dashboard API routes, frontend sections, and future action surfaces to future roles and permissions for planning visibility only.

The matrix does not enforce authentication, require headers, parse or validate JWTs, add route guards, enforce RBAC, hide frontend sections, create mutation endpoints, or execute Manual Review or Water Emergency actions. `enforcement_enabled`, `phase_allows_enforcement`, `token_verification_enabled`, `rbac_enforcement_enabled`, and `route_guarding_enabled` must remain false in Phase 0.

Water Emergency-related routes and sections stay marked separately from standard Manual Review visibility. Future legal, insurance, warranty, certification, billing, or customer-promise action surfaces are marked as requiring Alfonso owner review before any formal policy or executable workflow exists.

## Architecture

- FastAPI application package in `app/`
- API routes under `app/api/v1/`
- Pydantic Settings configuration in `app/core/config.py`
- structured logging foundation in `app/core/logging.py`
- request context middleware in `app/core/middleware.py`
- app lifecycle and health readiness state in `app/core/lifecycle.py`
- SQLAlchemy 2 models in `app/models/`
- PostgreSQL session foundation in `app/db/session.py`
- request-scoped DB dependency alias in `app/db/dependencies.py`
- thin repository layer in `app/repositories/`
- intake domain structures in `app/domain/intake.py`
- deterministic normalization, validation, confidence, review-preparation, Manual Review Queue, dispatch orchestration, operational intake persistence, operational job creation, operational work generation, assignment preparation, routing/dispatch preparation, route-assignment/dispatch-authorization, internal dispatch execution, external adapter preparation, controlled external adapter execution, external confirmation/recovery, operational event history, dispatch reconciliation, operational replay/recovery, operational governance, and operational accountability services
- Alembic migration environment in `app/db/migrations/`
- External integrations isolated under `app/adapters/`
- Business services under `app/services/`

## Local Setup

From the repository root:

```bash
python3 -m venv .venv
cd backend
make install
```

If `make` is unavailable:

```bash
../.venv/bin/python -m pip install -e ".[dev]"
```

Copy `backend/.env.example` to `backend/.env` for local development, then point it at a local PostgreSQL development database.

Do not commit `.env` files or production secrets.

## Local PostgreSQL Development Database

Module 27 defines the default local development database as:

```text
database: acs_fsm_dev
user: acs_fsm_dev
host: 127.0.0.1
port: 5432
```

Local `.env` example:

```bash
ACS_FSM_ENVIRONMENT=development
ACS_FSM_DATABASE_URL=postgresql+psycopg://acs_fsm_dev:acs_fsm_dev@127.0.0.1:5432/acs_fsm_dev
```

The username/password above are local-only development assumptions. Do not reuse them in production or in shared hosted databases.

Module 28 keeps PostgreSQL installation outside the repository. Do not install PostgreSQL automatically from project scripts. If PostgreSQL is missing on a Mac development workstation that uses Homebrew, install and start it manually:

```bash
brew install postgresql@18
brew services start postgresql@18
echo 'export PATH="/opt/homebrew/opt/postgresql@18/bin:$PATH"' >> ~/.zshrc
```

Safe local detection commands:

```bash
command -v psql
command -v pg_isready
command -v createdb
pg_isready -h 127.0.0.1 -p 5432
brew services list
```

If Homebrew PostgreSQL is installed but stopped, `brew services start postgresql@18` is the expected local development start command. Do not use this repository to modify production PostgreSQL services or production host configuration.

Example setup with a local PostgreSQL installation:

```bash
createuser acs_fsm_dev
createdb --owner=acs_fsm_dev acs_fsm_dev
```

If your local PostgreSQL setup requires passwords, create the user with your normal local admin workflow and keep the resulting password only in `backend/.env`.

Run migrations from `backend/` after the database exists:

```bash
make migrate
make db-check
```

Optional synthetic dashboard data for local read-model verification:

```bash
make seed-dashboard
```

The seed command upserts clearly labeled synthetic records with `source_system=module27_dev_seed`. It refuses production, refuses non-local hosts, refuses placeholder passwords, does not call vendors, and does not imply real ACS production state. The source name remains stable for compatibility with the original local seed set; Module 37 expands the scenario version reported by the seed output.

Module 29 seed scenarios cover:

- standard dispatch-ready work awaiting execution
- Manual Review blockers and deferred/resolved/archived review states
- blocked route assignment evidence
- external confirmation failure and retry-preparation evidence
- successful external confirmation evidence
- reconciliation and rollback-preparation evidence
- governance manual-intervention evidence
- accountability incident-preparation evidence
- ordered operational event timeline examples
- open and closed Water Emergency examples kept separate from standard dispatch
- Water Emergency synthetic work-order equipment notes, multi-visit chain context, and drying-check timeline evidence for read-only visibility
- Water Emergency synthetic open, deferred, and archived review/exception examples plus critical/blocker evidence for read-only visibility
- Water Emergency synthetic next-step readiness examples for Manual Review, equipment review, visit follow-up, missing data, ready-for-close-review visibility, and closed/no-active-action visibility
- Water Emergency synthetic operator queue examples for critical attention, blocked/missing information, visit follow-up, equipment review, monitoring, close review, and closed/resolved visibility
- Water Emergency synthetic aging/follow-up examples for newly opened, active monitoring, follow-up due, follow-up overdue, stale evidence, waiting review, ready-for-close-review, closed/resolved, and unknown timing visibility
- Water Emergency synthetic state coverage used by Module 38 filter/sort visibility for active, critical, review, blocked, follow-up, stale, close-review, closed/resolved, and unknown-timing groups

`make seed-dashboard` is safe to rerun. It updates seed-owned records by deterministic identifiers or natural seed keys, inserts missing seed records, and does not delete non-seed data. It does not reset the database.

Module 28 live verification confirmed this sequence on a local Homebrew PostgreSQL runtime:

```bash
make db-check
make migrate
make db-check
make seed-dashboard
make dashboard-check
```

The pre-migration database check may report `connected=true` and `migrated=false`; that means PostgreSQL is reachable and Alembic still needs to run.

Safe dev-only reset, if you intentionally want to recreate the local database:

```bash
dropdb acs_fsm_dev
createdb --owner=acs_fsm_dev acs_fsm_dev
make migrate
make seed-dashboard
```

Only run reset commands against the local `acs_fsm_dev` database. Never use this reset flow for production or shared databases.

Testing distinction:

- `acs_fsm_dev` is for running the local API and dashboard against PostgreSQL.
- Automated pytest tests do not require a live PostgreSQL database unless a future test explicitly opts into one.
- A future `acs_fsm_test` database may be added for integration tests, but Module 27 does not require it.

## Environment Rules

Supported environments:

- `development`
- `testing` (`test` is accepted as an alias)
- `production`

Production settings reject unsafe database values:

- local database hosts such as `localhost` or `127.0.0.1`
- placeholder hosts such as `db.example.internal`
- placeholder passwords such as `change-me`
- SQL echo logging

Use environment variables or server-level secret management for VPS deployment. Do not place production credentials in source control or documentation.

## Run API

From `backend/`:

```bash
make dev
```

Health check:

```text
GET /api/v1/health
```

The health endpoint reports service name, environment, version, readiness, and startup timestamp. It does not require a database connection during Phase 0.

API docs are versioned under:

```text
/api/v1/docs
/api/v1/redoc
/api/v1/openapi.json
```

Set `ACS_FSM_API_DOCS_ENABLED=false` to disable API documentation/OpenAPI routes in a deployment environment.

For Apache or another reverse proxy, configure the deployment process to pass proxy headers at the ASGI server layer and set `ACS_FSM_PROXY_ROOT_PATH` only if the backend is mounted under a path prefix.

## Dashboard API

Phase 0 dashboard endpoints are read-only and contract-focused:

```text
GET /api/v1/dashboard/overview
GET /api/v1/dashboard/lifecycle
GET /api/v1/dashboard/review
GET /api/v1/dashboard/manual-review/queue
GET /api/v1/dashboard/manual-review/queue/{review_item_id}
GET /api/v1/dashboard/dispatch
GET /api/v1/dashboard/water-emergency
GET /api/v1/dashboard/water-emergency/{water_emergency_id}
```

These routes summarize persisted backend state through dashboard read models. They do not mutate records, execute dispatch, resolve Manual Review, call integrations, or call AI.

The Manual Review Queue contract is dedicated to read-only safety visibility. `GET /api/v1/dashboard/manual-review/queue` exposes queue-item details, status counts, reason counts, severity counts, visibility group counts, available read-only filter groups, sort options, result-window metadata, conservative age buckets, active-attention counts, blocker indicators, entity links, Water Emergency links when specifically tied to the review item, decision-readiness counts, action-preflight counts, future-action preview counts, command-contract counts, audit-ledger dry-run counts, command-validation counts, execution-readiness audit metadata, auth-boundary readiness metadata, provisional role catalog metadata, future permission catalog metadata, auth configuration readiness metadata, auth diagnostics metadata, future claims mapping metadata, role-resolution rules, audit-correlation references, evidence references, and Randall-authorized Phase 0 review taxonomy metadata. `GET /api/v1/dashboard/manual-review/queue/{review_item_id}` returns one review item with reason/evidence context, decision-readiness context, future action-preflight context, future-action preview context, future command-contract/audit-envelope context, audit-ledger dry-run context, command-validation and safety-gate matrix context, auth-boundary/auth-configuration/auth-diagnostics/auth-claims readiness metadata, linked entity context, Water Emergency separation when applicable, data-gap counts, audit references, and chronological timeline evidence. These endpoints do not approve, reject, defer, archive, resolve, dispatch, escalate, call vendors, call AI, implement auth/RBAC, parse real tokens, verify tokens, fetch JWKS, emit auth headers, persist frontend preferences, make actions executable, validate commands for execution, or mutate review records.

The Water Emergency dashboard contract is dedicated to emergency visibility. It summarizes existing `WaterEmergency` records, status/stage distributions, equipment context, visit-chain summaries, drying-stage visibility, review/exception counts, blocker reason buckets, critical-alert indicators, read-only next-step readiness labels, operator queue/attention groups, aging/follow-up timing visibility, stale/missing evidence indicators, read-only filter/sort view-state metadata, Randall-authorized Phase 0 governance metadata, result-window scalability metadata, related job/work-order/visit references, data gaps, audit correlation references, and emergency timeline evidence. The detail contract returns one Water Emergency record, related job/work-order/visit references, specifically scoped Manual Review indicators, review/exception context, equipment notes/unknowns, visit-chain timing/status counts, drying-stage context, next-step readiness evidence, detail data gaps, audit correlations, and chronological timeline evidence. These endpoints do not create, close, dispatch, approve, edit, schedule, escalate, enforce SLA rules, persist frontend view state, or otherwise execute Water Emergency work.

Module 39 formalizes the current Water Emergency software-visible labels as a Randall-authorized Phase 0 visibility baseline. Timing labels remain conservative internal heuristics, not final SLA enforcement, insurance language, drying certification, customer-facing promises, or company policy. The dashboard contract exposes Alfonso owner-review boundaries for legal, insurance, warranty, compliance, or company-liability policy decisions without finalizing those policies in software.

Module 40 formalizes current Manual Review queue grouping as a Randall-authorized Phase 0 visibility baseline. Status, reason, age, blocked, dispatch-related, Water Emergency-related, duplicate/conflict, cancellation/status-uncertainty, and needs-operator-review labels are internal software visibility groups only. They do not define final Manual Review workflow action authority, legal policy, or company-liability policy.

Module 41 extends Manual Review visibility with a read-only single-item detail contract. The detail endpoint is investigation context only: it scopes linked job, work order, visit, route-assignment, and Water Emergency references from persisted IDs; orders related operational events chronologically; returns 404 for missing live records; and does not substitute mock data when the backend says a detail record was not found.

Module 42 extends Manual Review queue visibility with read-only filter/sort and result-window metadata. Filter groups such as open, deferred, resolved, archived, active-attention, Water Emergency-related, dispatch-related, missing-data, duplicate/conflict, cancellation/status-uncertainty, and needs-operator-review are internal software visibility groups only. The metadata prepares the frontend for local view-state and future query scaling without adding backend mutation, persisted preferences, action execution, auth, RBAC, pagination parameters, or workflow authority.

Module 43 extends Manual Review queue and detail visibility with deterministic decision-readiness labels such as needs-operator-review, needs-missing-information, needs-entity-context, needs-Water-Emergency-review, needs-dispatch-review, ready-for-operator-decision, ready-for-resolution-review, blocked-by-conflict, blocked-by-missing-data, resolved-or-archived, and unknown-readiness. These labels are read-only preparation context only. They do not approve, reject, defer, archive, resolve, dispatch, escalate, call vendors, call AI, mutate review records, or create workflow authority.

Module 44 extends Manual Review queue and detail visibility with deterministic action-preflight labels such as blocked-by-missing-entity-context, blocked-by-missing-data, blocked-by-conflict, blocked-by-Water-Emergency-context, blocked-by-resolved-or-archived-status, eligible-for-operator-decision, eligible-for-resolution-review, and unknown-action-eligibility. The preflight contract also exposes future-only requirements for authentication, operator identity, and audit reason capture. These labels are read-only preparation context only. They do not make any action currently executable, mutate review records, implement auth/RBAC, approve, reject, defer, archive, resolve, dispatch, call vendors, call AI, or create workflow authority.

Module 45 extends Manual Review queue and detail visibility with deterministic future-action preview labels such as future-approve-preview, future-reject-preview, future-defer-preview, future-archive-preview, future-resolve-preview, future-request-information-preview, future-operator-decision-preview, no-action-available missing-entity/conflict/Water-Emergency/resolved-or-archived states, and unknown-action-preview. The preview contract exposes expected non-binding outcome summaries, impacted entity references, blocker labels, and future operator identity/audit reason requirements. Every preview is explicitly non-executable in Phase 0 and does not mutate review records, implement auth/RBAC, approve, reject, defer, archive, resolve, dispatch, call vendors, call AI, or create workflow authority.

Module 46 extends Manual Review queue and detail visibility with deterministic future command-contract and audit-envelope metadata such as command-contract-read-only-phase, requires-future-auth, requires-operator-identity, requires-role-authorization, requires-audit-reason, requires-idempotency-key, requires-preflight-pass, requires-entity-context, requires-no-conflict-blocker, requires-Water-Emergency-scope-check, requires-immutable-event-recording, requires-post-action-consistency-check, and command-not-executable-phase-0. Every command contract is explicitly `is_currently_executable = false` and remains read-only preparation only. The contract does not create POST/PUT/PATCH/DELETE endpoints, persist audit envelopes, implement auth/RBAC, approve, reject, defer, archive, resolve, dispatch, call vendors, call AI, or create workflow authority.

Module 47 extends Manual Review queue and detail visibility with deterministic audit-ledger dry-run metadata such as dry-run-only Phase 0, audit-envelope required, operator-identity required, role-authorization required, idempotency-key required, immutable-event required, consistency-check required, command-execution blocked by read-only phase, missing entity, conflict, Water Emergency scope, resolved/archived status, and unknown dry-run readiness. Every dry-run record is explicitly `is_currently_executable = false` and `phase_allows_execution = false`. The contract proposes future event type/state, audit envelope fields, idempotency scope, consistency-check summary, and evidence references as read-only preparation only. It does not write audit events, persist idempotency keys, create POST/PUT/PATCH/DELETE endpoints, implement auth/RBAC, approve, reject, defer, archive, resolve, dispatch, call vendors, call AI, or create workflow authority.

Module 48 extends Manual Review queue and detail visibility with deterministic command-validation labels and a safety-gate matrix. Labels include validation read-only phase, validation passes future requirements, missing entity, missing audit reason, missing operator identity, missing role authorization, missing idempotency key, missing immutable-event plan, missing consistency check, Water Emergency scope, resolved/archived, conflict, warning requires review, and unknown validation state where persisted evidence supports them. Every validation record is explicitly `is_currently_executable = false`, `phase_allows_execution = false`, and contains required gates for entity context, active status, Water Emergency scope, no conflict blocker, missing data review, operator identity, role authorization, audit reason, idempotency key, immutable event recording, post-action consistency check, and Phase 0 execution blocking. The contract does not validate a command for current execution, write audit events, persist idempotency keys, create POST/PUT/PATCH/DELETE endpoints, implement auth/RBAC, approve, reject, defer, archive, resolve, dispatch, call vendors, call AI, or create workflow authority.

Module 49 extends Manual Review queue and detail visibility with deterministic operator-identity, role-authorization, and permission-readiness metadata. Labels include permission read-only phase, requires future auth, requires operator identity, requires role authorization, reviewer/dispatcher/operations-manager/owner future role requirements, service account not allowed, technician action not allowed, unknown operator blocked, Water Emergency scope blocked, resolved/archived blocked, and ready-for-future-auth-phase where persisted evidence supports them. Every permission-readiness record is explicitly `is_currently_executable = false` and `phase_allows_execution = false`. The contract does not implement auth, RBAC, login/session/token behavior, fake role enforcement, POST/PUT/PATCH/DELETE endpoints, review action execution, audit writes, dispatch execution, vendor calls, AI authority, or workflow authority.

Module 50 adds a read-only Manual Review execution-readiness audit and mutation-boundary lock to the queue read model. The audit summarizes active, resolved/archived, Water Emergency-related, dispatch-related, missing-entity, conflict, missing-data, future-preview, command-contract, dry-run, safety-gate, permission-readiness, Phase 0 blocked, and future auth/RBAC/audit/idempotency/immutable-event/consistency-check counts. It explicitly reports `manual_review_mutations_enabled = false`, `action_execution_phase = "read_only_phase_0"`, `currently_executable_count = 0`, and `mutation_endpoints_available = false`. The future transition checklist marks auth, RBAC, audit envelope, idempotency, immutable-event writing, consistency checks, action contracts, action UI review, ACSSDR update workflow, and Review GUI/ChatGPT review as prerequisites before any later mutation module. Liability-sensitive actions are flagged as requiring Alfonso owner review. This is read-model visibility only; it does not add tables, mutation endpoints, auth, RBAC, login/session/token behavior, action execution, audit writes, dispatch execution, vendor calls, AI authority, or workflow authority.

Module 51 adds read-only Manual Review auth-boundary readiness metadata to the queue and detail read models. The metadata defines future operator identity registry fields, a provisional role catalog, and a future permission catalog while explicitly reporting `auth_implemented = false`, `rbac_enforced = false`, `login_ui_available = false`, `action_execution_available = false`, `operator_identity_registry_available = false`, service accounts blocked for Manual Review actions, and future auth/RBAC/audit-actor requirements. Roles and permissions are Phase 0 planning labels only; they do not enforce access, hide UI, grant action authority, create fake users, add auth headers, or persist operator identities.

Module 52 adds read-only Manual Review auth configuration readiness metadata and safe future auth provider placeholders. The metadata reports `auth_provider_configured = false`, `auth_provider = "disabled"`, `token_verification_enabled = false`, `rbac_enforcement_enabled = false`, `frontend_auth_config_available = false`, `committed_credentials_allowed = false`, `local_dev_auth_mode = "disabled"`, and future provider selection still required. `.env.example` and `backend/.env.example` list safe `ACS_FSM_AUTH_*` placeholders only. They are not parsed into an active auth dependency, do not require real credentials for dev/test/build, do not verify tokens, do not enforce routes, and do not create login/session/token behavior.

Module 53 adds read-only Manual Review auth diagnostics and runtime safety visibility to the same auth-boundary read model. The metadata reports `auth_enabled = false`, `auth_headers_required = false`, `auth_headers_emitted_by_frontend = false`, `service_account_json_tracked = false`, `env_file_tracked = false`, `env_local_file_tracked = false`, `private_key_detected = false`, `placeholder_values_only = true`, and `runtime_auth_mode = "read_only_phase_0"`. The `backend/scripts/check_auth_config_safety.py` helper verifies tracked placeholders and obvious credential hazards without printing secret values, contacting services, mutating files, enforcing auth, or requiring real credentials.

Module 54 adds read-only Manual Review auth claims mapping and role-resolution readiness metadata to the auth-boundary read model. The metadata documents future subject, email, email verification, display name, role, permission, provider, issuer, audience, tenant/domain, expiration, issued-at, and auth-time claim expectations; reports token-verification dry-run visibility while keeping real token parsing, token verification, JWKS fetch, auth headers, and RBAC enforcement disabled; and documents service-account, technician, and unknown-role blocking rules for future Manual Review actions. The metadata and safe example claim fixtures do not contain real user data, tokens, private keys, service account JSON, auth credentials, JWT-like strings, login/session behavior, auth middleware, or action authority.

The result-window metadata is read-only preparation for future pagination/query scaling. It reports the current returned record count, visible count, result limit, sort key, generation time, and whether more records exist. Module 39 does not add backend pagination parameters, analytics engines, mutation routes, or saved-view persistence.

Module 33 does not add a dedicated equipment inventory table or final Water Emergency drying taxonomy. The read models expose existing persisted fields and explicit unknown indicators such as `equipment_inventory_not_modeled` until future Water Emergency workflow modules define those operational rules.

Module 34 does not add a final review/escalation taxonomy or Manual Review action workflow. It exposes existing Water Emergency `ReviewItem` status, severity, reason-code, blocker-like reason, review ID, and audit-correlation evidence as read-only visibility only. Per-record detail still scopes reviews through specific job, entity, or visit links so generic Water Emergency labels do not attach to every record.

Module 35 does not add a workflow engine or operator actions. It derives Water Emergency next-step readiness labels from persisted evidence only, including Manual Review presence, missing data, visit-chain context, equipment/drying context, closed/resolved state, and ready-for-close-review evidence. These labels are decision-support visibility only; they do not auto-close, auto-dispatch, auto-approve, or advance Water Emergency records.

Module 36 does not add a workflow engine, priority engine, or operator actions. It groups Water Emergency records into read-only operator queue and attention categories derived from Module 35 readiness evidence. Critical alerts sort above lower attention items, closed/resolved records remain separated from active attention, and unknown or incomplete records stay in safe blocked/review visibility instead of progressing automatically.

Module 37 does not add an SLA engine or operator actions. It derives Water Emergency aging, follow-up, stale-evidence, and unknown-timing visibility from persisted timestamps and separates closed/resolved records from active timing risks.

Module 38 does not add workflow execution, backend mutation, or persisted operator preferences. It exposes read-only filter options, sort options, filter group membership, primary view groups, deterministic sort labels, last-activity timestamps, and per-record view-state evidence so the frontend can filter and sort Water Emergency records without inferring hidden lifecycle state.

Local full-stack dashboard testing expects the backend on `http://127.0.0.1:8000` and the frontend `ACS_DASHBOARD_API_BASE_URL` set to that origin. A real local PostgreSQL database and migrations are still required for live backend reads; the frontend falls back to typed local data when the backend is unavailable.

Local endpoint verification after the backend is running:

```bash
make dashboard-check
```

The check calls only:

```text
GET /api/v1/health
GET /api/v1/dashboard/overview
GET /api/v1/dashboard/lifecycle
GET /api/v1/dashboard/review
GET /api/v1/dashboard/manual-review/queue
GET /api/v1/dashboard/dispatch
GET /api/v1/dashboard/water-emergency
```

Module 32 also exposes Water Emergency detail reads by ID:

```text
GET /api/v1/dashboard/water-emergency/{water_emergency_id}
```

Use a real persisted Water Emergency UUID from the summary endpoint. Missing records return 404.

## Migrations

From `backend/`:

```bash
make migration MIGRATION_MESSAGE="describe migration"
make migrate
make history
```

Alembic reads `ACS_FSM_DATABASE_URL` through the backend settings system.

Migration rules:

- Models are the schema source for Alembic autogeneration.
- Review autogenerated migrations before keeping them.
- Do not rewrite committed migrations unless explicitly directed.
- Do not connect to production databases from local development workflows.

## Verification

From `backend/`:

```bash
make lint
make format-check
make test
make history
make compileall
```

Full local verification:

```bash
make verify
```

Local database/dashboard verification:

```bash
make db-check
make migrate
make seed-dashboard
make dev
# in another terminal
make dashboard-check
```

Troubleshooting:

- If `make db-check` cannot connect, confirm PostgreSQL is installed, running, and listening on `127.0.0.1:5432`.
- If migrations fail, confirm `ACS_FSM_DATABASE_URL` points to the local development database and the local user owns it.
- If dashboard endpoints return `500`, check that migrations have run and the backend process is using the same `backend/.env` database URL.
- If `make seed-dashboard` refuses to run, confirm `ACS_FSM_ENVIRONMENT` is not `production`, the host is local, and the password is not a placeholder such as `change-me`.

## Logging

The backend defaults to structured JSON logs with request-safe fields:

- timestamp
- level
- logger
- message
- service
- environment
- request ID
- method
- path
- status code
- duration

Request logging records the path only, not query-string values. Future audit correlation can build on `X-Request-ID` and later correlation IDs.

## Database Access Boundaries

Database access should flow through explicit boundaries:

```text
API routes -> services / workflow modules -> repositories -> SQLAlchemy session -> PostgreSQL
```

Rules:

- API routes should not contain SQLAlchemy query logic.
- Repositories are thin data-access objects only.
- Repositories should not contain business workflow decisions, dispatch orchestration, integration calls, or AI decisions.
- Services and future workflow engines should coordinate transactions; repositories should use the session they are given.
- Request-scoped dependencies should use `get_db_session` or the `DBSession` alias from `app/db/dependencies.py`.
- `session_scope()` is available for future explicit transactional units outside request dependency wiring.

The current repository layer provides foundational `get`, `list`, `add`, and `delete` helpers plus domain-specific repository classes. It does not expose CRUD endpoints or implement operational workflows.

## Intake Pipeline Foundation

The Phase 0 intake foundation prepares future external ingestion without connecting to live vendors yet.

Current deterministic pipeline:

```text
RawIntakePayload
  -> IntakeNormalizationService
  -> IntakeValidationService
  -> DeterministicConfidenceScoringService
  -> ManualReviewPreparationService
```

Responsibilities:

- `app/domain/intake.py` defines raw intake, normalized intake, detection, issue, validation, confidence, and review recommendation structures.
- Normalization cleans whitespace, extracts AM/PM and supported state markers, and detects cancellation and Water Emergency keywords.
- Validation checks required fields, malformed address foundations, conflicting markers, cancellation safety, and Water Emergency workflow separation.
- Confidence scoring is deterministic only; AI scoring is intentionally not implemented.
- Manual Review preparation translates validation/confidence results into review-ready reason codes and recommended actions.

The intake pipeline itself does not import Google Calendar data, route technicians, export to Sheets/FastField, run background workers, or call AI. Durable review persistence is handled by the Manual Review Queue service after deterministic review preparation.

## Manual Review Queue Foundation

Phase 0 Module 6 adds the first durable operational safety layer for intake records that cannot continue safely.

Persistent review items can now store:

- review status and intake processing state
- deterministic reason codes and review categories
- severity and recommended operator action
- source system/source ID references
- normalization, validation, warning, and confidence snapshots
- operator notes and decision timestamps
- audit correlation IDs for future traceability
- queryable audit-log correlation support

Current lifecycle states:

```text
raw -> normalized -> validated -> flagged_for_review -> approved/rejected/deferred/archived
```

Current services keep responsibilities separate:

- `ManualReviewQueueService` creates persistent review items from normalized, validated intake.
- `ReviewClassificationService` maps deterministic issues to review categories.
- `ReviewEscalationService` assigns deterministic severity.
- `ReviewStateTransitionService` records approve, reject, defer, and archive transitions with operator decisions.
- `ReviewAuditTraceBuilder` prepares traceable audit-log evidence.

This foundation does not approve dispatch, create jobs, route technicians, call AI, or write to external systems.

## Dispatch Orchestration Preparation

Phase 0 Module 7 adds the deterministic preparation layer that composes intake processing into one explainable orchestration result.

Current internal flow:

```text
RawIntakePayload
  -> IntakeNormalizationService
  -> IntakeValidationService
  -> DeterministicConfidenceScoringService
  -> ManualReviewPreparationService
  -> DispatchOrchestrationService
```

The orchestration result includes:

- normalized intake
- validation result
- confidence score
- Manual Review recommendation
- orchestration warnings
- dispatch eligibility
- deterministic decision evidence

Dispatch eligibility currently tracks:

- eligible for dispatch
- requires review
- blocked
- deferred
- unsafe
- Water Emergency separated from standard dispatch
- deterministic reason codes

This layer does not persist jobs, create Manual Review records, approve dispatch, route technicians, export data, call AI, run background work, or execute integrations.

## Operational Intake Persistence

Phase 0 Module 8 adds the first durable storage boundary for deterministic orchestration outcomes.

Current persistence flow:

```text
DispatchOrchestrationService result
  -> OperationalIntakePersistenceService
  -> IntakeProcessingRecordRepository
  -> intake_processing_records
```

`IntakeProcessingRecord` stores:

- source system/source ID
- lifecycle state
- orchestration state
- review item linkage
- audit correlation ID
- orchestration result snapshot
- dispatch eligibility snapshot
- raw payload, normalized, validation, confidence, review, warning, and deterministic evidence snapshots

Current lifecycle states:

```text
intake_received -> normalized -> validated -> review_required/approved_for_dispatch/blocked/deferred/archived
```

Persistence rules:

- orchestration prepares decisions; persistence stores outcomes
- unsafe intake cannot be marked approved for dispatch
- Water Emergency intake cannot enter standard dispatch approval
- review-required intake remains review-required until explicitly resolved
- deterministic evidence must be stored with the operational intake record

This layer does not create jobs, visits, work orders, routes, exports, background jobs, AI actions, or live integrations.

## Operational Job Creation Foundation

Phase 0 Module 9 adds the first controlled transition from approved intake records into durable operational job structures.

Current creation flow:

```text
Approved IntakeProcessingRecord
  -> OperationalJobCreationService
  -> Job
  -> JobCreationRecord
```

`JobCreationRecord` stores:

- intake-to-job linkage
- review item linkage when present
- audit correlation ID
- creation snapshot
- intake snapshot
- orchestration snapshot
- dispatch eligibility snapshot
- review linkage snapshot
- deterministic evidence snapshot
- lifecycle metadata

Creation rules:

- only `approved_for_dispatch` intake records can create standard jobs
- blocked, unsafe, review-required, and invalid-lifecycle intake records are rejected
- Water Emergency intake remains separated and cannot create standard jobs
- duplicate job creation from the same intake record is blocked
- job creation sets the job to `awaiting_dispatch` only; dispatch has not executed

This layer does not route technicians, create visits or work orders, execute integrations, run background workers, call AI, or dispatch work.

## Operational Work Generation Foundation

Phase 0 Module 10 adds the first scheduling-ready operational execution preparation layer.

Current generation flow:

```text
Job + JobCreationRecord
  -> OperationalWorkGenerationService
  -> WorkOrder
  -> Visit
```

Work Orders now preserve:

- job linkage
- job creation record linkage
- review item linkage when present
- audit correlation ID
- generation snapshot
- intake snapshot
- orchestration snapshot
- dispatch eligibility snapshot
- review linkage snapshot
- deterministic evidence snapshot
- lifecycle metadata

Visits now preserve:

- job linkage
- work order linkage
- audit correlation ID
- generation snapshot
- work order snapshot
- review linkage snapshot
- deterministic evidence snapshot
- lifecycle metadata

Generation rules:

- only approved standard jobs in `awaiting_dispatch` can generate standard Work Orders
- blocked jobs, review-required jobs, invalid-lifecycle jobs, and Water Emergency jobs are rejected
- duplicate Work Order generation for the same job is blocked
- duplicate Visit generation for the same Work Order is blocked
- generated Work Orders are scheduling-ready, not dispatched
- generated Visits are awaiting assignment, not assigned or routed

This layer does not execute dispatch, route technicians, assign technicians, schedule visits, call integrations, run background workers, or call AI.

## Assignment And Scheduling Preparation

Phase 0 Module 11 adds deterministic readiness preparation for technician assignment and scheduling.

Current preparation flow:

```text
Generated Visit
  -> AssignmentPreparationService
  -> assignment readiness snapshot
  -> technician compatibility snapshot
  -> scheduling readiness snapshot
  -> operational readiness snapshot
```

Visit readiness snapshots now preserve:

- assignment eligibility
- assignment-required state
- technician active/inactive compatibility
- technician skills, service areas, vehicle label, and availability context
- AM/PM scheduling preference from deterministic normalization evidence
- service state markers from deterministic normalization evidence
- lifecycle blockers
- operational readiness metadata

Preparation rules:

- blocked Visits cannot be prepared for assignment
- review-required Visits cannot be prepared for assignment
- Water Emergency Visits cannot use the standard assignment path
- archived or invalid lifecycle Visits cannot be scheduled
- inactive technician candidates block compatibility
- unassigned Visits without a technician candidate remain `assignment_required`
- compatible technician candidates can move the Visit to `scheduling_ready`

This layer does not assign technicians, set scheduled times, route work, execute dispatch, sync calendars, call integrations, run background workers, or call AI.

## Routing And Dispatch Preparation

Phase 0 Module 12 adds deterministic readiness preparation for future routing and dispatch execution.

Current preparation flow:

```text
Prepared Visit
  -> RoutingDispatchPreparationService
  -> routing readiness snapshot
  -> technician readiness snapshot
  -> Visit dispatch readiness snapshot
  -> dispatch readiness snapshot
```

Visit readiness snapshots now preserve:

- routing readiness and routing blockers
- technician readiness, active/inactive state, skills, service areas, vehicle label, and availability context
- assignment readiness evidence from the Module 11 preparation boundary
- scheduling readiness evidence, AM/PM preference, service-state markers, and scheduled timestamps
- dispatch eligibility and dispatch blockers
- lifecycle state, audit correlation, and deterministic evidence

Preparation rules:

- blocked Visits cannot become dispatch-ready
- review-required lifecycle blocks dispatch preparation
- Water Emergency Visits cannot use the standard routing/dispatch path
- inactive technicians block dispatch readiness
- unscheduled Visits cannot become dispatch-ready
- unassigned Visits cannot become dispatch-ready
- routing-ready and dispatch-ready are preparation states only

This layer does not optimize routes, create route assignments, assign technicians, schedule Visits, execute dispatch, sync calendars, call integrations, run background workers, or call AI.

## Route Assignment And Dispatch Authorization

Phase 0 Module 13 adds the deterministic boundary between dispatch preparation and future dispatch execution.

Current authorization flow:

```text
Dispatch-ready Visit
  -> RouteAssignmentPreparationService
  -> route grouping snapshot
  -> route assignment readiness snapshot
  -> dispatch authorization snapshot
  -> awaiting dispatch execution
```

Route assignments now preserve:

- route grouping key, route date, region, and AM/PM window
- Visit, Job, technician, and audit-correlation references
- route assignment readiness evidence
- technician route compatibility evidence
- dispatch authorization evidence
- dispatch execution boundary evidence
- deterministic evidence snapshots

Authorization rules:

- blocked Visits cannot become dispatch-authorized
- review-required lifecycle blocks dispatch authorization
- Water Emergency Visits cannot use the standard authorization path
- inactive technicians block dispatch authorization
- unscheduled Visits cannot become dispatch-authorized
- unassigned Visits cannot become dispatch-authorized
- route-unready Visits cannot become dispatch-authorized
- authorization moves records to `awaiting_dispatch_execution`; dispatch execution has not run

This layer does not optimize routes, execute dispatch, sync calendars, write Sheets/FastField, call integrations, update technician mobile workflows, run background workers, or call AI.

## Dispatch Execution Foundation

Phase 0 Module 14 adds the deterministic internal dispatch execution lifecycle boundary.

Current execution flow:

```text
Authorized RouteAssignment
  -> DispatchExecutionService
  -> dispatch execution snapshot
  -> dispatch lifecycle snapshot
  -> dispatched
```

Route assignments now preserve:

- dispatch execution state
- dispatch execution snapshot
- dispatch lifecycle snapshot
- dispatch audit snapshot
- dispatched timestamp
- future dispatch-failed timestamp

Execution rules:

- only `awaiting_dispatch_execution` Route Assignments can dispatch
- blocked Visits cannot dispatch
- review-required lifecycle blocks dispatch execution
- Water Emergency Visits cannot use the standard execution path
- inactive technicians block dispatch execution
- unscheduled Visits cannot dispatch
- unassigned Visits cannot dispatch
- unauthorized Route Assignments cannot dispatch
- duplicate dispatch is blocked

This layer updates internal ACS lifecycle state only. It does not call FastField, sync Google Calendar, write Sheets, update technician mobile workflows, call external APIs, run background workers, optimize routes, or call AI.

## External Dispatch Adapter Preparation

Phase 0 Module 15 adds the deterministic boundary between internal dispatch execution and future external systems.

Current preparation flow:

```text
Dispatched RouteAssignment
  -> ExternalDispatchAdapterPreparationService
  -> external adapter request snapshot
  -> external payload snapshot
  -> awaiting external execution
```

Route assignments now preserve:

- external adapter lifecycle state
- adapter execution request snapshot
- adapter payload snapshots for FastField, Google Sheets, Google Calendar, and technician mobile sync
- adapter lifecycle and evidence snapshots
- adapter audit snapshot
- external-adapter prepared timestamp
- future external-adapter failed timestamp

Preparation rules:

- only internally dispatched Visits can prepare external adapter payloads
- blocked Visits cannot prepare external adapter payloads
- review-required lifecycle blocks adapter preparation
- Water Emergency Visits cannot use the standard external adapter path
- unauthorized Route Assignments cannot prepare external adapter payloads
- duplicate adapter preparation is blocked

This layer prepares payload evidence only. It does not call FastField, sync Google Calendar, write Google Sheets, update technician mobile workflows, call external APIs, run background workers, optimize routes, or call AI.

## External Adapter Execution

Phase 0 Module 18 adds the deterministic controlled execution boundary between prepared adapter payloads and external confirmation readiness.

Current execution flow:

```text
Awaiting external execution RouteAssignment
  -> ExternalAdapterExecutionService
  -> provider execution snapshots
  -> awaiting external confirmation or external execution failed
```

Route assignments now preserve:

- external execution lifecycle state
- external execution request snapshot
- provider execution evidence snapshots for FastField, Google Sheets, Google Calendar, and technician mobile sync
- external execution lifecycle, evidence, failure, and audit snapshots
- external execution started, completed, and failed timestamps

Execution rules:

- only prepared Route Assignments awaiting external execution can execute
- duplicate external execution attempts are blocked
- blocked or review-required Visits cannot execute externally
- Water Emergency Visits cannot use the standard external execution path
- unauthorized Route Assignments cannot execute externally
- provider failure records failure evidence but does not run automatic retry

This layer simulates controlled provider execution boundaries only. It does not call FastField, sync Google Calendar, write Google Sheets, update technician mobile workflows, execute retries, run background workers, optimize routes, or call AI.

## External Execution Confirmation And Recovery

Phase 0 Module 16 adds the deterministic resilience boundary after controlled external adapter execution reaches confirmation readiness.

Current confirmation flow:

```text
Awaiting external confirmation RouteAssignment
  -> ExternalExecutionConfirmationService
  -> confirmation, failure, retry, or reconciliation snapshots
  -> externally confirmed, awaiting retry, or reconciliation required
```

Route assignments now preserve:

- external confirmation lifecycle state
- external confirmation evidence snapshot
- external confirmation lifecycle and audit snapshots
- external failure snapshot
- retry preparation snapshot
- reconciliation-required snapshot
- confirmation, failure, retry-prepared, and reconciliation-required timestamps

Confirmation and recovery rules:

- only adapter-prepared Route Assignments awaiting external confirmation can confirm
- duplicate confirmations are blocked
- blocked or review-required Visits cannot confirm
- Water Emergency Visits cannot use the standard external confirmation path
- unauthorized Route Assignments cannot confirm
- retry preparation is allowed only from a failed confirmation state
- reconciliation preparation records evidence but does not run a reconciliation engine

This layer processes simulated external confirmation states and prepares evidence only. It does not call external APIs, execute retries, run reconciliation, update technician mobile workflows, run background workers, optimize routes, or call AI.

## Operational Event History And Immutable Timeline

Phase 0 Module 17 adds the append-only operational history boundary.

Current event flow:

```text
Lifecycle or execution evidence
  -> OperationalEventHistoryService
  -> immutable OperationalEventRecord
  -> route assignment / Visit / dispatch / recovery timeline
```

Operational event records preserve:

- event type and event state
- occurred and recorded timestamps
- entity, Route Assignment, Visit, Work Order, Job, technician, and audit-correlation references
- previous and new lifecycle states
- deterministic event fingerprint for duplicate prevention
- event, transition, immutable evidence, retry/recovery, reconciliation, and audit snapshots

Event-history rules:

- event history is append-only
- duplicate event fingerprints are blocked
- no hidden no-op lifecycle transitions are recorded
- audit correlation is required
- timeline entries are ordered chronologically
- event history records evidence; they do not execute workflows

This layer does not run workflow engines, analytics engines, reconciliation engines, AI orchestration, external integrations, event replay, or mutable history updates.

## Dispatch Reconciliation And Operational Consistency

Phase 0 Module 19 adds deterministic consistency verification and reconciliation preparation.

Current reconciliation flow:

```text
RouteAssignment lifecycle and external evidence
  -> DispatchReconciliationService
  -> consistency, divergence, mismatch, and audit snapshots
  -> consistency verified or reconciliation required
```

Route assignments now preserve:

- dispatch reconciliation lifecycle state
- consistency verification snapshot
- divergence evidence snapshot
- mismatch classification snapshot
- reconciliation blocker snapshot
- reconciliation audit snapshot
- reconciliation prepared, consistency verified, and blocked timestamps

Reconciliation rules:

- immutable operational event history cannot mutate
- Manual Review remains authoritative and cannot be bypassed
- Water Emergency Visits cannot use the standard reconciliation path
- unauthorized Route Assignments cannot reconcile
- duplicate reconciliation preparation is blocked
- invalid lifecycle reconciliation is blocked

This layer prepares consistency and reconciliation evidence only. It does not execute reconciliation, call external APIs, run analytics, replay workflows, mutate event history, execute retries, run background workers, or call AI.

## Operational Replay And Recovery Preparation

Phase 0 Module 20 adds deterministic replay, rollback-preparation, and recovery-coordination evidence after reconciliation has identified divergence or recovery context.

Current replay/recovery flow:

```text
Reconciliation, retry, or failure evidence
  -> OperationalReplayPreparationService
  -> replay eligibility, rollback preparation, recovery coordination, and audit snapshots
  -> replay prepared, rollback prepared, or replay blocked
```

Route assignments now preserve:

- replay/recovery lifecycle state
- replay preparation snapshot
- rollback preparation snapshot
- replay eligibility snapshot
- replay blocker snapshot
- recovery coordination snapshot
- replay/recovery audit snapshot
- replay-prepared, rollback-prepared, and blocked timestamps

Replay/recovery rules:

- immutable operational event history cannot mutate
- Manual Review remains authoritative and cannot be bypassed
- Water Emergency Visits cannot use the standard replay/recovery path
- unauthorized Route Assignments cannot prepare replay or rollback
- duplicate replay preparation is blocked
- invalid lifecycle replay preparation is blocked

This layer prepares recovery evidence only. It does not execute replay, execute rollback, call external APIs, run automatic retries, run workflow engines, mutate event history, or call AI.

## Operational Governance And Approval Control

Phase 0 Module 21 adds deterministic operator governance and approval-control evidence after replay/recovery preparation.

Current governance flow:

```text
Replay / rollback / reconciliation preparation
  -> OperationalGovernanceService
  -> operator approval, intervention authorization, and governance audit snapshots
  -> operator approved, intervention required, or governance blocked
```

Route assignments now preserve:

- governance lifecycle state
- governance approval snapshot
- intervention authorization snapshot
- replay authorization snapshot
- rollback authorization snapshot
- reconciliation approval snapshot
- governance blocker snapshot
- governance audit snapshot
- governance approved, rejected, intervention-required, and blocked timestamps

Governance rules:

- replay cannot execute without governance approval
- rollback cannot execute without governance approval
- reconciliation cannot bypass Manual Review
- Water Emergency Visits cannot use the standard governance path
- unauthorized operator actions are blocked
- duplicate governance approval is blocked
- immutable operational event history cannot mutate

This layer authorizes future operator-controlled actions only. It does not execute replay, execute rollback, execute reconciliation, call external APIs, run workflow engines, mutate event history, approve automatically, or call AI.

## Operational Accountability, Escalation, And Incident Preparation

Phase 0 Module 22 adds deterministic accountability and escalation preparation after governance approval.

Current accountability flow:

```text
Governed replay / rollback / reconciliation / divergence context
  -> OperationalAccountabilityService
  -> escalation, intervention-escalation, incident, and accountability audit snapshots
  -> escalation required, incident prepared, critical intervention required, or accountability blocked
```

Route assignments now preserve:

- accountability lifecycle state
- escalation preparation snapshot
- incident preparation snapshot
- accountability evidence snapshot
- escalation blocker snapshot
- intervention escalation snapshot
- operational incident snapshot
- accountability audit snapshot
- escalation-required, incident-prepared, critical-intervention-required, and blocked timestamps

Accountability rules:

- replay and recovery escalation cannot bypass governance approval
- critical divergence requires escalation preparation
- Water Emergency Visits cannot use the standard accountability path
- unauthorized intervention escalation is blocked
- duplicate escalation or incident preparation is blocked
- immutable operational event history cannot mutate

This layer prepares accountability evidence only. It does not execute escalation, execute incident workflows, execute intervention workflows, call external APIs, run workflow engines, mutate event history, approve automatically, or call AI.

## Safety Rules

- Database is the source of truth.
- Manual Review is a core safety system.
- AI is advisory only.
- External systems are adapters only.
- Uncertain jobs must never auto-dispatch.
