# ACS Frontend Foundation

Phase 0 Module 25 keeps the first frontend foundation read-only while adding the first visual QA and dashboard polish pass.

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

Example:

```bash
ACS_DASHBOARD_API_BASE_URL=http://127.0.0.1:8000
```

If the variable is unset, or the backend is unavailable, the dashboard uses typed local fallback data and clearly marks the screen as mock/fallback state.

## Verification

```bash
npm run lint
npm run typecheck
npm run test
npm run build
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

## Open Decisions

- Authentication and role-scoped dashboard visibility are not implemented.
- Production filtering, sorting, and pagination for event timelines are not finalized.
- Refresh cadence and stale-data rules need an explicit operations decision.
- Water Emergency may need dedicated dashboard screens and API contracts once its specialized workflow path is implemented.
