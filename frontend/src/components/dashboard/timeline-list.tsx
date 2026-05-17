import type { OperationalTimelineEntryResponse } from "@/lib/dashboard-contracts";
import { compactId, formatDateTime, humanizeLabel } from "@/lib/format";
import {
  badgeVariantForLabel,
  StatusBadge
} from "@/components/dashboard/status-badge";

type TimelineListProps = {
  entries: OperationalTimelineEntryResponse[];
};

export function TimelineList({ entries }: TimelineListProps) {
  if (entries.length === 0) {
    return <div className="text-sm text-slate-500">No event evidence returned.</div>;
  }

  return (
    <ol className="space-y-3">
      {entries.map((entry, index) => (
        <li
          key={`${entry.audit_correlation_id}-${entry.occurred_at}-${entry.entity_id}`}
          className="rounded-md border border-slate-200 bg-slate-50/70 p-4"
        >
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <span className="inline-flex min-h-7 items-center rounded-md border border-slate-200 bg-white px-2.5 py-1 text-xs font-semibold text-slate-600">
                  {String(index + 1).padStart(2, "0")}
                </span>
                <StatusBadge
                  label={humanizeLabel(entry.event_type)}
                  variant={badgeVariantForLabel(entry.event_type)}
                />
                <StatusBadge
                  label={humanizeLabel(entry.event_state)}
                  variant={badgeVariantForLabel(entry.event_state)}
                />
                <StatusBadge
                  label={entry.is_immutable ? "Immutable" : "Mutable"}
                  variant={entry.is_immutable ? "success" : "danger"}
                />
              </div>
              <div className="mt-3 text-sm font-semibold text-[#162033]">
                {humanizeLabel(entry.entity_type)} {compactId(entry.entity_id)}
              </div>
              <div className="mt-1 text-sm leading-6 text-slate-600">
                {humanizeLabel(entry.previous_state)} to{" "}
                {humanizeLabel(entry.new_state)}
              </div>
              <div className="mt-3 flex flex-wrap gap-2 text-xs font-semibold text-slate-500">
                {relatedRecordLabels(entry).map((label) => (
                  <span
                    key={`${entry.audit_correlation_id}-${label}`}
                    className="rounded-md border border-slate-200 bg-white px-2 py-1"
                  >
                    {label}
                  </span>
                ))}
              </div>
              <div className="mt-2 break-all font-mono text-xs font-medium text-slate-500">
                Audit correlation: {entry.audit_correlation_id}
              </div>
            </div>
            <time
              className="shrink-0 rounded-md bg-white px-2.5 py-1.5 text-sm font-medium text-slate-600 ring-1 ring-slate-200"
              dateTime={entry.occurred_at}
            >
              {formatDateTime(entry.occurred_at)}
            </time>
          </div>
        </li>
      ))}
    </ol>
  );
}

function relatedRecordLabels(entry: OperationalTimelineEntryResponse): string[] {
  return [
    entry.route_assignment_id ? `Route ${compactId(entry.route_assignment_id)}` : null,
    entry.visit_id ? `Visit ${compactId(entry.visit_id)}` : null,
    entry.work_order_id ? `Work order ${compactId(entry.work_order_id)}` : null,
    entry.job_id ? `Job ${compactId(entry.job_id)}` : null,
    entry.technician_id ? `Tech ${compactId(entry.technician_id)}` : null
  ].filter((label): label is string => label !== null);
}
