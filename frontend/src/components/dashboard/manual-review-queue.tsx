"use client";

import { useMemo, useState, useSyncExternalStore } from "react";
import type {
  DashboardFetchResult,
  ManualReviewAuthBoundaryReadinessResponse,
  ManualReviewExecutionReadinessAuditResponse,
  ManualReviewQueueItemResponse,
  ManualReviewQueueResponse,
  ManualReviewSafetyGateResponse,
} from "@/lib/dashboard-contracts";
import {
  deriveManualReviewVisibleRecords,
  type ManualReviewSortKey,
} from "@/lib/manual-review-view-state";
import {
  getManualReviewBrowserStorage,
  getManualReviewViewPreferencesServerSnapshot,
  getManualReviewViewPreferencesSnapshot,
  notifyManualReviewViewPreferencesChanged,
  readManualReviewViewPreferencesSnapshot,
  subscribeManualReviewViewPreferences,
  writeManualReviewViewPreferences,
} from "@/lib/manual-review-view-preferences";
import {
  compactId,
  formatCount,
  formatDateTime,
  humanizeLabel,
} from "@/lib/format";
import { CountBucketPanel } from "@/components/dashboard/count-bucket-panel";
import { SectionCard } from "@/components/dashboard/section-card";
import { SectionHeading } from "@/components/dashboard/section-heading";
import { StatCard } from "@/components/dashboard/stat-card";
import {
  badgeVariantForLabel,
  StatusBadge,
} from "@/components/dashboard/status-badge";

type ManualReviewQueueProps = {
  result: DashboardFetchResult<ManualReviewQueueResponse>;
};

export function ManualReviewQueue({ result }: ManualReviewQueueProps) {
  const { data } = result;
  const [fallbackPreferences, setFallbackPreferences] = useState({
    selectedFilter: "all",
    selectedSort: "attention" as ManualReviewSortKey,
  });
  const availableFilterKeys = useMemo(
    () => new Set(data.available_filters.map((option) => option.key)),
    [data.available_filters],
  );
  const availableSortKeys = useMemo(
    () => new Set(data.sort_options.map((option) => option.key)),
    [data.sort_options],
  );
  const preferenceSnapshot = useSyncExternalStore(
    subscribeManualReviewViewPreferences,
    getManualReviewViewPreferencesSnapshot,
    getManualReviewViewPreferencesServerSnapshot,
  );
  const preferenceReadResult = useMemo(
    () =>
      readManualReviewViewPreferencesSnapshot(preferenceSnapshot, {
        availableFilterKeys,
        availableSortKeys,
      }),
    [availableFilterKeys, availableSortKeys, preferenceSnapshot],
  );
  const selectedFilter =
    preferenceReadResult.preferences?.selectedFilter ??
    fallbackPreferences.selectedFilter;
  const selectedSort =
    preferenceReadResult.preferences?.selectedSort ??
    fallbackPreferences.selectedSort;
  const viewState = useMemo(
    () =>
      deriveManualReviewVisibleRecords(data, {
        selectedFilter,
        selectedSort,
      }),
    [data, selectedFilter, selectedSort],
  );
  const activeStandardItems = viewState.visibleStandardItems.filter(
    (item) => item.attention_indicator,
  );
  const inactiveStandardItems = viewState.visibleStandardItems.filter(
    (item) => !item.attention_indicator,
  );

  function savePreferences(nextPreferences: {
    selectedFilter: string;
    selectedSort: ManualReviewSortKey;
  }) {
    const writeResult = writeManualReviewViewPreferences(
      getManualReviewBrowserStorage(),
      nextPreferences,
    );

    if (writeResult.available) {
      notifyManualReviewViewPreferencesChanged();
      return;
    }

    setFallbackPreferences(nextPreferences);
  }

  return (
    <section className="space-y-4">
      <SectionHeading
        id="manual-review-queue"
        label="Manual Review Queue"
        title="Detailed Safety Review Visibility"
        description="Read-only Manual Review visibility grouped by status, reason, entity context, and attention indicators. This panel does not approve, reject, defer, archive, dispatch, or resolve any review item."
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Queue Items" value={data.total_items} />
        <StatCard
          label="Active Attention"
          value={data.active_attention_count}
          tone={data.active_attention_count > 0 ? "warning" : "good"}
        />
        <StatCard
          label="Water Emergency Related"
          value={data.water_emergency_related_count}
          tone={data.water_emergency_related_count > 0 ? "info" : "neutral"}
        />
        <StatCard
          label="Blocked Indicators"
          value={data.blocked_count}
          tone={data.blocked_count > 0 ? "danger" : "good"}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-4">
        <CountBucketPanel title="Review Status" buckets={data.status_counts} />
        <CountBucketPanel
          title="Reason Distribution"
          buckets={data.reason_counts}
        />
        <CountBucketPanel
          title="Visibility Groups"
          buckets={data.group_counts}
        />
        <CountBucketPanel
          title="Age Buckets"
          buckets={data.age_bucket_counts}
        />
        <CountBucketPanel
          title="Decision Readiness"
          buckets={data.decision_readiness_counts}
        />
        <CountBucketPanel
          title="Future Action Preflight"
          buckets={data.action_preflight_counts}
        />
        <CountBucketPanel
          title="Future Action Preview"
          buckets={data.future_action_preview_counts}
        />
        <CountBucketPanel
          title="Future Command Contract"
          buckets={data.command_contract_counts}
        />
        <CountBucketPanel
          title="Command Dry Run"
          buckets={data.audit_ledger_dry_run_counts}
        />
        <CountBucketPanel
          title="Command Validation"
          buckets={data.command_validation_counts}
        />
        <CountBucketPanel
          title="Permission Readiness"
          buckets={data.permission_readiness_counts}
        />
      </div>

      <ExecutionReadinessAuditPanel audit={data.execution_readiness_audit} />
      <AuthBoundaryReadinessPanel boundary={data.auth_boundary_readiness} />

      <SectionCard
        title="Manual Review View State"
        description="Read-only filter and sort controls change only this dashboard view. They do not approve, reject, defer, archive, dispatch, or update Manual Review records."
      >
        <div className="grid gap-4 xl:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)]">
          <div className="grid gap-3 md:grid-cols-2">
            <label className="text-sm font-semibold text-[#162033]">
              Filter review items
              <select
                id="manual-review-filter"
                name="manual-review-filter"
                className="mt-2 min-h-11 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-[#162033] shadow-sm focus:border-[#2f7ae5] focus:outline-none focus:ring-2 focus:ring-[#2f7ae5]/20"
                value={viewState.selectedFilter.key}
                onChange={(event) =>
                  savePreferences({
                    selectedFilter: event.target.value,
                    selectedSort,
                  })
                }
              >
                {data.available_filters.map((filter) => (
                  <option key={filter.key} value={filter.key}>
                    {filter.label} ({formatCount(filter.count)})
                  </option>
                ))}
              </select>
            </label>
            <label className="text-sm font-semibold text-[#162033]">
              Sort review items
              <select
                id="manual-review-sort"
                name="manual-review-sort"
                className="mt-2 min-h-11 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-[#162033] shadow-sm focus:border-[#2f7ae5] focus:outline-none focus:ring-2 focus:ring-[#2f7ae5]/20"
                value={viewState.selectedSort.key}
                onChange={(event) =>
                  savePreferences({
                    selectedFilter,
                    selectedSort: event.target.value as ManualReviewSortKey,
                  })
                }
              >
                {data.sort_options.map((sort) => (
                  <option key={sort.key} value={sort.key}>
                    {sort.label}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="rounded-md border border-slate-200 bg-slate-50 px-3 py-3">
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Saved view preferences
            </div>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              Stored on this device only. The selected Manual Review filter and
              sort order are browser view preferences, not backend operational
              state.
            </p>
          </div>
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          <MiniMetric
            label="Selected records"
            value={formatCount(viewState.visibleItems.length)}
          />
          <MiniMetric
            label="Backend result window"
            value={`${formatCount(data.result_window_metadata.visible_count)} of ${formatCount(data.result_window_metadata.total_count)}`}
          />
          <MiniMetric
            label="Current sort"
            value={viewState.selectedSort.label}
          />
        </div>
      </SectionCard>

      <SectionCard
        title="Randall-authorized Phase 0 review taxonomy baseline"
        description={`${data.taxonomy_metadata.baseline_note} These labels are internal software visibility groups, not legal policy, insurance language, or Manual Review action authority.`}
      >
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {data.taxonomy_metadata.group_definitions.slice(0, 6).map((group) => (
            <div
              key={group.key}
              className="rounded-md border border-slate-200 bg-slate-50/70 p-3"
            >
              <StatusBadge
                label={group.label}
                variant={badgeVariantForLabel(group.key)}
              />
              <p className="mt-2 text-sm leading-6 text-slate-600">
                {group.reason}
              </p>
            </div>
          ))}
        </div>
      </SectionCard>

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)]">
        <ReviewItemGroup
          title="Water Emergency-related reviews"
          description="Separated Manual Review visibility for review records tied to Water Emergency records, jobs, or visits."
          items={viewState.visibleWaterEmergencyItems}
          emptyLabel="No Water Emergency-related review items returned."
        />

        <ReviewItemGroup
          title="Standard dispatch and other reviews"
          description="Standard job, work-order, visit, route-assignment, and uncategorized review items remain read-only."
          items={[...activeStandardItems, ...inactiveStandardItems]}
          emptyLabel="No standard dispatch or other review items match the selected read-only filter."
        />
      </div>
    </section>
  );
}

function ExecutionReadinessAuditPanel({
  audit,
}: {
  audit: ManualReviewExecutionReadinessAuditResponse;
}) {
  const boundary = audit.mutation_boundary;
  const groupedPrerequisites = audit.future_transition_prerequisites.reduce<
    Record<string, typeof audit.future_transition_prerequisites>
  >((groups, prerequisite) => {
    const current = groups[prerequisite.category] ?? [];
    return {
      ...groups,
      [prerequisite.category]: [...current, prerequisite],
    };
  }, {});

  return (
    <SectionCard
      title="Execution Readiness Audit"
      description={`${audit.summary} This section is read-only operational visibility and does not enable Manual Review actions.`}
    >
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <MiniMetric
          label="Currently executable count"
          value={formatCount(audit.currently_executable_count)}
        />
        <MiniMetric
          label="Phase-blocked records"
          value={formatCount(audit.items_blocked_by_phase_execution)}
        />
        <MiniMetric
          label="Water Emergency readiness"
          value={formatCount(audit.water_emergency_related_review_items)}
        />
        <MiniMetric
          label="Mutation endpoints"
          value={boundary.mutation_endpoints_available ? "Available" : "Unavailable"}
        />
      </div>

      <div className="mt-4 rounded-md border border-rose-200 bg-rose-50/70 px-3 py-3">
        <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
          Mutation Boundary Lock
        </div>
        <div className="mt-2 flex flex-wrap gap-2">
          <StatusBadge
            label={
              boundary.manual_review_mutations_enabled
                ? "Manual Review mutations enabled"
                : "Manual Review mutations disabled"
            }
            variant={boundary.manual_review_mutations_enabled ? "danger" : "neutral"}
          />
          <StatusBadge
            label={humanizeLabel(boundary.action_execution_phase)}
            variant="neutral"
          />
          <StatusBadge
            label={`Currently executable count ${formatCount(boundary.currently_executable_count)}`}
            variant={
              boundary.currently_executable_count === 0 ? "success" : "danger"
            }
          />
          <StatusBadge
            label={
              boundary.mutation_endpoints_available
                ? "Mutation endpoints available"
                : "Mutation endpoints unavailable"
            }
            variant={boundary.mutation_endpoints_available ? "danger" : "neutral"}
          />
        </div>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          Manual Review actions are not executable in Phase 0. Auth, RBAC, audit
          envelope, idempotency, immutable event recording, and post-action
          consistency checks are required before any future action module.
        </p>
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        <MiniMetric
          label="Future auth required"
          value={formatCount(audit.required_future_auth_count)}
        />
        <MiniMetric
          label="Future RBAC required"
          value={formatCount(audit.required_future_rbac_count)}
        />
        <MiniMetric
          label="Future operator identity"
          value={formatCount(audit.required_future_operator_identity_count)}
        />
        <MiniMetric
          label="Future audit reason"
          value={formatCount(audit.required_future_audit_reason_count)}
        />
        <MiniMetric
          label="Future idempotency"
          value={formatCount(audit.required_future_idempotency_key_count)}
        />
        <MiniMetric
          label="Future immutable event"
          value={formatCount(audit.required_future_immutable_event_count)}
        />
        <MiniMetric
          label="Future consistency check"
          value={formatCount(
            audit.required_future_post_action_consistency_check_count,
          )}
        />
        <MiniMetric
          label="Missing entity context"
          value={formatCount(audit.items_with_missing_entity_context)}
        />
        <MiniMetric
          label="Conflict blockers"
          value={formatCount(audit.items_with_conflict_blockers)}
        />
      </div>

      <div className="mt-4 grid gap-3 lg:grid-cols-2">
        {Object.entries(groupedPrerequisites).map(([category, prerequisites]) => (
          <div
            key={category}
            className="rounded-md border border-slate-200 bg-slate-50/70 p-3"
          >
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              {humanizeLabel(category)}
            </div>
            <div className="mt-3 space-y-3">
              {prerequisites.map((prerequisite) => (
                <div key={prerequisite.key} className="min-w-0">
                  <div className="flex flex-wrap gap-2">
                    <StatusBadge
                      label={prerequisite.label}
                      variant={badgeVariantForLabel(prerequisite.key)}
                    />
                    <StatusBadge
                      label={humanizeLabel(prerequisite.status)}
                      variant={badgeVariantForLabel(prerequisite.status)}
                    />
                    {prerequisite.requires_alfonso_owner_review ? (
                      <StatusBadge
                        label="Requires Alfonso owner review"
                        variant="warning"
                      />
                    ) : null}
                  </div>
                  <p className="mt-2 text-sm leading-6 text-slate-600">
                    {prerequisite.reason}
                  </p>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 rounded-md border border-amber-200 bg-amber-50/70 px-3 py-3">
        <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
          Owner-review guardrails
        </div>
        <div className="mt-2 flex flex-wrap gap-2">
          {audit.owner_review_guardrail_labels.map((label) => (
            <StatusBadge
              key={label}
              label={humanizeLabel(label)}
              variant="warning"
            />
          ))}
        </div>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          Legal, insurance, warranty, drying certification, formal policy, and
          financial commitments remain non-binding visibility until Alfonso owner
          review is completed.
        </p>
      </div>
    </SectionCard>
  );
}

const authRbacBlockerGroupLabels: Record<string, string> = {
  provider_selection: "Provider selection",
  real_credentials_secret_hygiene: "Real credentials / secret hygiene",
  token_verification: "Token verification",
  claims_mapping: "Claims mapping",
  operator_identity: "Operator identity",
  rbac_role_policy: "RBAC / role policy",
  route_protection: "Route protection",
  manual_review_action_permissions: "Manual Review action permissions",
  water_emergency_action_permissions: "Water Emergency action permissions",
  audit_actor_idempotency: "Audit actor / idempotency",
  legal_owner_review: "Legal / owner review",
  review_workflow: "Review workflow",
};

const authRbacBlockerGroupOrder = [
  "provider_selection",
  "real_credentials_secret_hygiene",
  "token_verification",
  "claims_mapping",
  "operator_identity",
  "rbac_role_policy",
  "route_protection",
  "manual_review_action_permissions",
  "water_emergency_action_permissions",
  "audit_actor_idempotency",
  "legal_owner_review",
  "review_workflow",
];

function AuthBoundaryReadinessPanel({
  boundary,
}: {
  boundary: ManualReviewAuthBoundaryReadinessResponse;
}) {
  const diagnostics =
    boundary.auth_configuration_readiness.runtime_safety_diagnostics;
  const claimsMapping = boundary.auth_claims_mapping_readiness;
  const routeProtection = boundary.route_protection_readiness;
  const accessDryRun = routeProtection.access_decision_dry_run;
  const authRbacAudit = boundary.auth_rbac_readiness_audit;
  const enforcementLock = authRbacAudit.enforcement_boundary_lock;
  const transitionPrerequisitesByGroup =
    authRbacAudit.future_transition_prerequisites.reduce<
      Record<string, typeof authRbacAudit.future_transition_prerequisites>
    >((groups, prerequisite) => {
      const existing = groups[prerequisite.blocker_group] ?? [];
      groups[prerequisite.blocker_group] = [...existing, prerequisite];
      return groups;
    }, {});

  return (
    <SectionCard
      title="Auth Boundary Readiness"
      description={`${boundary.summary} This catalog is read-only planning visibility and does not authenticate users, enforce roles, or execute Manual Review actions.`}
    >
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <MiniMetric
          label="Auth implemented"
          value={boundary.auth_implemented ? "Yes" : "False"}
        />
        <MiniMetric
          label="RBAC enforced"
          value={boundary.rbac_enforced ? "Yes" : "False"}
        />
        <MiniMetric
          label="Sign-in UI available"
          value={boundary.login_ui_available ? "Yes" : "False"}
        />
        <MiniMetric
          label="Action execution"
          value={boundary.action_execution_available ? "Available" : "Unavailable"}
        />
      </div>

      <div className="mt-4 rounded-md border border-amber-200 bg-amber-50/60 p-3">
        <div className="text-xs font-semibold uppercase tracking-[0.14em] text-amber-700">
          Auth/RBAC Readiness Audit
        </div>
        <p className="mt-2 text-sm leading-6 text-slate-700">
          {authRbacAudit.summary} This is read-only operational visibility; it
          does not deny routes, hide UI, verify tokens, or unlock actions.
        </p>
        <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <MiniMetric
            label="Auth enforcement"
            value={
              enforcementLock.auth_enforcement_enabled
                ? "Auth enforcement enabled"
                : "Auth enforcement disabled"
            }
          />
          <MiniMetric
            label="RBAC enforcement"
            value={
              enforcementLock.rbac_enforcement_enabled
                ? "RBAC enforcement enabled"
                : "RBAC enforcement disabled"
            }
          />
          <MiniMetric
            label="Route guarding"
            value={
              enforcementLock.route_guarding_enabled
                ? "Route guarding enabled"
                : "Route guarding disabled"
            }
          />
          <MiniMetric
            label="Sign-in UI"
            value={
              enforcementLock.login_ui_available
                ? "Sign-in UI available"
                : "Sign-in UI unavailable"
            }
          />
          <MiniMetric
            label="Auth core scaffold"
            value={
              authRbacAudit.auth_core_module_available
                ? "Available for future modules"
                : "Unavailable"
            }
          />
          <MiniMetric
            label="Token verifier"
            value={
              authRbacAudit.disabled_token_verifier_available
                ? "Disabled verifier available"
                : "Unavailable"
            }
          />
          <MiniMetric
            label="Current routes require auth"
            value={authRbacAudit.current_routes_require_auth ? "Yes" : "No"}
          />
          <MiniMetric
            label="User management"
            value={
              enforcementLock.user_management_available
                ? "User management available"
                : "User management unavailable"
            }
          />
          <MiniMetric
            label="Manual Review actions"
            value={
              authRbacAudit.manual_review_action_execution_available
                ? "Manual Review actions available"
                : "Manual Review actions unavailable"
            }
          />
          <MiniMetric
            label="Water Emergency actions"
            value={
              authRbacAudit.water_emergency_action_execution_available
                ? "Water Emergency actions available"
                : "Water Emergency actions unavailable"
            }
          />
          <MiniMetric
            label="Readiness gaps"
            value={formatCount(authRbacAudit.readiness_gap_count)}
          />
        </div>
        <div className="mt-4 rounded-md border border-amber-200 bg-white p-3">
          <div className="text-xs font-semibold uppercase tracking-[0.14em] text-amber-700">
            Enforcement Boundary Lock
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            {[
              ["Auth enforcement disabled", !enforcementLock.auth_enforcement_enabled],
              [
                "Token verification disabled",
                !enforcementLock.token_verification_enabled,
              ],
              [
                "Real token parsing disabled",
                !enforcementLock.real_token_parsing_enabled,
              ],
              ["JWKS fetch disabled", !enforcementLock.jwks_fetch_enabled],
              ["RBAC enforcement disabled", !enforcementLock.rbac_enforcement_enabled],
              ["Route guarding disabled", !enforcementLock.route_guarding_enabled],
              [
                "Auth core scaffold available",
                authRbacAudit.auth_core_module_available,
              ],
              [
                "Disabled token verifier available",
                authRbacAudit.disabled_token_verifier_available,
              ],
              [
                "Optional auth context available",
                authRbacAudit.optional_auth_context_available,
              ],
              [
                "Current routes do not require auth",
                !authRbacAudit.current_routes_require_auth,
              ],
              [
                "Route protection not enforced",
                !authRbacAudit.route_protection_enforced,
              ],
              ["Sign-in UI unavailable", !enforcementLock.login_ui_available],
              [
                "User management unavailable",
                !enforcementLock.user_management_available,
              ],
              [
                "Manual Review actions unavailable",
                !enforcementLock.phase_allows_manual_review_actions,
              ],
              [
                "Manual Review authority not granted",
                !authRbacAudit.manual_review_action_authority_granted,
              ],
              [
                "Water Emergency authority not granted",
                !authRbacAudit.water_emergency_action_authority_granted,
              ],
              [
                "Mutation endpoints unavailable",
                !enforcementLock.mutation_endpoints_available,
              ],
            ].map(([label, locked]) => (
              <StatusBadge
                key={String(label)}
                label={String(label)}
                variant={locked ? "neutral" : "danger"}
              />
            ))}
          </div>
        </div>
        <div className="mt-4 grid gap-3 lg:grid-cols-2">
          {authRbacBlockerGroupOrder.map((groupKey) => {
            const prerequisites = transitionPrerequisitesByGroup[groupKey] ?? [];

            if (prerequisites.length === 0) {
              return null;
            }

            return (
              <div
                key={groupKey}
                className="rounded-md border border-amber-200 bg-white p-3"
              >
                <div className="text-sm font-semibold text-[#162033]">
                  {authRbacBlockerGroupLabels[groupKey] ?? humanizeLabel(groupKey)}
                </div>
                <div className="mt-3 space-y-3">
                  {prerequisites.map((prerequisite) => (
                    <div
                      key={prerequisite.key}
                      className="rounded-md border border-slate-200 bg-slate-50/70 p-3"
                    >
                      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                        <div className="min-w-0">
                          <div className="break-words text-sm font-semibold text-[#162033]">
                            {prerequisite.label}
                          </div>
                          <p className="mt-1 text-xs leading-5 text-slate-600">
                            {prerequisite.reason}
                          </p>
                        </div>
                        <StatusBadge
                          label={humanizeLabel(prerequisite.status)}
                          variant={
                            prerequisite.status === "satisfied_now"
                              ? "neutral"
                              : prerequisite.requires_alfonso_owner_review
                                ? "warning"
                                : "info"
                          }
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        <StatusBadge
          label={
            boundary.future_auth_required_before_actions
              ? "Future auth required before actions"
              : "Future auth requirement missing"
          }
          variant={boundary.future_auth_required_before_actions ? "info" : "danger"}
        />
        <StatusBadge
          label={
            boundary.future_rbac_required_before_actions
              ? "Future RBAC required before actions"
              : "Future RBAC requirement missing"
          }
          variant={boundary.future_rbac_required_before_actions ? "info" : "danger"}
        />
        <StatusBadge
          label={
            boundary.service_accounts_blocked_for_manual_review_actions
              ? "Service accounts blocked for Manual Review actions"
              : "Service accounts not blocked"
          }
          variant={
            boundary.service_accounts_blocked_for_manual_review_actions
              ? "warning"
              : "danger"
          }
        />
        <StatusBadge
          label={
            boundary.service_account_allowed_for_manual_review_actions
              ? "Service account action allowed"
              : "Service account action not allowed"
          }
          variant={
            boundary.service_account_allowed_for_manual_review_actions
              ? "danger"
              : "warning"
          }
        />
        <StatusBadge
          label={
            boundary.impersonation_allowed
              ? "Impersonation allowed"
              : "Impersonation not allowed"
          }
          variant={boundary.impersonation_allowed ? "danger" : "warning"}
        />
        <StatusBadge
          label={humanizeLabel(boundary.operator_identity_registry_mode)}
          variant="neutral"
        />
      </div>

      <div className="mt-4 rounded-md border border-slate-200 bg-slate-50/70 p-3">
        <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
          Auth Configuration Readiness
        </div>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          {boundary.auth_configuration_readiness.summary} No committed
          credentials, token verification, auth headers, or sign-in controls are
          active in Phase 0.
        </p>
        <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <MiniMetric
            label="Auth provider"
            value={`Auth provider ${humanizeLabel(
              boundary.auth_configuration_readiness.auth_provider,
            ).toLowerCase()}`}
          />
          <MiniMetric
            label="Token verification"
            value={
              boundary.auth_configuration_readiness.token_verification_enabled
                ? "Token verification enabled"
                : "Token verification disabled"
            }
          />
          <MiniMetric
            label="RBAC enforcement"
            value={
              boundary.auth_configuration_readiness.rbac_enforcement_enabled
                ? "RBAC enforcement enabled"
                : "RBAC enforcement disabled"
            }
          />
          <MiniMetric
            label="Local dev auth mode"
            value={`Local dev auth mode ${humanizeLabel(
              boundary.auth_configuration_readiness.local_dev_auth_mode,
            ).toLowerCase()}`}
          />
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          <StatusBadge
            label={
              boundary.auth_configuration_readiness.committed_credentials_allowed
                ? "Committed credentials allowed"
                : "Committed credentials not allowed"
            }
            variant={
              boundary.auth_configuration_readiness.committed_credentials_allowed
                ? "danger"
                : "warning"
            }
          />
          <StatusBadge
            label={
              boundary.auth_configuration_readiness.real_credentials_required
                ? "Real credentials required later"
                : "Real credentials not required"
            }
            variant={
              boundary.auth_configuration_readiness.real_credentials_required
                ? "info"
                : "danger"
            }
          />
          <StatusBadge
            label={
              boundary.auth_configuration_readiness.future_provider_selection_required
                ? "Future provider selection required"
                : "Future provider already selected"
            }
            variant={
              boundary.auth_configuration_readiness
                .future_provider_selection_required
                ? "info"
                : "danger"
            }
          />
          <StatusBadge
            label={
              boundary.auth_configuration_readiness
                .randall_controls_provider_configuration
                ? "Randall controls provider configuration"
                : "Provider configuration owner missing"
            }
            variant={
              boundary.auth_configuration_readiness
                .randall_controls_provider_configuration
                ? "neutral"
              : "danger"
            }
          />
        </div>
        <div className="mt-4 rounded-md border border-slate-200 bg-white p-3">
          <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
            Auth Diagnostics
          </div>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            {diagnostics.summary} The helper is{" "}
            {diagnostics.secret_hygiene_helper}.
          </p>
          <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <MiniMetric
              label="Runtime auth mode"
              value={humanizeLabel(diagnostics.runtime_auth_mode)}
            />
            <MiniMetric
              label="Auth headers required"
              value={
                diagnostics.auth_headers_required
                  ? "Auth headers required"
                  : "Auth headers not required"
              }
            />
            <MiniMetric
              label="Frontend auth headers"
              value={
                diagnostics.auth_headers_emitted_by_frontend
                  ? "Frontend auth headers emitted"
                  : "Frontend auth headers not emitted"
              }
            />
            <MiniMetric
              label="Placeholder status"
              value={
                diagnostics.placeholder_values_only
                  ? "Placeholder values only"
                  : "Placeholder issue detected"
              }
            />
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            <StatusBadge
              label={
                diagnostics.auth_enabled
                  ? "Auth enabled"
                  : "Auth disabled in Phase 0"
              }
              variant={diagnostics.auth_enabled ? "danger" : "neutral"}
            />
            <StatusBadge
              label={
                diagnostics.auth_headers_required
                  ? "Auth headers required"
                  : "Auth headers not required"
              }
              variant={diagnostics.auth_headers_required ? "danger" : "neutral"}
            />
            <StatusBadge
              label={
                diagnostics.auth_headers_emitted_by_frontend
                  ? "Frontend auth headers emitted"
                  : "Frontend auth headers not emitted"
              }
              variant={
                diagnostics.auth_headers_emitted_by_frontend
                  ? "danger"
                  : "neutral"
              }
            />
            <StatusBadge
              label={
                diagnostics.env_file_tracked
                  ? "Tracked .env file detected"
                  : "No tracked .env files"
              }
              variant={diagnostics.env_file_tracked ? "danger" : "neutral"}
            />
            <StatusBadge
              label={
                diagnostics.env_local_file_tracked
                  ? "Tracked .env.local file detected"
                  : "No tracked .env.local files"
              }
              variant={diagnostics.env_local_file_tracked ? "danger" : "neutral"}
            />
            <StatusBadge
              label={
                diagnostics.service_account_json_tracked
                  ? "Service account JSON tracked"
                  : "No service account JSON tracked"
              }
              variant={
                diagnostics.service_account_json_tracked ? "danger" : "neutral"
              }
            />
            <StatusBadge
              label={
                diagnostics.private_key_detected
                  ? "Private key detected"
                  : "Private key not detected"
              }
              variant={diagnostics.private_key_detected ? "danger" : "neutral"}
            />
            <StatusBadge
              label={
                diagnostics.placeholder_values_only
                  ? "Placeholder values only"
                  : "Non-placeholder values detected"
              }
              variant={diagnostics.placeholder_values_only ? "neutral" : "danger"}
            />
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            {diagnostics.diagnostic_checks.map((check) => (
              <StatusBadge
                key={check.key}
                label={check.label}
                variant={check.passed ? "neutral" : "danger"}
              />
            ))}
          </div>
        </div>
        <div className="mt-4 rounded-md border border-slate-200 bg-white p-3">
          <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
            Auth Claims Mapping
          </div>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            {claimsMapping.summary} Claims, roles, and permissions are future
            planning labels only.
          </p>
          <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <MiniMetric
              label="Token dry-run"
              value={
                claimsMapping.token_verification_dry_run_available
                  ? "Token verification dry-run available"
                  : "Token verification dry-run unavailable"
              }
            />
            <MiniMetric
              label="Real token parsing"
              value={
                claimsMapping.real_token_parsing_enabled
                  ? "Real token parsing enabled"
                  : "Real token parsing disabled"
              }
            />
            <MiniMetric
              label="JWKS fetch"
              value={
                claimsMapping.jwks_fetch_enabled
                  ? "JWKS fetch enabled"
                  : "JWKS fetch disabled"
              }
            />
            <MiniMetric
              label="Auth headers emitted"
              value={
                claimsMapping.auth_headers_emitted_by_frontend
                  ? "Auth headers emitted"
                  : "Auth headers not emitted"
              }
            />
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            <StatusBadge
              label={
                claimsMapping.required_claims_documented
                  ? "Required claims documented"
                  : "Required claims missing"
              }
              variant={claimsMapping.required_claims_documented ? "neutral" : "danger"}
            />
            <StatusBadge
              label={
                claimsMapping.service_account_block_rule_documented
                  ? "Service account block rule documented"
                  : "Service account block rule missing"
              }
              variant={
                claimsMapping.service_account_block_rule_documented
                  ? "warning"
                  : "danger"
              }
            />
            <StatusBadge
              label={
                claimsMapping.technician_block_rule_documented
                  ? "Technician block rule documented"
                  : "Technician block rule missing"
              }
              variant={
                claimsMapping.technician_block_rule_documented ? "warning" : "danger"
              }
            />
            <StatusBadge
              label={
                claimsMapping.example_claim_fixture_contains_real_user_data
                  ? "Fixture contains real user data"
                  : "Fixture contains no real user data"
              }
              variant={
                claimsMapping.example_claim_fixture_contains_real_user_data
                  ? "danger"
                  : "neutral"
              }
            />
          </div>
          <div className="mt-4 grid gap-3 lg:grid-cols-3">
            <div className="rounded-md border border-slate-200 bg-slate-50/70 p-3">
              <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                Required Claim Contract
              </div>
              <p className="mt-2 break-words text-sm leading-6 text-slate-600">
                {claimsMapping.claim_contracts
                  .map((claim) => `${claim.label}: ${claim.claim_name}`)
                  .join(", ")}
              </p>
            </div>
            <div className="rounded-md border border-slate-200 bg-slate-50/70 p-3">
              <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                Role Resolution Readiness
              </div>
              <div className="mt-2 flex flex-wrap gap-2">
                {claimsMapping.role_resolution_rules.map((rule) => (
                  <StatusBadge
                    key={rule.key}
                    label={rule.label}
                    variant={
                      rule.blocked_for_manual_review_actions ? "warning" : "neutral"
                    }
                  />
                ))}
              </div>
            </div>
            <div className="rounded-md border border-slate-200 bg-slate-50/70 p-3">
              <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                Safe Claim Fixtures
              </div>
              <div className="mt-2 flex flex-wrap gap-2">
                {claimsMapping.example_claim_fixtures.map((fixture) => (
                  <StatusBadge
                    key={fixture.key}
                    label={`${fixture.label}: ${fixture.email_domain}`}
                    variant={
                      fixture.contains_token || fixture.contains_secret
                        ? "danger"
                        : "neutral"
                    }
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
        <div className="mt-4 rounded-md border border-slate-200 bg-white p-3">
          <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
            Route Protection Matrix
          </div>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            {routeProtection.summary} Access labels are read-only planning
            metadata and do not hide dashboard sections or deny backend routes.
          </p>
          <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <MiniMetric
              label="Access Decision Dry-Run"
              value={
                accessDryRun.access_decision_dry_run_enabled
                  ? "Access Decision Dry-Run enabled"
                  : "Access Decision Dry-Run unavailable"
              }
            />
            <MiniMetric
              label="Enforcement"
              value={
                accessDryRun.enforcement_enabled
                  ? "Enforcement enabled"
                  : "Enforcement disabled"
              }
            />
            <MiniMetric
              label="Phase allows enforcement"
              value={
                accessDryRun.phase_allows_enforcement
                  ? "Phase allows enforcement: Yes"
                  : "Phase allows enforcement: No"
              }
            />
            <MiniMetric
              label="Route guarding"
              value={
                accessDryRun.route_guarding_enabled
                  ? "Route guarding enabled"
                  : "Route guarding disabled"
              }
            />
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            <StatusBadge
              label={
                accessDryRun.token_verification_enabled
                  ? "Token verification enabled"
                  : "Token verification disabled"
              }
              variant={accessDryRun.token_verification_enabled ? "danger" : "neutral"}
            />
            <StatusBadge
              label={
                accessDryRun.rbac_enforcement_enabled
                  ? "RBAC enforcement enabled"
                  : "RBAC enforcement disabled"
              }
              variant={accessDryRun.rbac_enforcement_enabled ? "danger" : "neutral"}
            />
            <StatusBadge
              label={
                accessDryRun.simulated_decisions_only
                  ? "Simulated decisions only"
                  : "Live access decisions active"
              }
              variant={accessDryRun.simulated_decisions_only ? "neutral" : "danger"}
            />
            <StatusBadge
              label={
                accessDryRun.currently_denied_by_auth
                  ? "Currently denied by auth"
                  : "Not currently denied by auth"
              }
              variant={accessDryRun.currently_denied_by_auth ? "danger" : "neutral"}
            />
            <StatusBadge
              label={
                accessDryRun.currently_denied_by_rbac
                  ? "Currently denied by RBAC"
                  : "Not currently denied by RBAC"
              }
              variant={accessDryRun.currently_denied_by_rbac ? "danger" : "neutral"}
            />
          </div>
          <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
            <MiniMetric
              label="Future protected surfaces"
              value={formatCount(accessDryRun.future_auth_required_count)}
            />
            <MiniMetric
              label="Manual Review protected surfaces"
              value={formatCount(
                accessDryRun.future_manual_review_protected_surface_count,
              )}
            />
            <MiniMetric
              label="Water Emergency protected surfaces"
              value={formatCount(
                accessDryRun.future_water_emergency_protected_surface_count,
              )}
            />
            <MiniMetric
              label="Future mutation surfaces"
              value={formatCount(accessDryRun.future_mutation_surface_count)}
            />
            <MiniMetric
              label="Unknown permission mappings"
              value={formatCount(accessDryRun.unknown_permission_mapping_count)}
            />
          </div>
          <div className="mt-4 grid gap-3 lg:grid-cols-2">
            {routeProtection.matrix_items.map((item) => (
              <div
                key={item.route_or_section_key}
                className="rounded-md border border-slate-200 bg-slate-50/70 p-3"
              >
                <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <div className="text-sm font-semibold text-[#162033]">
                      {item.label}
                    </div>
                    <div className="mt-1 break-words text-xs font-medium text-slate-500">
                      {item.route_or_section}
                    </div>
                  </div>
                  <StatusBadge
                    label={
                      item.enforcement_enabled
                        ? "Enforced"
                        : "Read-only mapping"
                    }
                    variant={item.enforcement_enabled ? "danger" : "neutral"}
                  />
                </div>
                <div className="mt-3 flex flex-wrap gap-2">
                  <StatusBadge
                    label={
                      item.currently_public_in_phase_0
                        ? "Public in Phase 0"
                        : "Future surface only"
                    }
                    variant={
                      item.currently_public_in_phase_0 ? "neutral" : "warning"
                    }
                  />
                  {item.manual_review_sensitive ? (
                    <StatusBadge
                      label="Manual Review sensitive"
                      variant="warning"
                    />
                  ) : null}
                  {item.water_emergency_sensitive ? (
                    <StatusBadge
                      label="Water Emergency sensitive"
                      variant="warning"
                    />
                  ) : null}
                  {item.mutation_sensitive ? (
                    <StatusBadge label="Mutation-sensitive" variant="danger" />
                  ) : null}
                  {item.owner_review_required_if_legal_or_insurance ? (
                    <StatusBadge
                      label="Alfonso owner review for legal or insurance policy"
                      variant="warning"
                    />
                  ) : null}
                </div>
                <p className="mt-3 text-sm leading-6 text-slate-600">
                  {item.reason}
                </p>
                <p className="mt-2 break-words text-xs font-semibold text-slate-500">
                  Future permissions:{" "}
                  {item.future_required_permissions.length > 0
                    ? item.future_required_permissions.join(", ")
                    : "none"}
                </p>
              </div>
            ))}
          </div>
        </div>
        <div className="mt-3 grid gap-3 lg:grid-cols-2">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Backend placeholders
            </div>
            <p className="mt-2 break-words text-sm leading-6 text-slate-600">
              {boundary.auth_configuration_readiness.backend_variables
                .map((variable) => variable.name)
                .join(", ")}
            </p>
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Frontend placeholders
            </div>
            <p className="mt-2 break-words text-sm leading-6 text-slate-600">
              {boundary.auth_configuration_readiness.frontend_variables
                .map((variable) => variable.name)
                .join(", ")}
            </p>
          </div>
        </div>
      </div>

      <div className="mt-4 grid gap-3 lg:grid-cols-3">
        <div className="rounded-md border border-slate-200 bg-slate-50/70 p-3">
          <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
            Operator Identity Registry
          </div>
          <div className="mt-2 flex flex-wrap gap-2">
            {boundary.operator_identity_fields.map((field) => (
              <StatusBadge
                key={field.key}
                label={`${field.label}: ${field.persisted_now ? "Persisted" : "Not persisted"}`}
                variant={field.required_for_future_actions ? "info" : "neutral"}
              />
            ))}
          </div>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Operator identities are not persisted in Phase 0. Production
            credentials and a real auth provider remain required before actions.
          </p>
        </div>

        <div className="rounded-md border border-slate-200 bg-slate-50/70 p-3">
          <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
            Role Catalog
          </div>
          <div className="mt-2 flex flex-wrap gap-2">
            {boundary.provisional_roles.map((role) => (
              <StatusBadge
                key={role.key}
                label={`${role.label}: ${
                  role.manual_review_action_allowed_future
                    ? "Future planning"
                    : "Not allowed"
                }`}
                variant={
                  role.manual_review_action_allowed_future ? "neutral" : "warning"
                }
              />
            ))}
          </div>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Roles are provisional Phase 0 labels only. No UI is hidden or
            unlocked based on these roles.
          </p>
        </div>

        <div className="rounded-md border border-slate-200 bg-slate-50/70 p-3">
          <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
            Permission Catalog
          </div>
          <p className="mt-2 break-words text-sm leading-6 text-slate-600">
            {boundary.future_permissions
              .map((permission) => permission.key)
              .join(", ")}
          </p>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Permissions are future-planning labels only. They do not authorize
            approve, reject, defer, archive, resolve, dispatch, or login
            behavior now.
          </p>
        </div>
      </div>
    </SectionCard>
  );
}

type ReviewItemGroupProps = {
  title: string;
  description: string;
  items: ManualReviewQueueItemResponse[];
  emptyLabel: string;
};

function ReviewItemGroup({
  title,
  description,
  items,
  emptyLabel,
}: ReviewItemGroupProps) {
  return (
    <SectionCard title={title} description={description}>
      {items.length > 0 ? (
        <div className="space-y-3">
          {items.map((item) => (
            <ReviewQueueItemCard key={item.review_item_id} item={item} />
          ))}
        </div>
      ) : (
        <div className="rounded-md border border-dashed border-slate-300 bg-slate-50 px-3 py-4 text-sm text-slate-600">
          {emptyLabel}
        </div>
      )}
    </SectionCard>
  );
}

function ReviewQueueItemCard({
  item,
}: {
  item: ManualReviewQueueItemResponse;
}) {
  const entityLabels = [
    item.job_id ? `Job ${compactId(item.job_id)}` : null,
    item.work_order_id ? `Work order ${compactId(item.work_order_id)}` : null,
    item.visit_id ? `Visit ${compactId(item.visit_id)}` : null,
    item.route_assignment_id
      ? `Route ${compactId(item.route_assignment_id)}`
      : null,
    item.water_emergency_id
      ? `Water Emergency ${compactId(item.water_emergency_id)}`
      : null,
  ].filter(Boolean);

  return (
    <article className="rounded-md border border-slate-200 bg-white p-4 shadow-sm ring-1 ring-black/[0.02]">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <StatusBadge
              label={humanizeLabel(item.reason_code)}
              variant={badgeVariantForLabel(item.reason_code)}
            />
            <StatusBadge
              label={humanizeLabel(item.status)}
              variant={badgeVariantForLabel(item.status)}
            />
            <StatusBadge
              label={humanizeLabel(item.age_bucket)}
              variant={badgeVariantForLabel(item.age_bucket)}
            />
            <StatusBadge
              label={humanizeLabel(item.decision_readiness.label)}
              variant={badgeVariantForLabel(item.decision_readiness.label)}
            />
            <StatusBadge
              label={humanizeLabel(item.action_preflight.label)}
              variant={badgeVariantForLabel(item.action_preflight.label)}
            />
            <StatusBadge
              label={humanizeLabel(item.future_action_preview.label)}
              variant={badgeVariantForLabel(item.future_action_preview.label)}
            />
            <StatusBadge
              label={humanizeLabel(item.command_contract.label)}
              variant={badgeVariantForLabel(item.command_contract.label)}
            />
            <StatusBadge
              label={humanizeLabel(item.audit_ledger_dry_run.label)}
              variant={badgeVariantForLabel(item.audit_ledger_dry_run.label)}
            />
            <StatusBadge
              label={humanizeLabel(item.command_validation.label)}
              variant={badgeVariantForLabel(item.command_validation.label)}
            />
            <StatusBadge
              label={humanizeLabel(item.permission_readiness.label)}
              variant={badgeVariantForLabel(item.permission_readiness.label)}
            />
          </div>
          <div className="mt-3 text-sm font-semibold text-[#162033]">
            {humanizeLabel(item.primary_group)}
          </div>
          <div className="mt-1 text-sm leading-6 text-slate-600">
            {item.recommended_action ??
              "Read-only queue evidence is available for operator review."}
          </div>
        </div>
        <time
          className="shrink-0 rounded-md bg-slate-50 px-2.5 py-1.5 text-sm font-medium text-slate-600 ring-1 ring-slate-200"
          dateTime={item.created_at}
        >
          {formatDateTime(item.created_at)}
        </time>
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {item.visibility_groups.map((group) => (
          <StatusBadge
            key={`${item.review_item_id}-${group}`}
            label={humanizeLabel(group)}
            variant={badgeVariantForLabel(group)}
          />
        ))}
      </div>

      <div className="mt-3 rounded-md border border-slate-200 bg-slate-50 px-3 py-3">
        <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
          Decision Readiness
        </div>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          {item.decision_readiness.summary}
        </p>
        <div className="mt-2 flex flex-wrap gap-2">
          {item.decision_readiness.reason_codes.map((reasonCode) => (
            <StatusBadge
              key={`${item.review_item_id}-${reasonCode}`}
              label={humanizeLabel(reasonCode)}
              variant={badgeVariantForLabel(reasonCode)}
            />
          ))}
        </div>
      </div>

      <div className="mt-3 rounded-md border border-slate-200 bg-white px-3 py-3">
        <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
          Future Action Preflight
        </div>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          {item.action_preflight.summary}
        </p>
        <div className="mt-3 flex flex-wrap gap-2">
          {item.action_preflight.blocker_codes.map((blockerCode) => (
            <StatusBadge
              key={`${item.review_item_id}-${blockerCode}`}
              label={humanizeLabel(blockerCode)}
              variant={badgeVariantForLabel(blockerCode)}
            />
          ))}
          {item.action_preflight.required_future_controls.map((control) => (
            <StatusBadge
              key={`${item.review_item_id}-${control}`}
              label={humanizeLabel(control)}
              variant={badgeVariantForLabel(control)}
            />
          ))}
        </div>
      </div>

      <div className="mt-3 rounded-md border border-slate-200 bg-slate-50 px-3 py-3">
        <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
          Future Action Preview
        </div>
        <div className="mt-2 flex flex-wrap gap-2">
          <StatusBadge
            label={humanizeLabel(item.future_action_preview.label)}
            variant={badgeVariantForLabel(item.future_action_preview.label)}
          />
          <StatusBadge
            label={
              item.future_action_preview.is_currently_executable
                ? "Currently executable"
                : "Not executable in Phase 0"
            }
            variant={
              item.future_action_preview.is_currently_executable
                ? "warning"
                : "neutral"
            }
          />
        </div>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          {item.future_action_preview.description}
        </p>
        <div className="mt-3 grid gap-3 lg:grid-cols-2">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Expected Outcome
            </div>
            <p className="mt-1 text-sm leading-6 text-slate-600">
              {item.future_action_preview.expected_outcome_summary}
            </p>
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Impacted Entities
            </div>
            <p className="mt-1 break-words text-sm leading-6 text-slate-600">
              {item.future_action_preview.impacted_entity_summary}
            </p>
          </div>
        </div>
      </div>

      <div className="mt-3 rounded-md border border-blue-200 bg-blue-50/70 px-3 py-3">
        <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
          Future Command Contract
        </div>
        <div className="mt-2 flex flex-wrap gap-2">
          <StatusBadge
            label={humanizeLabel(item.command_contract.label)}
            variant={badgeVariantForLabel(item.command_contract.label)}
          />
          <StatusBadge
            label={
              item.command_contract.is_currently_executable
                ? "Currently executable: Yes"
                : "Currently executable: No"
            }
            variant={
              item.command_contract.is_currently_executable
                ? "warning"
                : "neutral"
            }
          />
          {item.command_contract.requires_role_authorization ? (
            <StatusBadge label="Requires role authorization" variant="info" />
          ) : null}
          {item.command_contract.requires_idempotency_key ? (
            <StatusBadge label="Requires idempotency key" variant="info" />
          ) : null}
        </div>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          {item.command_contract.summary}
        </p>
        <div className="mt-3 grid gap-3 lg:grid-cols-2">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Audit Envelope Requirements
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              {item.command_contract.required_contract_labels.map((label) => (
                <StatusBadge
                  key={`${item.review_item_id}-${label}`}
                  label={humanizeLabel(label)}
                  variant={badgeVariantForLabel(label)}
                />
              ))}
            </div>
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Command blockers
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              {item.command_contract.blocker_codes.length > 0 ? (
                item.command_contract.blocker_codes.map((blockerCode) => (
                  <StatusBadge
                    key={`${item.review_item_id}-${blockerCode}`}
                    label={humanizeLabel(blockerCode)}
                    variant={badgeVariantForLabel(blockerCode)}
                  />
                ))
              ) : (
                <span className="text-sm text-slate-600">
                  No blocker codes beyond Phase 0 read-only status.
                </span>
              )}
            </div>
          </div>
        </div>
        <p className="mt-3 break-words text-sm leading-6 text-slate-600">
          {item.command_contract.impacted_entity_summary}
        </p>
      </div>

      <div className="mt-3 rounded-md border border-amber-200 bg-amber-50/70 px-3 py-3">
        <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
          Command Dry Run
        </div>
        <div className="mt-2 flex flex-wrap gap-2">
          <StatusBadge
            label={humanizeLabel(item.audit_ledger_dry_run.label)}
            variant={badgeVariantForLabel(item.audit_ledger_dry_run.label)}
          />
          <StatusBadge
            label={
              item.audit_ledger_dry_run.is_currently_executable
                ? "Currently executable: Yes"
                : "Currently executable: No"
            }
            variant={
              item.audit_ledger_dry_run.is_currently_executable
                ? "warning"
                : "neutral"
            }
          />
          <StatusBadge
            label={
              item.audit_ledger_dry_run.phase_allows_execution
                ? "Phase allows execution: Yes"
                : "Phase allows execution: No"
            }
            variant={
              item.audit_ledger_dry_run.phase_allows_execution
                ? "warning"
                : "neutral"
            }
          />
          {item.audit_ledger_dry_run.requires_idempotency_key ? (
            <StatusBadge label="Idempotency Key Required" variant="info" />
          ) : null}
          {item.audit_ledger_dry_run.requires_immutable_event_recording ? (
            <StatusBadge label="Immutable Event Required" variant="info" />
          ) : null}
          {item.audit_ledger_dry_run.requires_post_action_consistency_check ? (
            <StatusBadge label="Consistency Check Required" variant="info" />
          ) : null}
        </div>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          {item.audit_ledger_dry_run.summary}
        </p>
        <div className="mt-3 grid gap-3 lg:grid-cols-2">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Audit Ledger Preparation
            </div>
            <p className="mt-1 break-words text-sm leading-6 text-slate-600">
              {item.audit_ledger_dry_run.proposed_future_event_type} /{" "}
              {humanizeLabel(
                item.audit_ledger_dry_run.proposed_future_event_state,
              )}
            </p>
            <p className="mt-1 break-all font-mono text-xs leading-5 text-slate-600">
              {item.audit_ledger_dry_run.proposed_future_idempotency_scope}
            </p>
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Dry-run Requirements
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              {item.audit_ledger_dry_run.required_labels.map((label) => (
                <StatusBadge
                  key={`${item.review_item_id}-${label}`}
                  label={humanizeLabel(label)}
                  variant={badgeVariantForLabel(label)}
                />
              ))}
            </div>
          </div>
        </div>
        <p className="mt-3 text-sm leading-6 text-slate-600">
          {item.audit_ledger_dry_run.execution_unavailable_reason}
        </p>
      </div>

      <div className="mt-3 rounded-md border border-emerald-200 bg-emerald-50/70 px-3 py-3">
        <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
          Command Validation
        </div>
        <div className="mt-2 flex flex-wrap gap-2">
          <StatusBadge
            label={humanizeLabel(item.command_validation.label)}
            variant={badgeVariantForLabel(item.command_validation.label)}
          />
          <StatusBadge
            label={
              item.command_validation.is_currently_executable
                ? "Currently executable: Yes"
                : "Currently executable: No"
            }
            variant={
              item.command_validation.is_currently_executable
                ? "warning"
                : "neutral"
            }
          />
          <StatusBadge
            label={
              item.command_validation.phase_allows_execution
                ? "Phase allows execution: Yes"
                : "Phase allows execution: No"
            }
            variant={
              item.command_validation.phase_allows_execution
                ? "warning"
                : "neutral"
            }
          />
          {item.command_validation.requires_audit_reason ? (
            <StatusBadge label="Audit Reason Required" variant="info" />
          ) : null}
          {item.command_validation.requires_operator_identity ? (
            <StatusBadge label="Operator Identity Required" variant="info" />
          ) : null}
          {item.command_validation.requires_idempotency_key ? (
            <StatusBadge label="Idempotency Key Required" variant="info" />
          ) : null}
          {item.command_validation.requires_immutable_event_recording ? (
            <StatusBadge label="Immutable Event Required" variant="info" />
          ) : null}
          {item.command_validation.requires_post_action_consistency_check ? (
            <StatusBadge label="Consistency Check Required" variant="info" />
          ) : null}
        </div>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          {item.command_validation.summary}
        </p>
        <div className="mt-3 grid gap-3 lg:grid-cols-2">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Candidate Future Command
            </div>
            <p className="mt-1 break-words text-sm leading-6 text-slate-600">
              {humanizeLabel(item.command_validation.candidate_future_command_type)}
            </p>
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Execution Boundary
            </div>
            <p className="mt-1 text-sm leading-6 text-slate-600">
              {item.command_validation.execution_unavailable_reason}
            </p>
          </div>
        </div>
        <div className="mt-3 grid gap-3 lg:grid-cols-2">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Validation blockers
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              {item.command_validation.validation_blockers.map((blocker) => (
                <StatusBadge
                  key={`${item.review_item_id}-${blocker}`}
                  label={humanizeLabel(blocker)}
                  variant={badgeVariantForLabel(blocker)}
                />
              ))}
            </div>
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Validation warnings
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              {item.command_validation.validation_warnings.map((warning) => (
                <StatusBadge
                  key={`${item.review_item_id}-${warning}`}
                  label={humanizeLabel(warning)}
                  variant={badgeVariantForLabel(warning)}
                />
              ))}
            </div>
          </div>
        </div>
        <SafetyGateMatrix
          gates={item.command_validation.safety_gates}
          itemId={item.review_item_id}
        />
      </div>

      <div className="mt-3 rounded-md border border-violet-200 bg-violet-50/70 px-3 py-3">
        <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
          Future Authorization Boundary
        </div>
        <div className="mt-2 flex flex-wrap gap-2">
          <StatusBadge
            label={humanizeLabel(item.permission_readiness.label)}
            variant={badgeVariantForLabel(item.permission_readiness.label)}
          />
          <StatusBadge
            label={
              item.permission_readiness.is_currently_executable
                ? "Currently executable: Yes"
                : "Currently executable: No"
            }
            variant={
              item.permission_readiness.is_currently_executable
                ? "warning"
                : "neutral"
            }
          />
          <StatusBadge
            label={
              item.permission_readiness.phase_allows_execution
                ? "Phase allows execution: Yes"
                : "Phase allows execution: No"
            }
            variant={
              item.permission_readiness.phase_allows_execution
                ? "warning"
                : "neutral"
            }
          />
          {item.permission_readiness.future_operator_identity_required ? (
            <StatusBadge label="Future operator identity required" variant="info" />
          ) : null}
          {item.permission_readiness.future_role_authorization_required ? (
            <StatusBadge label="Future role authorization required" variant="info" />
          ) : null}
          {item.permission_readiness.service_account_allowed ? null : (
            <StatusBadge label="Service account not allowed" variant="warning" />
          )}
          {item.permission_readiness.technician_action_allowed ? null : (
            <StatusBadge label="Technician action not allowed" variant="warning" />
          )}
        </div>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          {item.permission_readiness.summary}
        </p>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          {item.permission_readiness.execution_unavailable_reason}
        </p>
        <div className="mt-3 grid gap-3 lg:grid-cols-3">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Future Required Roles
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              {item.permission_readiness.future_required_roles.length > 0 ? (
                item.permission_readiness.future_required_roles.map((role) => (
                  <StatusBadge
                    key={`${item.review_item_id}-${role}`}
                    label={humanizeLabel(role)}
                    variant="neutral"
                  />
                ))
              ) : (
                <span className="text-sm text-slate-600">
                  No active future role candidate for this review status.
                </span>
              )}
            </div>
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Future Required Permissions
            </div>
            <p className="mt-2 break-words text-sm leading-6 text-slate-600">
              {item.permission_readiness.future_required_permissions.length > 0
                ? item.permission_readiness.future_required_permissions.join(", ")
                : "No active future permission set for this review status."}
            </p>
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Identity Boundary
            </div>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              {item.permission_readiness.identity_unavailable_reason}
            </p>
          </div>
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          {item.permission_readiness.required_permission_labels.map((label) => (
            <StatusBadge
              key={`${item.review_item_id}-${label}`}
              label={humanizeLabel(label)}
              variant={badgeVariantForLabel(label)}
            />
          ))}
        </div>
      </div>

      {entityLabels.length > 0 ? (
        <div className="mt-3 flex flex-wrap gap-2 text-xs font-semibold text-slate-500">
          {entityLabels.map((label) => (
            <span
              key={`${item.review_item_id}-${label}`}
              className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1"
            >
              {label}
            </span>
          ))}
        </div>
      ) : null}

      <div className="mt-3 grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
        <MiniMetric label="Severity" value={humanizeLabel(item.severity)} />
        <MiniMetric
          label="Attention"
          value={item.attention_indicator ? "Requires review" : "Historical"}
        />
        <MiniMetric
          label="Readiness"
          value={
            item.decision_readiness.is_active_decision_need
              ? "Active decision need"
              : "Historical visibility"
          }
        />
        <MiniMetric
          label="Confidence"
          value={
            item.confidence_score === null
              ? "Not scored"
              : `${item.confidence_score}%`
          }
        />
        <MiniMetric
          label="Executable"
          value={
            item.action_preflight.is_currently_executable
              ? "Executable"
              : "Read-only Phase 0"
          }
        />
        <MiniMetric
          label="Preview Executable"
          value={
            item.future_action_preview.is_currently_executable
              ? "Executable"
              : "Read-only Phase 0"
          }
        />
        <MiniMetric
          label="Command Executable"
          value={
            item.command_contract.is_currently_executable
              ? "Executable"
              : "Read-only Phase 0"
          }
        />
        <MiniMetric
          label="Dry-run Executable"
          value={
            item.audit_ledger_dry_run.is_currently_executable
              ? "Executable"
              : "Read-only Phase 0"
          }
        />
        <MiniMetric
          label="Validation Executable"
          value={
            item.command_validation.is_currently_executable
              ? "Executable"
              : "Read-only Phase 0"
          }
        />
      </div>

      {item.audit_correlation_id ? (
        <div className="mt-3 break-all font-mono text-xs font-medium text-slate-500">
          Audit correlation: {item.audit_correlation_id}
        </div>
      ) : null}
    </article>
  );
}

function SafetyGateMatrix({
  gates,
  itemId,
}: {
  gates: ManualReviewSafetyGateResponse[];
  itemId: string;
}) {
  return (
    <div className="mt-4">
      <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
        Safety Gate Matrix
      </div>
      <div className="mt-2 grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
        {gates.map((gate) => (
          <div
            key={`${itemId}-${gate.key}`}
            className="rounded-md border border-slate-200 bg-white/80 p-2"
          >
            <div className="flex flex-wrap gap-1.5">
              <StatusBadge
                label={humanizeLabel(gate.label)}
                variant={gate.passed ? "success" : "danger"}
              />
              <StatusBadge
                label={gate.required ? "Required" : "Optional"}
                variant={gate.required ? "info" : "neutral"}
              />
            </div>
            <p className="mt-2 text-xs leading-5 text-slate-600">
              {gate.reason}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

function MiniMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2">
      <div className="text-xs font-semibold text-slate-500">{label}</div>
      <div className="mt-1 text-sm font-semibold text-[#162033]">{value}</div>
    </div>
  );
}
