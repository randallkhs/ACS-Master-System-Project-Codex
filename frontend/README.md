# ACS Frontend Foundation

Phase 1 Readiness Module 62 keeps the frontend foundation read-only and adds no frontend behavior changes. The module adds production infrastructure readiness documentation under `docs/obsidian-vault/` for future environment separation, deployment boundaries, secret-management expectations, backup/restore planning, monitoring planning, and production cutover prerequisites.

The Module 60 frontend foundation remains read-only while showing Phase 0 auth boundary completion and future cutover readiness visibility on top of the backend/frontend auth status bridge, frontend auth-core disabled session, API auth-boundary visibility, existing backend auth-core disabled scaffold visibility, Auth/RBAC readiness audit, enforcement-boundary lock, future transition prerequisite visibility, route protection matrix, access decision dry-run, UI permission-boundary readiness, Manual Review auth-boundary readiness, auth configuration readiness, auth diagnostics/runtime safety visibility, auth claims mapping, token-verification dry-run boundary, role-resolution readiness, safe secret-hygiene status, auth header disabled status, explicit disabled auth/token/RBAC status, operator identity registry field visibility, provisional role catalog visibility, future permission catalog visibility, queue filtering, sorting, browser-only saved view preferences, queue result metadata, decision-readiness context, action-preflight context, future-action preview context, future command-contract context, audit-ledger dry-run context, command-validation/safety-gate context, permission-readiness context, execution-readiness audit, mutation-boundary lock, future transition prerequisites, and owner-review guardrails.

The frontend is read-only. It consumes backend dashboard read-model contracts and does not execute dispatch, integrations, Manual Review resolution, AI decisions, or any operational mutation.

## Module 62 Documentation Alignment Notes

Module 62 does not add deployment UI, server controls, secret inputs, login UI, logout UI, user-management UI, route protection, token/session behavior, Authorization headers, action controls, mutation calls, dispatch execution, vendor calls, AI authority, or workflow execution. Production readiness guidance is captured in:

- `docs/obsidian-vault/00-Phase-1-Production-Infrastructure-Readiness.md`
- `docs/obsidian-vault/00-Phase-Roadmap.md`
- `docs/obsidian-vault/00-ACS-FSM-Risk-Register.md`

## Module 61 Documentation Alignment Notes

Module 61 does not add login UI, logout UI, user-management UI, route protection, token/session behavior, Authorization headers, action controls, mutation calls, dispatch execution, vendor calls, AI authority, or workflow execution. Frontend transition guidance is captured in:

- `docs/obsidian-vault/00-ACS-FSM-Master-System-Overview.md`
- `docs/obsidian-vault/00-Phase-Roadmap.md`
- `docs/obsidian-vault/00-Phase-0-Completion-Checklist.md`
- `docs/obsidian-vault/00-ACS-FSM-Risk-Register.md`

## Stack

- Next.js App Router
- TypeScript
- Tailwind CSS
- Vitest for lightweight contract and render checks

## Setup

```bash
npm install
cp .env.example .env.local
npm run dev
```

Set `ACS_DASHBOARD_API_BASE_URL` to the backend origin when using live backend data.

Local full-stack example:

```bash
ACS_DASHBOARD_API_BASE_URL=http://127.0.0.1:8000
```

If the variable is unset, or the backend is unavailable, the dashboard uses typed local fallback data and clearly marks the screen as mock/fallback state.

## Full-Stack Local Development

Use two terminals.

Backend:

```bash
cd backend
make dev
```

Expected backend origin:

```text
http://127.0.0.1:8000
```

Frontend:

```bash
cd frontend
cp .env.example .env.local
# set ACS_DASHBOARD_API_BASE_URL=http://127.0.0.1:8000
npm run dev
```

Expected frontend origin:

```text
http://127.0.0.1:3000
```

Dashboard route:

```text
http://127.0.0.1:3000/dashboard
```

Live backend dashboard endpoints:

```text
GET http://127.0.0.1:8000/api/v1/dashboard/overview
GET http://127.0.0.1:8000/api/v1/dashboard/lifecycle
GET http://127.0.0.1:8000/api/v1/dashboard/review
GET http://127.0.0.1:8000/api/v1/dashboard/dispatch
GET http://127.0.0.1:8000/api/v1/dashboard/water-emergency
GET http://127.0.0.1:8000/api/v1/dashboard/water-emergency/{water_emergency_id}
GET http://127.0.0.1:8000/api/v1/auth/status
```

The backend requires a configured local PostgreSQL database for live dashboard reads. If the backend is stopped, unavailable, unmigrated, or returns an error, the frontend displays typed fallback data and marks the page as mock/fallback state.

For live local data:

```bash
cd backend
cp .env.example .env
# confirm ACS_FSM_DATABASE_URL points to acs_fsm_dev on 127.0.0.1
make migrate
make seed-dashboard
make dev
```

Then run the frontend with:

```bash
cd frontend
cp .env.example .env.local
# set ACS_DASHBOARD_API_BASE_URL=http://127.0.0.1:8000
npm run dev
```

When the backend is reachable and migrated, the dashboard source indicator should show live backend/API data. When the backend cannot serve the read models, fallback remains visible and labeled.

## Verification

```bash
npm run lint
npm run typecheck
npm run test
npm run build
```

Or run the frontend verification bundle:

```bash
npm run verify
```

Browser QA should include `/dashboard` at desktop, laptop, and mobile widths. Use the production server after `npm run build` for final screenshot checks so development-only framework badges do not cover mobile content.

## Architecture Rules

- The frontend displays backend read models only.
- Backend services remain the source of workflow/business logic.
- API client helpers are read-only `GET` calls.
- No mutation endpoints, dispatch execution, vendor integration calls, or AI authority are implemented.
- Route protection and access decision panels are read-only planning visibility; they do not enforce auth, RBAC, route guards, token parsing, JWT validation, or section hiding.
- Frontend auth helpers are disabled Phase 0 scaffolding only; they create no session, store no token, emit no Authorization header, hide no UI, and grant no action authority.
- The auth status bridge is read-only visibility only; it does not create a login status, parse Authorization headers, report authenticated users, guard routes, or grant action authority.
- Manual Review remains authoritative and cannot be bypassed from the UI.
- Water Emergency remains first-class and is displayed as separated operational state where the backend contract exposes it.

## Current Dashboard Views

- Operational health and safety readiness summary
- Live scenario storyboard for local seed verification context
- Dedicated Water Emergency command view
- Water Emergency detail and evidence timeline view
- Water Emergency equipment, visit-chain, and drying-stage visibility panels
- Water Emergency review/exception, blocker, and critical-alert visibility panels
- Water Emergency next-step readiness and evidence panels
- Water Emergency operator queue and attention triage panel
- Water Emergency aging and follow-up risk visibility panel
- Water Emergency filter/sort view-state panel with frontend-only saved preferences
- Water Emergency Randall-authorized Phase 0 baseline and Alfonso owner-review boundary notes
- Manual Review queue filter/sort view-state panel with frontend-only saved preferences
- Manual Review auth claims mapping and role-resolution readiness panels with token parsing and JWKS fetch disabled
- Manual Review route protection matrix and access decision dry-run panels with enforcement, route guarding, token verification, and RBAC disabled
- Manual Review auth-core disabled scaffold labels showing the backend auth core, disabled token verifier, and optional auth context exist for future modules while current routes still do not require auth
- Manual Review frontend auth-boundary labels showing frontend auth disabled, session unavailable, token unavailable, token verification disabled, Authorization headers not emitted, and no Manual Review or Water Emergency action authority granted
- Manual Review cross-layer auth status bridge labels showing backend auth disabled, frontend auth disabled, backend auth headers not required, frontend auth headers not emitted, Authorization headers not parsed or authoritative, route protection not enforced, RBAC not enforced, and action authority unavailable
- Manual Review Phase 0 auth boundary completion and future cutover readiness labels showing the scaffold complete, future auth cutover not ready, current routes accessible without auth, frontend Authorization headers not emitted, and future prerequisites still blocked
- Manual Review action-preflight visibility for future operator identity, audit reason, auth, and blocker preparation
- Manual Review future-action preview visibility for expected non-binding outcomes, impacted entities, and future operator identity/audit reason requirements
- Manual Review future command-contract visibility for future auth, operator identity, role authorization, audit reason, idempotency key, immutable event recording, and post-action consistency check requirements
- Operational overview
- Dispatch lifecycle summary
- Manual Review summary
- Route assignment summary
- External execution summary
- Reconciliation and recovery summary
- Governance and accountability summary
- Operational event timeline preview

## Module 25 Visual QA Notes

- The first viewport now prioritizes read-only/fallback safety notices followed by an operational health summary.
- Safety, blocker, dispatch-ready, and Water Emergency signals are grouped before detailed dashboard sections.
- Responsive navigation remains link-only and wraps into a two-column mobile grid.
- Dashboard tests assert the API client stays `GET`-only and the rendered dashboard does not expose operational action buttons.
- Empty, fallback, and read-only states remain visible without creating fake workflow controls.

## Module 26 Integration Notes

- `ACS_DASHBOARD_API_BASE_URL` is server-side only and is not exposed through a `NEXT_PUBLIC_` variable.
- Local full-stack development uses `http://127.0.0.1:8000` for the FastAPI backend and `http://127.0.0.1:3000` for the Next.js frontend.
- Production deployments must set an environment-specific HTTPS backend origin rather than hardcoding localhost.
- The frontend API client only calls dashboard `GET` endpoints and uses `cache: "no-store"` for live read-model reads.
- Fallback data is for local development/layout continuity only and must remain visibly labeled in the UI.

## Module 27 Live Data Notes

- Live dashboard verification expects backend migrations to be applied to the local `acs_fsm_dev` PostgreSQL database.
- Optional backend seed data is synthetic, source-labeled, and intended only to exercise read-only dashboard states.
- The frontend should show `Live backend` only when all dashboard read models are fetched successfully from the configured backend.
- The frontend still has no mutation controls, dispatch actions, Manual Review actions, vendor execution controls, or AI controls.

## Module 29 Live Seed Notes

- The backend seed now provides broader synthetic examples for dispatch-ready, blocked, external execution, confirmation/recovery, reconciliation, governance/accountability, timeline, and Water Emergency separation states.
- These examples are for local dashboard data quality checks only and must not be treated as production/customer/vendor data.
- Browser verification should confirm `Live backend` is visible, `Mock fallback` is absent, seeded categories appear in the dashboard text, and no form/button/action controls are rendered.

## Module 30 Storyboard Notes

- The dashboard now includes a `Scenario Storyboard` section that groups existing backend read-model counts into local seed scenario families.
- Storyboard cards are display-only context for dispatch-ready work, Manual Review, blockers, external execution, recovery/reconciliation, governance/accountability, Water Emergency separation, and immutable timeline evidence.
- The storyboard does not introduce new API fields, lifecycle inference, mutation controls, dispatch actions, Manual Review actions, vendor calls, or AI controls.
- Mobile and desktop anchor navigation use scroll margins so sticky dashboard headers do not cover storyboard and timeline sections.

## Module 31 Water Emergency Notes

- The dashboard now fetches `GET /api/v1/dashboard/water-emergency` alongside the overview read model.
- The Water Emergency view is visually separated from standard dispatch and shows open/closed state, status/stage distribution, equipment and moisture-tracking indicators, multi-visit indicators, related references, review/escalation indicators, data gaps, and emergency timeline evidence.
- The Water Emergency view is display-only. It does not create, close, resolve, dispatch, approve, or execute Water Emergency work.
- The top source indicator shows live backend status only when both the overview and Water Emergency read models are fetched successfully; each Water Emergency section also labels live versus fallback state.

## Module 32 Water Emergency Detail Notes

- The dashboard now selects the first open Water Emergency record from the summary contract and fetches `GET /api/v1/dashboard/water-emergency/{water_emergency_id}` for read-only detail visibility.
- The detail section shows the focused record status/stage, related job/work-order/visit references, scoped Manual Review indicators, detail data gaps, audit references, and chronological evidence timeline entries.
- Detail fallback data remains typed local development data and is visibly labeled when the backend detail endpoint is unavailable.
- The detail view is still display-only. It does not create, edit, close, resolve, dispatch, approve, execute vendor calls, or add AI authority.

## Module 33 Water Emergency Visibility Notes

- The Water Emergency summary now displays backend-provided equipment context, visit-chain summary, and drying-stage visibility panels.
- The detail section now displays backend-provided equipment notes, inventory-modeling unknowns, visit-chain timing/status counts, and drying-stage context.
- Equipment visibility is not inventory management. The frontend shows existing flags, work-order equipment notes, and explicit unknown indicators only.
- Visit-chain visibility is not dispatch execution. Water Emergency visits remain separated from standard dispatch action counts and no action buttons are rendered.
- Drying-stage visibility uses persisted status/stage fields only and does not infer final drying taxonomy, closure readiness, pickup approval, or field authority.

## Module 34 Water Emergency Review Notes

- The Water Emergency summary now displays backend-provided review/exception counts, blocker reason buckets, critical-alert indicators, review IDs, and unknown review signals.
- The detail section now displays backend-provided scoped review/exception context for the selected Water Emergency record.
- Review visibility is not Manual Review action authority. The frontend does not approve, reject, resolve, close, dispatch, or clear Water Emergency records.
- Blocker and critical labels are derived from persisted review status/severity/reason evidence only and do not define the final Water Emergency escalation taxonomy.
- Generic Water Emergency review labels remain dashboard-level context only; detail visibility depends on specific job/entity/visit linkage from the backend contract.

## Module 35 Water Emergency Readiness Notes

- The Water Emergency summary now displays backend-provided next-step readiness labels, blocker/reason buckets, attention counts, and per-record readiness previews.
- The detail section now displays backend-provided readiness labels, explanation text, review/critical/blocker/unknown counts, and evidence references for the selected Water Emergency record.
- Readiness visibility is decision context only. The frontend does not create, close, approve, dispatch, schedule, resolve, replay, or advance Water Emergency records.
- `ready_for_close_review` is displayed only as a read-only signal from persisted status/stage/evidence. It is not a close action and does not imply final closure rules.
- Missing-data, Manual Review, equipment, visit-chain, and drying-stage readiness labels remain backend-owned and do not define the final Water Emergency operating taxonomy.

## Module 36 Water Emergency Queue Notes

- The Water Emergency summary now displays a backend-provided Operator Queue panel with active attention, critical attention, closed/resolved, queue-group, and attention-label counts.
- Queue items are derived from backend readiness evidence only. They show attention labels, reasons, review/critical/blocker/unknown counts, related job/visit references, and audit evidence without adding workflow controls.
- Closed or resolved Water Emergency records are displayed separately from active attention items.
- Critical alerts and Manual Review evidence remain visibility signals only. The frontend does not prioritize work as operational authority, dispatch Water Emergency visits, approve reviews, close records, or execute vendor/AI calls.
- The queue labels are not the final ACS operations taxonomy; future authenticated workflow modules still need Luis-confirmed rules and operator authority design.

## Module 37 Water Emergency Aging Notes

- The Water Emergency summary now displays a backend-provided Aging & Follow-Up Risk panel with active timing risk, follow-up due/overdue, stale evidence, unknown timing, and closed/resolved counts.
- Timing items are derived from backend timestamp evidence only. They show time-sensitivity labels, timing groups, age/follow-up buckets, reason codes, missing timestamp indicators, related references, and audit evidence without adding workflow controls.
- Closed or resolved Water Emergency records are displayed separately from active timing risks and are not shown as active overdue work.
- Aging visibility is not an SLA engine. The frontend does not schedule follow-ups, escalate work, approve reviews, close records, dispatch Water Emergency visits, or execute vendor/AI calls.
- Timing labels are not the final ACS operations taxonomy; future authenticated workflow modules still need Luis-confirmed SLA/follow-up rules and operator authority design.

## Module 38 Water Emergency View-State Notes

- The Water Emergency summary displays backend-provided filter groups, sort options, group counts, and per-record view-state items.
- Filter and sort controls change only frontend display state. They do not call mutation endpoints, store backend operational state, approve work, close records, dispatch visits, or escalate records.
- Closed/resolved records remain visually separated from active records even when active lists are limited.
- Filter labels are Phase 0 visibility categories, not final ACS operating taxonomy.

## Module 39 Water Emergency Governance And Saved-View Notes

- The Water Emergency dashboard now displays a subtle Randall-authorized Phase 0 visibility baseline note for internal labels, filters, timing heuristics, readiness groups, and view-state defaults.
- The frontend can persist only the selected Water Emergency filter and sort option in browser localStorage. It stores no tokens, secrets, PII, customer data, backend records, or operational workflow state.
- If localStorage is unavailable, the dashboard falls back to safe defaults without blocking the read-only view.
- Legal, insurance, warranty, drying certification, SLA enforcement, customer-facing promises, or company-liability policies remain outside the software baseline and require Alfonso owner review before finalization.
- Future role-scoped visibility is documented only; the frontend does not implement auth, RBAC, fake roles, or hidden authorization behavior.

## Module 40 Manual Review Queue Notes

- The dashboard now fetches `GET /api/v1/dashboard/manual-review/queue` for detailed read-only Manual Review visibility.
- The Manual Review Queue panel shows status, reason, severity, visibility group, age bucket, attention, blocker, entity-context, audit, and evidence-reference data from the backend read model.
- Water Emergency-related review items are visually separated from standard dispatch and other review items.
- Review taxonomy labels are shown as a Randall-authorized Phase 0 visibility baseline only. They are not final action authority, legal policy, insurance language, or company-liability policy.
- The frontend still does not render approve, reject, defer, archive, resolve, dispatch, vendor, or AI controls.

## Module 41 Manual Review Detail Notes

- The dashboard now fetches `GET /api/v1/dashboard/manual-review/queue/{review_item_id}` for a selected Manual Review detail record when one is available.
- The Manual Review detail panel shows the selected review summary, reason/evidence context, linked entity context, Water Emergency separation when applicable, data-gap indicators, audit references, and backend-ordered timeline evidence.
- A live 404 for the detail endpoint renders a safe not-found/null detail state instead of substituting mock detail data.
- The detail panel is read-only and does not add approve, reject, defer, archive, resolve, dispatch, vendor, or AI controls.

## Module 42 Manual Review Filter And Saved-View Notes

- The Manual Review Queue now displays read-only filter and sort controls backed by backend-provided filter options, sort options, counts, and result-window metadata.
- Filters can isolate open, deferred, resolved, archived, active-attention, Water Emergency-related, dispatch-related, missing-data, duplicate/conflict, cancellation/status-uncertainty, and needs-operator-review records without changing backend state.
- The selected Manual Review filter and sort option can persist only in browser localStorage. The preference stores no tokens, secrets, PII, customer data, backend records, or operational workflow state.
- If localStorage is unavailable, the dashboard falls back to in-memory defaults without blocking Manual Review visibility.
- The UI still does not add approve, reject, defer, archive, resolve, dispatch, vendor, AI, auth, RBAC, or workflow execution controls.

## Module 43 Manual Review Decision-Readiness Notes

- The Manual Review Queue and detail panel now display backend-provided decision-readiness labels, summaries, reason codes, and evidence references.
- Readiness labels explain whether a review needs missing information, entity context, Water Emergency review, dispatch review, conflict resolution preparation, future operator decision review, or historical visibility.
- Water Emergency-related readiness remains visibly separated from standard dispatch Manual Review readiness.
- Resolved and archived review items are shown as historical visibility instead of active decision needs.
- The UI still does not add approve, reject, defer, archive, resolve, dispatch, vendor, AI, auth, RBAC, or workflow execution controls.

## Module 44 Manual Review Action-Preflight Notes

- The Manual Review Queue and detail panel now display backend-provided action-preflight labels, blocker codes, future requirement labels, and evidence references.
- Preflight labels explain whether a future Manual Review action is blocked by missing entity context, missing data, duplicate/conflict evidence, Water Emergency context, resolved/archived status, or unknown action eligibility.
- Future authorization requirements are displayed as read-only text only: future auth, operator identity, and audit reason capture are not implemented as controls.
- Water Emergency-related action preflight remains visibly separated from standard Manual Review action-preparation context.
- The UI still does not add approve, reject, defer, archive, resolve, dispatch, vendor, AI, auth, RBAC, or workflow execution controls.

## Module 45 Manual Review Future-Action Preview Notes

- The Manual Review Queue and detail panel now display backend-provided future-action preview labels, expected non-binding outcome summaries, impacted entity summaries, blocker labels, future requirement labels, and evidence references.
- Preview labels explain whether future action preparation points toward approve, reject, defer, archive, resolve, request-information, operator-decision, or no-action states because of missing entity context, conflict, Water Emergency context, resolved/archived status, or unknown evidence.
- Future operator identity and audit reason requirements are displayed as read-only text only. They are not authentication controls, RBAC controls, forms, buttons, or mutation triggers.
- Water Emergency-related future-action preview remains visibly separated from standard Manual Review action-preparation context.
- Preview labels are not styled as buttons and are never currently executable in Phase 0.
- The UI still does not add approve, reject, defer, archive, resolve, dispatch, vendor, AI, auth, RBAC, or workflow execution controls.

## Module 46 Manual Review Future Command-Contract Notes

- The Manual Review Queue and detail panel now display backend-provided future command-contract labels, audit-envelope requirements, command blockers, impacted entity summaries, and evidence references.
- Command-contract labels explain future-only requirements for auth, operator identity, role authorization, audit reason, idempotency key, immutable event recording, post-action consistency checks, preflight pass, entity context, no conflict blocker, and Water Emergency scope checks.
- Every command contract renders as `Currently executable: No` in Phase 0. These labels are not buttons, forms, inputs, mutation controls, auth controls, RBAC controls, or action execution controls.
- Water Emergency-related command contract context remains visibly separated from standard Manual Review command preparation.
- The UI still does not add approve, reject, defer, archive, resolve, dispatch, vendor, AI, auth, RBAC, workflow execution controls, or future command data-entry fields.

## Module 47 Manual Review Audit-Ledger Dry-Run Notes

- The Manual Review Queue and detail panel now display backend-provided audit-ledger dry-run labels, proposed future event type/state, proposed audit envelope fields, idempotency scope, consistency-check summary, audit/evidence references, and explicit non-executable flags.
- Dry-run labels explain future-only requirements for audit reason, operator identity, role authorization, idempotency key, immutable event recording, and post-action consistency checks before any later mutation module is allowed.
- Every dry-run record renders as `Currently executable: No` and `Phase allows execution: No` in Phase 0. These labels are not buttons, forms, inputs, mutation controls, auth controls, RBAC controls, audit-write controls, or action execution controls.
- Water Emergency-related dry-run context remains visibly separated from standard Manual Review command preparation.
- The UI still does not add approve, reject, defer, archive, resolve, dispatch, vendor, AI, auth, RBAC, workflow execution controls, audit forms, command forms, or future command data-entry fields.

## Module 48 Manual Review Command-Validation Notes

- The Manual Review Queue and detail panel now display backend-provided command-validation labels, validation blockers, validation warnings, candidate future command type, explicit non-executable flags, and a read-only safety gate matrix.
- Safety gates show whether entity context, active status, Water Emergency scope, conflict review, missing-data review, operator identity, role authorization, audit reason, idempotency key, immutable event recording, post-action consistency check, and Phase 0 execution allowance are present or required.
- Every validation record renders as `Currently executable: No` and `Phase allows execution: No` in Phase 0. These labels are not buttons, forms, inputs, mutation controls, auth controls, RBAC controls, validation execution controls, audit-write controls, or action execution controls.
- Water Emergency-related command validation remains visibly separated from standard Manual Review validation context.
- The UI still does not add approve, reject, defer, archive, resolve, dispatch, vendor, AI, auth, RBAC, workflow execution controls, audit forms, command forms, or future command data-entry fields.

## Module 49 Manual Review Operator-Identity And Permission-Readiness Notes

- The Manual Review Queue and detail panel now display backend-provided permission-readiness labels, future required roles, future forbidden roles, future permission sets, identity requirement labels, audit/evidence references, and explicit non-executable flags.
- Permission-readiness visibility explains that future Manual Review commands will require authenticated operator identity, role authorization, audit actor capture, audit reason, idempotency key, immutable event recording, and post-action consistency checks before any later action module can exist.
- Every permission-readiness record renders as `Currently executable: No` and `Phase allows execution: No` in Phase 0. These labels are not buttons, forms, inputs, login controls, user-management controls, mutation controls, auth controls, RBAC controls, audit-write controls, or action execution controls.
- Water Emergency-related authorization requirements remain visibly separated from standard Manual Review authorization planning.
- The UI still does not add login, signup, user management, approve, reject, defer, archive, resolve, dispatch, vendor, AI, auth, RBAC, workflow execution controls, audit forms, command forms, or future command data-entry fields.

## Module 50 Manual Review Execution-Readiness Audit Notes

- The Manual Review Queue now displays backend-provided execution-readiness audit counts, a mutation-boundary lock, future transition prerequisites, and Alfonso owner-review guardrails as read-only operational visibility.
- The mutation-boundary panel renders `Manual Review mutations disabled`, `read_only_phase_0`, `currently_executable_count = 0`, and mutation endpoints unavailable. These labels are not buttons, forms, inputs, login controls, user-management controls, mutation controls, auth controls, RBAC controls, audit-write controls, or action execution controls.
- Future prerequisites remain grouped as visibility for auth/RBAC, audit envelope, idempotency, immutable event, consistency check, action-contract, frontend action UI, ACSSDR report workflow, Review GUI/ChatGPT review workflow, and Alfonso owner review. They do not mark Manual Review mutation readiness as satisfied.
- Water Emergency-related readiness counts remain separate from standard Manual Review counts.
- The UI still does not add login, signup, user management, approve, reject, defer, archive, resolve, dispatch, vendor, AI, auth, RBAC, workflow execution controls, audit forms, command forms, or future command data-entry fields.

## Module 51 Manual Review Auth-Boundary Readiness Notes

- The Manual Review Queue and detail panel now display backend-provided auth-boundary readiness metadata as read-only operational visibility.
- The auth-boundary panel renders `auth_implemented = false`, `rbac_enforced = false`, sign-in UI unavailable, action execution unavailable, metadata-only operator registry mode, service accounts blocked for Manual Review actions, and future auth/RBAC/audit-actor requirements.
- The operator identity registry fields, provisional roles, and future permissions are planning labels only. They do not persist operator identities, enforce roles, hide/show UI based on roles, add auth headers, create token/session behavior, or authorize Manual Review actions.
- Service accounts, technicians, and unknown operators remain blocked for future Manual Review operator actions unless a later reviewed module explicitly changes that boundary.
- The UI still does not add login, signup, user management, role assignment, approve, reject, defer, archive, resolve, dispatch, vendor, AI, auth, RBAC, workflow execution controls, audit forms, command forms, or future command data-entry fields.

## Module 52 Auth Configuration Readiness Notes

- The Manual Review Queue and detail panel now display backend-provided auth configuration readiness as read-only operational visibility.
- The auth configuration panel renders `auth_provider = disabled`, token verification disabled, RBAC enforcement disabled, local dev auth mode disabled, committed credentials not allowed, real credentials required later, and future provider selection required.
- Backend placeholders such as `ACS_FSM_AUTH_PROVIDER` and frontend placeholders such as `NEXT_PUBLIC_ACS_AUTH_ENABLED` are shown as safe planning labels only.
- `frontend/.env.example` lists public future auth placeholders only. These do not enable login, logout, token/session behavior, auth headers, fake users, role assignment, or current RBAC behavior.
- The UI still does not add login, logout, signup, user management, role assignment, approve, reject, defer, archive, resolve, dispatch, vendor, AI, auth enforcement, RBAC enforcement, workflow execution controls, audit forms, command forms, or future command data-entry fields.

## Module 53 Auth Diagnostics And Secret Hygiene Notes

- The Manual Review Queue and detail panel now display read-only auth diagnostics showing auth disabled, token verification disabled, RBAC disabled, auth headers not required, frontend auth headers not emitted, and runtime auth mode `read_only_phase_0`.
- Secret-hygiene status is shown only as safe booleans: no tracked `.env`, no tracked `.env.local`, no tracked service account JSON, private key not detected, and placeholder values only.
- The frontend does not render secret values, does not add login/logout/user-management controls, does not add token/session behavior, and does not add auth headers to the dashboard API client.

## Module 54 Auth Claims Mapping And Role Resolution Notes

- The Manual Review Queue and detail panel display read-only future auth claims, role-resolution, and token-verification dry-run readiness.
- Token verification, real token parsing, JWKS fetch, auth headers, and RBAC enforcement remain disabled. Claim, role, and permission labels are not clickable controls and do not hide or unlock UI.
- Safe example claim fixtures contain placeholder domains only and do not render real users, credentials, tokens, JWT samples, private keys, or service account JSON.

## Module 55 Route Protection Matrix And Access Decision Dry-Run Notes

- The Manual Review Queue and detail panel display backend-provided route protection matrix and access decision dry-run visibility.
- Future API routes, frontend sections, and future action surfaces are mapped to future role and permission labels only. Enforcement, Phase 0 enforcement allowance, route guarding, token verification, and RBAC enforcement remain disabled.
- Route, permission, and access labels are read-only evidence. They do not deny routes, hide sections, emit auth headers, add JWT parsing, or create action authority.

## Module 56 Auth/RBAC Readiness Audit Notes

- The Manual Review Queue panel now displays the Auth/RBAC readiness audit, enforcement-boundary lock, and future transition prerequisites as read-only operational visibility.
- The audit shows auth enforcement disabled, token verification disabled, real token parsing disabled, JWKS fetch disabled, RBAC enforcement disabled, route guarding disabled, sign-in UI unavailable, user management unavailable, Manual Review actions unavailable, and Water Emergency actions unavailable.
- Future prerequisites are grouped by provider selection, real credentials/secret hygiene, token verification, claims mapping, operator identity, RBAC/role policy, route protection, Manual Review action permissions, Water Emergency action permissions, audit actor/idempotency, legal/owner review, and review workflow.
- The UI still does not add login/logout/signup/user-management controls, role assignment, forms, inputs, auth headers, token/session behavior, route guards, section hiding, approve/reject/defer/archive controls, dispatch controls, vendor calls, AI controls, or executable readiness labels.

## Module 57 Backend Auth Core Disabled Scaffold Notes

- The Manual Review Queue panel now displays backend auth-core scaffold, disabled token verifier, optional auth context, current-route auth requirement, route-protection enforcement, Manual Review authority, and Water Emergency authority labels as read-only operational visibility.
- The labels show that the backend auth core exists for future modules, but current routes still do not require auth, token verification remains disabled, route protection is not enforced, and no Manual Review or Water Emergency action authority is granted.
- The UI still does not add login/logout/signup/user-management controls, role assignment, forms, inputs, auth headers, token/session behavior, JWT parsing, route guards, section hiding, approve/reject/defer/archive controls, dispatch controls, vendor calls, AI controls, or executable readiness labels.

## Module 58 Frontend Auth Core Disabled Session Notes

- The new `src/lib/auth/` module defines frontend auth/session/principal/token-state types for future modules while returning a deterministic disabled Phase 0 session today.
- `getDisabledFrontendAuthSession()` and `getAnonymousPhase0Principal()` report auth disabled, unauthenticated, session unavailable, token unavailable, token verification disabled, RBAC unenforced, route protection unenforced, and no Manual Review or Water Emergency action authority.
- `frontendAuthHeadersForRequest()` returns an empty header object in Phase 0. The dashboard API client remains `GET`-only and does not emit `Authorization` or lowercase `authorization` headers.
- The Manual Review Queue displays a read-only Frontend Auth Boundary panel for disabled session/token/API auth state. It does not add sign-in/sign-out UI, user management, role assignment, token storage, JWT parsing, UI hiding, or mutation controls.

## Module 59 Backend/Frontend Auth Status Bridge Notes

- The dashboard now fetches `GET /api/v1/auth/status` as a read-only disabled auth status bridge when a backend base URL is configured.
- The auth status API client call remains GET-only and emits no `Authorization` or lowercase `authorization` headers.
- The Manual Review Queue displays cross-layer backend/frontend auth status visibility: backend auth disabled, frontend auth disabled, auth headers not required/emitted, Authorization headers not parsed or authoritative, route protection not enforced, RBAC not enforced, and no Manual Review or Water Emergency action authority.
- If the auth status endpoint is unavailable, the frontend fallback remains disabled and does not report authentication success, token verification success, RBAC success, route protection, or action authority.
- The UI still does not add login/logout/signup/user-management controls, role assignment, token/session storage, JWT parsing, section hiding, approve/reject/defer/archive controls, dispatch controls, vendor calls, AI controls, or executable readiness labels.

## Module 60 Auth Boundary Completion And Cutover Readiness Notes

- The Manual Review Queue now displays a read-only Phase 0 Auth Boundary Complete panel sourced from the disabled backend auth status response or disabled fallback status.
- The panel shows that future auth cutover is not ready, current routes remain accessible without auth, frontend Authorization headers are not emitted, Manual Review and Water Emergency action authority are not granted, and mutation endpoints remain unavailable.
- Future cutover prerequisites remain visible as planning labels for provider selection, real credentials outside Git, secret management, token verification, JWKS policy, frontend sign-in/sign-out UX, operator identity, RBAC, route guarding, Manual Review action permissions, Water Emergency owner review, audit actor, idempotency, immutable events, consistency checks, staging smoke testing, ACSSDR reporting, and Review GUI/ChatGPT review.
- Current route accessibility audit labels are read-only and do not guard routes, hide sections, deny access, or create current permission authority.
- The UI still does not add login/logout/signup/user-management controls, role assignment, token/session storage, JWT parsing, Authorization headers, section hiding, approve/reject/defer/archive controls, dispatch controls, vendor calls, AI controls, mutation controls, or executable readiness labels.

## Module 38 Water Emergency View-State Notes

- The Water Emergency summary now displays a `Water Emergency View State` panel with backend-provided filter options, sort options, selected group counts, active visible records, and closed/resolved visible records.
- Filter and sort controls are frontend view-state controls only. They do not call mutation endpoints, persist preferences, approve reviews, dispatch visits, close records, escalate work, call vendors, or call AI.
- Closed or resolved Water Emergency records remain visually separated from active records even when filters and active-list limits are used.
- View-state records combine backend queue labels, aging/follow-up labels, readiness labels, review/critical/blocker/unknown counts, last-activity timestamps, related references, and evidence references.
- Filter labels are not the final ACS operations taxonomy; future authenticated workflow modules still need Luis-confirmed triage/filter rules, role-scoped visibility, and production pagination decisions.

## Troubleshooting

- If the dashboard shows `Mock fallback`, confirm `frontend/.env.local` contains `ACS_DASHBOARD_API_BASE_URL=http://127.0.0.1:8000`.
- If the backend endpoint returns an error, confirm the backend server is running and the local PostgreSQL database is configured, migrated, and optionally seeded.
- If browser requests are added in the future, configure backend CORS explicitly; the current dashboard reads happen server-side from Next.js.
- Do not add production credentials to `.env.example`, `.env.local`, or committed documentation.

## Open Decisions

- Authentication and role-scoped dashboard visibility are not implemented.
- Production filtering, sorting, and pagination for event timelines are not finalized.
- Refresh cadence and stale-data rules need an explicit operations decision.
- Water Emergency execution workflow, closure rules, final readiness taxonomy, final drying taxonomy, equipment inventory records, moisture reading records, and role-scoped emergency operations remain future backend modules.
- Storyboard grouping may need to become backend-provided scenario metadata if production operators need formal scenario filters instead of local QA context.
