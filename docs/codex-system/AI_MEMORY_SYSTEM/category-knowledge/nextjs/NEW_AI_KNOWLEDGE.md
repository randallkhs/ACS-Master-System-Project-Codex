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

## Next.js App Router Server-Side Dashboard Fetching

Category:
Frontend architecture
Date Added:
2026-05-16
Last Verified:
2026-05-16
Expiration Window:
60 days
Framework/Library Version:
Next.js 16.2.6
Source Links:
https://nextjs.org/docs/app/guides/environment-variables
https://nextjs.org/docs/app/getting-started/fetching-data

### Discovery
Next.js App Router Server Components can read server-only environment variables and fetch backend data server-side. For ACS dashboard screens, keep the backend origin in an environment variable such as `ACS_DASHBOARD_API_BASE_URL` and keep public browser-exposed variables separate unless a future client component truly requires them.

Server-side dashboard fetches should keep `ACS_DASHBOARD_API_BASE_URL` unprefixed and server-only. If future dashboard code moves API calls into browser/client components, add explicit CORS and public-runtime configuration as a separate architecture decision.

### Why It Matters
The ACS frontend must be deployable behind future production routing without localhost assumptions, and workflow state should remain backend-owned.

### Reusability
Use this pattern for future ACS admin dashboard pages that consume backend read-only contracts.

### Verification Notes
Verified against current Next.js documentation through Context7 and by running the Module 24 and Module 26 frontend builds.
