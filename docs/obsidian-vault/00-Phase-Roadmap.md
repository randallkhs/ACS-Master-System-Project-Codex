# ACS-FSM Phase Roadmap

Date: 2026-05-27
Status: Phase 0 transition-readiness baseline

This roadmap is planning documentation only. It does not authorize execution, deployment, auth enforcement, RBAC, route protection, vendor calls, AI authority, or Manual Review/Water Emergency actions.

Phase 1 production infrastructure readiness is documented in [[00-Phase-1-Production-Infrastructure-Readiness]]. That document is a readiness baseline only; it does not deploy ACS-FSM or provision production resources.

## Phase 0 - Read-Only Foundations And Safety Boundaries

Goal: Build deterministic foundations, read-only visibility, local verification, Manual Review safety boundaries, Water Emergency separation, disabled auth/RBAC readiness, and stakeholder reporting.

Expected capabilities:

- backend foundation and database model
- local PostgreSQL and seed verification
- read-only dashboard and ACSSDR reporting
- Manual Review readiness and future action planning
- Water Emergency separated visibility
- disabled auth/RBAC scaffolding and cutover checklist
- master documentation, inventory, checklist, and risk register

Prerequisites: current docs and tests remain stable; no production action execution.

Must not happen prematurely: production deployment, real auth, token verification, RBAC enforcement, route guards, action buttons, vendor writes, or AI authority.

Risks: historical documentation gaps, readiness metadata mistaken for executable capability, stale stakeholder reporting.

Owner-review concerns: Water Emergency legal/insurance/company-liability policy remains future owner review.

## Phase 1 - Production Infrastructure Readiness

Goal: Prepare the production environment without turning on real operational actions.

Expected capabilities:

- VPS/app runtime plan
- production database provisioning plan
- secure environment and secret storage plan
- backup/restore and migration rollout runbook
- monitoring/logging plan
- deployment rollback plan
- ACSSDR/reporting continuity
- environment separation and deployment boundary checklist

Prerequisites: Phase 0 docs complete, tests stable, dashboard read-only stable, review workflow stable, production infrastructure plan approved.

Must not happen prematurely: real auth, action execution, vendor writes, production data mutation without backup/rollback plan.

Risks: deployment drift, incomplete backup/restore, secrets mishandling, local assumptions leaking into production.

Owner-review concerns: production operational policy and company-liability controls may need owner review.

## Phase 2 - Real Auth/RBAC Implementation

Goal: Implement real authentication and authorization after provider, secret storage, and route guard plans are approved.

Expected capabilities:

- selected auth provider
- secure credentials outside Git
- backend token verification
- JWKS/network policy
- frontend sign-in/sign-out/session UX
- persisted operator identity
- RBAC role/permission enforcement
- route protection
- role-scoped visibility

Prerequisites: production environment ready, secret management ready, auth provider selected by Randall, deployment pipeline stable, rollback plan exists.

Must not happen prematurely: auth headers emitted before backend verification, fake users, fake roles, route hiding without backend enforcement, Manual Review action authority.

Risks: token leakage, incomplete RBAC, role confusion, service-account misuse, technician role overreach.

Owner-review concerns: formal access policies that affect company liability may need owner review.

## Phase 3 - Controlled Manual Review Actions

Goal: Add authenticated, audited Manual Review actions after auth/RBAC and audit actor support exist.

Expected capabilities:

- approve/reject/defer/archive/request-info actions
- audit actor capture
- required audit reasons
- idempotency keys
- immutable event writes
- post-action consistency checks
- role-scoped action authority

Prerequisites: real auth implemented, RBAC enforced, audit actor available, Manual Review action permissions approved, immutable event writes tested, idempotency tested.

Must not happen prematurely: unauthenticated action execution, hidden lifecycle transitions, vendor calls, Water Emergency actions through standard flow.

Risks: wrong entity mutation, duplicate action, missing audit reason, bypassing Manual Review safety.

Owner-review concerns: any action that creates customer, billing, legal, warranty, insurance, or formal company-policy consequences may require Alfonso owner review.

## Phase 4 - Dispatch Execution Engine

Goal: Execute standard dispatch through controlled internal workflow paths and approved operator/system authority.

Expected capabilities:

- route/visit dispatch execution
- dispatch audit events
- standard-work-only dispatch action controls
- integration-preparation handoff
- rollback/replay evidence

Prerequisites: Manual Review actions stable, standard dispatch permission model approved, audit/event/idempotency foundations active.

Must not happen prematurely: Water Emergency through standard dispatch, external vendor writes without adapter approval, AI dispatch authority.

Risks: dispatching canceled jobs, dispatching blocked jobs, wrong technician/route assignment.

Owner-review concerns: dispatch policy that affects customer commitments or company liability may require review.

## Phase 5 - Water Emergency Execution

Goal: Add controlled Water Emergency workflow actions after owner-reviewed policy boundaries are approved.

Expected capabilities:

- separated emergency action model
- visit/equipment/drying lifecycle actions
- moisture/equipment history
- close/pickup/readiness actions only after rules are approved
- owner-review flags for legal/insurance-sensitive outputs

Prerequisites: Water Emergency data model approved, owner-review boundaries resolved, auth/RBAC/action audit stack active.

Must not happen prematurely: auto-close, drying certification, warranty/customer promises, billing/insurance policy claims, standard dispatch path execution.

Risks: legal/insurance exposure, incomplete equipment tracking, incorrect closure, customer promise ambiguity.

Owner-review concerns: high. Alfonso owner review is likely required for formal policy, closure, certification, warranty, billing, insurance, or customer-liability behavior.

## Phase 6 - External Integrations

Goal: Turn adapter preparation into controlled external execution after internal source-of-truth and action authority exist.

Expected capabilities:

- Google Calendar sync/write controls
- Google Sheets transitional output
- FastField sends
- email/notification sends
- possible routing/maps/GPS adapters
- provider execution outcomes written back to database

Prerequisites: production secret management, adapter approval, audit/idempotency, retry/recovery policy, dry-run verification, rollback strategy.

Must not happen prematurely: vendor writes without preview/approval, external systems becoming source of truth, automatic retries without policy.

Risks: credential leakage, duplicate sends, vendor-side divergence, retry storms, Water Emergency sent through standard path.

Owner-review concerns: external customer/vendor communication and billing/insurance implications may require review.

## Phase 7 - Technician And Field Operations

Goal: Support technician-facing workflows after core dispatch and Water Emergency execution are safe.

Expected capabilities:

- technician app/portal
- assigned visits and route order
- field notes/photos
- equipment updates
- status updates
- future GPS/vehicle context

Prerequisites: auth/RBAC, technician identity model, mobile UX approval, offline/error handling, audit trail.

Must not happen prematurely: unauthenticated technician updates, unreviewed field status authority, hidden customer-facing commitments.

Risks: stale mobile data, wrong technician identity, incomplete offline handling, equipment mismatch.

Owner-review concerns: technician policy and customer-facing communication may require review.

## Phase 8 - Analytics, Reporting, And Management

Goal: Provide management reporting and analytics from trusted operational data.

Expected capabilities:

- operational KPIs
- Water Emergency lifecycle reporting
- technician workload reporting
- dispatch efficiency
- review queue trends
- integration reliability

Prerequisites: stable production data, event history, role-scoped reporting, data retention policy.

Must not happen prematurely: treating synthetic/local data as production truth, exposing sensitive data broadly.

Risks: misleading metrics, privacy exposure, stale reporting, unapproved financial/billing interpretation.

Owner-review concerns: financial, customer, employee, and policy reporting may require review.

## Phase 9 - AI Advisory Enhancements

Goal: Add AI assistance only after deterministic workflows and review boundaries are stable.

Expected capabilities:

- advisory summaries
- anomaly explanations
- classification suggestions
- review triage suggestions
- operator-facing risk explanations

Prerequisites: deterministic evidence, audit boundaries, labeling, prompt/response retention policy, no-action authority boundary.

Must not happen prematurely: AI approving, dispatching, closing, overriding, hiding uncertainty, or mutating workflow state.

Risks: hallucination, overtrust, privacy exposure, implicit authority.

Owner-review concerns: AI-generated customer-facing or policy-sensitive outputs may require review.

## Transition Criteria Summary

Phase 0 to Phase 1:

- Phase 0 docs complete
- local tests stable
- review workflow stable
- dashboard read-only stable
- ACSSDR reporting stable
- production infrastructure plan approved
- database provisioning plan approved
- backup/restore plan drafted

Phase 1 to Phase 2:

- production environment ready
- secret management ready
- auth provider selected
- deployment pipeline stable
- rollback plan exists

Phase 2 to Phase 3:

- real auth implemented
- RBAC enforced
- audit actor available
- Manual Review action permissions approved
- immutable event writes tested
- idempotency tested
