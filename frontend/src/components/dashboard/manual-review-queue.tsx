"use client";

import { useMemo, useState, useSyncExternalStore } from "react";
import type {
  DashboardFetchResult,
  ManualReviewQueueItemResponse,
  ManualReviewQueueResponse
} from "@/lib/dashboard-contracts";
import {
  deriveManualReviewVisibleRecords,
  type ManualReviewSortKey
} from "@/lib/manual-review-view-state";
import {
  getManualReviewBrowserStorage,
  getManualReviewViewPreferencesServerSnapshot,
  getManualReviewViewPreferencesSnapshot,
  notifyManualReviewViewPreferencesChanged,
  readManualReviewViewPreferencesSnapshot,
  subscribeManualReviewViewPreferences,
  writeManualReviewViewPreferences
} from "@/lib/manual-review-view-preferences";
import { compactId, formatCount, formatDateTime, humanizeLabel } from "@/lib/format";
import { CountBucketPanel } from "@/components/dashboard/count-bucket-panel";
import { SectionCard } from "@/components/dashboard/section-card";
import { SectionHeading } from "@/components/dashboard/section-heading";
import { StatCard } from "@/components/dashboard/stat-card";
import {
  badgeVariantForLabel,
  StatusBadge
} from "@/components/dashboard/status-badge";

type ManualReviewQueueProps = {
  result: DashboardFetchResult<ManualReviewQueueResponse>;
};

export function ManualReviewQueue({ result }: ManualReviewQueueProps) {
  const { data } = result;
  const [fallbackPreferences, setFallbackPreferences] = useState({
    selectedFilter: "all",
    selectedSort: "attention" as ManualReviewSortKey
  });
  const availableFilterKeys = useMemo(
    () => new Set(data.available_filters.map((option) => option.key)),
    [data.available_filters]
  );
  const availableSortKeys = useMemo(
    () => new Set(data.sort_options.map((option) => option.key)),
    [data.sort_options]
  );
  const preferenceSnapshot = useSyncExternalStore(
    subscribeManualReviewViewPreferences,
    getManualReviewViewPreferencesSnapshot,
    getManualReviewViewPreferencesServerSnapshot
  );
  const preferenceReadResult = useMemo(
    () =>
      readManualReviewViewPreferencesSnapshot(preferenceSnapshot, {
        availableFilterKeys,
        availableSortKeys
      }),
    [availableFilterKeys, availableSortKeys, preferenceSnapshot]
  );
  const selectedFilter =
    preferenceReadResult.preferences?.selectedFilter ?? fallbackPreferences.selectedFilter;
  const selectedSort =
    preferenceReadResult.preferences?.selectedSort ?? fallbackPreferences.selectedSort;
  const viewState = useMemo(
    () =>
      deriveManualReviewVisibleRecords(data, {
        selectedFilter,
        selectedSort
      }),
    [data, selectedFilter, selectedSort]
  );
  const activeStandardItems = viewState.visibleStandardItems.filter(
    (item) => item.attention_indicator
  );
  const inactiveStandardItems = viewState.visibleStandardItems.filter(
    (item) => !item.attention_indicator
  );

  function savePreferences(nextPreferences: {
    selectedFilter: string;
    selectedSort: ManualReviewSortKey;
  }) {
    const writeResult = writeManualReviewViewPreferences(
      getManualReviewBrowserStorage(),
      nextPreferences
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

      <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-5">
        <CountBucketPanel title="Review Status" buckets={data.status_counts} />
        <CountBucketPanel title="Reason Distribution" buckets={data.reason_counts} />
        <CountBucketPanel title="Visibility Groups" buckets={data.group_counts} />
        <CountBucketPanel title="Age Buckets" buckets={data.age_bucket_counts} />
        <CountBucketPanel
          title="Decision Readiness"
          buckets={data.decision_readiness_counts}
        />
      </div>

      <SectionCard
        title="Manual Review View State"
        description="Read-only filter and sort controls change only this dashboard view. They do not approve, reject, defer, archive, dispatch, or update Manual Review records."
      >
        <div className="grid gap-4 xl:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)]">
          <div className="grid gap-3 md:grid-cols-2">
            <label className="text-sm font-semibold text-[#162033]">
              Filter review items
              <select
                className="mt-2 min-h-11 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-[#162033] shadow-sm focus:border-[#2f7ae5] focus:outline-none focus:ring-2 focus:ring-[#2f7ae5]/20"
                value={viewState.selectedFilter.key}
                onChange={(event) =>
                  savePreferences({
                    selectedFilter: event.target.value,
                    selectedSort
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
                className="mt-2 min-h-11 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-[#162033] shadow-sm focus:border-[#2f7ae5] focus:outline-none focus:ring-2 focus:ring-[#2f7ae5]/20"
                value={viewState.selectedSort.key}
                onChange={(event) =>
                  savePreferences({
                    selectedFilter,
                    selectedSort: event.target.value as ManualReviewSortKey
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
  emptyLabel
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

function ReviewQueueItemCard({ item }: { item: ManualReviewQueueItemResponse }) {
  const entityLabels = [
    item.job_id ? `Job ${compactId(item.job_id)}` : null,
    item.work_order_id ? `Work order ${compactId(item.work_order_id)}` : null,
    item.visit_id ? `Visit ${compactId(item.visit_id)}` : null,
    item.route_assignment_id
      ? `Route ${compactId(item.route_assignment_id)}`
      : null,
    item.water_emergency_id
      ? `Water Emergency ${compactId(item.water_emergency_id)}`
      : null
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
          value={item.confidence_score === null ? "Not scored" : `${item.confidence_score}%`}
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

function MiniMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2">
      <div className="text-xs font-semibold text-slate-500">{label}</div>
      <div className="mt-1 text-sm font-semibold text-[#162033]">{value}</div>
    </div>
  );
}
