import type {
  WaterEmergencyDashboardResponse,
  WaterEmergencyFilterOptionResponse,
  WaterEmergencySortOptionResponse,
  WaterEmergencyViewStateItemResponse
} from "@/lib/dashboard-contracts";

export type WaterEmergencySortKey = "attention" | "last_activity" | "status";

type WaterEmergencyViewStateOptions = {
  selectedFilter: string;
  selectedSort: WaterEmergencySortKey;
};

export type WaterEmergencyVisibleRecords = {
  selectedFilter: WaterEmergencyFilterOptionResponse;
  selectedSort: WaterEmergencySortOptionResponse;
  visibleItems: WaterEmergencyViewStateItemResponse[];
  visibleActiveItems: WaterEmergencyViewStateItemResponse[];
  visibleClosedItems: WaterEmergencyViewStateItemResponse[];
};

const fallbackFilter: WaterEmergencyFilterOptionResponse = {
  key: "all",
  label: "All records",
  count: 0,
  description: "Every Water Emergency record returned by the read-only dashboard."
};

const fallbackSort: WaterEmergencySortOptionResponse = {
  key: "attention",
  label: "Attention priority",
  description: "Backend-provided deterministic attention ordering."
};

export function deriveWaterEmergencyVisibleRecords(
  data: WaterEmergencyDashboardResponse,
  options: WaterEmergencyViewStateOptions
): WaterEmergencyVisibleRecords {
  const filter =
    data.view_state_summary.available_filters.find(
      (option) => option.key === options.selectedFilter
    ) ??
    data.view_state_summary.available_filters[0] ??
    fallbackFilter;
  const sort =
    data.view_state_summary.sort_options.find(
      (option) => option.key === options.selectedSort
    ) ??
    data.view_state_summary.sort_options[0] ??
    fallbackSort;
  const visibleItems = sortWaterEmergencyViewStateItems(
    data.view_state_summary.items.filter((item) =>
      filter.key === "all" ? true : item.filter_groups.includes(filter.key)
    ),
    sort.key as WaterEmergencySortKey
  );

  return {
    selectedFilter: filter,
    selectedSort: sort,
    visibleItems,
    visibleActiveItems: visibleItems.filter(
      (item) => item.primary_filter_group !== "closed_or_resolved" && item.is_active
    ),
    visibleClosedItems: visibleItems.filter(
      (item) => item.primary_filter_group === "closed_or_resolved" || !item.is_active
    )
  };
}

function sortWaterEmergencyViewStateItems(
  items: WaterEmergencyViewStateItemResponse[],
  sortKey: WaterEmergencySortKey
) {
  return [...items].sort((first, second) => {
    if (sortKey === "last_activity") {
      return (
        timestampSortValue(second.last_activity_at) -
          timestampSortValue(first.last_activity_at) ||
        first.sort_rank - second.sort_rank ||
        first.water_emergency_id.localeCompare(second.water_emergency_id)
      );
    }

    if (sortKey === "status") {
      return (
        first.current_status.localeCompare(second.current_status) ||
        (first.current_stage ?? "").localeCompare(second.current_stage ?? "") ||
        first.sort_rank - second.sort_rank ||
        first.water_emergency_id.localeCompare(second.water_emergency_id)
      );
    }

    return (
      first.sort_rank - second.sort_rank ||
      first.primary_filter_group.localeCompare(second.primary_filter_group) ||
      first.water_emergency_id.localeCompare(second.water_emergency_id)
    );
  });
}

function timestampSortValue(value: string | null) {
  return value ? Date.parse(value) || 0 : 0;
}
