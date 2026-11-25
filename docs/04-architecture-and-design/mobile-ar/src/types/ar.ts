export type TelemetryFreshnessStatus = "online" | "stale" | "offline" | "no_data";

export type AlertSeverity = "critical" | "high" | "warning" | "info" | "unknown";

export interface NodeLocationPath {
  site: string;
  room: string;
  rack: string;
}

export interface ArNodeInfo {
  id: string;
  code: string;
  name: string;
  serial: string;
  location: NodeLocationPath;
}

export interface TelemetryMetricItem {
  key: string;
  label: string;
  value: number | string | null;
  unit: string;
}

export interface ArTelemetrySnapshot {
  metrics: TelemetryMetricItem[];
  measuredAt: string | null;
  ageSeconds: number | null;
  status: TelemetryFreshnessStatus;
  statusReason?: string;
}

export interface ArAlertSummary {
  activeCount: number;
  highestSeverity: AlertSeverity | null;
  latestTitle?: string;
}

export interface ArMarkerLookupResult {
  markerCode: string;
  node: ArNodeInfo;
  telemetry: ArTelemetrySnapshot;
  alerts: ArAlertSummary;
  isSimulated: boolean;
  fetchedAt: string;
}

export interface ArRuntimeConfig {
  apiBaseUrl: string;
  pollIntervalMs: number;
  staleThresholdSeconds: number;
  allowSimulationFallback: boolean;
  authToken?: string;
}
