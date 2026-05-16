type SectionHeadingProps = {
  id: string;
  label: string;
  title: string;
  description: string;
};

export function SectionHeading({
  id,
  label,
  title,
  description
}: SectionHeadingProps) {
  return (
    <div id={id} className="scroll-mt-36">
      <div className="text-xs font-semibold uppercase tracking-[0.16em] text-[#2563eb]">
        {label}
      </div>
      <h2 className="mt-2 text-xl font-semibold tracking-normal text-[#162033]">
        {title}
      </h2>
      <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
        {description}
      </p>
    </div>
  );
}
