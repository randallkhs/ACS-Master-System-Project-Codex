# ACS-FSM Risk Register

Date: 2026-05-27
Status: Module 61 documentation/readiness baseline

This risk register is operational planning documentation, not legal advice.

| Risk | Severity | Current mitigation | Future mitigation | Owner | Alfonso owner review may be required |
| --- | --- | --- | --- | --- | --- |
| Auth/RBAC not implemented | High | Phase 0 reports auth disabled and cutover not ready. | Select provider, configure secrets, implement token verification/RBAC/route guards. | Randall | Possible if access policy affects company liability |
| Action execution not implemented | High | Manual Review and Water Emergency remain read-only. | Add authenticated, audited, idempotent action modules after RBAC. | Randall | Yes for liability-sensitive actions |
| Production deployment not implemented | High | Local verification only; ACSSDR is report-only. | Create production deployment, rollback, backup, and monitoring runbooks. | Randall | Possible |
| Integrations not implemented | High | Adapter boundaries and dry-run evidence only. | Implement approved Calendar/Sheets/FastField/email/routing adapters with audit and retries. | Randall | Yes for customer/vendor-facing outputs |
| Water Emergency legal/insurance concerns | High | Water Emergency remains separated and read-only; owner-review flags documented. | Owner-reviewed action policy, equipment/moisture model, closure rules, audit evidence. | Alfonso/Randall | Yes |
| Manual Review action safety | High | No action controls or mutation endpoints exist. | Authenticated actions with audit actor, idempotency, immutable events, and post-action checks. | Randall | Yes for binding actions |
| Data migration / backup / restore risk | High | Alembic local migrations exist; production not active. | Production backup/restore test, migration rollout plan, rollback plan. | Randall | Possible |
| External API credentials risk | High | Example placeholders only; secret hygiene helper checks tracked files. | Secret manager/runtime env ownership, rotation, access policy. | Randall | Possible |
| iCloud/local dev path risk | Medium | Current repo path is known and checked before work. | Production deployment should not depend on iCloud path semantics. | Randall | No |
| ACSSDR public reporting risk | Medium | ACSSDR is stakeholder-friendly and avoids secrets; updated only after prior module commit. | Continue public verification and avoid sensitive internal data. | Randall | Possible if customer/company-sensitive details are proposed |
| AI overreach risk | High | AI remains advisory-only in docs; no AI authority implemented. | Keep advisory labels, require deterministic evidence and Manual Review before actions. | Randall | Yes for customer/policy-facing AI output |
| Historical module documentation uncertainty | Medium | Inventory marks uncertainty instead of inventing history. | Preserve future review metadata and ACSSDR update evidence per module. | Randall | No |
| Synthetic data mistaken for production | Medium | Seed data is labeled synthetic/local-only. | Keep demo data isolated and visibly labeled. | Randall | No |
| Water Emergency standard-dispatch leakage | High | Current docs and read models keep Water Emergency separated. | Enforce separate schemas/actions before execution modules. | Randall | Yes |
| Authorization header false authority | High | Phase 0 status reports headers not required, parsed, or authoritative. | Future token verifier must reject invalid tokens and never treat presence alone as authority. | Randall | Possible |
| Public route visibility before auth | Medium | Phase 0 is read-only and explicitly public/non-enforcing. | Add auth/RBAC only after Phase 1/2 criteria are met. | Randall | Possible |
| Review workflow bypass | High | Codex writes external reports; Randall commits manually after review. | Keep Review GUI/ChatGPT review mandatory before commit. | Randall | No |

