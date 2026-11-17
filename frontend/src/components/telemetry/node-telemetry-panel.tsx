"use client";
import TelemetryHistoryPanel from "./telemetry-history";
import { useEffect, useRef, useState } from "react";
import { ApiError } from "@/lib/api-client";
import { getLatestTelemetry } from "@/lib/telemetry";
import type {
  ConnectionStatus,
  DataStatus,
  TelemetrySnapshot,
} from "@/types/telemetry";

type Props = {
  nodeId: string;
};

const CONNECTION_LABELS: Record<ConnectionStatus, string> = {
  never_seen: "Chưa từng nhận dữ liệu",
  online: "Đang kết nối",
  offline: "Mất kết nối",
  unknown: "Chưa xác định",
};

const DATA_LABELS: Record<DataStatus, string> = {
  no_data: "Chưa có dữ liệu",
  fresh: "Dữ liệu còn mới",
  stale: "Dữ liệu đã cũ",
  invalid_time: "Thời điểm đo không hợp lệ",
};

function formatTime(value: string | null): string {
  if (!value) return "Chưa có";

  const date = new Date(value);

  if (!Number.isFinite(date.getTime())) {
    return "Thời gian không hợp lệ";
  }

  return date.toLocaleString("vi-VN", {
    hour12: false,
    timeZoneName: "short",
  });
}

function badgeClass(status: string): string {
  if (status === "online" || status === "fresh") {
    return "bg-emerald-100 text-emerald-800";
  }

  if (status === "offline") {
    return "bg-red-100 text-red-800";
  }

  if (status === "stale" || status === "invalid_time") {
    return "bg-amber-100 text-amber-800";
  }

  return "bg-slate-100 text-slate-700";
}

function NodeTelemetryContent({ nodeId }: Props) {
  const [snapshot, setSnapshot] = useState<TelemetrySnapshot | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [elapsed, setElapsed] = useState(0);
  const [retryVersion, setRetryVersion] = useState(0);

  const lastSuccessAt = useRef<number | null>(null);

  useEffect(() => {
    let disposed = false;
    let stopPolling = false;
    let pollDelay = 5000;

    let pollTimer: ReturnType<typeof setTimeout> | undefined;
    let requestTimer: ReturnType<typeof setTimeout> | undefined;
    let controller: AbortController | null = null;

    async function refresh() {
      if (disposed) return;

      controller = new AbortController();
      let timedOut = false;

      requestTimer = setTimeout(() => {
        timedOut = true;
        controller?.abort();
      }, 10000);

      try {
        const data = await getLatestTelemetry(
          nodeId,
          controller.signal,
        );

        if (disposed) return;

        lastSuccessAt.current = performance.now();
        setSnapshot(data);
        setElapsed(0);
        setError("");

        if (
          Number.isFinite(data.poll_interval_seconds) &&
          data.poll_interval_seconds > 0
        ) {
          pollDelay = Math.max(
            1000,
            data.poll_interval_seconds * 1000,
          );
        }
      } catch (err) {
        if (disposed) return;

        if (
          err instanceof Error &&
          err.name === "AbortError" &&
          !timedOut
        ) {
          return;
        }

        if (
          err instanceof ApiError &&
          (err.status === 401 || err.status === 403)
        ) {
          stopPolling = true;
        }

        setError(
          timedOut
            ? "Yêu cầu giám sát quá thời gian chờ."
            : err instanceof Error
              ? err.message
              : "Không tải được dữ liệu giám sát.",
        );
      } finally {
        clearTimeout(requestTimer);

        if (!disposed) {
          setLoading(false);

          // Chỉ lên lịch sau khi request trước đã kết thúc.
          if (!stopPolling) {
            pollTimer = setTimeout(() => {
              void refresh();
            }, pollDelay);
          }
        }
      }
    }

    const clockTimer = setInterval(() => {
      if (lastSuccessAt.current !== null) {
        setElapsed(
          Math.max(
            0,
            (performance.now() - lastSuccessAt.current) / 1000,
          ),
        );
      }
    }, 1000);

    void refresh();

    return () => {
      disposed = true;
      clearTimeout(pollTimer);
      clearTimeout(requestTimer);
      clearInterval(clockTimer);
      controller?.abort();
    };
  }, [nodeId, retryVersion]);

  const monitoring = snapshot?.monitoring;

  // Tuổi dữ liệu bắt đầu từ giá trị Backend tính,
  // sau đó cộng thời gian trôi qua bằng đồng hồ đơn điệu.
  const receivedAge =
    monitoring?.seconds_since_received == null
      ? null
      : monitoring.seconds_since_received + elapsed;

  const measuredAge =
    monitoring?.seconds_since_measured == null
      ? null
      : monitoring.seconds_since_measured + elapsed;

  let connectionStatus: ConnectionStatus = "never_seen";

  if (error || (receivedAge !== null && receivedAge < 0)) {
    connectionStatus = "unknown";
  } else if (receivedAge !== null && monitoring) {
    connectionStatus =
      receivedAge > monitoring.offline_after_seconds
        ? "offline"
        : "online";
  }

  let dataStatus: DataStatus = "no_data";

  if (measuredAge !== null && monitoring) {
    dataStatus =
      measuredAge < 0
        ? "invalid_time"
        : measuredAge > monitoring.stale_after_seconds
          ? "stale"
          : "fresh";
  }

  const latest = snapshot?.latest;

  return (
    <section
      className="mt-6 rounded-xl border border-slate-200 bg-white p-4 sm:p-6"
      aria-labelledby={`telemetry-title-${nodeId}`}
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3
          id={`telemetry-title-${nodeId}`}
          className="text-lg font-semibold text-slate-900"
        >
          Giám sát Node
        </h3>

        <button
          type="button"
          onClick={() => setRetryVersion((value) => value + 1)}
          disabled={loading}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:opacity-50"
        >
          Tải lại
        </button>
      </div>

      {loading && !snapshot && (
        <p role="status" className="mt-4 text-slate-500">
          Đang tải dữ liệu giám sát...
        </p>
      )}

      {error && (
        <div
          role="alert"
          className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-800"
        >
          <p>{error}</p>
          {snapshot && (
            <p className="mt-1">
              Đang giữ dữ liệu lần đọc thành công trước.
              Chưa thể xác minh trạng thái kết nối hiện tại.
            </p>
          )}
        </div>
      )}

      {snapshot && monitoring && (
        <>
          <div className="mt-4 flex flex-wrap gap-2" aria-live="polite">
            <span
              className={`rounded-full px-3 py-1 text-sm font-medium ${badgeClass(connectionStatus)}`}
            >
              {CONNECTION_LABELS[connectionStatus]}
            </span>

            <span
              className={`rounded-full px-3 py-1 text-sm font-medium ${badgeClass(dataStatus)}`}
            >
              {DATA_LABELS[dataStatus]}
            </span>
          </div>

          {latest ? (
            <div className="mt-5 grid gap-3 sm:grid-cols-3">
              {[
                { label: "CPU", value: latest.cpu_percent },
                { label: "RAM", value: latest.memory_percent },
                { label: "Disk", value: latest.disk_percent },
              ].map(({ label, value }) => {
                const valid =
                  Number.isFinite(value) &&
                  value >= 0 &&
                  value <= 100;

                return (
                  <div
                    key={label}
                    className="rounded-lg border border-slate-200 p-4"
                  >
                    <p className="text-sm text-slate-500">{label}</p>
                    <p className="mt-2 text-2xl font-semibold">
                      {valid ? `${value.toFixed(1)}%` : "—"}
                    </p>

                    {valid && (
                      <div
                        aria-hidden="true"
                        className="mt-3 h-2 overflow-hidden rounded bg-slate-100"
                      >
                        <div
                          className="h-full bg-cyan-600"
                          style={{ width: `${value}%` }}
                        />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="mt-5 text-sm text-slate-500">
              Node chưa có mẫu telemetry để hiển thị.
            </p>
          )}

          {dataStatus === "stale" && (
            <p className="mt-4 text-sm font-medium text-amber-800">
              Các giá trị đang hiển thị là số liệu cũ.
            </p>
          )}

          {dataStatus === "invalid_time" && (
            <p className="mt-4 text-sm text-amber-800">
              Thời điểm đo nằm trong tương lai. Cần kiểm tra đồng hồ
              thiết bị trước khi sử dụng số liệu.
            </p>
          )}

          <dl className="mt-5 grid gap-4 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-slate-500">Thời điểm đo</dt>
              <dd className="mt-1">
                {formatTime(monitoring.last_measured_at)}
              </dd>
            </div>

            <div>
              <dt className="text-slate-500">
                Liên lạc hợp lệ gần nhất
              </dt>
              <dd className="mt-1">
                {formatTime(monitoring.last_received_at)}
              </dd>
            </div>
          </dl>

          <p className="mt-4 text-xs text-slate-500">
            Tự cập nhật sau mỗi khoảng{" "}
            {snapshot.poll_interval_seconds} giây.
            Dữ liệu cũ khi quá {monitoring.stale_after_seconds} giây;
            mất kết nối khi quá {monitoring.offline_after_seconds} giây.
          </p>

          <TelemetryHistoryPanel
            nodeId={nodeId}
            serverTime={snapshot.server_time}
          />
        </>
      )}
    </section>
  );
}

export default function NodeTelemetryPanel({ nodeId }: Props) {
  // Đổi Node sẽ tạo một phiên giám sát mới.
  return <NodeTelemetryContent key={nodeId} nodeId={nodeId} />;
}