# ACS FSM — AI Automation Rules

## Purpose

This file defines the durable AI operating rules for the ACS FSM platform.

AI is an assistant layer. It is not the operational authority.

---

## Core Rule

If the system is not confident, it must stop automation, explain the issue, and send the item to Manual Review.

No uncertain job should be silently dispatched, exported, closed, canceled, or skipped.

---

## Allowed AI Uses

AI may assist with:

- job classification suggestions
- anomaly detection
- confidence scoring support
- summarizing operational notes
- extracting likely fields from messy text
- recommending review actions
- explaining why an item may be risky

AI output must be stored as advisory context, not final truth.

---

## Forbidden AI Uses

AI must never:

- override an operator
- silently dispatch jobs
- auto-confirm cancellations
- auto-close Water Emergency workflows
- bypass Manual Review
- bypass deterministic validation rules
- change workflow state without explicit system rules and human authorization where required
- treat freeform text interpretation as the only source of operational truth

---

## Deterministic Rules First

The system should run deterministic validation before depending on AI interpretation.

Examples:

- required address fields
- supported state markers
- known cancellation indicators
- AM/PM marker parsing
- duplicate detection
- Water Emergency status checks
- technician availability and mapping checks

AI may help explain ambiguous cases, but deterministic rules and operator decisions remain authoritative.

---

## Phase 0 Module 5 Boundary

The intake normalization and validation foundation is deterministic only.

Current deterministic responsibilities:

- whitespace cleanup
- AM/PM marker extraction
- supported state marker extraction
- cancellation keyword detection
- Water Emergency keyword detection
- required-field validation
- conflicting marker detection
- confidence scoring from validation results
- Manual Review recommendation preparation

AI is not used in this module.

Future AI may assist with ambiguous text extraction or explanation, but it must consume deterministic results as context and must not override validation failures, dispatch safety blocks, cancellation handling, Water Emergency separation, or Manual Review requirements.

## Phase 0 Module 6 Boundary

The persistent Manual Review Queue foundation stores deterministic review reasons, severity, confidence snapshots, validation evidence, normalization evidence, source references, operator notes, and audit correlation.

AI is still not used in this module.

Future AI may add advisory context to a review item only if deterministic validation and queue state remain authoritative. AI must not approve, reject, defer, archive, dispatch, route, export, or silently clear any Manual Review item.

## Phase 0 Module 7 Boundary

The dispatch orchestration preparation layer is deterministic only.

It may compose normalized intake, validation results, deterministic confidence scores, Manual Review recommendations, review reasons, warnings, dispatch eligibility, and evidence snapshots.

AI is still not used in this module.

Future AI orchestration may provide advisory context only after deterministic evidence exists. AI must not change dispatch eligibility, clear unsafe flags, remove Water Emergency separation, bypass Manual Review, create jobs, route technicians, or execute integrations.

## Phase 0 Module 8 Boundary

Operational intake persistence stores deterministic orchestration outcomes and evidence.

AI is still not used in this module.

Future AI may add advisory evidence only through explicit fields and after deterministic orchestration has produced auditable results. AI must not mark records approved for dispatch, resolve review-required records, convert Water Emergency intake into standard dispatch, create jobs, or alter persisted deterministic evidence.

## Phase 0 Module 9 Boundary

Operational job creation is deterministic only.

AI is still not used in this module.

Only explicitly approved standard intake records can create standard jobs. AI must not create jobs, bypass duplicate protection, mark review-required intake as approved, convert Water Emergency intake into standard jobs, change lifecycle state, dispatch work, route technicians, or alter creation evidence.

## Phase 0 Module 10 Boundary

Work Order and Visit generation is deterministic only.

AI is still not used in this module.

Only approved standard jobs can generate standard Work Orders, and only generated standard Work Orders can generate Visits. AI must not create Work Orders or Visits, bypass duplicate prevention, approve review-required jobs, convert Water Emergency jobs into the standard path, assign technicians, schedule visits, route work, dispatch work, or alter generation evidence.

## Phase 0 Module 11 Boundary

Technician assignment and scheduling preparation is deterministic only.

AI is still not used in this module.

AI must not assign technicians, declare inactive technicians compatible, bypass blocked/review-required/Water Emergency lifecycle blockers, create schedule times, route work, dispatch work, sync calendars, or alter readiness evidence. Future AI may only add advisory context after deterministic readiness evidence exists and Manual Review remains authoritative.

## Phase 0 Module 12 Boundary

Routing and dispatch preparation is deterministic only.

AI is still not used in this module.

AI must not declare Visits routing-ready or dispatch-ready, clear blocked/review-required/Water Emergency lifecycle blockers, treat inactive technicians as dispatch-ready, assign technicians, schedule Visits, optimize routes, create route assignments, execute dispatch, sync calendars, or alter readiness evidence. Future AI may only add advisory context after deterministic routing and dispatch readiness evidence exists, and Manual Review remains authoritative.

## Phase 0 Module 13 Boundary

Route assignment and dispatch authorization is deterministic only.

AI is still not used in this module.

AI must not authorize dispatch, clear route or dispatch blockers, create standard route assignments for Water Emergency Visits, treat inactive technicians as dispatch-authorized, bypass Manual Review, execute dispatch, optimize routes, sync calendars, write Sheets/FastField, call integrations, or alter authorization evidence. Future AI may only add advisory context after deterministic authorization evidence exists and must remain subordinate to Manual Review and operator/system authorization.

## Phase 0 Module 14 Boundary

Dispatch execution is deterministic only.

AI is still not used in this module.

AI must not execute dispatch, clear execution blockers, create standard dispatch execution for Water Emergency Visits, treat inactive technicians as dispatch-ready, bypass Manual Review, retry duplicate dispatch, sync calendars, write Sheets/FastField, call external integrations, update technician mobile workflows, or alter execution evidence. Future AI may only add advisory context after deterministic execution evidence exists and must remain subordinate to Manual Review and operator/system authorization.

## Phase 0 Module 15 Boundary

External dispatch adapter preparation is deterministic only.

AI is still not used in this module.

AI must not prepare external adapter payloads, clear adapter blockers, create standard external payloads for Water Emergency Visits, bypass Manual Review, retry duplicate adapter preparation, call FastField, sync Google Calendar, write Sheets, update technician mobile workflows, run background execution, call external APIs, or alter adapter evidence. Future AI may only add advisory context after deterministic adapter evidence exists and must remain subordinate to Manual Review and operator/system authorization.

## Phase 0 Module 18 Boundary

External adapter execution is deterministic controlled execution only.

AI is still not used in this module.

AI must not execute provider adapters, clear external execution blockers, create standard provider execution records for Water Emergency Visits, bypass Manual Review, retry duplicate external execution, call FastField, sync Google Calendar, write Sheets, update technician mobile workflows, run background execution, call real provider APIs, or alter execution evidence. Future AI may only add advisory context after deterministic external execution evidence exists and must remain subordinate to Manual Review and operator/system authorization.

## Phase 0 Module 16 Boundary

External confirmation and failure recovery preparation is deterministic only.

AI is still not used in this module.

AI must not confirm external execution, clear confirmation blockers, create standard confirmation records for Water Emergency Visits, bypass Manual Review, execute retries, run reconciliation, call external APIs, update technician mobile workflows, run background execution, or alter confirmation/recovery evidence. Future AI may only add advisory context after deterministic confirmation, failure, retry, or reconciliation evidence exists and must remain subordinate to Manual Review and operator/system authorization.

## Phase 0 Module 17 Boundary

Operational event history is deterministic and append-only.

AI is still not used in this module.

AI must not create, mutate, delete, reorder, replay, summarize into authoritative state, or reinterpret immutable operational event records as workflow authority. Future AI may help explain event timelines for operators only after deterministic event records exist, and those explanations must remain advisory context separate from the source-of-truth event history.

## Phase 0 Module 19 Boundary

Dispatch reconciliation and operational consistency verification are deterministic only.

AI is still not used in this module.

AI must not execute reconciliation, clear reconciliation blockers, classify divergence as resolved, create standard reconciliation for Water Emergency Visits, bypass Manual Review, mutate operational event history, replay workflows, call external APIs, execute retries, run analytics as workflow authority, or alter reconciliation evidence. Future AI may only add advisory explanation after deterministic consistency and divergence evidence exists and must remain subordinate to Manual Review and operator decisions.

## Phase 0 Module 20 Boundary

Operational replay and recovery preparation is deterministic only.

AI is still not used in this module.

AI must not prepare replay as authorized, clear replay blockers, execute replay, execute rollback, execute retries, create standard replay/recovery for Water Emergency Visits, bypass Manual Review, mutate operational event history, call external APIs, run workflow engines, or alter replay/recovery evidence. Future AI may only add advisory explanation after deterministic replay eligibility and recovery evidence exists and must remain subordinate to Manual Review and operator decisions.

## Phase 0 Module 21 Boundary

Operational governance and approval control are deterministic only.

AI is still not used in this module.

AI must not approve operator actions, authorize replay, authorize rollback, approve reconciliation, clear governance blockers, execute manual interventions, create standard governance for Water Emergency Visits, bypass Manual Review, mutate operational event history, call external APIs, run workflow engines, or alter governance evidence. Future AI may only add advisory explanation after deterministic governance evidence exists and must remain subordinate to Manual Review and authenticated operator decisions.

## Phase 0 Module 22 Boundary

Operational accountability, escalation preparation, intervention escalation, and incident preparation are deterministic only.

AI is still not used in this module.

AI must not prepare escalation as authorized, create incidents, execute incident workflows, escalate interventions, clear accountability blockers, create standard accountability for Water Emergency Visits, bypass governance approval, bypass Manual Review, mutate operational event history, call external APIs, run workflow engines, or alter accountability evidence. Future AI may only add advisory explanation after deterministic accountability evidence exists and must remain subordinate to Manual Review, governance authority, and authenticated operator decisions.

## Phase 0 Module 23 Boundary

Operational dashboard read models and dashboard API contracts are deterministic only.

AI is still not used in this module.

AI must not generate authoritative dashboard state, infer hidden lifecycle transitions, clear blockers, summarize uncertainty into operational approval, resolve Manual Review, execute dispatch, trigger integrations, or reinterpret immutable event history as workflow authority. Future AI may only provide advisory explanations of already persisted dashboard evidence, and those explanations must remain separate from the read models that drive operational UI state.

## Phase 0 Module 24 Boundary

The frontend dashboard foundation is display-only and deterministic.

AI is still not used in this module.

AI must not generate dashboard authority, create hidden workflow state, override backend read models, clear Manual Review items, execute dispatch, call integrations, approve governance/accountability actions, or present advisory output as operational fact. Any future AI-facing dashboard feature must remain separate from backend read-model truth and must be labeled as advisory explanation only.

## Phase 0 Module 29 Boundary

Local dashboard seed scenario expansion is deterministic and synthetic only.

AI is still not used in this module.

AI must not generate production-like seed records, infer hidden lifecycle transitions, treat synthetic examples as operational truth, clear Manual Review states, execute dispatch, call integrations, approve governance/accountability actions, or transform fake dashboard data into production workflow authority. Future AI-assisted demo generation, if ever introduced, must remain advisory and must preserve explicit synthetic-data labeling.

## Phase 0 Module 25 Boundary

The frontend visual QA and polish pass is display-only and deterministic.

AI is still not used in this module.

AI must not provide dashboard authority, generate hidden lifecycle state, create operational action controls, override backend read models, clear blockers, resolve Manual Review, execute dispatch, call integrations, or reinterpret visual dashboard summaries as approval. Future AI dashboard assistance must remain advisory and separate from persisted dashboard evidence.

## Phase 0 Module 26 Boundary

The full-stack dashboard integration pass is display-only and deterministic.

AI is still not used in this module.

AI must not influence frontend/backend dashboard integration, generate dashboard data, bypass fallback labeling, infer lifecycle transitions, clear backend blockers, resolve Manual Review, execute dispatch, call integrations, or change read-model authority. Future AI dashboard explanation features must remain advisory and separated from persisted backend dashboard read models.

## Phase 0 Module 27 Boundary

The local PostgreSQL live dashboard verification pass is deterministic and development-only.

AI is still not used in this module.

AI must not generate dashboard seed data, classify seed records as production evidence, bypass Manual Review, infer hidden lifecycle transitions from demo records, clear blockers, resolve Manual Review, execute dispatch, call integrations, authorize recovery/governance/escalation, or change backend read-model authority. Future AI explanation features must remain advisory and separate from persisted dashboard evidence.

## Phase 0 Module 30 Boundary

The live dashboard scenario storyboard is deterministic, display-only, and frontend-only.

AI is still not used in this module.

AI must not generate storyboard authority, infer hidden lifecycle transitions from grouped dashboard counts, treat synthetic seed examples as production evidence, clear Manual Review states, execute dispatch, call integrations, authorize recovery/governance/escalation, or transform read-only scenario visualization into workflow control. Future AI-assisted dashboard explanations must remain advisory and separate from persisted backend dashboard read models.

## Phase 0 Module 31 Boundary

The dedicated Water Emergency dashboard contract and frontend view are deterministic, display-only, and read-only.

AI is still not used in this module.

AI must not generate Water Emergency dashboard authority, infer hidden emergency lifecycle transitions, auto-close emergency work, clear Manual Review states, execute dispatch, call vendor integrations, authorize equipment pickup, or transform read-only emergency visibility into workflow control. Future AI explanations for Water Emergency evidence must remain advisory and separate from persisted backend dashboard read models.

## Phase 0 Module 32 Boundary

The Water Emergency detail read model and timeline visualization are deterministic, display-only, and read-only.

AI is still not used in this module.

AI must not generate Water Emergency detail authority, infer hidden lifecycle transitions from timeline events, edit or close emergency work, clear scoped Manual Review indicators, execute dispatch, call vendor integrations, authorize equipment pickup, or transform detail evidence into workflow control. Future AI explanations for Water Emergency detail evidence must remain advisory and separate from persisted backend read models.

## Phase 0 Module 33 Boundary

Water Emergency equipment, visit-chain, and drying-stage visibility are deterministic, display-only, and read-only.

AI is still not used in this module.

AI must not infer final Water Emergency drying taxonomy, create equipment inventory, authorize equipment pickup, schedule visits, close emergency work, clear Manual Review indicators, execute dispatch, call vendor integrations, or transform read-only equipment/visit/drying context into workflow control. Future AI explanations for these views must remain advisory and separate from persisted backend read models.

## Phase 0 Module 34 Boundary

Water Emergency review, exception, blocker, and critical-alert visibility is deterministic, display-only, and read-only.

AI is still not used in this module.

AI must not infer final Water Emergency review taxonomy, clear critical alerts, resolve Manual Review items, approve/reject emergency work, execute escalation, close emergency work, dispatch Water Emergency visits, call vendor integrations, or transform read-only review/exception context into workflow control. Future AI explanations for Water Emergency review evidence must remain advisory and separate from persisted backend read models.

## Phase 0 Module 35 Boundary

Water Emergency next-step readiness visibility is deterministic, display-only, and read-only.

AI is still not used in this module.

AI must not infer final Water Emergency readiness taxonomy, choose operational next actions, approve Manual Review, close emergency work, schedule follow-up visits, authorize equipment pickup, confirm drying stages, dispatch Water Emergency visits, call vendor integrations, or transform read-only readiness context into workflow control. Future AI explanations for Water Emergency readiness evidence must remain advisory and separate from persisted backend read models.

## Phase 0 Module 36 Boundary

Water Emergency operator queue and attention triage visibility is deterministic, display-only, and read-only.

AI is still not used in this module.

AI must not infer final Water Emergency queue taxonomy, prioritize work as operational authority, approve Manual Review, close emergency work, schedule follow-up visits, authorize equipment pickup, confirm drying stages, dispatch Water Emergency visits, call vendor integrations, or transform read-only queue context into workflow control. Future AI explanations for Water Emergency queue evidence must remain advisory and separate from persisted backend read models.

## Phase 0 Module 37 Boundary

Water Emergency aging, follow-up risk, stale evidence, and unknown timing visibility is deterministic, display-only, and read-only.

AI is still not used in this module.

AI must not infer final Water Emergency SLA taxonomy, decide overdue authority, auto-escalate, approve Manual Review, close emergency work, schedule follow-up visits, authorize equipment pickup, confirm drying stages, dispatch Water Emergency visits, call vendor integrations, or transform read-only timing context into workflow control. Future AI explanations for Water Emergency timing evidence must remain advisory and separate from persisted backend read models.

## Phase 0 Module 38 Boundary

Water Emergency filtering, sorting, grouping, and operator view-state visibility is deterministic, display-only, and read-only.

AI is still not used in this module.

AI must not infer final Water Emergency filter taxonomy, choose operational priority, persist user view preferences, approve Manual Review, close emergency work, schedule follow-up visits, authorize equipment pickup, confirm drying stages, dispatch Water Emergency visits, call vendor integrations, or transform read-only filter/sort context into workflow control. Future AI explanations for Water Emergency view-state evidence must remain advisory and separate from persisted backend read models.

## Phase 0 Module 39 Boundary

Water Emergency governance metadata, saved view preferences, role-visibility planning, and scalability readiness are deterministic, display-only, and read-only.

AI is still not used in this module.

AI must not infer final Water Emergency legal policy, insurance policy, SLA taxonomy, warranty language, drying certification language, owner-review outcomes, role authorization, saved-view authority, or workflow priority. AI must not approve Manual Review, close emergency work, schedule follow-up visits, authorize equipment pickup, confirm drying stages, dispatch Water Emergency visits, call vendor integrations, persist backend preferences, implement auth/RBAC, or transform governance metadata into workflow control. Future AI explanations for Water Emergency governance evidence must remain advisory and separate from persisted backend read models and Alfonso owner-review policy decisions.

## Phase 0 Module 40 Boundary

Manual Review queue visibility is deterministic, display-only, and read-only.

AI is still not used in this module.

AI must not infer final Manual Review action taxonomy, approve, reject, defer, archive, resolve, dispatch, escalate, clear blockers, call vendor integrations, or transform queue visibility into workflow control. Future AI explanations for Manual Review queue evidence must remain advisory and separate from persisted backend read models.

## Phase 0 Module 41 Boundary

Manual Review detail and evidence timeline visibility is deterministic, display-only, and read-only.

AI is still not used in this module.

AI must not infer hidden lifecycle transitions from Manual Review detail evidence, approve, reject, defer, archive, resolve, dispatch, escalate, clear blockers, call vendor integrations, or transform timeline context into workflow control. Future AI explanations for Manual Review detail evidence must remain advisory and separate from persisted backend read models.

## Phase 0 Module 42 Boundary

Manual Review filtering, sorting, saved view preferences, and queue scalability visibility are deterministic, display-only, and read-only.

AI is still not used in this module.

AI must not infer final Manual Review filter taxonomy, choose operational priority, approve, reject, defer, archive, resolve, dispatch, escalate, persist backend preferences, implement auth/RBAC, call vendor integrations, or transform frontend view-state into workflow control. Future AI explanations for Manual Review filter/sort evidence must remain advisory and separate from persisted backend read models.

## Phase 0 Module 43 Boundary

Manual Review decision-readiness, blocker, and resolution-preparation visibility is deterministic, display-only, and read-only.

AI is still not used in this module.

AI must not infer final Manual Review readiness taxonomy, approve, reject, defer, archive, resolve, dispatch, escalate, clear blockers, decide missing information is sufficient, call vendor integrations, implement auth/RBAC, or transform readiness labels into workflow authority. Future AI explanations for Manual Review readiness evidence must remain advisory and separate from persisted backend read models.

## Phase 0 Module 44 Boundary

Manual Review action-preflight, future authorization readiness, blocker evidence, operator identity preparation, and audit-reason preparation visibility is deterministic, display-only, and read-only.

AI is still not used in this module.

AI must not infer final Manual Review action eligibility, approve, reject, defer, archive, resolve, dispatch, escalate, clear blockers, decide missing information is sufficient, create auth/RBAC behavior, create operator identity, create audit reasons, call vendor integrations, or transform action-preflight labels into workflow authority. Future AI explanations for Manual Review action-preflight evidence must remain advisory and separate from persisted backend read models and authenticated operator actions.

## Phase 0 Module 45 Boundary

Manual Review future-action preview, expected outcome preparation, impacted entity visibility, operator identity preparation, and audit-reason preparation visibility is deterministic, display-only, and read-only.

AI is still not used in this module.

AI must not infer final Manual Review action preview taxonomy, approve, reject, defer, archive, resolve, dispatch, escalate, clear blockers, decide missing information is sufficient, create auth/RBAC behavior, create operator identity, create audit reasons, decide expected outcomes, call vendor integrations, or transform future-action preview labels into workflow authority. Future AI explanations for Manual Review future-action preview evidence must remain advisory and separate from persisted backend read models and authenticated operator actions.

---

## Confidence And Review

Suggested confidence behavior:

- 95-100: safe automation if all deterministic rules pass
- 75-94: warning state; operator visibility required before sensitive actions
- below 75: Manual Review required

Any critical contradiction should override the numeric score and trigger Manual Review.

Examples:

- possible cancellation typo
- conflicting AM/PM or state tags
- missing or malformed address
- Water Emergency detected but workflow state is unclear
- FastField form mapping is ambiguous
- no matching technician user

---

## Audit Requirements

AI-assisted decisions must be traceable.

Log:

- input source
- AI task type
- advisory result
- confidence score when available
- deterministic validation result
- final operator/system action
- reason for Manual Review when triggered

Do not log secrets or sensitive credentials.

---

## Operational Boundary

The ACS FSM platform must remain state-driven and database-first.

AI may enrich records, but it must not become the source of truth for:

- dispatch status
- cancellation status
- Water Emergency lifecycle status
- technician assignment
- route approval
- FastField dispatch approval
- final job completion

---

## Phase 0 Module 46 Manual Review Command-Contract Boundary

Manual Review command-contract and audit-envelope labels are deterministic backend read-model metadata.

AI boundary:

- AI must not decide command eligibility
- AI must not generate executable approve/reject/defer/archive/resolve commands
- AI must not bypass Manual Review, auth, operator identity, role authorization, audit reason, idempotency, immutable event recording, or post-action consistency checks
- AI must not convert command-contract visibility into dispatch execution, vendor calls, or workflow transitions
- Water Emergency-related command contracts must remain separated from standard dispatch and cannot be auto-scoped by AI

Future AI assistance, if added, may only provide advisory evidence summaries after deterministic backend safety gates remain authoritative.

## Phase 0 Module 47 Manual Review Audit-Ledger Dry-Run Boundary

Manual Review audit-ledger dry-run labels are deterministic backend read-model metadata.

AI boundary:

- AI must not decide dry-run readiness
- AI must not generate executable approve/reject/defer/archive/resolve commands
- AI must not write audit events, generate authoritative audit reasons, persist idempotency keys, or mark immutable event recording complete
- AI must not bypass Manual Review, auth, operator identity, role authorization, audit reason, idempotency, immutable event recording, or post-action consistency checks
- AI must not convert dry-run visibility into dispatch execution, vendor calls, audit writes, or workflow transitions
- Water Emergency-related dry-runs must remain separated from standard dispatch and cannot be auto-scoped by AI

Future AI assistance, if added, may only provide advisory evidence summaries after deterministic backend safety gates and future authenticated audit/event controls remain authoritative.

## Phase 0 Module 48 Manual Review Command-Validation Boundary

Manual Review command-validation labels and safety gates are deterministic backend read-model metadata.

AI boundary:

- AI must not decide command validation results
- AI must not mark safety gates passed or executable
- AI must not generate executable approve/reject/defer/archive/resolve commands
- AI must not write audit events, generate authoritative audit reasons, persist idempotency keys, or mark immutable event recording complete
- AI must not bypass Manual Review, auth, operator identity, role authorization, audit reason, idempotency, immutable event recording, post-action consistency checks, or the Phase 0 execution block
- AI must not convert validation or safety-gate visibility into dispatch execution, vendor calls, audit writes, or workflow transitions
- Water Emergency-related validation must remain separated from standard dispatch and cannot be auto-scoped by AI

Future AI assistance, if added, may only provide advisory evidence summaries after deterministic backend validation, safety gates, and future authenticated audit/event controls remain authoritative.

## Phase 0 Module 49 Manual Review Operator-Identity And Permission Boundary

Manual Review permission-readiness labels, future role requirements, future forbidden roles, future permission sets, and operator-identity requirements are deterministic backend read-model metadata.

AI boundary:

- AI must not decide operator identity or role authorization
- AI must not create fake roles, fake operators, login/session/token behavior, or RBAC enforcement
- AI must not generate executable approve/reject/defer/archive/resolve commands
- AI must not write audit events, generate authoritative audit actors or audit reasons, persist idempotency keys, or mark immutable event recording complete
- AI must not bypass Manual Review, auth, operator identity, role authorization, audit reason, idempotency, immutable event recording, post-action consistency checks, or the Phase 0 execution block
- AI must not convert permission-readiness visibility into dispatch execution, vendor calls, audit writes, role enforcement, or workflow transitions
- Water Emergency-related authorization requirements must remain separated from standard dispatch and cannot be auto-scoped by AI

Future AI assistance, if added, may only provide advisory evidence summaries after deterministic backend permission readiness and future authenticated auth/RBAC/audit/event controls remain authoritative.

## Phase 0 Module 50 Manual Review Execution-Readiness Boundary

Manual Review execution-readiness audit labels, mutation-boundary metadata, future transition prerequisites, and owner-review guardrails are deterministic backend read-model metadata.

AI boundary:

- AI must not decide execution readiness for current action
- AI must not enable Manual Review mutations or mark mutation endpoints available
- AI must not change `currently_executable_count` or bypass the Phase 0 execution block
- AI must not create fake roles, fake operators, login/session/token behavior, auth headers, or RBAC enforcement
- AI must not generate executable approve/reject/defer/archive/resolve commands
- AI must not write audit events, generate authoritative audit actors or audit reasons, persist idempotency keys, mark immutable event recording complete, or mark post-action consistency complete
- AI must not bypass Manual Review, auth, operator identity, role authorization, audit reason, idempotency, immutable event recording, post-action consistency checks, owner review, or the Review GUI/ChatGPT review workflow
- AI must not convert execution-readiness visibility into dispatch execution, vendor calls, audit writes, role enforcement, mutation endpoints, or workflow transitions
- Water Emergency-related readiness must remain separated from standard dispatch and cannot be auto-scoped by AI

Future AI assistance, if added, may only provide advisory evidence summaries after deterministic backend mutation boundaries and future authenticated auth/RBAC/audit/event controls remain authoritative.

## Phase 0 Module 55 Route Protection Matrix Boundary

Route protection matrix labels, future route-to-permission mappings, UI permission-boundary labels, and access decision dry-run counts are deterministic backend read-model metadata.

AI boundary:

- AI must not decide route access
- AI must not enable route guards, route denial, UI section hiding, token verification, JWT parsing, auth headers, or RBAC enforcement
- AI must not create fake roles, fake operators, login/session/token behavior, or fake route protection
- AI must not generate executable approve/reject/defer/archive/resolve commands
- AI must not bypass Manual Review, auth, operator identity, role authorization, audit reason, idempotency, immutable event recording, post-action consistency checks, owner review, or the Phase 0 execution block
- AI must not convert route protection visibility into dispatch execution, vendor calls, audit writes, route enforcement, role enforcement, mutation endpoints, or workflow transitions
- Water Emergency-related route protection must remain separated from standard dispatch and cannot be auto-scoped by AI

Future AI assistance, if added, may only provide advisory evidence summaries after deterministic backend route protection and future authenticated auth/RBAC/audit/event controls remain authoritative.

## Phase 0 Module 56 Auth/RBAC Readiness Audit Boundary

Auth/RBAC readiness audit labels, enforcement-boundary lock labels, and future transition prerequisites are deterministic backend read-model metadata.

AI boundary:

- AI must not decide auth/RBAC readiness
- AI must not enable auth enforcement, token verification, real token parsing, JWKS fetch, RBAC enforcement, route guarding, UI section hiding, auth headers, or user management
- AI must not mark future transition prerequisites satisfied except where deterministic backend metadata already reports them satisfied
- AI must not create fake roles, fake operators, login/session/token behavior, fake route protection, fake owner review, or fake audit actors
- AI must not generate executable approve/reject/defer/archive/resolve commands
- AI must not bypass Manual Review, auth, operator identity, role authorization, audit reason, idempotency, immutable event recording, post-action consistency checks, owner review, the Phase 0 execution block, or the Review GUI/ChatGPT review workflow
- AI must not convert Auth/RBAC readiness visibility into dispatch execution, vendor calls, audit writes, route enforcement, role enforcement, mutation endpoints, or workflow transitions
- Water Emergency-related authorization readiness must remain separated from standard dispatch and cannot be auto-scoped by AI

Future AI assistance, if added, may only provide advisory evidence summaries after deterministic backend auth/RBAC, route protection, audit/event, and action controls remain authoritative.

## Phase 0 Module 57 Backend Auth Core Disabled Scaffold Boundary

Backend auth-core scaffold labels, disabled token-verifier labels, optional auth-context labels, and current-route auth requirement labels are deterministic backend metadata.

AI boundary:

- AI must not decide authentication status
- AI must not treat Authorization header presence as an authenticated operator
- AI must not enable token verification, real token parsing, JWKS fetch, provider network calls, RBAC enforcement, route guarding, UI section hiding, auth headers, login/session/token behavior, or user management
- AI must not create fake roles, fake operators, fake auth contexts, fake route access, fake owner review, or fake audit actors
- AI must not generate executable approve/reject/defer/archive/resolve commands
- AI must not bypass Manual Review, auth, operator identity, role authorization, audit reason, idempotency, immutable event recording, post-action consistency checks, owner review, the Phase 0 execution block, or the Review GUI/ChatGPT review workflow
- AI must not convert disabled auth-core visibility into dispatch execution, vendor calls, audit writes, route enforcement, role enforcement, mutation endpoints, or workflow transitions
- Water Emergency-related authorization readiness must remain separated from standard dispatch and cannot be auto-scoped by AI

Future AI assistance, if added, may only provide advisory evidence summaries after deterministic backend auth/RBAC, route protection, audit/event, and action controls remain authoritative.
