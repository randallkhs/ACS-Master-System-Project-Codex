import { DashboardView } from "@/components/dashboard/dashboard-view";
import {
  getDashboardOverview,
  getDashboardWaterEmergency
} from "@/lib/dashboard-api";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export default async function DashboardPage() {
  const [dashboardResult, waterEmergencyResult] = await Promise.all([
    getDashboardOverview(),
    getDashboardWaterEmergency()
  ]);

  return (
    <DashboardView
      result={dashboardResult}
      waterEmergencyResult={waterEmergencyResult}
    />
  );
}
