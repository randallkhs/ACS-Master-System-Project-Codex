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
    <ol className="space-y-4">
      {entries.map((entry) => (
        <li
          key={`${entry.audit_correlation_id}-${entry.occurred_at}-${entry.entity_id}`}
          className="border-l-2 border-slate-200 pl-4"
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
              <div className="mt-2 text-xs font-medium text-slate-500">
                Audit correlation: {entry.audit_correlation_id}
              </div>
            </div>
            <time className="text-sm text-slate-500" dateTime={entry.occurred_at}>
              {formatDateTime(entry.occurred_at)}
            </time>
          </div>
        </li>
      ))}
    </ol>
  );
}
