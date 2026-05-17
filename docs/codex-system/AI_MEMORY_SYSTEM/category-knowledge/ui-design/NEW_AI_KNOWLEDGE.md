# Python Development Knowledge

## Purpose

Store:
- important Python discoveries
- reusable workflows
- modern best practices
- debugging breakthroughs
- framework updates
- architecture improvements

Only store high-value reusable knowledge.

---

# Entry Format

## Title

Category:
Date Added:
Last Verified:
Expiration Window:
Framework/Library Version:
Source Links:

### Discovery
Describe the discovery concisely.

### Why It Matters
Explain why the discovery is important.

### Reusability
Explain where this knowledge can be reused.

### Verification Notes
Document:
- compatibility checks
- update confirmations
- breaking changes if discovered

---

# Storage Rules

Only include:
- reusable knowledge
- future-useful discoveries
- difficult debugging solutions
- architecture improvements

Avoid:
- trivial notes
- temporary experiments
- repetitive discoveries

---

# Freshness Rules

If a note exceeds its expiration window:
- re-check sources
- verify compatibility
- update verification date

Avoid relying on stale framework knowledge.

---

## ACS Dashboard Scenario Storyboards

Category:
UI design / operational dashboard
Date Added:
2026-05-17
Last Verified:
2026-05-17
Expiration Window:
90 days
Framework/Library Version:
Next.js 16.2.6 / React 19.2.6 / Tailwind CSS 4.3.0
Source Links:
Internal ACS-FSM Phase 0 Module 30 verification

### Discovery
For ACS-FSM local dashboard QA, a read-only scenario storyboard is useful when it groups existing backend dashboard read-model counts into operational story families without adding UI actions or workflow logic. The storyboard should label local seed context clearly, preserve live/mock source indicators, and keep Water Emergency visibly separated from standard dispatch examples.

### Why It Matters
The ACS dashboard needs operator scanability, but the frontend must not become workflow authority. Scenario cards can improve comprehension while still treating backend read models and Manual Review as authoritative.

### Reusability
Use this pattern for future ACS dashboard modules that need to explain complex persisted operational states before mutation workflows, auth, or role-scoped actions exist.

### Verification Notes
Module 30 browser QA verified the storyboard against live local PostgreSQL-backed dashboard data at desktop, laptop, and mobile viewports with no console errors, no horizontal overflow, and no operational action controls.

---

## ACS Water Emergency Dashboard Separation

Category:
UI design / operational dashboard
Date Added:
2026-05-17
Last Verified:
2026-05-17
Expiration Window:
90 days
Framework/Library Version:
Next.js 16.2.6 / React 19.2.6 / Tailwind CSS 4.3.0
Source Links:
Internal ACS-FSM Phase 0 Module 31 verification

### Discovery
Water Emergency dashboard visibility should use a dedicated backend read-model contract and a dedicated frontend section instead of relying only on standard dispatch summaries or storyboard grouping. The UI should show open/closed state, status/stage distribution, equipment and moisture indicators, multi-visit indicators, related references, review/escalation indicators, data gaps, and emergency timeline evidence while keeping all controls read-only.

### Why It Matters
Water Emergency is a first-class ACS workflow with different operational risk than standard dispatch. A separated dashboard view keeps operators aware of emergency state without implying standard dispatch execution or frontend-owned workflow authority.

### Reusability
Use this pattern for future ACS Water Emergency modules, technician/mobile emergency views, and other high-risk workflow dashboards where visibility must be distinct from execution.

### Verification Notes
Module 31 tests verify the dedicated Water Emergency section renders separately from standard dispatch, the frontend API client remains GET-only, and no emergency mutation controls are present. Full browser QA should continue to confirm live backend source labeling, responsive layout, no console errors, and no horizontal overflow.
