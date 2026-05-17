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
