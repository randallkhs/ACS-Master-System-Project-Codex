import { formatCount } from "@/lib/format";

type StatCardTone = "neutral" | "good" | "warning" | "danger" | "info";

type StatCardProps = {
  label: string;
  value: number;
  detail?: string;
  tone?: StatCardTone;
};

const toneClasses: Record<StatCardTone, string> = {
  neutral: "border-slate-200 bg-white",
  good: "border-emerald-200 bg-white",
  warning: "border-amber-200 bg-white",
  danger: "border-rose-200 bg-white",
  info: "border-blue-200 bg-white"
};

const markerClasses: Record<StatCardTone, string> = {
  neutral: "from-slate-400 to-slate-500",
  good: "from-emerald-400 to-emerald-600",
  warning: "from-amber-400 to-amber-600",
  danger: "from-rose-400 to-rose-600",
  info: "from-blue-400 to-blue-600"
};

export function StatCard({
  label,
  value,
  detail,
  tone = "neutral"
}: StatCardProps) {
  return (
    <article
      className={`relative min-h-32 overflow-hidden rounded-md border p-4 shadow-sm ring-1 ring-black/[0.02] ${toneClasses[tone]}`}
    >
      <span
        className={`absolute inset-x-0 top-0 h-1 bg-gradient-to-r ${markerClasses[tone]}`}
        aria-hidden="true"
      />
      <div className="flex items-start justify-between gap-3">
        <div className="text-sm font-semibold leading-5 text-slate-700">{label}</div>
        <span
          className={`mt-1 h-2.5 w-2.5 shrink-0 rounded-full bg-gradient-to-br ${markerClasses[tone]}`}
          aria-hidden="true"
        />
      </div>
      <div className="mt-4 text-[2rem] font-semibold leading-none tracking-normal text-[#162033]">
        {formatCount(value)}
      </div>
      {detail ? (
        <div className="mt-3 text-sm leading-5 text-slate-600">{detail}</div>
      ) : null}
    </article>
  );
}
