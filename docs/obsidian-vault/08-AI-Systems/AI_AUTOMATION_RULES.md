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
