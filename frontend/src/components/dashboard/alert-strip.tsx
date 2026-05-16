import type { ReactNode } from "react";

type AlertStripProps = {
  title: string;
  children: ReactNode;
  tone?: "info" | "warning";
};

const toneClasses = {
  info: "border-blue-200 bg-blue-50 text-blue-950",
  warning: "border-amber-200 bg-amber-50 text-amber-950"
};

export function AlertStrip({
  title,
  children,
  tone = "info"
}: AlertStripProps) {
  return (
    <section className={`rounded-md border px-4 py-3 shadow-sm ${toneClasses[tone]}`}>
      <div className="font-semibold">{title}</div>
      <div className="mt-1 text-sm leading-6">{children}</div>
    </section>
  );
}
