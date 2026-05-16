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

## Tailwind CSS v4 PostCSS Setup

Category:
Frontend styling
Date Added:
2026-05-16
Last Verified:
2026-05-16
Expiration Window:
60 days
Framework/Library Version:
Tailwind CSS 4.3.0
Source Links:
https://tailwindcss.com/docs/installation/using-postcss

### Discovery
Tailwind CSS v4 uses the `tailwindcss` package with the `@tailwindcss/postcss` plugin and imports Tailwind from the global stylesheet with `@import "tailwindcss"`.

### Why It Matters
The ACS frontend scaffold should use the current Tailwind setup instead of older `@tailwind base/components/utilities` patterns.

### Reusability
Use this setup for future ACS Next.js dashboard modules until the note expires or Tailwind changes its installation pattern.

### Verification Notes
Verified against current Tailwind documentation through Context7 and by running the Module 24 frontend build.
