# Phase 1 Production Infrastructure Readiness

Date: 2026-05-27
Status: Module 62 production-infrastructure readiness baseline
Authority: Randall-authorized Phase 1 readiness baseline for technical planning

This document is planning and readiness documentation only. It does not deploy ACS-FSM, change a VPS, install Apache configuration, provision production PostgreSQL, create production secrets, enable auth, execute actions, call vendors, or grant workflow authority.

## Phase 1 Purpose

Phase 1 prepares ACS-FSM for a future production environment without turning on production behavior. The goal is to define deployment boundaries, environment separation, database and secret expectations, backup/restore needs, health checks, rollback planning, and approval gates before any production deployment module is attempted.

Phase 1 must preserve all Phase 0 safety rules:

- Manual Review remains authoritative.
- Water Emergency remains isolated from standard flows.
- AI remains advisory-only.
- Auth/RBAC remains disabled until a later reviewed implementation phase.
- Current dashboard behavior remains read-only.
- No vendor integration writes or operational actions are executed.

## Deployment Boundary

Current state:

- `production_deployment_ready: false`
- `staging_deployment_ready: false`
- `production_database_provisioned: false`
- `production_secrets_configured: false`
- `apache_reverse_proxy_configured: false`
- `backup_plan_approved: false`
- `restore_drill_completed: false`
- `monitoring_configured: false`
- `rollback_plan_approved: false`
- `auth_enforcement_ready: false`
- `manual_review_actions_ready: false`
- `water_emergency_actions_ready: false`
- `external_integrations_ready: false`
- `phase1_readiness_documented: true`

These values are informational readiness labels only. They must not block routes, hide UI, enforce permissions, grant authority, or mutate runtime state.

## Environment Separation

| Environment | Purpose | Database source | Credentials policy | Allowed data type | Deployment target | Auth state | External integrations state | ACSSDR visibility | Backup requirement | Owner/review requirement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `local_dev` | Developer workstation testing and read-only dashboard verification. | Local-only development database such as `acs_fsm_dev`. | Local `.env` only; no real production credentials. | Synthetic/dev data only. | Local machine. | Disabled/non-enforcing. | Disabled; no live vendor calls. | Not directly public except summarized after reviewed modules. | Optional local backup before risky dev changes. | Randall technical approval. |
| `test` | Automated tests and isolated verification. | Test database or in-memory/unit-test fixtures. | Test-only placeholders. | Synthetic/test data only. | Local/CI future. | Disabled unless a future auth test profile explicitly enables safe test doubles. | Disabled; no live vendor calls. | Not public. | Disposable or resettable test data. | Randall technical approval. |
| `staging_future` | Future production-like rehearsal before real cutover. | Separate staging database, not local and not production. | Staging secrets outside Git. | Approved staging/demo data only; no unapproved customer data. | Future staging runtime. | Future auth only after Phase 2 readiness. | Dry-run or staging-only providers unless approved. | May be summarized in ACSSDR without sensitive details. | Required before staging migrations or rehearsals. | Randall approval; production owner approval if infrastructure/security risk exists. |
| `production_future` | Future live ACS operational system. | Separate production PostgreSQL instance. | Production secrets outside Git through approved secret management. | Real operational data only after production approval. | Future production VPS/app runtime. | Future real auth/RBAC after approved implementation. | Live integrations only after approved action/integration phases. | Stakeholder-friendly summary only; no secrets or sensitive internals. | Required, scheduled, retained, and restore-tested. | Randall approval; Alfonso owner review for legal/insurance/company-liability workflows. |

## Future VPS Deployment Concept

Future production deployment should use a dedicated runtime boundary, not the iCloud development path.

Planning assumptions:

- Use a dedicated application account or service account approved by Randall.
- Use a dedicated repository checkout or release artifact directory, represented here as `<acs-fsm-release-dir>`.
- Keep runtime environment files outside Git.
- Keep logs in an approved application log location, represented here as `<acs-fsm-log-dir>`.
- Use a process manager approved in a future deployment module.
- Keep deployment actions repeatable, reversible, and documented.

Backend runtime concept:

- Run FastAPI with an approved ASGI server and process manager.
- Bind the backend to a private local interface or protected internal port.
- Expose backend API traffic only through the approved reverse proxy path.
- Keep `/api/v1/health` available for health checks.
- Do not enable production auth or action endpoints until later reviewed phases.

Frontend runtime concept:

- Build the Next.js frontend in a controlled release process.
- Serve it through an approved Node runtime, static export strategy, or reverse-proxied frontend service chosen in a future deployment module.
- Configure `ACS_DASHBOARD_API_BASE_URL` per environment.
- Do not emit Authorization headers or add login/session behavior in this module.

No VPS command was run for this module. No production service was created, restarted, or modified.

## Apache Reverse Proxy Planning

Future Apache planning should be documented as a template concept only until a reviewed deployment module installs it.

Expected concepts:

- HTTPS must be active before production use.
- Frontend requests should route to the approved frontend runtime.
- Backend API requests should route to the approved backend runtime under a clear API path.
- Reverse proxy timeouts should support dashboard reads without hiding backend failures.
- Forwarded headers should be reviewed so request IDs, scheme, and client context are trustworthy.
- Security headers should be reviewed before public production use.
- ACSSDR must remain separated from the ACS-FSM app runtime and must not be accidentally proxied through the application service.

No Apache virtual host, `.htaccess`, proxy rule, certificate, or server config is installed by this module. Any sample config in future work must be labeled as inactive template material.

## Production PostgreSQL Planning

Production PostgreSQL must be separate from local `acs_fsm_dev`.

Future requirements:

- Dedicated production database name approved by Randall.
- Dedicated least-privilege application database user.
- No local development password reuse.
- No production connection string committed to Git.
- Migration rollout policy with explicit pre-migration backup.
- Post-migration validation checklist.
- Restore procedure documented and tested.
- No production database dump committed.
- No real production customer data used in local or test seed data.

Migration expectations:

1. Confirm target environment.
2. Confirm maintenance/rollback window if needed.
3. Create or verify a current backup.
4. Run migrations through the approved deployment process.
5. Verify schema version and health checks.
6. Verify read-only dashboard behavior.
7. Record outcome and rollback decision if validation fails.

## Production Secret Management

Secrets must live outside Git.

Rules:

- `.env` and `.env.local` remain untracked.
- Service account JSON files must not be committed.
- Private keys must not be committed.
- Real JWTs or signed-token examples must not be committed.
- Auth provider credentials are future-only.
- Google, FastField, email, routing/maps, and GPS credentials are future-only.
- Production secrets must be supplied by Randall through an approved method.
- Secret rotation and emergency revocation procedures must be documented before production use.
- Logs and diagnostics must never print secret values.

Current readiness:

- `production_secrets_configured: false`
- `real_credentials_required_for_future_deployment: true`
- `committed_credentials_allowed: false`

## Backup And Restore Expectations

Production deployment must not proceed without backup/restore planning.

Future requirements:

- Scheduled production PostgreSQL backups.
- Retention policy approved by Randall.
- Pre-deployment backup before risky releases.
- Pre-migration backup before schema changes.
- Restore drill completed before production trust.
- Restore verification includes schema version, application health, and read-only dashboard smoke checks.
- Backup storage location and access controls approved.
- No backup archive or database dump committed to Git.

Current readiness:

- `backup_plan_approved: false`
- `restore_drill_completed: false`
- `disaster_recovery_ready: false`

## Rollback Expectations

Future deployment modules need rollback plans before production cutover.

Rollback planning should include:

- release artifact or Git commit identification
- database migration rollback policy
- backup restore decision point
- process restart procedure
- health-check gates
- operator communication plan
- post-rollback verification checklist

Current readiness:

- `rollback_plan_approved: false`
- `deployment_cutover_ready: false`

## Health And Monitoring Expectations

Future production monitoring should include:

- backend `/api/v1/health`
- dashboard API read checks
- frontend smoke test
- server process health
- application logs
- reverse proxy logs
- database connectivity checks
- auth/secret hygiene check before release
- error monitoring
- uptime monitoring
- alerting/escalation ownership

Current readiness:

- `monitoring_configured: false`
- `alerting_configured: false`
- `production_health_check_runbook_ready: false`

## Security Boundaries

Phase 1 readiness does not weaken any existing security boundary.

Required future approvals:

- production environment owner approval before any server change
- secret-management approval before real credentials
- auth provider approval before Phase 2 implementation
- backup/restore approval before production data
- Alfonso owner review for legal, insurance, warranty, billing, customer-liability, or formal company-policy workflows

Forbidden in this module:

- production deployment
- VPS modification
- Apache config installation
- production DB provisioning
- production secret creation
- auth enforcement
- token verification
- JWT parsing
- JWKS fetch
- RBAC enforcement
- route protection enforcement
- login/signup/logout/user-management UI
- Authorization headers from the frontend API client
- action execution
- dispatch execution
- Water Emergency close/resolve/certification behavior
- vendor calls
- AI authority

## Future Deployment Checklist

Before any real deployment module, confirm:

- [ ] production owner approval exists
- [ ] target host and application account are approved
- [ ] release path is approved
- [ ] process manager is selected
- [ ] reverse proxy design is approved
- [ ] HTTPS/TLS plan is approved
- [ ] production database is provisioned separately from local dev
- [ ] least-privilege database user is approved
- [ ] production secrets are stored outside Git
- [ ] backup plan is approved
- [ ] restore drill is completed
- [ ] rollback plan is approved
- [ ] health checks are documented
- [ ] monitoring/alerting ownership is defined
- [ ] current routes remain read-only until later action modules
- [ ] ACSSDR stakeholder reporting remains one reviewed module behind active implementation
- [ ] ChatGPT review and Review GUI approval remain mandatory before commit

## What Is Not Implemented Yet

- no production runtime
- no staging runtime
- no Apache deployment config
- no production PostgreSQL
- no production secrets
- no deployment automation
- no production monitoring
- no backup/restore drill
- no rollback runbook execution
- no auth/RBAC enforcement
- no route protection
- no operational action execution
- no external integration execution

