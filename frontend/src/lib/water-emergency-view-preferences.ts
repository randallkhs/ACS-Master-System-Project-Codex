import type { WaterEmergencySortKey } from "@/lib/water-emergency-view-state";

export const waterEmergencyViewPreferencesStorageKey =
  "acs.waterEmergency.viewPreferences.v1";
export const waterEmergencyViewPreferencesChangedEvent =
  "acs.waterEmergency.viewPreferences.changed";

export type WaterEmergencyViewPreferences = {
  selectedFilter: string;
  selectedSort: WaterEmergencySortKey;
};

export type WaterEmergencyViewPreferenceReadOptions = {
  availableFilterKeys: ReadonlySet<string>;
  availableSortKeys: ReadonlySet<string>;
};

export type WaterEmergencyViewPreferenceReadResult = {
  available: boolean;
  preferences: WaterEmergencyViewPreferences | null;
};

export type WaterEmergencyViewPreferenceWriteResult = {
  available: boolean;
};

type StoredWaterEmergencyViewPreferences = WaterEmergencyViewPreferences & {
  version: 1;
};

export function readWaterEmergencyViewPreferences(
  storage: Storage | null | undefined,
  options: WaterEmergencyViewPreferenceReadOptions
): WaterEmergencyViewPreferenceReadResult {
  if (!storage) {
    return { available: false, preferences: null };
  }

  try {
    const rawValue = storage.getItem(waterEmergencyViewPreferencesStorageKey);
    return readWaterEmergencyViewPreferencesValue(rawValue, options);
  } catch {
    return { available: false, preferences: null };
  }
}

export function readWaterEmergencyViewPreferencesSnapshot(
  snapshot: string,
  options: WaterEmergencyViewPreferenceReadOptions
): WaterEmergencyViewPreferenceReadResult {
  if (snapshot === "storage:server" || snapshot === "storage:unavailable") {
    return { available: false, preferences: null };
  }

  if (snapshot === "storage:empty") {
    return { available: true, preferences: null };
  }

  return readWaterEmergencyViewPreferencesValue(snapshot, options);
}

function readWaterEmergencyViewPreferencesValue(
  rawValue: string | null,
  options: WaterEmergencyViewPreferenceReadOptions
): WaterEmergencyViewPreferenceReadResult {
  if (!rawValue) {
    return { available: true, preferences: null };
  }

  try {
    const parsedValue = JSON.parse(rawValue) as Partial<StoredWaterEmergencyViewPreferences>;
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
        selectedSort: parsedValue.selectedSort as WaterEmergencySortKey
      }
    };
  } catch {
    return { available: true, preferences: null };
  }
}

export function writeWaterEmergencyViewPreferences(
  storage: Storage | null | undefined,
  preferences: WaterEmergencyViewPreferences
): WaterEmergencyViewPreferenceWriteResult {
  if (!storage) {
    return { available: false };
  }

  try {
    const value: StoredWaterEmergencyViewPreferences = {
      version: 1,
      ...preferences
    };
    storage.setItem(waterEmergencyViewPreferencesStorageKey, JSON.stringify(value));
    return { available: true };
  } catch {
    return { available: false };
  }
}

export function subscribeWaterEmergencyViewPreferences(callback: () => void) {
  if (typeof window === "undefined") {
    return () => {};
  }

  window.addEventListener("storage", callback);
  window.addEventListener(waterEmergencyViewPreferencesChangedEvent, callback);

  return () => {
    window.removeEventListener("storage", callback);
    window.removeEventListener(waterEmergencyViewPreferencesChangedEvent, callback);
  };
}

export function getWaterEmergencyViewPreferencesSnapshot() {
  try {
    return (
      getBrowserStorage()?.getItem(waterEmergencyViewPreferencesStorageKey) ??
      "storage:empty"
    );
  } catch {
    return "storage:unavailable";
  }
}

export function getWaterEmergencyViewPreferencesServerSnapshot() {
  return "storage:server";
}

export function notifyWaterEmergencyViewPreferencesChanged() {
  if (typeof window === "undefined") return;

  window.dispatchEvent(new Event(waterEmergencyViewPreferencesChangedEvent));
}

export function getBrowserStorage(): Storage | null {
  if (typeof window === "undefined") {
    return null;
  }

  try {
    return window.localStorage ?? null;
  } catch {
    return null;
  }
}
