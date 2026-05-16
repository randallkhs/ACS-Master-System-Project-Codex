export function formatCount(value: number): string {
  return new Intl.NumberFormat("en-US").format(value);
}

export function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}

export function humanizeLabel(value: string | null): string {
  if (!value) {
    return "None";
  }

  return value
    .replaceAll("_", " ")
    .replaceAll(".", " ")
    .split(" ")
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

export function compactId(value: string | null): string {
  if (!value) {
    return "Not linked";
  }

  return value.slice(0, 8);
}
