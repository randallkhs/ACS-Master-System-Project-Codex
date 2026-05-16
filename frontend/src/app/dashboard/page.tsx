import { DashboardView } from "@/components/dashboard/dashboard-view";
import { getDashboardOverview } from "@/lib/dashboard-api";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export default async function DashboardPage() {
  const dashboardResult = await getDashboardOverview();

  return <DashboardView result={dashboardResult} />;
}
