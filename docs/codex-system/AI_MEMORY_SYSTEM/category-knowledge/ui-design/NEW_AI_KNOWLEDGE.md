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

---

## ACS Water Emergency Detail Timeline

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
Internal ACS-FSM Phase 0 Module 32 verification

### Discovery
Water Emergency detail screens should be read-only drilldowns backed by backend detail read models. The UI should show one focused emergency record, related job/work-order/visit references, scoped Manual Review indicators, data gaps, audit references, and chronological timeline evidence without offering close, resolve, dispatch, approval, vendor, or AI controls.

### Why It Matters
Water Emergency work is long-lived and evidence-heavy. A dedicated detail/timeline panel improves operator context while preserving backend ownership of lifecycle state and Manual Review authority.

### Reusability
Use this pattern for future high-risk operational detail views where operators need evidence and audit context before mutation workflows are designed.

### Verification Notes
Module 32 tests verify the detail section renders separately, the API client remains GET-only, scoped reviews remain per-record, and missing records return 404. Browser QA should continue to verify live backend source labeling, mobile layout, no console errors, no horizontal overflow, and no mutation controls.

---

## Water Emergency Equipment, Visit-Chain, And Drying-Stage Visibility

Category:
UI design / operational dashboard / Water Emergency
Date Added:
2026-05-18
Last Verified:
2026-05-18
Expiration Window:
90 days
Framework/Library Version:
Next.js 16.2.6 / React 19.2.6 / Tailwind CSS 4.3.0
Source Links:
Internal ACS-FSM Phase 0 Module 33 verification

### Discovery
Water Emergency equipment, visit-chain, and drying-stage panels should display backend read-model fields only. Equipment context can show existing onsite/moisture flags and work-order equipment notes, but must also show explicit unknowns when dedicated equipment inventory entities are not modeled. Visit-chain context can show related visit counts, status buckets, and timestamps without becoming dispatch execution. Drying-stage context can show persisted status/stage/next-action values without inventing a final taxonomy.

### Why It Matters
Water Emergency work is long-lived and operationally sensitive. Operators need to see equipment and drying context, but premature UI authority around pickup, closure, or drying approval would create unsafe workflow assumptions.

### Reusability
Use this pattern for future high-risk dashboard sections where the UI needs to expose partial persisted context while making missing domain models explicit.

### Verification Notes
Module 33 tests verify summary/detail equipment context, visit-chain visibility, drying-stage visibility, Water Emergency separation from standard dispatch-ready counts, no mutation controls, and GET-only dashboard API behavior. Browser QA should continue to verify live backend source labeling, responsive layout, no console errors, and no horizontal overflow.

---

## Water Emergency Review, Exception, And Critical-Alert Visibility

Category:
UI design / operational dashboard / Water Emergency
Date Added:
2026-05-18
Last Verified:
2026-05-18
Expiration Window:
90 days
Framework/Library Version:
Next.js 16.2.6 / React 19.2.6 / Tailwind CSS 4.3.0
Source Links:
Internal ACS-FSM Phase 0 Module 34 verification

### Discovery
Water Emergency review and alert panels should display backend-provided `ReviewItem` evidence only: status counts, reason buckets, blocker reason buckets, critical unresolved counts, escalation indicators, review IDs, audit references, and explicit unknowns. Summary visibility may include all persisted Water Emergency review evidence, but detail visibility must only show reviews scoped to the selected Water Emergency through job, entity, or visit linkage.

### Why It Matters
Water Emergency review visibility helps operators see safety blockers and exception context before action workflows exist. It must not imply approval/rejection authority, alert clearing, escalation execution, dispatch, closure, vendor calls, or AI authority.

### Reusability
Use this pattern for future high-risk review/alert dashboards where the UI needs strong warning visibility without introducing mutation controls or frontend-owned workflow decisions.

### Verification Notes
Module 34 tests verify backend review/exception summaries, per-record review scoping, blocker/unknown indicators, frontend rendering of review/critical/blocker panels, no mutation controls, and GET-only dashboard API behavior. Browser QA should continue to verify live backend source labeling, responsive layout, no console errors, and no horizontal overflow.

---

## Water Emergency Governance And Saved View Preferences

Category:
UI design / operational dashboard / Water Emergency
Date Added:
2026-05-22
Last Verified:
2026-05-22
Expiration Window:
90 days
Framework/Library Version:
Next.js 16.2.6 / React 19.2.6 / Tailwind CSS 4.3.0
Source Links:
Internal ACS-FSM Phase 0 Module 39 verification

### Discovery
Water Emergency filter/sort preferences can be saved safely as browser-local view preferences when they store only non-sensitive UI state. The dashboard should pair saved view controls with a governance note that labels provisional Water Emergency filters, attention groups, timing heuristics, and readiness categories as Randall-authorized Phase 0 visibility baselines, not final SLA or legal policy.

### Why It Matters
Operators benefit from persistent scan settings, but saved view preferences must not become backend workflow state or hidden authority. Governance notes keep Phase 0 labels useful while preserving Alfonso owner review for formal legal, insurance, warranty, drying certification, customer-facing, or company-liability policy.

### Reusability
Use this pattern for future read-only ACS dashboard controls that improve local operator ergonomics before auth, RBAC, account-level preferences, or workflow actions exist.

### Verification Notes
Module 39 tests verify localStorage preference helpers persist filter/sort values, fail safely when storage is unavailable, governance notes render without action controls, backend metadata is marked as Randall-authorized Phase 0 baseline, and metadata does not claim final legal or insurance policy.

---

## Water Emergency Next-Step Readiness Visibility

Category:
UI design / operational dashboard / Water Emergency
Date Added:
2026-05-21
Last Verified:
2026-05-21
Expiration Window:
90 days
Framework/Library Version:
Next.js 16.2.6 / React 19.2.6 / Tailwind CSS 4.3.0
Source Links:
Internal ACS-FSM Phase 0 Module 35 verification

### Discovery
Water Emergency next-step readiness panels should display backend-provided readiness labels, summaries, reason codes, attention counts, blocker/unknown counts, and evidence references only. Labels such as Manual Review needed, visit follow-up needed, equipment review needed, drying-stage confirmation needed, blocked by missing data, ready for close review, and closed with no active next-step action must remain visibility signals, not workflow authority.

### Why It Matters
Operators need a clear way to understand what evidence is still unresolved before Water Emergency execution modules exist. Readiness visibility improves review context while preserving Manual Review authority, backend lifecycle ownership, and separation from standard dispatch.

### Reusability
Use this pattern for future decision-context dashboards where the UI needs to explain likely next review areas without adding action buttons, workflow mutations, vendor calls, or frontend-owned state transitions.

### Verification Notes
Module 35 tests verify backend readiness labels for open reviews, missing data, ready-for-close-review visibility, and closed/no-active-action records; frontend tests verify the readiness panels render evidence without mutation controls. Browser QA should continue to verify live backend source labeling, responsive layout, no console errors, no horizontal overflow, and no action controls.

---

## Water Emergency Operator Queue And Attention Visibility

Category:
UI design / operational dashboard / Water Emergency
Date Added:
2026-05-21
Last Verified:
2026-05-21
Expiration Window:
90 days
Framework/Library Version:
Next.js 16.2.6 / React 19.2.6 / Tailwind CSS 4.3.0
Source Links:
Internal ACS-FSM Phase 0 Module 36 verification

### Discovery
Water Emergency operator queue panels should display backend-provided queue groups, attention labels, attention counts, reason codes, review/critical/blocker/unknown counts, related references, and audit evidence only. Critical attention can sort ahead of lower attention items, and closed/resolved records should remain visually separate from active attention records.

### Why It Matters
Queue visibility improves scanability for operators without creating a workflow engine, operational priority authority, approval control, dispatch action, closure action, vendor call, or AI authority. It keeps Manual Review and backend read models authoritative while preparing for future authenticated Water Emergency workflows.

### Reusability
Use this pattern for future triage dashboards where records need to be grouped for visibility while the final operations taxonomy and action authority remain undecided.

### Verification Notes
Module 36 tests verify backend queue grouping, closed/resolved separation, critical/open-review/blocker evidence ordering, frontend rendering of the Operator Queue panel, no mutation controls, and GET-only dashboard API behavior. Browser QA should continue to verify live backend source labeling, responsive layout, no console errors, no horizontal overflow, and no action controls.

---

## Water Emergency Aging And Follow-Up Risk Visibility

Category:
UI design / operational dashboard / Water Emergency
Date Added:
2026-05-22
Last Verified:
2026-05-22
Expiration Window:
90 days
Framework/Library Version:
Next.js 16.2.6 / React 19.2.6 / Tailwind CSS 4.3.0
Source Links:
Internal ACS-FSM Phase 0 Module 37 verification

### Discovery
Water Emergency aging and follow-up panels should display backend-provided time-sensitivity labels, timing groups, age buckets, follow-up buckets, stale/missing evidence indicators, reason codes, timestamps, related references, and audit evidence only. Labels such as newly opened, active monitoring, follow-up due, follow-up overdue, stale evidence, waiting for review, ready for close review, closed/resolved, and unknown timing must remain visibility signals, not SLA or workflow authority.

### Why It Matters
Operators need time-sensitive awareness for Water Emergency work before action workflows exist. Aging visibility improves scanability while preserving Manual Review authority, backend lifecycle ownership, separation from standard dispatch, and the distinction between timing awareness and SLA execution.

### Reusability
Use this pattern for future time-sensitive dashboards where records need aging and stale-evidence visibility while final operations taxonomy, escalation rules, and action authority remain undecided.

### Verification Notes
Module 37 tests verify backend aging/follow-up labels, closed/resolved separation from active overdue work, unknown timing for missing timestamps, frontend rendering of the Aging & Follow-Up Risk panel, closed timing visibility beyond active limits, no mutation controls, and GET-only dashboard API behavior. Browser QA should continue to verify live backend source labeling, responsive layout, no console errors, no horizontal overflow, and no action controls.

---

## Water Emergency Filtering, Sorting, And View-State Visibility

Category:
UI design / operational dashboard / Water Emergency
Date Added:
2026-05-22
Last Verified:
2026-05-22
Expiration Window:
90 days
Framework/Library Version:
Next.js 16.2.6 / React 19.2.6 / Tailwind CSS 4.3.0
Source Links:
Internal ACS-FSM Phase 0 Module 38 verification

### Discovery
Water Emergency filter/sort panels should display backend-provided available filters, sort options, group counts, per-record filter memberships, primary view groups, queue labels, timing labels, readiness labels, counts, last-activity timestamps, related references, and audit evidence only. Frontend controls may change local display state, but they must not persist preferences, call mutation endpoints, or infer workflow authority.

### Why It Matters
Operators need to isolate critical, Manual Review, blocked, follow-up, stale, ready-for-close, unknown, active, and closed/resolved Water Emergency records quickly. View-state controls improve scanability while preserving backend lifecycle ownership, Manual Review authority, and separation from standard dispatch.

### Reusability
Use this pattern for future read-only dashboards where user controls should filter and sort existing backend read models without becoming operational controls or workflow engines.

### Verification Notes
Module 38 tests verify backend filter metadata, deterministic group membership, closed/resolved separation, frontend view-state filtering, empty-state rendering, no mutation controls, and GET-only dashboard API behavior. Browser QA should continue to verify live backend source labeling, responsive layout, no console errors, no horizontal overflow, and no action controls.
