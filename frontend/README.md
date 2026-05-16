# ACS Frontend Foundation

Phase 0 Module 24 adds the first frontend foundation for the ACS Master System admin dashboard.

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

## Architecture Rules

- The frontend displays backend read models only.
- Backend services remain the source of workflow/business logic.
- API client helpers are read-only `GET` calls.
- No mutation endpoints, dispatch execution, vendor integration calls, or AI authority are implemented.
- Manual Review remains authoritative and cannot be bypassed from the UI.
- Water Emergency remains first-class and is displayed as separated operational state where the backend contract exposes it.

## Current Dashboard Views

- Operational overview
- Dispatch lifecycle summary
- Manual Review summary
- Route assignment summary
- External execution summary
- Reconciliation and recovery summary
- Governance and accountability summary
- Operational event timeline preview

## Open Decisions

- Authentication and role-scoped dashboard visibility are not implemented.
- Production filtering, sorting, and pagination for event timelines are not finalized.
- Refresh cadence and stale-data rules need an explicit operations decision.
- Water Emergency may need dedicated dashboard screens and API contracts once its specialized workflow path is implemented.
