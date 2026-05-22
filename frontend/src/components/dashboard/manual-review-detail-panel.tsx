import type {
  DashboardFetchResult,
  ManualReviewDetailResponse
} from "@/lib/dashboard-contracts";
import { compactId, formatDateTime, humanizeLabel } from "@/lib/format";
import { CountBucketPanel } from "@/components/dashboard/count-bucket-panel";
import { SectionCard } from "@/components/dashboard/section-card";
import { SectionHeading } from "@/components/dashboard/section-heading";
import {
  badgeVariantForLabel,
  StatusBadge
} from "@/components/dashboard/status-badge";
import { TimelineList } from "@/components/dashboard/timeline-list";

type ManualReviewDetailPanelProps = {
  result?: DashboardFetchResult<ManualReviewDetailResponse | null>;
};

export function ManualReviewDetailPanel({ result }: ManualReviewDetailPanelProps) {
  if (!result) {
    return null;
  }

  const { data } = result;

  return (
    <section className="space-y-4">
      <SectionHeading
        id="manual-review-detail"
        label="Manual Review Detail"
        title="Read-only detail visibility"
        description="Focused Manual Review investigation context with linked entity, reason, and timeline evidence. This panel does not approve, reject, defer, archive, dispatch, or resolve review items."
      />

      {data ? (
        <ManualReviewDetailContent detail={data} />
      ) : (
        <SectionCard
          title="No Manual Review detail selected"
          description={
            result.errorMessage ??
            "No Manual Review record is currently selected for detail display."
          }
        >
          <div className="rounded-md border border-dashed border-slate-300 bg-slate-50 px-3 py-4 text-sm text-slate-600">
            Selectable workflow controls are intentionally absent in this Phase
            0 foundation. Detail visibility remains read-only and backend-driven.
          </div>
        </SectionCard>
      )}
    </section>
  );
}

function ManualReviewDetailContent({
  detail
}: {
  detail: ManualReviewDetailResponse;
}) {
  const { review_item: item, linked_entity_context: context } = detail;

  return (
    <div className="space-y-4">
      <SectionCard
        title="Review summary"
        description={`${humanizeLabel(item.reason_code)} is displayed as a read-only Manual Review item. Manual Review remains the safety authority for future action modules.`}
      >
        <div className="flex flex-wrap gap-2">
          <StatusBadge
            label={humanizeLabel(item.status)}
            variant={badgeVariantForLabel(item.status)}
          />
          <StatusBadge
            label={humanizeLabel(item.primary_group)}
            variant={badgeVariantForLabel(item.primary_group)}
          />
          <StatusBadge
            label={item.attention_indicator ? "Requires review" : "Historical"}
            variant={item.attention_indicator ? "warning" : "neutral"}
          />
          {context.is_water_emergency_related ? (
            <StatusBadge label="Water Emergency review detail" variant="info" />
          ) : null}
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <DetailMetric label="Severity" value={humanizeLabel(item.severity)} />
          <DetailMetric
            label="Age bucket"
            value={humanizeLabel(item.age_bucket)}
          />
          <DetailMetric
            label="Confidence"
            value={
              item.confidence_score === null
                ? "Not scored"
                : `${item.confidence_score}%`
            }
          />
          <DetailMetric
            label="Created"
            value={formatDateTime(item.created_at)}
          />
        </div>

        <p className="mt-4 text-sm leading-6 text-slate-600">
          {item.recommended_action ??
            "Read-only evidence is available for operator review."}
        </p>
      </SectionCard>

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <SectionCard
          title="Reason And Evidence Context"
          description="Reason fields and evidence references are projected from persisted review data only."
        >
          <div className="space-y-3">
            <DetailRow
              label="Reason code"
              value={humanizeLabel(detail.reason_context.reason_code)}
            />
            <DetailRow
              label="Review reason codes"
              value={
                detail.reason_context.review_reason_codes.length > 0
                  ? detail.reason_context.review_reason_codes
                      .map(humanizeLabel)
                      .join(", ")
                  : "No structured reason list returned"
              }
            />
            <DetailRow
              label="Snapshot evidence"
              value={
                detail.reason_context.snapshot_keys.length > 0
                  ? detail.reason_context.snapshot_keys.map(humanizeLabel).join(", ")
                  : "No snapshot evidence returned"
              }
            />
            <EvidenceList references={detail.reason_context.evidence_references} />
          </div>
        </SectionCard>

        <SectionCard
          title="Linked Entity Context"
          description={
            context.is_water_emergency_related
              ? "Water Emergency-related Manual Review detail is separated from standard dispatch review detail."
              : "Standard dispatch, job, work-order, visit, or route context is displayed without workflow authority."
          }
        >
          <div className="grid gap-3 sm:grid-cols-2">
            <DetailMetric
              label="Entity"
              value={`${humanizeLabel(context.entity_type)} ${compactNullableId(
                context.entity_id
              )}`}
            />
            <DetailMetric
              label="Job"
              value={`${humanizeLabel(context.job_status)} ${compactNullableId(
                context.job_id
              )}`}
            />
            <DetailMetric
              label="Work order"
              value={`${humanizeLabel(context.work_order_status)} ${compactNullableId(
                context.work_order_id
              )}`}
            />
            <DetailMetric
              label="Visit"
              value={`${humanizeLabel(context.visit_status)} ${compactNullableId(
                context.visit_id
              )}`}
            />
            <DetailMetric
              label="Route"
              value={`${humanizeLabel(
                context.route_assignment_status
              )} ${compactNullableId(context.route_assignment_id)}`}
            />
            <DetailMetric
              label="Water Emergency"
              value={`${humanizeLabel(
                context.water_emergency_status
              )} ${compactNullableId(context.water_emergency_id)}`}
            />
          </div>

          {context.unknown_indicators.length > 0 ? (
            <div className="mt-4 flex flex-wrap gap-2">
              {context.unknown_indicators.map((indicator) => (
                <StatusBadge
                  key={indicator}
                  label={humanizeLabel(indicator)}
                  variant="warning"
                />
              ))}
            </div>
          ) : null}
        </SectionCard>
      </div>

      <div className="grid gap-4 lg:grid-cols-[minmax(0,0.8fr)_minmax(0,1.2fr)]">
        <CountBucketPanel title="Detail Data Gaps" buckets={detail.data_gap_counts} />
        <SectionCard
          title="Manual Review Evidence Timeline"
          description="Timeline entries are ordered by backend read models and preserve audit correlation references."
        >
          <TimelineList entries={detail.timeline_summary.entries} />
        </SectionCard>
      </div>
    </div>
  );
}

function DetailMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2">
      <div className="text-xs font-semibold text-slate-500">{label}</div>
      <div className="mt-1 break-words text-sm font-semibold text-[#162033]">
        {value}
      </div>
    </div>
  );
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs font-semibold text-slate-500">{label}</div>
      <div className="mt-1 break-words text-sm font-semibold text-[#162033]">
        {value}
      </div>
    </div>
  );
}

function EvidenceList({ references }: { references: string[] }) {
  if (references.length === 0) {
    return (
      <div className="rounded-md border border-dashed border-slate-300 bg-slate-50 px-3 py-4 text-sm text-slate-600">
        No evidence references returned.
      </div>
    );
  }

  return (
    <div className="flex flex-wrap gap-2">
      {references.map((reference) => (
        <span
          key={reference}
          className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1 font-mono text-xs font-medium text-slate-600"
        >
          {reference}
        </span>
      ))}
    </div>
  );
}

function compactNullableId(value: string | null): string {
  return value ? compactId(value) : "Not linked";
}
