import type { ReactNode } from "react";
import type {
  CountBucket,
  DashboardFetchResult,
  WaterEmergencyDetailResponse,
  WaterEmergencyEquipmentNoteResponse,
  WaterEmergencyNextStepReadinessResponse,
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
  const reviewException = data.review_exception_context;
  const nextStep = data.next_step_readiness;

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

      <ReferencePanel title="Next-Step Readiness">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
          <div className="min-w-0">
            <div className="flex flex-wrap gap-2">
              <StatusBadge
                label={humanizeLabel(nextStep.primary_label)}
                variant={nextStep.requires_operator_attention ? "warning" : "success"}
              />
              <StatusBadge label="Read-only readiness visibility" variant="info" />
              <StatusBadge
                label={
                  nextStep.requires_operator_attention
                    ? "Operator attention"
                    : "No active workflow action"
                }
                variant={nextStep.requires_operator_attention ? "warning" : "success"}
              />
            </div>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
              {nextStep.summary}
            </p>
          </div>
          <div className="grid min-w-[16rem] grid-cols-2 gap-2">
            <DetailMetric label="Reviews" value={nextStep.open_review_count} />
            <DetailMetric label="Critical" value={nextStep.critical_alert_count} />
            <DetailMetric label="Blockers" value={nextStep.blocker_count} />
            <DetailMetric label="Unknowns" value={nextStep.unknown_count} />
          </div>
        </div>

        <div className="mt-4 grid gap-4 lg:grid-cols-3">
          <ReadinessDetailBlock title="Labels" values={nextStep.labels} />
          <ReadinessDetailBlock title="Reasons" values={nextStep.reason_codes} />
          <ReadinessDetailBlock
            title="Evidence"
            values={nextStep.evidence_references.slice(0, 8)}
          />
        </div>
      </ReferencePanel>

      <ReferencePanel title="Detail Review Exceptions">
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
          <DetailMetric label="Open" value={reviewException.open_review_count} />
          <DetailMetric label="Deferred" value={reviewException.deferred_review_count} />
          <DetailMetric label="Resolved" value={reviewException.resolved_review_count} />
          <DetailMetric label="Archived" value={reviewException.archived_review_count} />
          <DetailMetric
            label="Critical"
            value={reviewException.critical_unresolved_count}
          />
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          <StatusBadge
            label="Read-only scoped review visibility"
            variant={reviewException.total_review_count > 0 ? "warning" : "neutral"}
          />
          <StatusBadge
            label={
              reviewException.critical_unresolved_count > 0
                ? "Critical Alerts"
                : "No critical alerts"
            }
            variant={
              reviewException.critical_unresolved_count > 0 ? "danger" : "success"
            }
          />
        </div>
        <div className="mt-4 text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
          Review reasons
        </div>
        <BucketSummary buckets={reviewException.review_reason_counts} />
        <div className="mt-4 text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
          Blocker reasons
        </div>
        <BucketSummary buckets={reviewException.blocker_reason_counts} />
        <InlineTags values={reviewException.unknown_indicators} />
      </ReferencePanel>

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

      <div className="grid gap-4 xl:grid-cols-3">
        <ReferencePanel title="Detail Equipment Context">
          <div className="flex flex-wrap gap-2">
            <StatusBadge
              label={data.equipment_context.equipment_onsite ? "Equipment onsite" : "No onsite flag"}
              variant={data.equipment_context.equipment_onsite ? "warning" : "neutral"}
            />
            <StatusBadge
              label={
                data.equipment_context.moisture_tracking_required
                  ? "Moisture tracking required"
                  : "Moisture tracking not required"
              }
              variant={data.equipment_context.moisture_tracking_required ? "info" : "neutral"}
            />
            <StatusBadge
              label={
                data.equipment_context.inventory_entity_available
                  ? "Equipment inventory modeled"
                  : "Equipment inventory not modeled"
              }
              variant={
                data.equipment_context.inventory_entity_available
                  ? "success"
                  : "warning"
              }
            />
          </div>
          <div className="mt-3 space-y-2">
            {data.equipment_context.required_equipment_notes.length > 0 ? (
              data.equipment_context.required_equipment_notes.map((note) => (
                <EquipmentNote key={note.work_order_id} note={note} />
              ))
            ) : (
              <EmptyDetailText label="No required equipment notes returned." />
            )}
          </div>
          <InlineTags values={data.equipment_context.unknown_indicators} />
        </ReferencePanel>

        <ReferencePanel title="Detail Visit Chain">
          <div className="grid grid-cols-2 gap-2">
            <DetailMetric label="Visits" value={data.visit_chain.total_visits} />
            <DetailMetric label="Open" value={data.visit_chain.open_visit_count} />
            <DetailMetric
              label="Complete"
              value={data.visit_chain.completed_visit_count}
            />
            <DetailMetric
              label="Next"
              value={data.visit_chain.next_scheduled_visit_at ? 1 : 0}
            />
          </div>
          <div className="mt-3 text-sm leading-6 text-slate-600">
            First{" "}
            {data.visit_chain.first_visit_at
              ? formatDateTime(data.visit_chain.first_visit_at)
              : "not recorded"}
            <br />
            Latest{" "}
            {data.visit_chain.latest_visit_at
              ? formatDateTime(data.visit_chain.latest_visit_at)
              : "not recorded"}
          </div>
          <BucketSummary buckets={data.visit_chain.visit_status_counts} />
        </ReferencePanel>

        <ReferencePanel title="Detail Drying Stage">
          <div className="space-y-2 text-sm leading-6 text-slate-600">
            <ReferenceLine label="Status" value={humanizeLabel(data.drying_stage_context.status)} />
            <ReferenceLine
              label="Stage"
              value={humanizeLabel(data.drying_stage_context.current_stage)}
            />
            <ReferenceLine
              label="Next"
              value={data.drying_stage_context.next_required_action ?? "Not recorded"}
            />
            <ReferenceLine
              label="Moisture"
              value={
                data.drying_stage_context.moisture_tracking_required
                  ? "Required"
                  : "Not required"
              }
            />
          </div>
          <InlineTags values={data.drying_stage_context.missing_indicators} />
        </ReferencePanel>
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

function EquipmentNote({ note }: { note: WaterEmergencyEquipmentNoteResponse }) {
  return (
    <div className="rounded-md border border-slate-200 bg-white p-3">
      <div className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">
        Work order {compactId(note.work_order_id)}
      </div>
      <p className="mt-2 text-sm leading-6 text-slate-600">
        {note.required_equipment_notes}
      </p>
    </div>
  );
}

function DetailMetric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md border border-slate-200 bg-white px-2 py-2 text-center">
      <div className="text-base font-semibold leading-none text-[#162033]">
        {formatCount(value)}
      </div>
      <div className="mt-1 text-xs font-semibold leading-4 text-slate-500">
        {label}
      </div>
    </div>
  );
}

function BucketSummary({ buckets }: { buckets: CountBucket[] }) {
  if (buckets.length === 0) {
    return <EmptyDetailText label="No visit-chain status buckets returned." />;
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

function InlineTags({ values }: { values: string[] }) {
  if (values.length === 0) {
    return (
      <div className="mt-3 text-sm leading-6 text-slate-500">
        No missing context returned.
      </div>
    );
  }

  return (
    <div className="mt-3 flex flex-wrap gap-2">
      {values.map((value) => (
        <span
          key={value}
          className="rounded-md border border-amber-200 bg-amber-50 px-2 py-1 text-xs font-semibold text-amber-900"
        >
          {humanizeLabel(value)}
        </span>
      ))}
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

function ReadinessDetailBlock({
  title,
  values
}: {
  title: string;
  values: WaterEmergencyNextStepReadinessResponse["labels"];
}) {
  return (
    <div>
      <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
        {title}
      </div>
      {values.length > 0 ? (
        <div className="mt-3 flex flex-wrap gap-2">
          {values.map((value) => (
            <ReferenceChip key={`${title}-${value}`} label={humanizeLabel(value)} />
          ))}
        </div>
      ) : (
        <EmptyDetailText label="No readiness evidence returned." />
      )}
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
