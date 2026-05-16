import type { CountBucket } from "@/lib/dashboard-contracts";
import { formatCount, humanizeLabel } from "@/lib/format";
import {
  badgeVariantForLabel,
  StatusBadge
} from "@/components/dashboard/status-badge";

type CountBucketPanelProps = {
  title: string;
  buckets: CountBucket[];
};

export function CountBucketPanel({ title, buckets }: CountBucketPanelProps) {
  const largestCount = Math.max(...buckets.map((bucket) => bucket.count), 1);

  return (
    <article className="rounded-md border border-slate-200 bg-white p-4 shadow-sm">
      <h3 className="text-sm font-semibold text-[#162033]">{title}</h3>
      <div className="mt-4 space-y-3">
        {buckets.length > 0 ? (
          buckets.map((bucket) => {
            const width = `${Math.max((bucket.count / largestCount) * 100, 6)}%`;

            return (
              <div key={`${title}-${bucket.label}`}>
                <div className="flex items-center justify-between gap-3">
                  <StatusBadge
                    label={humanizeLabel(bucket.label)}
                    variant={badgeVariantForLabel(bucket.label)}
                  />
                  <span className="text-sm font-semibold text-slate-700">
                    {formatCount(bucket.count)}
                  </span>
                </div>
                <div className="mt-2 h-2 rounded-full bg-slate-100">
                  <div
                    className="h-2 rounded-full bg-[#2563eb]"
                    style={{ width }}
                    aria-hidden="true"
                  />
                </div>
              </div>
            );
          })
        ) : (
          <div className="text-sm text-slate-500">No persisted counts.</div>
        )}
      </div>
    </article>
  );
}
