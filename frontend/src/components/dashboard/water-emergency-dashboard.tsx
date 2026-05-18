import type { ReactNode } from "react";
import type {
  DashboardFetchResult,
  WaterEmergencyDashboardResponse
} from "@/lib/dashboard-contracts";
import { compactId, formatCount, formatDateTime, humanizeLabel } from "@/lib/format";
import { AlertStrip } from "@/components/dashboard/alert-strip";
import { CountBucketPanel } from "@/components/dashboard/count-bucket-panel";
import { SectionCard } from "@/components/dashboard/section-card";
import { StatCard } from "@/components/dashboard/stat-card";
import { StatusBadge } from "@/components/dashboard/status-badge";
import { TimelineList } from "@/components/dashboard/timeline-list";

type WaterEmergencyDashboardProps = {
  result: DashboardFetchResult<WaterEmergencyDashboardResponse>;
};

export function WaterEmergencyDashboard({
  result
}: WaterEmergencyDashboardProps) {
  const { data, source, errorMessage } = result;

  return (
    <SectionCard
      id="water-emergency"
      title="Water Emergency Command View"
      description="Dedicated Water Emergency visibility is separated from standard dispatch and remains display-only."
    >
      <div className="space-y-5">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.16em] text-[#2563eb]">
              Water Emergency
            </div>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Read-only Water Emergency visibility shows persisted emergency
              records, review indicators, equipment flags, and evidence
              references without creating, closing, dispatching, or approving
              emergency work.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <StatusBadge
              label={
                source === "api"
                  ? "Live Water Emergency read model"
                  : "Mock Water Emergency fallback"
              }
              variant={source === "api" ? "success" : "warning"}
            />
            <StatusBadge label="Separated from dispatch" variant="info" />
          </div>
        </div>

        {source === "mock" && errorMessage ? (
          <AlertStrip title="Water Emergency fallback data is active" tone="warning">
            {errorMessage}
          </AlertStrip>
        ) : null}

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
          <StatCard
            label="Open"
            value={data.open_count}
            tone={data.open_count > 0 ? "info" : "neutral"}
          />
          <StatCard label="Closed" value={data.closed_count} tone="good" />
          <StatCard
            label="Multi-Visit"
            value={data.multi_visit_count}
            detail="Jobs with multiple related visits"
            tone={data.multi_visit_count > 0 ? "info" : "neutral"}
          />
          <StatCard
            label="Equipment Onsite"
            value={data.equipment_onsite_count}
            tone={data.equipment_onsite_count > 0 ? "warning" : "neutral"}
          />
          <StatCard
            label="Review Indicators"
            value={data.review_indicator_count}
            tone={data.review_indicator_count > 0 ? "warning" : "good"}
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard
            label="Moisture Tracking"
            value={data.moisture_tracking_required_count}
            tone={data.moisture_tracking_required_count > 0 ? "info" : "neutral"}
          />
          <StatCard label="Related Jobs" value={data.related_job_count} />
          <StatCard label="Related Visits" value={data.related_visit_count} />
          <StatCard
            label="Escalation"
            value={data.escalation_indicator_count}
            tone={data.escalation_indicator_count > 0 ? "danger" : "good"}
          />
        </div>

        <div className="grid gap-4 xl:grid-cols-3">
          <VisibilityPanel title="Equipment Context">
            <div className="grid grid-cols-2 gap-2">
              <RecordMetric
                label="Onsite"
                value={data.equipment_summary.equipment_onsite_count}
              />
              <RecordMetric
                label="Moisture"
                value={data.equipment_summary.moisture_tracking_required_count}
              />
              <RecordMetric
                label="WO Notes"
                value={data.equipment_summary.work_orders_with_equipment_notes_count}
              />
              <RecordMetric
                label="Unknown"
                value={data.equipment_summary.records_missing_equipment_context_count}
              />
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              <StatusBadge
                label={
                  data.equipment_summary.inventory_entity_available
                    ? "Equipment inventory modeled"
                    : "Equipment inventory not modeled"
                }
                variant={
                  data.equipment_summary.inventory_entity_available
                    ? "success"
                    : "warning"
                }
              />
              {data.equipment_summary.unknown_counts.map((bucket) => (
                <StatusBadge
                  key={bucket.label}
                  label={`${humanizeLabel(bucket.label)}: ${formatCount(bucket.count)}`}
                  variant="warning"
                />
              ))}
            </div>
          </VisibilityPanel>

          <VisibilityPanel title="Visit Chain">
            <div className="grid grid-cols-2 gap-2">
              <RecordMetric
                label="Visits"
                value={data.visit_chain_summary.total_visits}
              />
              <RecordMetric
                label="Multi"
                value={data.visit_chain_summary.multi_visit_record_count}
              />
              <RecordMetric
                label="Scheduled"
                value={data.visit_chain_summary.scheduled_visit_count}
              />
              <RecordMetric
                label="Complete"
                value={data.visit_chain_summary.completed_visit_count}
              />
            </div>
            <BucketPills buckets={data.visit_chain_summary.visit_status_counts} />
          </VisibilityPanel>

          <VisibilityPanel title="Drying Stage Visibility">
            <div className="grid grid-cols-2 gap-2">
              <RecordMetric
                label="Missing"
                value={data.drying_stage_summary.missing_stage_count}
              />
              <RecordMetric
                label="Moisture"
                value={data.drying_stage_summary.moisture_tracking_required_count}
              />
            </div>
            <div className="mt-3">
              <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                Active stages
              </div>
              <BucketPills buckets={data.drying_stage_summary.active_stage_counts} />
            </div>
          </VisibilityPanel>
        </div>

        <div className="grid gap-4 lg:grid-cols-3">
          <CountBucketPanel title="Emergency Status" buckets={data.status_counts} />
          <CountBucketPanel title="Drying Stage" buckets={data.stage_counts} />
          <CountBucketPanel title="Unknowns And Gaps" buckets={data.data_gap_counts} />
        </div>

        <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(20rem,0.8fr)]">
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-[#162033]">
              Emergency Records
            </h3>
            <div className="grid gap-3">
              {data.records.map((record) => (
                <article
                  key={record.water_emergency_id}
                  className="rounded-md border border-slate-200 bg-slate-50/70 p-4"
                >
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <StatusBadge
                          label={record.is_open ? "Open" : "Closed"}
                          variant={record.is_open ? "info" : "success"}
                        />
                        <StatusBadge
                          label={humanizeLabel(record.status)}
                          variant={record.open_review_count > 0 ? "warning" : "neutral"}
                        />
                      </div>
                      <div className="mt-3 text-sm font-semibold text-[#162033]">
                        Job {compactId(record.job_id)}
                      </div>
                      <div className="mt-1 text-sm leading-6 text-slate-600">
                        {humanizeLabel(record.drying_stage)} -{" "}
                        {record.next_required_action ?? "No next action recorded"}
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-center text-xs font-semibold text-slate-600">
                      <RecordMetric label="Visits" value={record.related_visit_ids.length} />
                      <RecordMetric
                        label="Reviews"
                        value={record.open_review_count}
                      />
                      <RecordMetric
                        label="Events"
                        value={record.timeline_event_count}
                      />
                    </div>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-2 text-xs font-semibold text-slate-500">
                    <span className="rounded-md border border-slate-200 bg-white px-2 py-1">
                      Water Emergency {compactId(record.water_emergency_id)}
                    </span>
                    {record.related_visit_ids.slice(0, 3).map((visitId) => (
                      <span
                        key={visitId}
                        className="rounded-md border border-slate-200 bg-white px-2 py-1"
                      >
                        Visit {compactId(visitId)}
                      </span>
                    ))}
                    {record.audit_correlation_ids.slice(0, 2).map((auditId) => (
                      <span
                        key={auditId}
                        className="rounded-md border border-slate-200 bg-white px-2 py-1"
                      >
                        Audit {auditId}
                      </span>
                    ))}
                  </div>
                  <div className="mt-3 text-xs font-medium text-slate-500">
                    Opened{" "}
                    {record.opened_at ? formatDateTime(record.opened_at) : "not recorded"}
                    {record.closed_at
                      ? ` - Closed ${formatDateTime(record.closed_at)}`
                      : ""}
                  </div>
                </article>
              ))}
            </div>
          </div>

          <div className="rounded-md border border-slate-200 bg-slate-50/70 p-4">
            <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <h3 className="text-sm font-semibold text-[#162033]">
                Emergency Evidence Timeline
              </h3>
              <span className="text-sm font-semibold text-slate-600">
                {formatCount(data.timeline_summary.returned_events)} events
              </span>
            </div>
            <TimelineList entries={data.timeline_summary.entries} />
          </div>
        </div>
      </div>
    </SectionCard>
  );
}

function VisibilityPanel({
  title,
  children
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <div className="rounded-md border border-slate-200 bg-slate-50/70 p-4">
      <h3 className="text-sm font-semibold text-[#162033]">{title}</h3>
      <div className="mt-3">{children}</div>
    </div>
  );
}

function BucketPills({ buckets }: { buckets: { label: string; count: number }[] }) {
  if (buckets.length === 0) {
    return (
      <div className="mt-3 text-sm leading-6 text-slate-500">
        No persisted bucket data returned.
      </div>
    );
  }

  return (
    <div className="mt-3 flex flex-wrap gap-2">
      {buckets.map((bucket) => (
        <span
          key={bucket.label}
          className="rounded-md border border-slate-200 bg-white px-2 py-1 text-xs font-semibold text-slate-600"
        >
          {humanizeLabel(bucket.label)} {formatCount(bucket.count)}
        </span>
      ))}
    </div>
  );
}

function RecordMetric({ label, value }: { label: string; value: number }) {
  return (
    <div className="min-w-14 rounded-md border border-slate-200 bg-white px-2 py-2">
      <div className="text-base font-semibold leading-none text-[#162033]">
        {formatCount(value)}
      </div>
      <div className="mt-1 leading-4">{label}</div>
    </div>
  );
}
