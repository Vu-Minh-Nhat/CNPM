export type ConnectionStatus =
  | "never_seen"
  | "online"
  | "offline"
  | "unknown";

export type DataStatus =
  | "no_data"
  | "fresh"
  | "stale"
  | "invalid_time";

export type TelemetryRecord = {
  id: string;
  message_id: string;
  node_id: string;
  measured_at: string;
  received_at: string;
  cpu_percent: number;
  memory_percent: number;
  disk_percent: number;
};

export type NodeMonitoring = {
  connection_status: ConnectionStatus;
  data_status: DataStatus;
  last_received_at: string | null;
  last_measured_at: string | null;
  seconds_since_received: number | null;
  seconds_since_measured: number | null;
  stale_after_seconds: number;
  offline_after_seconds: number;
};

export type TelemetrySnapshot = {
  node_id: string;
  server_time: string;
  latest: TelemetryRecord | null;
  monitoring: NodeMonitoring;
  poll_interval_seconds: number;
};

export type TelemetryHistory = {
  node_id: string;
  start: string;
  end: string;
  limit: number;
  count: number;
  limit_reached: boolean;
  items: TelemetryRecord[];
};