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
