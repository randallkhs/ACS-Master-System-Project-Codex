import { DashboardView } from "@/components/dashboard/dashboard-view";
import {
  getDashboardOverview,
  getDashboardWaterEmergencyDetail,
  getDashboardWaterEmergency
} from "@/lib/dashboard-api";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export default async function DashboardPage() {
  const [dashboardResult, waterEmergencyResult] = await Promise.all([
    getDashboardOverview(),
    getDashboardWaterEmergency()
  ]);
  const selectedWaterEmergencyId =
    waterEmergencyResult.data.records.find((record) => record.is_open)
      ?.water_emergency_id ??
    waterEmergencyResult.data.records[0]?.water_emergency_id ??
    null;
  const waterEmergencyDetailResult = await getDashboardWaterEmergencyDetail(
    selectedWaterEmergencyId
  );

  return (
    <DashboardView
      result={dashboardResult}
      waterEmergencyResult={waterEmergencyResult}
      waterEmergencyDetailResult={waterEmergencyDetailResult}
    />
  );
}
