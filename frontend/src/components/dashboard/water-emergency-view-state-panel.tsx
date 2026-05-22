"use client";

import { useMemo, useState } from "react";
import type {
  WaterEmergencyDashboardResponse,
  WaterEmergencyViewStateItemResponse
} from "@/lib/dashboard-contracts";
import {
  deriveWaterEmergencyVisibleRecords,
  type WaterEmergencySortKey
} from "@/lib/water-emergency-view-state";
import { compactId, formatCount, formatDateTime, humanizeLabel } from "@/lib/format";
import { StatusBadge } from "@/components/dashboard/status-badge";

type WaterEmergencyViewStatePanelProps = {
  data: WaterEmergencyDashboardResponse;
};

const activeLimit = 8;

export function WaterEmergencyViewStatePanel({
  data
}: WaterEmergencyViewStatePanelProps) {
  const [selectedFilter, setSelectedFilter] = useState("all");
  const [selectedSort, setSelectedSort] =
    useState<WaterEmergencySortKey>("attention");
  const viewState = useMemo(
    () =>
      deriveWaterEmergencyVisibleRecords(data, {
        selectedFilter,
        selectedSort
      }),
    [data, selectedFilter, selectedSort]
  );
  const visibleActiveItems = viewState.visibleActiveItems.slice(0, activeLimit);
  const hiddenActiveCount =
    viewState.visibleActiveItems.length - visibleActiveItems.length;
  const hasVisibleItems = viewState.visibleItems.length > 0;

  return (
    <div className="rounded-md border border-slate-200 bg-slate-50/70 p-4">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
        <div className="min-w-0">
          <h3 className="text-sm font-semibold text-[#162033]">
            Water Emergency View State
          </h3>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
            Read-only filter and sort controls change only this dashboard view.
            They do not approve, dispatch, close, escalate, or update Water
            Emergency records.
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            <StatusBadge label="Frontend view state only" variant="info" />
            <StatusBadge label="No backend mutation" variant="success" />
            <StatusBadge label="Closed records separated" variant="info" />
          </div>
        </div>
        <div className="grid w-full gap-3 sm:grid-cols-2 xl:w-[28rem]">
          <label className="text-sm font-semibold text-slate-700">
            Filter group
            <select
              className="mt-2 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-[#162033] outline-none transition focus:border-[#2563eb] focus:ring-2 focus:ring-[#2563eb]/20"
              value={selectedFilter}
              onChange={(event) => setSelectedFilter(event.target.value)}
            >
              {data.view_state_summary.available_filters.map((option) => (
                <option key={option.key} value={option.key}>
                  {option.label} ({formatCount(option.count)})
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm font-semibold text-slate-700">
            Sort order
            <select
              className="mt-2 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-[#162033] outline-none transition focus:border-[#2563eb] focus:ring-2 focus:ring-[#2563eb]/20"
              value={selectedSort}
              onChange={(event) =>
                setSelectedSort(event.target.value as WaterEmergencySortKey)
              }
            >
              {data.view_state_summary.sort_options.map((option) => (
                <option key={option.key} value={option.key}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-3">
        <ViewStateMetric
          label="Selected"
          value={viewState.selectedFilter.count}
          detail={viewState.selectedFilter.label}
        />
        <ViewStateMetric
          label="Active visible"
          value={viewState.visibleActiveItems.length}
          detail="Open records in view"
        />
        <ViewStateMetric
          label="Closed visible"
          value={viewState.visibleClosedItems.length}
          detail="Separated records in view"
        />
      </div>

      <div className="mt-4 rounded-md border border-slate-200 bg-white p-3">
        <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
          Active filter
        </div>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          {viewState.selectedFilter.description}
        </p>
        <p className="mt-1 text-xs font-semibold text-slate-500">
          Sort: {viewState.selectedSort.description}
        </p>
      </div>

      {!hasVisibleItems ? (
        <div className="mt-4 rounded-md border border-dashed border-slate-300 bg-white p-4 text-sm leading-6 text-slate-500">
          No Water Emergency records match this read-only view filter.
        </div>
      ) : null}

      <div className="mt-4 grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(18rem,0.65fr)]">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
            Active attention view
          </div>
          {visibleActiveItems.length > 0 ? (
            <div className="mt-2 grid gap-3 lg:grid-cols-2">
              {visibleActiveItems.map((item) => (
                <WaterEmergencyViewStateCard key={item.water_emergency_id} item={item} />
              ))}
            </div>
          ) : (
            <p className="mt-2 text-sm leading-6 text-slate-500">
              No active Water Emergency records match this view.
            </p>
          )}
          {hiddenActiveCount > 0 ? (
            <p className="mt-3 text-sm leading-6 text-slate-500">
              Showing first {formatCount(visibleActiveItems.length)} active attention
              records.
            </p>
          ) : null}
        </div>

        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
            Closed or resolved view
          </div>
          {viewState.visibleClosedItems.length > 0 ? (
            <div className="mt-2 grid gap-3">
              {viewState.visibleClosedItems.map((item) => (
                <WaterEmergencyViewStateCard key={item.water_emergency_id} item={item} />
              ))}
            </div>
          ) : (
            <p className="mt-2 text-sm leading-6 text-slate-500">
              No closed or resolved Water Emergency records match this view.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

function WaterEmergencyViewStateCard({
  item
}: {
  item: WaterEmergencyViewStateItemResponse;
}) {
  return (
    <article className="rounded-md border border-slate-200 bg-white p-3">
      <div className="flex flex-wrap items-center gap-2">
        <StatusBadge
          label={humanizeLabel(item.primary_filter_group)}
          variant={viewStateVariant(item.primary_filter_group)}
        />
        <StatusBadge label={humanizeLabel(item.time_sensitivity_label)} variant="info" />
      </div>
      <p className="mt-2 text-sm leading-6 text-slate-600">{item.summary}</p>
      <div className="mt-3 grid grid-cols-2 gap-2 text-xs font-semibold text-slate-600 sm:grid-cols-4">
        <ViewStateMetric label="Reviews" value={item.open_review_count} />
        <ViewStateMetric label="Critical" value={item.critical_alert_count} />
        <ViewStateMetric label="Blocked" value={item.blocker_count} />
        <ViewStateMetric label="Unknown" value={item.unknown_count} />
      </div>
      <div className="mt-3 flex flex-wrap gap-2 text-xs font-semibold text-slate-500">
        <span className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1">
          Water Emergency {compactId(item.water_emergency_id)}
        </span>
        <span className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1">
          Job {compactId(item.related_job_id)}
        </span>
        <span className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1">
          Visits {formatCount(item.related_visit_ids.length)}
        </span>
        <span className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1">
          Last activity{" "}
          {item.last_activity_at ? formatDateTime(item.last_activity_at) : "not recorded"}
        </span>
      </div>
      {item.reason_codes.length > 0 ? (
        <div className="mt-3 flex flex-wrap gap-2">
          {item.reason_codes.slice(0, 4).map((reason) => (
            <span
              key={reason}
              className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1 text-xs font-semibold text-slate-600"
            >
              {humanizeLabel(reason)}
            </span>
          ))}
        </div>
      ) : null}
    </article>
  );
}

function ViewStateMetric({
  label,
  value,
  detail
}: {
  label: string;
  value: number;
  detail?: string;
}) {
  return (
    <div className="rounded-md border border-slate-200 bg-white px-3 py-2">
      <div className="text-base font-semibold leading-none text-[#162033]">
        {formatCount(value)}
      </div>
      <div className="mt-1 text-xs font-semibold text-slate-600">{label}</div>
      {detail ? <div className="mt-1 text-xs leading-4 text-slate-500">{detail}</div> : null}
    </div>
  );
}

function viewStateVariant(label: string) {
  if (
    label === "critical_attention" ||
    label === "followup_overdue" ||
    label === "stale_evidence"
  ) {
    return "danger";
  }
  if (
    label === "needs_manual_review" ||
    label === "blocked_missing_data" ||
    label === "followup_due" ||
    label === "unknown_timing"
  ) {
    return "warning";
  }
  if (label === "closed_or_resolved" || label === "active") return "success";
  return "info";
}
