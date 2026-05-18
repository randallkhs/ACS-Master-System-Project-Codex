import type { ReactNode } from "react";
import type {
  DashboardFetchResult,
  WaterEmergencyDetailResponse,
  WaterEmergencyReviewIndicatorResponse,
  WaterEmergencyVisitReferenceResponse,
  WaterEmergencyWorkOrderReferenceResponse
} from "@/lib/dashboard-contracts";
import { compactId, formatCount, formatDateTime, humanizeLabel } from "@/lib/format";
import { AlertStrip } from "@/components/dashboard/alert-strip";
import { CountBucketPanel } from "@/components/dashboard/count-bucket-panel";
import { SectionCard } from "@/components/dashboard/section-card";
import { StatCard } from "@/components/dashboard/stat-card";
import { StatusBadge } from "@/components/dashboard/status-badge";
import { TimelineList } from "@/components/dashboard/timeline-list";

type WaterEmergencyDetailPanelProps = {
  result: DashboardFetchResult<WaterEmergencyDetailResponse | null>;
};

export function WaterEmergencyDetailPanel({
  result
}: WaterEmergencyDetailPanelProps) {
  const { data, source, errorMessage } = result;

  return (
    <SectionCard
      id="water-emergency-detail"
      title="Water Emergency Detail"
      description="Focused read-only record visibility, scoped review indicators, related references, and timeline evidence for one Water Emergency record."
    >
      <div className="space-y-5">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.16em] text-[#2563eb]">
              Focused read-only record
            </div>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Read-only detail visibility shows persisted evidence for the
              selected Water Emergency record. It does not close, dispatch,
              approve, edit, or execute Water Emergency work.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <StatusBadge
              label={
                source === "api"
                  ? "Live detail read model"
                  : "Mock detail fallback"
              }
              variant={source === "api" ? "success" : "warning"}
            />
            <StatusBadge label="Separated from standard dispatch" variant="info" />
          </div>
        </div>

        {source === "mock" && errorMessage ? (
          <AlertStrip title="Water Emergency detail fallback is active" tone="warning">
            {errorMessage}
          </AlertStrip>
        ) : null}

        {!data ? (
          <AlertStrip title="No Water Emergency detail selected" tone="info">
            {errorMessage ??
              "No persisted Water Emergency record was available for detail display."}
          </AlertStrip>
        ) : (
          <WaterEmergencyDetailContent data={data} />
        )}
      </div>
    </SectionCard>
  );
}

function WaterEmergencyDetailContent({
  data
}: {
  data: WaterEmergencyDetailResponse;
}) {
  const { record } = data;

  return (
    <div className="space-y-5">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Work Orders"
          value={data.work_orders.length}
          tone={data.work_orders.length > 0 ? "info" : "warning"}
        />
        <StatCard
          label="Visits"
          value={data.visits.length}
          tone={data.visits.length > 0 ? "info" : "warning"}
        />
        <StatCard
          label="Scoped Reviews"
          value={record.open_review_count}
          tone={record.open_review_count > 0 ? "warning" : "good"}
        />
        <StatCard
          label="Evidence Events"
          value={data.timeline_summary.returned_events}
          tone={data.timeline_summary.returned_events > 0 ? "info" : "warning"}
        />
      </div>

      <div className="rounded-md border border-blue-100 bg-blue-50/70 p-4">
        <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <StatusBadge
                label={record.is_open ? "Open" : "Closed"}
                variant={record.is_open ? "info" : "success"}
              />
              <StatusBadge label={humanizeLabel(record.status)} variant="info" />
              <StatusBadge
                label={humanizeLabel(record.drying_stage)}
                variant={record.drying_stage ? "info" : "warning"}
              />
            </div>
            <h3 className="mt-3 text-sm font-semibold text-[#162033]">
              Water Emergency {compactId(record.water_emergency_id)}
            </h3>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              {record.next_required_action ?? "No next action recorded"}
            </p>
            <div className="mt-3 flex flex-wrap gap-2 text-xs font-semibold text-slate-600">
              <ReferenceChip label={`Job ${compactId(record.job_id)}`} />
              {record.related_visit_ids.slice(0, 4).map((visitId) => (
                <ReferenceChip key={visitId} label={`Visit ${compactId(visitId)}`} />
              ))}
              {record.related_work_order_ids.slice(0, 4).map((workOrderId) => (
                <ReferenceChip
                  key={workOrderId}
                  label={`Work order ${compactId(workOrderId)}`}
                />
              ))}
            </div>
          </div>
          <div className="text-sm leading-6 text-slate-600">
            <div>
              Opened{" "}
              {record.opened_at ? formatDateTime(record.opened_at) : "not recorded"}
            </div>
            <div>
              Closed{" "}
              {record.closed_at ? formatDateTime(record.closed_at) : "not recorded"}
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <ReferencePanel title="Related Job">
          {data.job ? (
            <div className="space-y-2 text-sm leading-6 text-slate-600">
              <ReferenceLine label="Job" value={compactId(data.job.job_id)} />
              <ReferenceLine label="Type" value={humanizeLabel(data.job.job_type)} />
              <ReferenceLine label="Status" value={humanizeLabel(data.job.status)} />
              <ReferenceLine label="Priority" value={humanizeLabel(data.job.priority)} />
              <ReferenceLine
                label="Source"
                value={data.job.source_system ?? "Not recorded"}
              />
            </div>
          ) : (
            <EmptyDetailText label="No related job reference returned." />
          )}
        </ReferencePanel>

        <ReferencePanel title="Related Work Orders">
          {data.work_orders.length > 0 ? (
            <div className="space-y-3">
              {data.work_orders.map((workOrder) => (
                <WorkOrderReference key={workOrder.work_order_id} workOrder={workOrder} />
              ))}
            </div>
          ) : (
            <EmptyDetailText label="No related work order reference returned." />
          )}
        </ReferencePanel>
      </div>

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <ReferencePanel title="Related Visits">
          {data.visits.length > 0 ? (
            <div className="space-y-3">
              {data.visits.map((visit) => (
                <VisitReference key={visit.visit_id} visit={visit} />
              ))}
            </div>
          ) : (
            <EmptyDetailText label="No related visit reference returned." />
          )}
        </ReferencePanel>

        <ReferencePanel title="Scoped Manual Review">
          {data.review_indicators.length > 0 ? (
            <div className="space-y-3">
              {data.review_indicators.map((review) => (
                <ReviewReference key={review.review_item_id} review={review} />
              ))}
            </div>
          ) : (
            <EmptyDetailText label="No scoped Manual Review indicator returned." />
          )}
        </ReferencePanel>
      </div>

      <div className="grid gap-4 xl:grid-cols-[minmax(0,0.8fr)_minmax(0,1.2fr)]">
        <CountBucketPanel title="Detail Unknowns And Gaps" buckets={data.data_gap_counts} />

        <div className="rounded-md border border-slate-200 bg-slate-50/70 p-4">
          <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <h3 className="text-sm font-semibold text-[#162033]">
              Evidence Timeline
            </h3>
            <span className="text-sm font-semibold text-slate-600">
              {formatCount(data.timeline_summary.returned_events)} events
            </span>
          </div>
          <TimelineList entries={data.timeline_summary.entries} />
        </div>
      </div>
    </div>
  );
}

function ReferencePanel({
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

function WorkOrderReference({
  workOrder
}: {
  workOrder: WaterEmergencyWorkOrderReferenceResponse;
}) {
  return (
    <div className="rounded-md border border-slate-200 bg-white p-3">
      <div className="flex flex-wrap items-center gap-2">
        <StatusBadge label={humanizeLabel(workOrder.status)} variant="info" />
        {workOrder.dispatch_status ? (
          <StatusBadge
            label={humanizeLabel(workOrder.dispatch_status)}
            variant="neutral"
          />
        ) : null}
      </div>
      <div className="mt-3 text-sm font-semibold text-[#162033]">
        {workOrder.work_order_number ?? `Work order ${compactId(workOrder.work_order_id)}`}
      </div>
      <div className="mt-2 break-all text-xs font-medium text-slate-500">
        Audit {workOrder.audit_correlation_id ?? "not recorded"}
      </div>
    </div>
  );
}

function VisitReference({ visit }: { visit: WaterEmergencyVisitReferenceResponse }) {
  return (
    <div className="rounded-md border border-slate-200 bg-white p-3">
      <div className="flex flex-wrap items-center gap-2">
        <StatusBadge label={humanizeLabel(visit.status)} variant="warning" />
        <StatusBadge label={humanizeLabel(visit.visit_type)} variant="info" />
      </div>
      <div className="mt-3 text-sm font-semibold text-[#162033]">
        Visit {compactId(visit.visit_id)}
      </div>
      <div className="mt-2 text-sm leading-6 text-slate-600">
        Scheduled{" "}
        {visit.scheduled_start_at
          ? formatDateTime(visit.scheduled_start_at)
          : "not recorded"}
      </div>
      <div className="mt-2 break-all text-xs font-medium text-slate-500">
        Audit {visit.audit_correlation_id ?? "not recorded"}
      </div>
    </div>
  );
}

function ReviewReference({
  review
}: {
  review: WaterEmergencyReviewIndicatorResponse;
}) {
  return (
    <div className="rounded-md border border-slate-200 bg-white p-3">
      <div className="flex flex-wrap items-center gap-2">
        <StatusBadge label={humanizeLabel(review.status)} variant="warning" />
        <StatusBadge label={humanizeLabel(review.severity)} variant="danger" />
      </div>
      <div className="mt-3 text-sm font-semibold text-[#162033]">
        {humanizeLabel(review.reason_code)}
      </div>
      <p className="mt-2 text-sm leading-6 text-slate-600">
        {review.recommended_action ?? "No recommended action recorded"}
      </p>
      <div className="mt-2 flex flex-wrap gap-2 text-xs font-semibold text-slate-500">
        <ReferenceChip label={`Review ${compactId(review.review_item_id)}`} />
        {review.visit_id ? (
          <ReferenceChip label={`Visit ${compactId(review.visit_id)}`} />
        ) : null}
      </div>
    </div>
  );
}

function ReferenceLine({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3">
      <span className="font-semibold text-slate-500">{label}</span>
      <span className="break-all text-right text-[#162033]">{value}</span>
    </div>
  );
}

function ReferenceChip({ label }: { label: string }) {
  return (
    <span className="rounded-md border border-slate-200 bg-white px-2 py-1">
      {label}
    </span>
  );
}

function EmptyDetailText({ label }: { label: string }) {
  return <div className="text-sm leading-6 text-slate-500">{label}</div>;
}
