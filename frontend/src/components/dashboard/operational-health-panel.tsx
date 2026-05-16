import type {
  DispatchLifecycleSummaryResponse,
  OperationalDashboardSummaryResponse
} from "@/lib/dashboard-contracts";
import { formatCount } from "@/lib/format";
import { StatusBadge } from "@/components/dashboard/status-badge";

type OperationalHealthPanelProps = {
  summary: OperationalDashboardSummaryResponse;
  lifecycle: DispatchLifecycleSummaryResponse;
};

const healthItems = [
  {
    key: "manual-review",
    label: "Manual Review open",
    description: "Items waiting for human safety review",
    value: (props: OperationalHealthPanelProps) =>
      props.summary.open_manual_reviews,
    tone: (props: OperationalHealthPanelProps) =>
      props.summary.open_manual_reviews > 0 ? "warning" : "success"
  },
  {
    key: "blocked",
    label: "Blocked operations",
    description: "Backend blocker evidence returned",
    value: (props: OperationalHealthPanelProps) =>
      props.summary.blocked_operations,
    tone: (props: OperationalHealthPanelProps) =>
      props.summary.blocked_operations > 0 ? "danger" : "success"
  },
  {
    key: "ready",
    label: "Dispatch-ready visits",
    description: "Ready state reported by backend",
    value: (props: OperationalHealthPanelProps) =>
      props.lifecycle.dispatch_ready_visits,
    tone: () => "info"
  },
  {
    key: "water",
    label: "Water Emergency",
    description: "Separated first-class workflow records",
    value: (props: OperationalHealthPanelProps) =>
      props.summary.open_water_emergencies,
    tone: (props: OperationalHealthPanelProps) =>
      props.summary.open_water_emergencies > 0 ? "info" : "neutral"
  }
] as const;

export function OperationalHealthPanel(props: OperationalHealthPanelProps) {
  const safetySignals =
    props.summary.open_manual_reviews +
    props.summary.blocked_operations +
    props.summary.escalation_indicators;

  return (
    <section
      aria-labelledby="dashboard-health-title"
      className="rounded-md border border-slate-200 bg-white p-5 shadow-sm ring-1 ring-black/[0.02]"
    >
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.16em] text-[#2563eb]">
            Operational Health
          </div>
          <h2
            id="dashboard-health-title"
            className="mt-2 text-xl font-semibold tracking-normal text-[#162033]"
          >
            Safety signals and readiness
          </h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
            This summary is a display of persisted dashboard evidence only. It
            does not approve, dispatch, reconcile, or resolve work.
          </p>
        </div>
        <StatusBadge
          label={`${formatCount(safetySignals)} open safety signals`}
          variant={safetySignals > 0 ? "warning" : "success"}
        />
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {healthItems.map((item) => {
          const tone = item.tone(props);

          return (
            <div
              key={item.key}
              className="rounded-md border border-slate-200 bg-slate-50/70 p-4"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="text-sm font-semibold text-slate-700">
                  {item.label}
                </div>
                <StatusBadge label={tone} variant={tone} />
              </div>
              <div className="mt-4 text-3xl font-semibold leading-none text-[#162033]">
                {formatCount(item.value(props))}
              </div>
              <p className="mt-3 text-sm leading-5 text-slate-600">
                {item.description}
              </p>
            </div>
          );
        })}
      </div>
    </section>
  );
}
