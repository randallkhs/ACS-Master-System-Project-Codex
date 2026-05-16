import type { CountBucket } from "@/lib/dashboard-contracts";
import { formatCount, humanizeLabel } from "@/lib/format";
import {
  badgeVariantForLabel,
  type StatusBadgeVariant,
  StatusBadge
} from "@/components/dashboard/status-badge";

type CountBucketPanelProps = {
  title: string;
  buckets: CountBucket[];
};

export function CountBucketPanel({ title, buckets }: CountBucketPanelProps) {
  const largestCount = Math.max(...buckets.map((bucket) => bucket.count), 1);

  return (
    <article className="rounded-md border border-slate-200 bg-white p-4 shadow-sm ring-1 ring-black/[0.02]">
      <h3 className="text-sm font-semibold text-[#162033]">{title}</h3>
      <div className="mt-4 space-y-2.5">
        {buckets.length > 0 ? (
          buckets.map((bucket) => {
            const width = `${Math.max((bucket.count / largestCount) * 100, 6)}%`;
            const variant = badgeVariantForLabel(bucket.label);

            return (
              <div
                key={`${title}-${bucket.label}`}
                className="rounded-md border border-slate-100 bg-slate-50/70 p-2.5"
              >
                <div className="flex items-center justify-between gap-3">
                  <StatusBadge
                    label={humanizeLabel(bucket.label)}
                    variant={variant}
                  />
                  <span className="text-sm font-semibold text-slate-700">
                    {formatCount(bucket.count)}
                  </span>
                </div>
                <div className="mt-2 h-2 rounded-full bg-white shadow-inner">
                  <div
                    className={`h-2 rounded-full ${barClassForVariant(variant)}`}
                    style={{ width }}
                    aria-hidden="true"
                  />
                </div>
              </div>
            );
          })
        ) : (
          <div className="rounded-md border border-dashed border-slate-300 bg-slate-50 px-3 py-4 text-sm text-slate-600">
            No persisted counts returned.
          </div>
        )}
      </div>
    </article>
  );
}

function barClassForVariant(variant: StatusBadgeVariant): string {
  const barClasses: Record<StatusBadgeVariant, string> = {
    neutral: "bg-slate-400",
    success: "bg-emerald-500",
    warning: "bg-amber-500",
    danger: "bg-rose-500",
    info: "bg-blue-500"
  };

  return barClasses[variant];
}
