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
  neutral: "bg-slate-400",
  good: "bg-emerald-500",
  warning: "bg-amber-500",
  danger: "bg-rose-500",
  info: "bg-blue-500"
};

export function StatCard({
  label,
  value,
  detail,
  tone = "neutral"
}: StatCardProps) {
  return (
    <article
      className={`min-h-32 rounded-md border p-4 shadow-sm ${toneClasses[tone]}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="text-sm font-medium leading-5 text-slate-600">{label}</div>
        <span
          className={`mt-1 h-2.5 w-2.5 shrink-0 rounded-full ${markerClasses[tone]}`}
          aria-hidden="true"
        />
      </div>
      <div className="mt-4 text-3xl font-semibold tracking-normal text-[#162033]">
        {formatCount(value)}
      </div>
      {detail ? (
        <div className="mt-2 text-sm leading-5 text-slate-500">{detail}</div>
      ) : null}
    </article>
  );
}
