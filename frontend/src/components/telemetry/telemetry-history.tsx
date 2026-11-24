"use client";

import { useEffect, useState } from "react";
import { getTelemetryHistory } from "@/lib/telemetry";
import type { TelemetryHistory } from "@/types/telemetry";

type Props = {
  nodeId: string;
  serverTime: string;
};

const METRICS = [
  { key: "cpu_percent", label: "CPU", color: "#0284c7" },
  { key: "memory_percent", label: "RAM", color: "#7c3aed" },
  { key: "disk_percent", label: "Disk", color: "#d97706" },
] as const;

function timeLabel(timestamp: number) {
  return new Date(timestamp).toLocaleTimeString("vi-VN", {
    hour12: false,
  });
}

function HistoryContent({
  nodeId,
  serverTime,
  minutes,
}: Props & { minutes: number }) {
  const [history, setHistory] = useState<TelemetryHistory | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let disposed = false;
    let timedOut = false;
    const controller = new AbortController();

    const timeout = setTimeout(() => {
      timedOut = true;
      controller.abort();
    }, 10000);

    async function load() {
      try {
        const end = new Date(serverTime);
        const start = new Date(end.getTime() - minutes * 60_000);

        const data = await getTelemetryHistory(nodeId, {
          start,
          end,
          limit: 1000,
          signal: controller.signal,
        });

        if (disposed) return;

        setHistory(data);
        setError("");
      } catch (err) {
        if (disposed) return;

        setError(
          timedOut
            ? "Truy vấn lịch sử quá thời gian chờ."
            : err instanceof Error
              ? err.message
              : "Không tải được lịch sử telemetry.",
        );
      } finally {
        clearTimeout(timeout);
      }
    }

    void load();

    return () => {
      disposed = true;
      clearTimeout(timeout);
      controller.abort();
    };
  }, [nodeId, serverTime, minutes]);

  if (!history) {
    return (
      <p
        role={error ? "alert" : "status"}
        className="mt-4 text-sm text-slate-600"
      >
        {error || "Đang tải lịch sử telemetry..."}
      </p>
    );
  }

  const start = Date.parse(history.start);
  const end = Date.parse(history.end);

  const records = history.items
    .filter((item) => {
      const timestamp = Date.parse(item.measured_at);

      return (
        item.node_id === nodeId &&
        Number.isFinite(timestamp) &&
        timestamp >= start &&
        timestamp < end
      );
    })
    .sort(
      (a, b) =>
        Date.parse(a.measured_at) - Date.parse(b.measured_at),
    );

  const width = 800;
  const height = 260;
  const left = 48;
  const right = 20;
  const top = 20;
  const bottom = 40;

  const x = (timestamp: number) =>
    left +
    ((timestamp - start) / (end - start)) *
      (width - left - right);

  const y = (value: number) =>
    top + ((100 - value) / 100) * (height - top - bottom);

  return (
    <div className="mt-4">
      {error && (
        <p role="alert" className="mb-3 text-sm text-red-700">
          {error} Đang giữ kết quả lần đọc thành công trước.
        </p>
      )}

      {history.limit_reached && (
        <p className="mb-3 text-sm text-amber-800">
          Đã đạt giới hạn {history.limit} mẫu. Dữ liệu có thể chưa
          đầy đủ; hãy chọn khoảng thời gian ngắn hơn.
        </p>
      )}

      {records.length === 0 ? (
        <p className="text-sm text-slate-500">
          Không có dữ liệu trong khoảng thời gian đã chọn.
        </p>
      ) : (
        <>
          <div className="flex flex-wrap gap-4 text-sm">
            {METRICS.map((metric) => (
              <span key={metric.key} className="flex items-center gap-2">
                <span
                  aria-hidden="true"
                  className="h-3 w-3 rounded-full"
                  style={{ backgroundColor: metric.color }}
                />
                {metric.label}
              </span>
            ))}
          </div>

          <svg
            viewBox={`0 0 ${width} ${height}`}
            className="mt-3 w-full"
            role="img"
            aria-label="Lịch sử CPU, RAM và Disk theo thời điểm đo, đơn vị phần trăm"
          >
            {[0, 25, 50, 75, 100].map((value) => (
              <g key={value}>
                <line
                  x1={left}
                  x2={width - right}
                  y1={y(value)}
                  y2={y(value)}
                  stroke="#e2e8f0"
                />
                <text
                  x={left - 8}
                  y={y(value) + 4}
                  textAnchor="end"
                  fontSize={12}
                  fill="#475569"
                >
                  {value}%
                </text>
              </g>
            ))}

            {METRICS.map((metric) => {
              let previousTime: number | null = null;

              const path = records
                .map((record) => {
                  const value = record[metric.key];
                  const timestamp = Date.parse(record.measured_at);

                  if (
                    !Number.isFinite(value) ||
                    value < 0 ||
                    value > 100
                  ) {
                    previousTime = null;
                    return "";
                  }

                  // Ngắt đường khi thiếu mẫu quá 30 giây.
                  const command =
                    previousTime === null ||
                    timestamp - previousTime > 30_000
                      ? "M"
                      : "L";

                  previousTime = timestamp;
                  return `${command} ${x(timestamp)} ${y(value)}`;
                })
                .join(" ");

              return (
                <g key={metric.key}>
                  <path
                    d={path}
                    fill="none"
                    stroke={metric.color}
                    strokeWidth={2}
                  />

                  {records.map((record) => {
                    const value = record[metric.key];

                    if (
                      !Number.isFinite(value) ||
                      value < 0 ||
                      value > 100
                    ) {
                      return null;
                    }

                    const timestamp = Date.parse(record.measured_at);

                    return (
                      <circle
                        key={record.id}
                        cx={x(timestamp)}
                        cy={y(value)}
                        r={2}
                        fill={metric.color}
                      >
                        <title>
                          {`${metric.label}: ${value.toFixed(1)}% — ${timeLabel(timestamp)}`}
                        </title>
                      </circle>
                    );
                  })}
                </g>
              );
            })}

            {[0, 0.5, 1].map((fraction) => {
              const timestamp = start + fraction * (end - start);

              return (
                <text
                  key={fraction}
                  x={x(timestamp)}
                  y={height - 12}
                  textAnchor={
                    fraction === 0
                      ? "start"
                      : fraction === 1
                        ? "end"
                        : "middle"
                  }
                  fontSize={12}
                  fill="#475569"
                >
                  {timeLabel(timestamp)}
                </text>
              );
            })}
          </svg>

          <p className="text-xs text-slate-500">
            {records.length} mẫu: {timeLabel(start)} – {timeLabel(end)}.
            Khoảng thiếu mẫu trên 30 giây được ngắt đường biểu diễn.
          </p>
        </>
      )}
    </div>
  );
}

export default function TelemetryHistoryPanel(props: Props) {
  const [minutes, setMinutes] = useState(15);

  return (
    <section className="mt-6 border-t border-slate-200 pt-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h4 className="font-semibold text-slate-900">
          Lịch sử giám sát
        </h4>

        <label className="flex items-center gap-2 text-sm">
          Khoảng thời gian
          <select
            value={minutes}
            onChange={(event) => setMinutes(Number(event.target.value))}
            className="rounded-lg border border-slate-300 bg-white px-3 py-2"
          >
            <option value={5}>5 phút gần nhất</option>
            <option value={15}>15 phút gần nhất</option>
            <option value={60}>60 phút gần nhất</option>
          </select>
        </label>
      </div>

      <HistoryContent
        key={`${props.nodeId}-${minutes}`}
        {...props}
        minutes={minutes}
      />
    </section>
  );
}