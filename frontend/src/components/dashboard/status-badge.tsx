export type StatusBadgeVariant =
  | "neutral"
  | "success"
  | "warning"
  | "danger"
  | "info";

type StatusBadgeProps = {
  label: string;
  variant?: StatusBadgeVariant;
};

const variantClasses: Record<StatusBadgeVariant, string> = {
  neutral: "border-slate-200 bg-slate-50 text-slate-700",
  success: "border-emerald-200 bg-emerald-50 text-emerald-800",
  warning: "border-amber-200 bg-amber-50 text-amber-900",
  danger: "border-rose-200 bg-rose-50 text-rose-800",
  info: "border-blue-200 bg-blue-50 text-blue-800"
};

const dotClasses: Record<StatusBadgeVariant, string> = {
  neutral: "bg-slate-400",
  success: "bg-emerald-500",
  warning: "bg-amber-500",
  danger: "bg-rose-500",
  info: "bg-blue-500"
};

export function StatusBadge({
  label,
  variant = "neutral"
}: StatusBadgeProps) {
  return (
    <span
      className={`inline-flex min-h-7 max-w-full items-center gap-1.5 rounded-md border px-2.5 py-1 text-left text-xs font-semibold leading-5 ${variantClasses[variant]}`}
    >
      <span
        className={`h-2 w-2 shrink-0 rounded-full ${dotClasses[variant]}`}
        aria-hidden="true"
      />
      <span className="min-w-0 break-words">{label}</span>
    </span>
  );
}

export function badgeVariantForLabel(label: string): StatusBadgeVariant {
  const normalizedLabel = label.toLowerCase();

  if (
    normalizedLabel.includes("blocked") ||
    normalizedLabel.includes("failed") ||
    normalizedLabel.includes("mismatch") ||
    normalizedLabel.includes("divergence")
  ) {
    return "danger";
  }

  if (
    normalizedLabel.includes("review") ||
    normalizedLabel.includes("pending") ||
    normalizedLabel.includes("deferred") ||
    normalizedLabel.includes("retry") ||
    normalizedLabel.includes("escalation")
  ) {
    return "warning";
  }

  if (
    normalizedLabel.includes("approved") ||
    normalizedLabel.includes("ready") ||
    normalizedLabel.includes("confirmed") ||
    normalizedLabel.includes("completed") ||
    normalizedLabel.includes("consistent") ||
    normalizedLabel.includes("executed")
  ) {
    return "success";
  }

  if (
    normalizedLabel.includes("water") ||
    normalizedLabel.includes("prepared") ||
    normalizedLabel.includes("authorized")
  ) {
    return "info";
  }

  return "neutral";
}
