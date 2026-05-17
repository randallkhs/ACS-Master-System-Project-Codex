import type { ReactNode } from "react";
import type { DashboardSource } from "@/lib/dashboard-contracts";
import { formatDateTime } from "@/lib/format";
import { StatusBadge } from "@/components/dashboard/status-badge";

type AppShellProps = {
  children: ReactNode;
  generatedAt: string;
  source: DashboardSource;
};

const navItems = [
  { label: "Storyboard", href: "#scenario-storyboard" },
  { label: "Overview", href: "#overview" },
  { label: "Lifecycle", href: "#lifecycle" },
  { label: "Manual Review", href: "#manual-review" },
  { label: "Dispatch", href: "#dispatch" },
  { label: "Execution", href: "#external-execution" },
  { label: "Recovery", href: "#recovery" },
  { label: "Governance", href: "#governance" },
  { label: "Timeline", href: "#timeline" }
];

export function AppShell({ children, generatedAt, source }: AppShellProps) {
  return (
    <div className="min-h-screen bg-[#f5f7f9] text-[#162033]">
      <a
        href="#main-content"
        className="sr-only z-50 rounded-md bg-white px-4 py-2 font-semibold text-[#162033] shadow focus:not-sr-only focus:fixed focus:left-4 focus:top-4"
      >
        Skip to dashboard content
      </a>

      <aside className="fixed inset-y-0 left-0 z-20 hidden w-[17rem] border-r border-white/10 bg-[#111827] text-white lg:block">
        <div className="flex h-full flex-col">
          <div className="border-b border-white/10 px-6 py-6">
            <div className="text-xs font-semibold uppercase tracking-[0.18em] text-[#84cc16]">
              Apple Cleaning Systems
            </div>
            <div className="mt-3 text-2xl font-semibold tracking-normal">
              ACS Master System
            </div>
            <div className="mt-2 text-sm leading-6 text-slate-300">
              Operations dashboard foundation
            </div>
          </div>

          <nav
            className="flex-1 space-y-1 px-3 py-5"
            aria-label="Dashboard sections"
          >
            {navItems.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className="block rounded-md px-3 py-2.5 text-sm font-semibold text-slate-200 transition hover:bg-white/10 hover:text-white focus-visible:outline-white"
              >
                {item.label}
              </a>
            ))}
          </nav>

          <div className="border-t border-white/10 px-6 py-5 text-xs leading-5 text-slate-300">
            <div>Database remains source of truth.</div>
            <div>Dashboard is read-only.</div>
          </div>
        </div>
      </aside>

      <div className="lg:pl-[17rem]">
        <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/95 backdrop-blur">
          <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 sm:px-6 lg:px-8">
            <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                <div className="text-xs font-semibold uppercase tracking-[0.18em] text-[#2563eb]">
                  Admin Dashboard
                </div>
                <h1 className="mt-1 text-2xl font-semibold leading-tight tracking-normal text-[#162033] sm:text-3xl">
                  Operational Control View
                </h1>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                <StatusBadge
                  label={source === "api" ? "Live backend" : "Mock fallback"}
                  variant={source === "api" ? "success" : "warning"}
                />
                <StatusBadge label="Read-only" variant="info" />
              </div>
            </div>

            <div className="flex flex-col gap-3 text-sm text-slate-600 lg:flex-row lg:items-center lg:justify-between">
              <span className="font-medium">Generated {formatDateTime(generatedAt)}</span>
              <div className="no-scrollbar grid grid-cols-2 gap-2 sm:flex sm:flex-wrap lg:hidden">
                {navItems.map((item) => (
                  <a
                    key={item.href}
                    href={item.href}
                    className="min-h-9 rounded-md border border-slate-200 bg-white px-3 py-2 text-center text-xs font-semibold text-slate-700 shadow-sm transition hover:border-blue-300 hover:text-blue-700 sm:shrink-0"
                  >
                    {item.label}
                  </a>
                ))}
              </div>
            </div>
          </div>
        </header>

        <main
          id="main-content"
          className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8"
        >
          {children}
        </main>
      </div>
    </div>
  );
}
