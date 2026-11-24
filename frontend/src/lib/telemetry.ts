import { apiFetch } from "./api-client";
import type {
  TelemetryHistory,
  TelemetrySnapshot,
} from "@/types/telemetry";

export async function getLatestTelemetry(
  nodeId: string,
  signal?: AbortSignal,
): Promise<TelemetrySnapshot> {
  const data = await apiFetch<TelemetrySnapshot>(
    `/telemetry/nodes/${encodeURIComponent(nodeId)}/latest`,
    {
      method: "GET",
      signal,
    },
  );

  if (data.node_id !== nodeId) {
    throw new Error("Dữ liệu giám sát không khớp Node đã chọn.");
  }

  return data;
}

type HistoryOptions = {
  start: Date;
  end: Date;
  limit?: number;
  signal?: AbortSignal;
};

export async function getTelemetryHistory(
  nodeId: string,
  options: HistoryOptions,
): Promise<TelemetryHistory> {
  const { start, end, limit = 1000, signal } = options;

  if (
    !Number.isFinite(start.getTime()) ||
    !Number.isFinite(end.getTime()) ||
    start.getTime() >= end.getTime()
  ) {
    throw new Error("Khoảng thời gian truy vấn không hợp lệ.");
  }

  if (!Number.isInteger(limit) || limit < 1 || limit > 1000) {
    throw new Error("Giới hạn số bản ghi phải từ 1 đến 1000.");
  }

  const query = new URLSearchParams({
    start: start.toISOString(),
    end: end.toISOString(),
    limit: String(limit),
  });

  const data = await apiFetch<TelemetryHistory>(
    `/telemetry/nodes/${encodeURIComponent(nodeId)}/history?${query}`,
    {
      method: "GET",
      signal,
    },
  );

  if (data.node_id !== nodeId) {
    throw new Error("Lịch sử telemetry không khớp Node đã chọn.");
  }

  return data;
}