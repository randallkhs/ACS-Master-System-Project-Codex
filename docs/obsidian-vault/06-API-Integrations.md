# ACS FSM — API Integrations

## Purpose

This file records the integration philosophy and known adapter boundaries for ACS FSM.

---

## Adapter Rule

All external systems must be isolated behind adapters.

The core ACS FSM platform should use internal domain models and services, not vendor-specific data structures.

---

## Initial Integrations

## Google Calendar

Role: schedule input adapter.

Initial use:

- import target-date jobs
- preserve source event IDs
- normalize freeform event data into structured internal records

Google Calendar is not the source of truth after import.

## Google Sheets

Role: transitional dispatch output adapter.

Initial use:

- preserve existing operational sheet compatibility
- preview before write
- support AppleJobs and Water Emergency output separation

Long-term goal: replace spreadsheet dependence with database-driven UI.

## FastField

Role: transitional work-order/dispatch adapter.

Initial use:

- support current standard-job dispatch
- support separate Water Emergency workflow/form requirements
- preview before send

Critical rule: never send Water Emergency jobs through the regular FastField work-order path.

Long-term goal: replace FastField with native ACS technician workflows.

## Verizon Connect

Role: future vehicle/GPS adapter.

Future use:

- technician/vehicle location
- route visibility
- dynamic reassignment support

## AI Providers

Role: assistant and validation adapter.

Allowed use:

- classification suggestions
- anomaly detection
- confidence scoring support
- summarization

Forbidden use:

- operational authority
- silent dispatch
- auto-confirmed cancellation
- auto-closed Water Emergency workflows

See [[08-AI-Systems/AI_AUTOMATION_RULES]].

---

## Integration Safety Requirements

- Use environment variables or secure secret storage for credentials.
- Do not hardcode API keys or passwords.
- Log imports, exports, sends, failures, and operator approvals.
- Support preview/dry-run for risky outputs.
- Send uncertain records to Manual Review before external write/send.

## Phase 0 Module 15 External Adapter Boundary

External dispatch adapter preparation is deterministic and prepare-only.

Current payload foundations:

- FastField standard dispatch payload snapshot
- Google Sheets standard-job dispatch row snapshot
- Google Calendar dispatch-status sync snapshot
- technician mobile standard-visit sync snapshot

Rules:

- prepared payloads are evidence, not live sends
- external API calls remain `not_executed`
- Water Emergency work cannot use the standard adapter path
- blocked, review-required, unauthorized, undispatched, or duplicate-prepared records cannot reach adapter preparation
- future live adapters must write execution outcomes back to the database without becoming workflow authority

## Phase 0 Module 16 External Confirmation And Recovery Boundary

External confirmation and recovery preparation is deterministic and simulation-only.

Current outcome foundations:

- external confirmation success evidence
- external confirmation failure evidence
- retry preparation evidence
- reconciliation-required evidence
- confirmation audit evidence

Rules:

- confirmation processing consumes adapter-prepared records awaiting external confirmation
- external API calls remain `not_executed`
- retries are prepared only, not executed automatically
- reconciliation is prepared only, not executed automatically
- Water Emergency work cannot use the standard external confirmation path
- blocked, review-required, unauthorized, duplicate-confirmed, adapter-unready, or invalid-lifecycle records cannot reach confirmation
- future live adapters must write confirmation outcomes back to the database without becoming workflow authority
