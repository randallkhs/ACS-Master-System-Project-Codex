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

## ACS Local PostgreSQL Dashboard Verification

Category:
Local development database
Date Added:
2026-05-16
Last Verified:
2026-05-16
Expiration Window:
60 days
Framework/Library Version:
Alembic 1.17 / SQLAlchemy 2 / psycopg 3
Source Links:
https://alembic.sqlalchemy.org/en/latest/tutorial.html
https://docs.sqlalchemy.org/en/20/core/engines.html
https://docs.sqlalchemy.org/en/20/dialects/postgresql.html

### Discovery
ACS-FSM local dashboard verification should use an environment-driven PostgreSQL URL, run Alembic migrations against the configured local database, and keep synthetic dashboard seed data clearly separated from production state. The local default is `acs_fsm_dev` on `127.0.0.1` with a local-only `postgresql+psycopg://...` URL.

### Why It Matters
The dashboard read models need live persisted state for meaningful local frontend verification, but the local workflow must not become production deployment infrastructure or introduce unsafe seed behavior.

### Reusability
Use this pattern for future ACS local database setup, read-model verification, and integration-test planning.

### Verification Notes
Context7 confirmed Alembic `upgrade head` behavior and SQLAlchemy PostgreSQL psycopg URL shape. Module 28 later found Homebrew PostgreSQL 18.4 available on this workstation but stopped, started the local `postgresql@18` development service, created the missing `acs_fsm_dev` role/database, ran migrations to `20260515_0018`, inserted synthetic dashboard seed data, and verified live backend dashboard reads plus frontend live-backend rendering. Repository scripts still must not install PostgreSQL or manage production services.

Module 29 expanded the seed into named synthetic scenarios for dispatch-ready work, Manual Review, blocked operations, external confirmation, reconciliation/recovery, governance/accountability, timeline evidence, and Water Emergency separation. The seed is rerunnable through upsert behavior for seed-owned records and remains local-development-only.

Module 35 expanded the same local-only seed family with Water Emergency next-step readiness examples for Manual Review, equipment review, visit follow-up, missing data, ready-for-close-review visibility, and closed/no-active-action visibility. These records remain synthetic read-model examples only and must not imply production workflow execution or final operations taxonomy.

Module 36 expanded the same local-only seed family with Water Emergency operator queue examples for critical attention, blocked/missing information, visit follow-up, equipment review, monitoring, close-review visibility, and closed/resolved visibility. These records remain synthetic, local-development-only read-model examples and must not imply production priority rules, workflow execution, or final ACS triage taxonomy.
