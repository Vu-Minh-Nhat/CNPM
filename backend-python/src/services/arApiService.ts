import {
  AlertSeverity,
  ArAlertSummary,
  ArMarkerLookupResult,
  ArNodeInfo,
  ArRuntimeConfig,
  ArTelemetrySnapshot,
  TelemetryFreshnessStatus,
} from "../types/ar";

interface LookupApiPayload {
  marker_code?: string;
  markerCode?: string;
  node?: Record<string, unknown>;
  asset?: Record<string, unknown>;
  telemetry?: Record<string, unknown>;
  latest_telemetry?: Record<string, unknown>;
  alerts?: Record<string, unknown> | unknown[];
  alert_summary?: Record<string, unknown>;
  is_simulated?: boolean;
}

function normalizeSeverity(raw: unknown): AlertSeverity | null {
  if (!raw) return null;
  const s = String(raw).toLowerCase();
  if (s.includes("crit")) return "critical";
  if (s.includes("high") || s.includes("major")) return "high";
  if (s.includes("warn") || s.includes("med")) return "warning";
  if (s.includes("info") || s.includes("low")) return "info";
  return "unknown";
}

function normalizeStatus(
  rawStatus: unknown,
  hasMetrics: boolean,
  ageSeconds: number | null,
  staleThresholdSeconds: number,
  networkError: boolean
): TelemetryFreshnessStatus {
  if (networkError) return "offline";
  const normalized = String(rawStatus ?? "").toLowerCase();
  if (normalized === "offline" || normalized === "disconnected") return "offline";
  if (normalized === "no_data" || normalized === "nodata" || normalized === "empty") {
    return "no_data";
  }
  if (normalized === "stale") return "stale";
  if (normalized === "online" || normalized === "fresh" || normalized === "ok") {
    if (ageSeconds !== null && ageSeconds > staleThresholdSeconds) {
      return "stale";
    }
    return "online";
  }
  if (!hasMetrics) return "no_data";
  if (ageSeconds !== null && ageSeconds > staleThresholdSeconds) return "stale";
  return "online";
}

function parseNode(rawNode: Record<string, unknown> | undefined, markerCode: string): ArNodeInfo {
  const src = rawNode ?? {};
  const locObj =
    (typeof src.location === "object" && src.location !== null
      ? (src.location as Record<string, unknown>)
      : src) ?? {};

  return {
    id: String(src.id ?? src.node_id ?? markerCode),
    code: String(src.code ?? src.node_code ?? markerCode),
    name: String(src.name ?? src.node_name ?? `Node ${markerCode}`),
    serial: String(src.serial ?? src.serial_number ?? "N/A"),
    location: {
      site: String(locObj.site ?? locObj.site_name ?? "Site ?"),
      room: String(locObj.room ?? locObj.room_name ?? "Room ?"),
      rack: String(locObj.rack ?? locObj.rack_name ?? "Rack ?"),
    },
  };
}

function parseTelemetry(
  rawTel: Record<string, unknown> | undefined,
  staleThresholdSeconds: number,
  networkError: boolean
): ArTelemetrySnapshot {
  const src = rawTel ?? {};
  const measuredAtRaw = src.measured_at ?? src.measuredAt ?? src.timestamp ?? null;
  const measuredAt = measuredAtRaw ? String(measuredAtRaw) : null;

  let ageSeconds: number | null =
    typeof src.age_seconds === "number"
      ? src.age_seconds
      : typeof src.ageSeconds === "number"
      ? src.ageSeconds
      : null;

  if (ageSeconds === null && measuredAt) {
    const parsedTime = Date.parse(measuredAt);
    if (!Number.isNaN(parsedTime)) {
      ageSeconds = Math.max(0, Math.floor((Date.now() - parsedTime) / 1000));
    }
  }

  const metrics = [];
  if (src.cpu_percent !== undefined || src.cpu !== undefined) {
    metrics.push({
      key: "cpu",
      label: "CPU",
      value: (src.cpu_percent ?? src.cpu) as number | string,
      unit: "%",
    });
  }
  if (src.ram_percent !== undefined || src.memory_percent !== undefined || src.ram !== undefined) {
    metrics.push({
      key: "ram",
      label: "RAM",
      value: (src.ram_percent ?? src.memory_percent ?? src.ram) as number | string,
      unit: "%",
    });
  }
  if (src.disk_percent !== undefined || src.disk !== undefined) {
    metrics.push({
      key: "disk",
      label: "Disk",
      value: (src.disk_percent ?? src.disk) as number | string,
      unit: "%",
    });
  }
  if (src.temperature_c !== undefined || src.temp !== undefined) {
    metrics.push({
      key: "temp",
      label: "Nhiệt độ",
      value: (src.temperature_c ?? src.temp) as number | string,
      unit: "°C",
    });
  }

  const hasMetrics = metrics.length > 0 && metrics.some((m) => m.value !== null && m.value !== undefined);
  const status = normalizeStatus(
    src.status ?? src.freshness_status ?? src.connection_status,
    hasMetrics,
    ageSeconds,
    staleThresholdSeconds,
    networkError
  );

  return {
    metrics,
    measuredAt,
    ageSeconds,
    status,
    statusReason: src.status_reason ? String(src.status_reason) : undefined,
  };
}

function parseAlerts(
  rawSummary: Record<string, unknown> | undefined,
  rawAlerts: Record<string, unknown> | unknown[] | undefined
): ArAlertSummary {
  if (rawSummary) {
    const activeCount = Number(rawSummary.active_count ?? rawSummary.activeCount ?? rawSummary.count ?? 0);
    const highestSeverity = normalizeSeverity(
      rawSummary.highest_severity ?? rawSummary.highestSeverity ?? rawSummary.severity
    );
    return {
      activeCount: Number.isNaN(activeCount) ? 0 : activeCount,
      highestSeverity,
      latestTitle: rawSummary.latest_title ? String(rawSummary.latest_title) : undefined,
    };
  }

  if (Array.isArray(rawAlerts)) {
    const activeItems = rawAlerts.filter((item) => {
      if (typeof item !== "object" || item === null) return false;
      const st = String((item as Record<string, unknown>).status ?? "active").toLowerCase();
      return st !== "resolved" && st !== "closed";
    });
    const severities = activeItems
      .map((item) => normalizeSeverity((item as Record<string, unknown>).severity))
      .filter((s): s is AlertSeverity => s !== null);

    const priority: Record<AlertSeverity, number> = {
      critical: 4,
      high: 3,
      warning: 2,
      info: 1,
      unknown: 0,
    };
    severities.sort((a, b) => priority[b] - priority[a]);

    const firstTitle =
      activeItems.length > 0 && typeof activeItems[0] === "object" && activeItems[0] !== null
        ? (activeItems[0] as Record<string, unknown>).title
        : undefined;

    return {
      activeCount: activeItems.length,
      highestSeverity: severities[0] ?? null,
      latestTitle: firstTitle ? String(firstTitle) : undefined,
    };
  }

  return { activeCount: 0, highestSeverity: null };
}

export function buildSimulatedMarkerData(markerCode: string): ArMarkerLookupResult {
  const nowIso = new Date().toISOString();
  const normalizedCode = markerCode.trim().toUpperCase();

  return {
    markerCode: normalizedCode,
    node: {
      id: `sim-${normalizedCode.toLowerCase()}`,
      code: normalizedCode,
      name: `Demo Node (${normalizedCode})`,
      serial: `SN-SIM-${normalizedCode.slice(-4).padStart(4, "0")}`,
      location: {
        site: "DC-HCM-01",
        room: "Hall-A",
        rack: "Rack-02",
      },
    },
    telemetry: {
      metrics: [
        { key: "cpu", label: "CPU", value: 42.5, unit: "%" },
        { key: "ram", label: "RAM", value: 61.2, unit: "%" },
        { key: "disk", label: "Disk", value: 54.0, unit: "%" },
      ],
      measuredAt: nowIso,
      ageSeconds: 2,
      status: "online",
    },
    alerts: {
      activeCount: 1,
      highestSeverity: "warning",
      latestTitle: "Cảnh báo mô phỏng: CPU tăng nhẹ",
    },
    isSimulated: true,
    fetchedAt: nowIso,
  };
}

export async function lookupMarkerSnapshot(
  markerCode: string,
  config: ArRuntimeConfig,
  signal?: AbortSignal
): Promise<ArMarkerLookupResult> {
  const trimmedCode = markerCode.trim();
  const baseUrl = config.apiBaseUrl.replace(/\/+$/, "");
  const headers: Record<string, string> = {
    Accept: "application/json",
    "Content-Type": "application/json",
  };
  if (config.authToken) {
    headers.Authorization = `Bearer ${config.authToken}`;
  }

  try {
    const response = await fetch(`${baseUrl}/markers/lookup`, {
      method: "POST",
      headers,
      body: JSON.stringify({ marker_code: trimmedCode, code: trimmedCode }),
      signal,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status} khi tra cứu marker ${trimmedCode}`);
    }

    const payload = (await response.json()) as LookupApiPayload;
    const rawNode =
      payload.node ??
      (typeof payload.asset === "object" && payload.asset !== null
        ? (payload.asset as Record<string, unknown>)
        : undefined);
    const rawTel =
      payload.telemetry ??
      (typeof payload.latest_telemetry === "object" && payload.latest_telemetry !== null
        ? (payload.latest_telemetry as Record<string, unknown>)
        : undefined);
    const rawSummary =
      payload.alert_summary ??
      (!Array.isArray(payload.alerts) && typeof payload.alerts === "object" && payload.alerts !== null
        ? (payload.alerts as Record<string, unknown>)
        : undefined);

    return {
      markerCode: String(payload.marker_code ?? payload.markerCode ?? trimmedCode),
      node: parseNode(rawNode, trimmedCode),
      telemetry: parseTelemetry(rawTel, config.staleThresholdSeconds, false),
      alerts: parseAlerts(rawSummary, payload.alerts),
      isSimulated: Boolean(payload.is_simulated),
      fetchedAt: new Date().toISOString(),
    };
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") {
      throw error;
    }

    if (config.allowSimulationFallback) {
      return buildSimulatedMarkerData(trimmedCode);
    }

    const message = error instanceof Error ? error.message : "Lỗi kết nối tới Backend";
    return {
      markerCode: trimmedCode,
      node: {
        id: trimmedCode,
        code: trimmedCode,
        name: `Node ${trimmedCode}`,
        serial: "N/A",
        location: { site: "-", room: "-", rack: "-" },
      },
      telemetry: {
        metrics: [],
        measuredAt: null,
        ageSeconds: null,
        status: "offline",
        statusReason: message,
      },
      alerts: { activeCount: 0, highestSeverity: null },
      isSimulated: false,
      fetchedAt: new Date().toISOString(),
    };
  }
}