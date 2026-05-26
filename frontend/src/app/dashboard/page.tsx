import { DashboardView } from "@/components/dashboard/dashboard-view";
import {
  getAuthStatus,
  getDashboardManualReviewDetail,
  getDashboardManualReviewQueue,
  getDashboardOverview,
  getDashboardWaterEmergencyDetail,
  getDashboardWaterEmergency
} from "@/lib/dashboard-api";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export default async function DashboardPage() {
  const [
    dashboardResult,
    waterEmergencyResult,
    manualReviewQueueResult,
    authStatusResult
  ] =
    await Promise.all([
      getDashboardOverview(),
      getDashboardWaterEmergency(),
      getDashboardManualReviewQueue(),
      getAuthStatus()
    ]);
  const selectedWaterEmergencyId =
    waterEmergencyResult.data.records.find((record) => record.is_open)
      ?.water_emergency_id ??
    waterEmergencyResult.data.records[0]?.water_emergency_id ??
    null;
  const waterEmergencyDetailResult = await getDashboardWaterEmergencyDetail(
    selectedWaterEmergencyId
  );
  const selectedManualReviewId =
    manualReviewQueueResult.data.items.find((item) => item.attention_indicator)
      ?.review_item_id ??
    manualReviewQueueResult.data.items[0]?.review_item_id ??
    null;
  const manualReviewDetailResult = await getDashboardManualReviewDetail(
    selectedManualReviewId
  );

  return (
    <DashboardView
      result={dashboardResult}
      waterEmergencyResult={waterEmergencyResult}
      waterEmergencyDetailResult={waterEmergencyDetailResult}
      manualReviewQueueResult={manualReviewQueueResult}
      manualReviewDetailResult={manualReviewDetailResult}
      authStatusResult={authStatusResult}
    />
  );
}
