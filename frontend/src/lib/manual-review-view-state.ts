import type {
  ManualReviewFilterOptionResponse,
  ManualReviewQueueItemResponse,
  ManualReviewQueueResponse,
  ManualReviewSortOptionResponse
} from "@/lib/dashboard-contracts";

export type ManualReviewSortKey = "attention" | "newest" | "status";

type ManualReviewViewStateOptions = {
  selectedFilter: string;
  selectedSort: ManualReviewSortKey;
};

export type ManualReviewVisibleRecords = {
  selectedFilter: ManualReviewFilterOptionResponse;
  selectedSort: ManualReviewSortOptionResponse;
  visibleItems: ManualReviewQueueItemResponse[];
  visibleActiveItems: ManualReviewQueueItemResponse[];
  visibleHistoricalItems: ManualReviewQueueItemResponse[];
  visibleWaterEmergencyItems: ManualReviewQueueItemResponse[];
  visibleStandardItems: ManualReviewQueueItemResponse[];
};

const fallbackFilter: ManualReviewFilterOptionResponse = {
  key: "all",
  label: "All reviews",
  count: 0,
  description: "Every Manual Review item returned by the read-only queue."
};

const fallbackSort: ManualReviewSortOptionResponse = {
  key: "attention",
  label: "Attention priority",
  description: "Backend-aligned deterministic Manual Review attention ordering."
};

export function deriveManualReviewVisibleRecords(
  data: ManualReviewQueueResponse,
  options: ManualReviewViewStateOptions
): ManualReviewVisibleRecords {
  const selectedFilter =
    data.available_filters.find((filter) => filter.key === options.selectedFilter) ??
    data.available_filters[0] ??
    fallbackFilter;
  const selectedSort =
    data.sort_options.find((sort) => sort.key === options.selectedSort) ??
    data.sort_options[0] ??
    fallbackSort;
  const visibleItems = sortManualReviewItems(
    data.items.filter((item) =>
      selectedFilter.key === "all"
        ? true
        : itemMatchesManualReviewFilter(item, selectedFilter.key)
    ),
    selectedSort.key as ManualReviewSortKey
  );

  return {
    selectedFilter,
    selectedSort,
    visibleItems,
    visibleActiveItems: visibleItems.filter((item) => item.attention_indicator),
    visibleHistoricalItems: visibleItems.filter((item) => !item.attention_indicator),
    visibleWaterEmergencyItems: visibleItems.filter((item) =>
      item.visibility_groups.includes("water_emergency_related")
    ),
    visibleStandardItems: visibleItems.filter(
      (item) => !item.visibility_groups.includes("water_emergency_related")
    )
  };
}

function itemMatchesManualReviewFilter(
  item: ManualReviewQueueItemResponse,
  filterKey: string
) {
  if (filterKey === "active_attention") {
    return item.attention_indicator;
  }

  return item.visibility_groups.includes(filterKey);
}

function sortManualReviewItems(
  items: ManualReviewQueueItemResponse[],
  sortKey: ManualReviewSortKey
) {
  return [...items].sort((first, second) => {
    if (sortKey === "newest") {
      return (
        timestampSortValue(second.created_at) -
          timestampSortValue(first.created_at) ||
        first.review_item_id.localeCompare(second.review_item_id)
      );
    }

    if (sortKey === "status") {
      return (
        first.status.localeCompare(second.status) ||
        first.reason_code.localeCompare(second.reason_code) ||
        attentionRank(first) - attentionRank(second) ||
        first.review_item_id.localeCompare(second.review_item_id)
      );
    }

    return (
      attentionRank(first) - attentionRank(second) ||
      statusRank(first.status) - statusRank(second.status) ||
      severityRank(first.severity) - severityRank(second.severity) ||
      timestampSortValue(second.created_at) -
        timestampSortValue(first.created_at) ||
      first.review_item_id.localeCompare(second.review_item_id)
    );
  });
}

function attentionRank(item: ManualReviewQueueItemResponse) {
  return item.attention_indicator ? 0 : 1;
}

function statusRank(status: string) {
  const normalizedStatus = normalizeLabel(status);
  const ranks: Record<string, number> = {
    open: 0,
    pending: 0,
    flagged_for_review: 0,
    review_required: 0,
    deferred: 1,
    resolved: 3,
    approved: 3,
    rejected: 3,
    closed: 3,
    archived: 4
  };
  return ranks[normalizedStatus] ?? 2;
}

function severityRank(severity: string | null) {
  const ranks: Record<string, number> = {
    critical: 0,
    high: 1,
    medium: 2,
    low: 3
  };
  return ranks[normalizeLabel(severity)] ?? 4;
}

function normalizeLabel(value: string | null) {
  return (value ?? "").trim().toLowerCase();
}

function timestampSortValue(value: string | null) {
  return value ? Date.parse(value) || 0 : 0;
}
