import type { ReactNode } from "react";

type SectionCardProps = {
  title: string;
  description?: string;
  children: ReactNode;
  id?: string;
};

export function SectionCard({
  title,
  description,
  children,
  id
}: SectionCardProps) {
  return (
    <section
      id={id}
      className="scroll-mt-[26rem] rounded-md border border-slate-200 bg-white p-5 shadow-sm ring-1 ring-black/[0.02] sm:scroll-mt-44"
    >
      <div className="mb-5">
        <h2 className="text-lg font-semibold tracking-normal text-[#162033]">
          {title}
        </h2>
        {description ? (
          <p className="mt-1 text-sm leading-6 text-slate-600">{description}</p>
        ) : null}
      </div>
      {children}
    </section>
  );
}
