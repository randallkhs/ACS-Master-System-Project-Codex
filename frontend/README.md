# ACS Frontend Foundation

Phase 0 Module 39 keeps the frontend foundation read-only while adding Water Emergency governance notes, frontend-only saved view preferences, and scalability/read-model metadata visibility backed by separated backend contracts.

The frontend is read-only. It consumes backend dashboard read-model contracts and does not execute dispatch, integrations, Manual Review resolution, AI decisions, or any operational mutation.

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
