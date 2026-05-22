import type { ReactNode } from "react";
import type {
  DashboardFetchResult,
  WaterEmergencyAgingFollowUpItemResponse,
  WaterEmergencyDashboardResponse,
  WaterEmergencyNextStepReadinessResponse,
  WaterEmergencyQueueItemResponse
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
  const reviewException = data.review_exception_summary;
  const nextStep = data.next_step_summary;
  const operatorQueue = data.operator_queue_summary;
  const agingFollowup = data.aging_followup_summary;
  const activeQueueItems = operatorQueue.items.filter(
    (item) => item.queue_group !== "closed_or_resolved"
  );
  const closedQueueItems = operatorQueue.items.filter(
    (item) => item.queue_group === "closed_or_resolved"
  );
  const visibleActiveQueueItems = activeQueueItems.slice(0, 6);
  const hiddenActiveQueueItemCount =
    activeQueueItems.length - visibleActiveQueueItems.length;
  const activeTimingItems = agingFollowup.items.filter(
    (item) => item.timing_group !== "closed_or_resolved"
  );
  const closedTimingItems = agingFollowup.items.filter(
    (item) => item.timing_group === "closed_or_resolved"
  );
  const visibleActiveTimingItems = activeTimingItems.slice(0, 6);
  const hiddenActiveTimingItemCount =
    activeTimingItems.length - visibleActiveTimingItems.length;

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

        <VisibilityPanel title="Operator Queue">
          <div className="flex flex-col gap-4 xl:flex-row xl:items-start">
            <div className="grid gap-2 sm:grid-cols-2 xl:w-[22rem] xl:shrink-0">
              <RecordMetric
                label="Active"
                value={operatorQueue.active_attention_count}
              />
              <RecordMetric
                label="Critical"
                value={operatorQueue.critical_attention_count}
              />
              <RecordMetric
                label="Closed"
                value={operatorQueue.closed_or_resolved_count}
              />
              <RecordMetric
                label="Groups"
                value={operatorQueue.queue_group_counts.length}
              />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap gap-2">
                <StatusBadge label="Read-only triage visibility" variant="info" />
                <StatusBadge label="Separated from standard dispatch" variant="info" />
              </div>
              <div className="mt-4">
                <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                  Active attention records
                </div>
                {visibleActiveQueueItems.length > 0 ? (
                  <div className="mt-2 grid gap-3 xl:grid-cols-2">
                    {visibleActiveQueueItems.map((item) => (
                      <OperatorQueueItemCard
                        key={item.water_emergency_id}
                        item={item}
                      />
                    ))}
                  </div>
                ) : (
                  <p className="mt-2 text-sm leading-6 text-slate-500">
                    No active attention queue records returned.
                  </p>
                )}
                {hiddenActiveQueueItemCount > 0 ? (
                  <p className="mt-3 text-sm leading-6 text-slate-500">
                    Showing first {visibleActiveQueueItems.length} active attention
                    records.
                  </p>
                ) : null}
              </div>
              {closedQueueItems.length > 0 ? (
                <div className="mt-5">
                  <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                    Closed or resolved records
                  </div>
                  <div className="mt-2 grid gap-3 xl:grid-cols-2">
                    {closedQueueItems.map((item) => (
                      <OperatorQueueItemCard
                        key={item.water_emergency_id}
                        item={item}
                      />
                    ))}
                  </div>
                </div>
              ) : (
                <p className="mt-5 text-sm leading-6 text-slate-500">
                  No closed or resolved queue records returned.
                </p>
              )}
              <div className="mt-4 grid gap-3 md:grid-cols-2">
                <div>
                  <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                    Queue groups
                  </div>
                  <BucketPills buckets={operatorQueue.queue_group_counts} />
                </div>
                <div>
                  <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                    Attention labels
                  </div>
                  <BucketPills buckets={operatorQueue.attention_label_counts} />
                </div>
              </div>
            </div>
          </div>
        </VisibilityPanel>

        <VisibilityPanel title="Aging & Follow-Up Risk">
          <div className="flex flex-col gap-4 xl:flex-row xl:items-start">
            <div className="grid gap-2 sm:grid-cols-2 xl:w-[22rem] xl:shrink-0">
              <RecordMetric
                label="Active Risk"
                value={agingFollowup.active_timing_risk_count}
              />
              <RecordMetric label="Due" value={agingFollowup.followup_due_count} />
              <RecordMetric
                label="Overdue"
                value={agingFollowup.followup_overdue_count}
              />
              <RecordMetric label="Stale" value={agingFollowup.stale_evidence_count} />
              <RecordMetric
                label="Unknown"
                value={agingFollowup.unknown_timing_count}
              />
              <RecordMetric
                label="Closed"
                value={agingFollowup.closed_or_resolved_count}
              />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap gap-2">
                <StatusBadge label="Read-only timing visibility" variant="info" />
                <StatusBadge label="Not an SLA engine" variant="warning" />
                <StatusBadge label="No workflow execution" variant="info" />
              </div>
              <div className="mt-4">
                <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                  Active timing risks
                </div>
                {visibleActiveTimingItems.length > 0 ? (
                  <div className="mt-2 grid gap-3 xl:grid-cols-2">
                    {visibleActiveTimingItems.map((item) => (
                      <AgingFollowUpItemCard
                        key={item.water_emergency_id}
                        item={item}
                      />
                    ))}
                  </div>
                ) : (
                  <p className="mt-2 text-sm leading-6 text-slate-500">
                    No active aging or follow-up risk records returned.
                  </p>
                )}
                {hiddenActiveTimingItemCount > 0 ? (
                  <p className="mt-3 text-sm leading-6 text-slate-500">
                    Showing first {visibleActiveTimingItems.length} active timing
                    records.
                  </p>
                ) : null}
              </div>
              {closedTimingItems.length > 0 ? (
                <div className="mt-5">
                  <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                    Closed or resolved timing records
                  </div>
                  <div className="mt-2 grid gap-3 xl:grid-cols-2">
                    {closedTimingItems.map((item) => (
                      <AgingFollowUpItemCard
                        key={item.water_emergency_id}
                        item={item}
                      />
                    ))}
                  </div>
                </div>
              ) : (
                <p className="mt-5 text-sm leading-6 text-slate-500">
                  No closed or resolved timing records returned.
                </p>
              )}
              <div className="mt-4 grid gap-3 md:grid-cols-3">
                <div>
                  <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                    Time labels
                  </div>
                  <BucketPills buckets={agingFollowup.label_counts} />
                </div>
                <div>
                  <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                    Age buckets
                  </div>
                  <BucketPills buckets={agingFollowup.age_bucket_counts} />
                </div>
                <div>
                  <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                    Follow-up buckets
                  </div>
                  <BucketPills buckets={agingFollowup.followup_bucket_counts} />
                </div>
              </div>
            </div>
          </div>
        </VisibilityPanel>

        <div className="grid gap-4 xl:grid-cols-3">
          <VisibilityPanel title="Next-Step Readiness">
            <div className="grid grid-cols-2 gap-2">
              <RecordMetric label="Records" value={nextStep.total_records} />
              <RecordMetric
                label="Needs Attention"
                value={nextStep.needs_attention_count}
              />
              <RecordMetric
                label="Closed"
                value={nextStep.closed_without_active_action_count}
              />
              <RecordMetric label="Labels" value={nextStep.label_counts.length} />
            </div>
            <div className="mt-4 text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Readiness labels
            </div>
            <BucketPills buckets={nextStep.label_counts} />
            <div className="mt-4 text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Readiness blockers
            </div>
            <BucketPills buckets={nextStep.blocker_counts} />
            <div className="mt-4 space-y-2">
              {nextStep.records.slice(0, 3).map((record) => (
                <ReadinessSummaryCard key={record.water_emergency_id} record={record} />
              ))}
            </div>
          </VisibilityPanel>

          <VisibilityPanel title="Review Exception Visibility">
            <div className="grid grid-cols-2 gap-2">
              <RecordMetric label="Open" value={reviewException.open_review_count} />
              <RecordMetric
                label="Deferred"
                value={reviewException.deferred_review_count}
              />
              <RecordMetric
                label="Resolved"
                value={reviewException.resolved_review_count}
              />
              <RecordMetric
                label="Archived"
                value={reviewException.archived_review_count}
              />
            </div>
            <BucketPills buckets={reviewException.review_reason_counts} />
          </VisibilityPanel>

          <VisibilityPanel title="Critical Alerts">
            <div className="grid grid-cols-2 gap-2">
              <RecordMetric
                label="Critical"
                value={reviewException.critical_unresolved_count}
              />
              <RecordMetric
                label="Escalation"
                value={reviewException.escalation_indicator_count}
              />
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              <StatusBadge
                label="Read-only alert visibility"
                variant={
                  reviewException.critical_unresolved_count > 0 ? "danger" : "success"
                }
              />
              {reviewException.review_item_ids.slice(0, 3).map((reviewId) => (
                <span
                  key={reviewId}
                  className="rounded-md border border-slate-200 bg-white px-2 py-1 text-xs font-semibold text-slate-600"
                >
                  Review {compactId(reviewId)}
                </span>
              ))}
            </div>
          </VisibilityPanel>

          <VisibilityPanel title="Blocker Unknowns">
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Blocker reasons
            </div>
            <BucketPills buckets={reviewException.blocker_reason_counts} />
            <div className="mt-4 text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
              Unknown signals
            </div>
            <BucketPills buckets={reviewException.unknown_counts} />
          </VisibilityPanel>
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

function AgingFollowUpItemCard({
  item
}: {
  item: WaterEmergencyAgingFollowUpItemResponse;
}) {
  const latestEvidenceAt = latestVisibleEvidenceDate(item);

  return (
    <article className="rounded-md border border-slate-200 bg-white p-3">
      <div className="flex flex-wrap items-center gap-2">
        <StatusBadge
          label={humanizeLabel(item.time_sensitivity_label)}
          variant={timingVariant(item.time_sensitivity_label)}
        />
        <StatusBadge label={humanizeLabel(item.timing_group)} variant="info" />
      </div>
      <p className="mt-2 text-sm leading-6 text-slate-600">{item.summary}</p>
      <div className="mt-3 grid grid-cols-2 gap-2 text-xs font-semibold text-slate-600 sm:grid-cols-4">
        <TimingMetric label="Age" value={formatNullableHours(item.age_hours)} />
        <TimingMetric
          label="Last Visit"
          value={formatNullableHours(item.hours_since_last_visit)}
        />
        <TimingMetric
          label="Last Review"
          value={formatNullableHours(item.hours_since_last_review)}
        />
        <TimingMetric
          label="Last Event"
          value={formatNullableHours(item.hours_since_last_event)}
        />
      </div>
      <div className="mt-3 grid gap-2 text-xs font-semibold text-slate-500 sm:grid-cols-2">
        <span className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1">
          Age {humanizeLabel(item.age_bucket)}
        </span>
        <span className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1">
          Follow-up {humanizeLabel(item.followup_bucket)}
        </span>
        <span className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1">
          Opened {item.opened_at ? formatDateTime(item.opened_at) : "not recorded"}
        </span>
        <span className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1">
          Last Evidence{" "}
          {latestEvidenceAt ? formatDateTime(latestEvidenceAt) : "not recorded"}
        </span>
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
      </div>
      {item.reason_codes.length > 0 ? (
        <div className="mt-3">
          <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
            Timing evidence
          </div>
          <div className="mt-2 flex flex-wrap gap-2">
            {item.reason_codes.slice(0, 4).map((reason) => (
              <span
                key={reason}
                className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1 text-xs font-semibold text-slate-600"
              >
                {humanizeLabel(reason)}
              </span>
            ))}
          </div>
        </div>
      ) : null}
      {item.missing_timestamp_indicators.length > 0 ? (
        <div className="mt-3 flex flex-wrap gap-2">
          {item.missing_timestamp_indicators.map((indicator) => (
            <StatusBadge
              key={indicator}
              label={humanizeLabel(indicator)}
              variant="warning"
            />
          ))}
        </div>
      ) : null}
    </article>
  );
}

function OperatorQueueItemCard({ item }: { item: WaterEmergencyQueueItemResponse }) {
  return (
    <article className="rounded-md border border-slate-200 bg-white p-3">
      <div className="flex flex-wrap items-center gap-2">
        <StatusBadge
          label={humanizeLabel(item.attention_label)}
          variant={attentionVariant(item.attention_label)}
        />
        <StatusBadge label={humanizeLabel(item.queue_group)} variant="info" />
      </div>
      <p className="mt-2 text-sm leading-6 text-slate-600">{item.summary}</p>
      <div className="mt-3 grid grid-cols-2 gap-2 text-xs font-semibold text-slate-600 sm:grid-cols-4">
        <RecordMetric label="Reviews" value={item.open_review_count} />
        <RecordMetric label="Critical" value={item.critical_alert_count} />
        <RecordMetric label="Blocked" value={item.blocker_count} />
        <RecordMetric label="Unknown" value={item.unknown_count} />
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
      </div>
      <div className="mt-3">
        <div className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
          Reasons
        </div>
        <div className="mt-2 flex flex-wrap gap-2">
          {item.reason_codes.slice(0, 4).map((reason) => (
            <span
              key={reason}
              className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1 text-xs font-semibold text-slate-600"
            >
              {humanizeLabel(reason)}
            </span>
          ))}
        </div>
      </div>
    </article>
  );
}

function ReadinessSummaryCard({
  record
}: {
  record: WaterEmergencyNextStepReadinessResponse;
}) {
  return (
    <div className="rounded-md border border-slate-200 bg-white p-3">
      <div className="flex flex-wrap items-center gap-2">
        <StatusBadge
          label={humanizeLabel(record.primary_label)}
          variant={record.requires_operator_attention ? "warning" : "success"}
        />
        <StatusBadge label={humanizeLabel(record.current_status)} variant="info" />
      </div>
      <p className="mt-2 text-sm leading-6 text-slate-600">{record.summary}</p>
      <div className="mt-2 flex flex-wrap gap-2 text-xs font-semibold text-slate-500">
        <span className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1">
          Water Emergency {compactId(record.water_emergency_id)}
        </span>
        <span className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1">
          Reviews {formatCount(record.open_review_count)}
        </span>
        <span className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1">
          Unknowns {formatCount(record.unknown_count)}
        </span>
      </div>
    </div>
  );
}

function attentionVariant(label: string) {
  if (label === "critical_attention") return "danger";
  if (label === "closed_or_resolved" || label === "monitoring") return "success";
  if (label === "ready_for_close_review") return "info";
  return "warning";
}

function timingVariant(label: string) {
  if (label === "followup_overdue" || label === "stale_evidence") return "danger";
  if (label === "followup_due" || label === "waiting_for_review") return "warning";
  if (label === "closed_or_resolved" || label === "active_monitoring") return "success";
  if (label === "newly_opened" || label === "ready_for_close_review") return "info";
  return "warning";
}

function latestVisibleEvidenceDate(item: WaterEmergencyAgingFollowUpItemResponse) {
  return item.last_event_at ?? item.last_review_at ?? item.last_visit_at;
}

function formatNullableHours(value: number | null) {
  return value === null ? "Not recorded" : `${formatCount(value)}h`;
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

function TimingMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-14 rounded-md border border-slate-200 bg-white px-2 py-2">
      <div className="text-sm font-semibold leading-5 text-[#162033]">{value}</div>
      <div className="mt-1 leading-4">{label}</div>
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
