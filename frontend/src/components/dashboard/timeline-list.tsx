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
      {entries.map((entry) => (
        <li
          key={`${entry.audit_correlation_id}-${entry.occurred_at}-${entry.entity_id}`}
          className="rounded-md border border-slate-200 bg-slate-50/70 p-4"
        >
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <StatusBadge
                  label={humanizeLabel(entry.event_type)}
                  variant={badgeVariantForLabel(entry.event_type)}
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
              <div className="mt-2 font-mono text-xs font-medium text-slate-500">
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
