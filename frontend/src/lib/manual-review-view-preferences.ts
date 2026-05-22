import type { ManualReviewSortKey } from "@/lib/manual-review-view-state";

export const manualReviewViewPreferencesStorageKey =
  "acs.manualReview.viewPreferences.v1";
export const manualReviewViewPreferencesChangedEvent =
  "acs.manualReview.viewPreferences.changed";

export type ManualReviewViewPreferences = {
  selectedFilter: string;
  selectedSort: ManualReviewSortKey;
};

export type ManualReviewViewPreferenceReadOptions = {
  availableFilterKeys: ReadonlySet<string>;
  availableSortKeys: ReadonlySet<string>;
};

export type ManualReviewViewPreferenceReadResult = {
  available: boolean;
  preferences: ManualReviewViewPreferences | null;
};

export type ManualReviewViewPreferenceWriteResult = {
  available: boolean;
};

type StoredManualReviewViewPreferences = ManualReviewViewPreferences & {
  version: 1;
};

export function readManualReviewViewPreferences(
  storage: Storage | null | undefined,
  options: ManualReviewViewPreferenceReadOptions
): ManualReviewViewPreferenceReadResult {
  if (!storage) {
    return { available: false, preferences: null };
  }

  try {
    const rawValue = storage.getItem(manualReviewViewPreferencesStorageKey);
    return readManualReviewViewPreferencesValue(rawValue, options);
  } catch {
    return { available: false, preferences: null };
  }
}

export function readManualReviewViewPreferencesSnapshot(
  snapshot: string,
  options: ManualReviewViewPreferenceReadOptions
): ManualReviewViewPreferenceReadResult {
  if (snapshot === "storage:server" || snapshot === "storage:unavailable") {
    return { available: false, preferences: null };
  }

  if (snapshot === "storage:empty") {
    return { available: true, preferences: null };
  }

  return readManualReviewViewPreferencesValue(snapshot, options);
}

function readManualReviewViewPreferencesValue(
  rawValue: string | null,
  options: ManualReviewViewPreferenceReadOptions
): ManualReviewViewPreferenceReadResult {
  if (!rawValue) {
    return { available: true, preferences: null };
  }

  try {
    const parsedValue = JSON.parse(rawValue) as Partial<StoredManualReviewViewPreferences>;
    if (
      parsedValue.version !== 1 ||
      typeof parsedValue.selectedFilter !== "string" ||
      typeof parsedValue.selectedSort !== "string" ||
      !options.availableFilterKeys.has(parsedValue.selectedFilter) ||
      !options.availableSortKeys.has(parsedValue.selectedSort)
    ) {
      return { available: true, preferences: null };
    }

    return {
      available: true,
      preferences: {
        selectedFilter: parsedValue.selectedFilter,
        selectedSort: parsedValue.selectedSort as ManualReviewSortKey
      }
    };
  } catch {
    return { available: true, preferences: null };
  }
}

export function writeManualReviewViewPreferences(
  storage: Storage | null | undefined,
  preferences: ManualReviewViewPreferences
): ManualReviewViewPreferenceWriteResult {
  if (!storage) {
    return { available: false };
  }

  try {
    const value: StoredManualReviewViewPreferences = {
      version: 1,
      ...preferences
    };
    storage.setItem(manualReviewViewPreferencesStorageKey, JSON.stringify(value));
    return { available: true };
  } catch {
    return { available: false };
  }
}

export function subscribeManualReviewViewPreferences(callback: () => void) {
  if (typeof window === "undefined") {
    return () => {};
  }

  window.addEventListener("storage", callback);
  window.addEventListener(manualReviewViewPreferencesChangedEvent, callback);

  return () => {
    window.removeEventListener("storage", callback);
    window.removeEventListener(manualReviewViewPreferencesChangedEvent, callback);
  };
}

export function getManualReviewViewPreferencesSnapshot() {
  try {
    return (
      getManualReviewBrowserStorage()?.getItem(manualReviewViewPreferencesStorageKey) ??
      "storage:empty"
    );
  } catch {
    return "storage:unavailable";
  }
}

export function getManualReviewViewPreferencesServerSnapshot() {
  return "storage:server";
}

export function notifyManualReviewViewPreferencesChanged() {
  if (typeof window === "undefined") return;

  window.dispatchEvent(new Event(manualReviewViewPreferencesChangedEvent));
}

export function getManualReviewBrowserStorage(): Storage | null {
  if (typeof window === "undefined") {
    return null;
  }

  try {
    return window.localStorage ?? null;
  } catch {
    return null;
  }
}
