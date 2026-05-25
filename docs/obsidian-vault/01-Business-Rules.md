# ACS FSM — Business Rules

# Purpose

This document defines the official operational rules of the Apple Cleaning Systems FSM platform.

These rules override assumptions, AI interpretation, or inferred logic.

All workflows must follow these rules strictly.

---

# 1. Operational Philosophy

The system must prioritize:

1. Operational reliability
2. Human verification
3. Deterministic workflows
4. Structured data
5. Auditability
6. Extensibility

The system must NOT depend heavily on AI interpretation of unpredictable human-written text.

---

# 2. Source of Truth Rules

## Official Source of Truth

The internal PostgreSQL database is the primary operational source of truth.

External systems are integrations only.

Examples:
- Google Calendar
- Google Sheets
- FastField
- Email
- Verizon Connect

These systems may provide input/output data, but they are NOT authoritative.

---

# 3. Job Categories

## 3.1 Standard Jobs

Examples:
- carpet cleaning
- upholstery
- air duct cleaning
- deep cleaning
- dryer vents
- LVT cleaning

Characteristics:
- usually single-day
- usually single-visit
- normally closed same day
- assigned to technicians for completion

---

## 3.2 Water Emergency Jobs

Water Emergency jobs are NOT treated as normal jobs.

They are long-lived operational workflows.

Characteristics:
- multi-visit
- multi-day
- may involve multiple technicians
- equipment lifecycle tracking required
- drying progress required
- moisture checks required
- completion state controlled separately
- may remain open for multiple days

Water Emergency workflows are first-class operational entities.

---

# 4. Calendar Import Rules

## Import Window

The system normally processes:
- NEXT DAY schedule
not:
- current day schedule

Example:
- today = 2026-05-14
- system processes = 2026-05-15

---

## Calendar Events

Calendar events are considered:
- operational input
NOT:
- operational truth

Imported calendar data must be normalized before use.

---

# 5. Cancellation Rules

## Cancellation Detection

Cancellation detection must NEVER rely only on exact spelling.

Examples of valid cancellation indicators:
- CANCELED
- CANCELLED
- canceled
- cancelled
- canseled
- cancelld
- canneled

The system must use:
- fuzzy matching
- confidence scoring
- manual review triggers

---

## Cancellation Confidence

If confidence is low:
- DO NOT auto-dispatch
- send to manual review queue

Operational safety is more important than automation speed.

---

# 6. AM/PM Time Window Rules

Jobs may contain operational time windows.

Examples:
- AM/DE
- DE/AM
- PM/NJ
- NJ/PM

States currently used:
- DE = Delaware
- MD = Maryland
- PA = Pennsylvania
- NJ = New Jersey

Rules:
- AM jobs require morning scheduling priority
- PM jobs require afternoon scheduling priority
- time windows affect routing decisions
- time windows affect technician assignment

---

# 7. Routing Rules

## Routing Objective

Routing exists to:
- reduce drive time
- optimize technician allocation
- improve operational efficiency

---

## Geographic Grouping

Current routing strategy:
- North group
- South group

based on:
- depot location

This routing system may evolve in future versions.

---

## Routing Constraints

Routing must eventually support:
- AM/PM windows
- technician skills
- water emergency priority
- technician availability
- equipment requirements
- geographic efficiency

---

# 8. Technician Rules

Technicians may have:
- skill specializations
- certifications
- equipment limitations
- geographic preferences
- availability states

Future versions will support:
- live GPS
- dynamic reassignment
- mobile technician workflows

---

# 9. Manual Review Queue

The manual review queue is a core operational safety system.

The queue exists to prevent:
- bad dispatches
- incorrect cancellations
- incomplete jobs
- malformed addresses
- AI uncertainty failures

---

## Manual Review Triggers

Examples:
- low confidence parsing
- unclear cancellation
- invalid address
- missing customer info
- conflicting state markers
- malformed dates
- duplicate jobs
- uncertain AI classification

## Phase 0 Module 40 Manual Review Visibility

The Manual Review Queue now has a read-only dashboard detail view. It groups review items by persisted status, reason, severity, entity links, Water Emergency relation, age bucket, blocker/attention signals, and audit evidence.

This visibility does not approve, reject, defer, archive, resolve, dispatch, or otherwise execute review actions. Manual Review remains authoritative until future authenticated action workflows are explicitly designed.

## Phase 0 Module 41 Manual Review Detail Visibility

Manual Review now has a read-only single-item detail view for operator investigation context. The detail view shows the selected review item, reason and evidence context, linked job/work-order/visit/route-assignment context, Water Emergency context when specifically linked, audit references, and chronological timeline evidence.

This detail visibility is a Randall-authorized Phase 0 baseline for internal review investigation only. It does not approve, reject, defer, archive, resolve, dispatch, escalate, call AI, call vendors, or create final company policy.

## Phase 0 Module 42 Manual Review Filter, Sort, And Saved-View Visibility

Manual Review now has read-only queue filter and sort visibility for operator scanability. The queue can expose internal view groups such as open, deferred, resolved, archived, active attention, Water Emergency-related, dispatch-related, missing data, duplicate/conflict, cancellation/status uncertainty, and needs operator review.

These groups are Randall-authorized Phase 0 visibility baselines only. They do not approve, reject, defer, archive, resolve, dispatch, escalate, enforce SLA rules, create legal/company policy, or replace future authenticated Manual Review action workflows.

Frontend saved view preferences are browser-only UI preferences. They may remember the selected Manual Review filter and sort option, but they must not store tokens, secrets, customer data, PII, backend operational state, or Manual Review decisions.

## Phase 0 Module 43 Manual Review Decision-Readiness Visibility

Manual Review now has read-only decision-readiness and resolution-preparation visibility. The queue and detail read models can expose internal labels such as needs operator review, needs missing information, needs entity context, needs Water Emergency review, needs dispatch review, ready for operator decision, ready for resolution review, blocked by conflict, blocked by missing data, resolved or archived, and unknown readiness.

These labels are Randall-authorized Phase 0 visibility baselines only. They explain why a review record needs attention or why it is historical, but they do not approve, reject, defer, archive, resolve, dispatch, escalate, call vendors, call AI, or execute any workflow.

Water Emergency-related readiness must remain visually separated from standard dispatch readiness. Resolved and archived review items must not be shown as active decision needs.

## Phase 0 Module 44 Manual Review Action-Preflight Visibility

Manual Review now has read-only action-preflight and future authorization-readiness visibility. The queue and detail read models can expose internal labels such as action not available in read-only phase, eligible for future operator decision, eligible for future resolution review, blocked by missing entity context, blocked by missing data, blocked by conflict, blocked by Water Emergency context, blocked by resolved or archived status, requires future auth, requires operator identity, requires audit reason, and unknown action eligibility.

These labels are Randall-authorized Phase 0 visibility baselines only. They prepare future Manual Review action modules by showing blockers and required evidence, but they do not make any action executable and do not implement auth, RBAC, approve, reject, defer, archive, resolve, dispatch, vendor calls, AI authority, or workflow execution.

Water Emergency-related action preflight must remain visually separated from standard dispatch review context. Resolved and archived review items must not be shown as eligible for active future review actions.

## Phase 0 Module 45 Manual Review Future-Action Preview Visibility

Manual Review now has read-only future-action preview and outcome-preparation visibility. The queue and detail read models can expose internal labels such as future approve preview, future reject preview, future defer preview, future archive preview, future resolve preview, future request information preview, future operator decision preview, no action available for resolved or archived history, no action available for missing entity context, no action available for conflict, no action available for Water Emergency context, and unknown action preview.

These labels are Randall-authorized Phase 0 visibility baselines only. They show expected non-binding outcomes, impacted entity references, blockers, future operator identity requirements, and future audit reason requirements so later action modules can be designed safely. They do not approve, reject, defer, archive, resolve, dispatch, escalate, call vendors, call AI, implement auth/RBAC, mutate review records, or make any preview executable.

Water Emergency-related future-action preview must remain visually separated from standard dispatch review context. Missing entity context, duplicate/conflict evidence, Water Emergency context, and resolved or archived status must block active action previews until a future authenticated workflow explicitly handles them.

---

# 10. Confidence Scoring

The system should assign operational confidence scores.

Example:

- 95–100 → safe automation
- 75–94 → warning state
- below 75 → manual review required

---

# 11. AI Usage Rules

AI is an ASSISTANT.

AI is NOT:
- operational authority
- dispatch authority
- cancellation authority

Humans always override AI decisions.

---

# 12. FastField Rules

FastField is transitional infrastructure.

The system must NOT tightly couple internal architecture to FastField.

Future versions will replace FastField with:
- ACS technician workflows
- ACS mobile app
- internal work order management

---

# 13. Audit Logging Rules

Important actions must be logged.

Examples:
- imports
- dispatches
- cancellations
- technician assignments
- overrides
- manual reviews
- route generation
- exports

Logs must support:
- debugging
- compliance
- operational tracing

---

# 14. Future Expansion Rules

The system must be designed for future modules:

- billing
- inventory
- CRM
- payroll support
- customer portal
- technician app
- equipment lifecycle
- analytics
- AI operational assistant
- Verizon Connect integration

Architecture decisions today must NOT block future expansion.

---

# 15. Safety Rules

Operational safety always overrides automation convenience.

When uncertainty exists:
- stop automation
- request human review

Never risk:
- dispatching canceled jobs
- losing water emergency tracking
- assigning wrong technicians
- corrupting operational data

---

# 16. Phase 0 Manual Review Command Contract Boundary

Module 46 adds read-only Manual Review future command-contract and audit-envelope visibility.

Rules:

- command-contract labels are Randall-authorized Phase 0 visibility baselines only
- every future command contract remains currently non-executable
- future commands require auth, operator identity, role authorization, audit reason, idempotency key, immutable event recording, and post-action consistency checks before any mutation module exists
- missing entity context, missing data, duplicate/conflict evidence, Water Emergency context, and resolved/archived status remain blockers or historical visibility states
- Water Emergency-related Manual Review command contracts must remain separated from standard dispatch review context
- no approve, reject, defer, archive, resolve, dispatch, vendor, AI, auth, RBAC, or workflow execution authority is created

Open concerns:

- final Manual Review action workflow and role authority remain future work
- legal, insurance, compliance, customer-liability, or formal company-policy language requires Alfonso owner review

---

# 17. Phase 0 Manual Review Audit Ledger And Command Dry-Run Boundary

Module 47 adds read-only Manual Review audit-ledger preparation and command dry-run visibility.

Rules:

- audit-ledger and dry-run labels are Randall-authorized Phase 0 visibility baselines only
- every dry-run record remains currently non-executable and Phase 0 does not allow execution
- future commands require audit reason, operator identity, role authorization, idempotency key, immutable event recording, and post-action consistency checks before any mutation module exists
- proposed future event type/state, audit envelope fields, idempotency scope, and consistency-check summaries are preparation metadata only
- missing entity context, duplicate/conflict evidence, Water Emergency scope, and resolved/archived status remain blockers or historical visibility states
- Water Emergency-related Manual Review dry-runs must remain separated from standard dispatch review context
- no audit write, approve, reject, defer, archive, resolve, dispatch, vendor, AI, auth, RBAC, or workflow execution authority is created

Open concerns:

- final Manual Review command execution workflow and audit-ledger persistence remain future work
- legal, insurance, compliance, customer-liability, or formal company-policy language requires Alfonso owner review

---

# 18. Phase 0 Manual Review Command Validation And Safety Gate Boundary

Module 48 adds read-only Manual Review command-validation and safety-gate matrix visibility.

Rules:

- command-validation labels and safety gates are Randall-authorized Phase 0 visibility baselines only
- every validation record remains currently non-executable and Phase 0 does not allow execution
- the `phase_allows_execution` safety gate must remain false in Phase 0
- future commands require linked entity context, audit reason, operator identity, role authorization, idempotency key, immutable event recording, and post-action consistency checks before any mutation module exists
- missing entity context, duplicate/conflict evidence, Water Emergency scope, and resolved/archived status remain blockers or historical visibility states
- Water Emergency-related Manual Review validation must remain separated from standard dispatch review context
- no validation execution, audit write, approve, reject, defer, archive, resolve, dispatch, vendor, AI, auth, RBAC, or workflow execution authority is created

Open concerns:

- final Manual Review command validation/execution workflow and safety-gate persistence remain future work
- legal, insurance, compliance, customer-liability, or formal company-policy language requires Alfonso owner review

---

# 19. Phase 0 Manual Review Operator Identity And Permission Boundary

Module 49 adds read-only Manual Review operator-identity, role-authorization, and permission-readiness visibility.

Rules:

- permission-readiness labels are Randall-authorized Phase 0 visibility baselines only
- every permission-readiness record remains currently non-executable and Phase 0 does not allow execution
- future Manual Review commands require future auth, operator identity, role authorization, audit actor capture, audit reason, idempotency key, immutable event recording, and post-action consistency checks before any mutation module exists
- service accounts and technicians are not future Manual Review operator-action actors
- missing entity context, Water Emergency scope, resolved/archived status, and unknown operator context remain blockers or historical visibility states
- Water Emergency-related Manual Review authorization requirements must remain separated from standard dispatch review context
- no login, signup, user management, token/session behavior, auth headers, fake role enforcement, approve, reject, defer, archive, resolve, dispatch, vendor, AI, RBAC, or workflow execution authority is created

Open concerns:

- final ACS-FSM auth provider, operator identity schema, RBAC model, permission taxonomy, and Manual Review action authority remain future work
- legal, insurance, compliance, customer-liability, or formal company-policy language requires Alfonso owner review

---

# 20. Phase 0 Manual Review Execution Readiness And Mutation Boundary

Module 50 adds a read-only execution-readiness audit, mutation-boundary lock, and future transition plan for Manual Review action modules.

Rules:

- execution-readiness audit labels are Randall-authorized Phase 0 visibility baselines only
- `manual_review_mutations_enabled` must remain false in Phase 0
- `action_execution_phase` must remain `read_only_phase_0`
- `currently_executable_count` must remain zero in Phase 0
- `mutation_endpoints_available` must remain false in Phase 0
- future Manual Review mutation modules require real auth, RBAC, operator identity, audit envelope, audit reason, idempotency, immutable event recording, post-action consistency checks, approved action contracts, reviewed action UI, ACSSDR report updates, and the Review GUI/ChatGPT review workflow
- Water Emergency-related readiness must remain separated from standard Manual Review readiness
- customer-facing promises, insurance documentation, warranty status, drying certification language, formal policy commitments, and billing/financial commitments require Alfonso owner review before any binding action or policy exists
- no login, signup, user management, token/session behavior, auth headers, fake role enforcement, approve, reject, defer, archive, resolve, dispatch, vendor, AI, RBAC, mutation endpoint, or workflow execution authority is created

Open concerns:

- final ACS-FSM auth provider, operator identity schema, RBAC model, permission taxonomy, audit envelope schema, idempotency strategy, immutable event write strategy, rollback/replay strategy, post-action consistency checks, and Manual Review action authority remain future work
- legal, insurance, compliance, customer-liability, or formal company-policy language requires Alfonso owner review

# 21. Phase 0 Manual Review Auth Boundary And Operator Catalog

Module 51 adds read-only auth-boundary readiness metadata for future Manual Review operator identity, role catalog, and permission catalog planning.

Rules:

- auth-boundary metadata is a Randall-authorized Phase 0 planning baseline only
- `auth_implemented` must remain false in Phase 0
- `rbac_enforced` must remain false in Phase 0
- `login_ui_available` must remain false in Phase 0
- `action_execution_available` must remain false in Phase 0
- `operator_identity_registry_available` must remain false while the registry is metadata-only and not persisted
- future operator identity registry fields may be listed for planning, but they do not persist operator identities yet
- provisional roles such as owner, operations manager, office admin, dispatcher, reviewer, technician, system service, and unknown operator are planning labels only
- future permissions such as Manual Review view/detail/future action labels, Water Emergency review labels, dashboard view, and audit view are planning labels only
- service accounts, technicians, and unknown operators are not allowed for future Manual Review operator actions unless a later reviewed module explicitly changes the boundary
- Water Emergency-related authorization and future action scope must remain separated from standard Manual Review readiness
- no login, signup, user management, token/session behavior, auth headers, fake user identity, fake role enforcement, approve, reject, defer, archive, resolve, dispatch, vendor, AI, RBAC, mutation endpoint, audit write, or workflow execution authority is created

Open concerns:

- final ACS-FSM auth provider, production credential ownership, durable operator registry schema, RBAC role model, permission taxonomy, role-scoped visibility, and Manual Review action authority remain future work

---

# 22. Phase 0 Auth Provider Configuration And Environment Safety

Module 52 adds a read-only future auth provider configuration contract and safe environment placeholder baseline.

Rules:

- auth configuration metadata is a Randall-authorized Phase 0 planning baseline only
- `auth_provider_configured` must remain false in Phase 0
- `auth_provider` must remain `disabled` in Phase 0
- `token_verification_enabled` must remain false in Phase 0
- `rbac_enforcement_enabled` must remain false in Phase 0
- `login_ui_available` must remain false in Phase 0
- `frontend_auth_config_available` remains false until a future reviewed auth module intentionally enables frontend auth behavior
- committed credentials are not allowed
- `.env.example`, `backend/.env.example`, and `frontend/.env.example` may include safe placeholders only
- real auth credentials, tenant values, private keys, service account JSON, tokens, `.env`, and `.env.local` must not be committed
- Randall controls future Google/account/provider technical configuration decisions
- Alfonso owner review is required only where auth-related decisions create legal, insurance, compliance, contractual, financial-liability, customer-liability, or formal company-policy consequences
- no login, logout, signup, user management, token/session behavior, auth headers, fake user identity, fake role enforcement, approve, reject, defer, archive, resolve, dispatch, vendor, AI, RBAC, mutation endpoint, audit write, or workflow execution authority is created

Open concerns:

- final ACS-FSM auth provider selection, credential ownership, local development auth mode, production VPS secret configuration, token verification, RBAC enforcement, and role-scoped Manual Review action authority remain future work

---

# 23. Phase 0 Auth Diagnostics And Secret Hygiene Visibility

Module 53 adds read-only auth configuration diagnostics, secret-hygiene verification, and runtime safety visibility.

Rules:

- auth diagnostics metadata is a Randall-authorized Phase 0 planning baseline only
- `auth_enabled` must remain false in Phase 0
- `auth_provider` must remain `disabled` in Phase 0
- `token_verification_enabled` must remain false in Phase 0
- `rbac_enforcement_enabled` must remain false in Phase 0
- `login_ui_available` must remain false in Phase 0
- `auth_headers_required` and `auth_headers_emitted_by_frontend` must remain false in Phase 0
- diagnostics may report secret-hygiene booleans, but must never expose credential values
- `.env`, `.env.local`, service account JSON, private keys, real tokens, and real credentials must not be committed
- the secret-hygiene helper must not contact external services, mutate files, or print secret values
- no login, logout, signup, user management, token/session behavior, auth headers, fake user identity, fake role enforcement, approve, reject, defer, archive, resolve, dispatch, vendor, AI, RBAC, mutation endpoint, audit write, or workflow execution authority is created

Open concerns:

- final ACS-FSM auth provider selection, production credential ownership, VPS secret configuration, local development auth mode, token verification, RBAC enforcement, role-scoped visibility, and authenticated Manual Review action authority remain future work
