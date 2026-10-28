const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const r = await fetch(BASE + path, {
    ...options,
    signal: AbortSignal.timeout(90000),
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!r.ok) {
    let message = `Request failed (${r.status})`;
    try {
      const e = await r.json();
      message = e.error?.message || e.detail || message;
    } catch {
      /* use HTTP message */
    }
    throw new Error(typeof message === "string" ? message : "Invalid request");
  }
  return r.json();
}
export function formatValue(value: number | null | undefined, unit?: string) {
  if (value == null) return "Unavailable";
  if (unit === "USD")
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    }).format(value);
  if (unit === "percent") return value.toFixed(1) + "%";
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 }).format(
    value,
  );
}
export function officialLink(
  value: string | null | undefined,
): string | undefined {
  if (!value) return undefined;
  try {
    const u = new URL(value);
    return u.protocol === "https:" &&
      [
        "geoportal.hawaii.gov",
        "geodata.hawaii.gov",
        "api.census.gov",
        "files.hawaii.gov",
        "www.census.gov",
        "dbedt.hawaii.gov",
      ].includes(u.hostname)
      ? value
      : undefined;
  } catch {
    return undefined;
  }
}

export function apiUrl(path: string) {
  return BASE + path;
}
export function sourceWorkbookLink(
  provenance: Record<string, unknown>,
): string | undefined {
  const value = provenance.workbook_url;
  return typeof value === "string" &&
    /^\/v1\/sources\/acs-2024-5yr\/workbooks\/(house|senate|county|state)$/.test(
      value,
    )
    ? apiUrl(value)
    : undefined;
}

export function formatMoe(value: number | null | undefined, unit?: string) {
  return value == null
    ? "Unavailable"
    : unit === "percent"
      ? value.toFixed(1) + " pp"
      : formatValue(value, unit);
}
