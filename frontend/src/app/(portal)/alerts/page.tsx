
"use client";

import { useCallback, useEffect, useState } from "react";
import { acknowledgeAlert, getAlerts } from "@/lib/alerts";
import { getUserRole } from "@/lib/auth-storage";
import type { Alert } from "@/types/alert";

const statusLabels: Record<string, string> = {
  FIRING: "Đang phát sinh",
  ACKNOWLEDGED: "Đã xác nhận",
  RECOVERED: "Đã khôi phục",
};

const severityLabels: Record<string, string> = {
  LOW: "Thấp",
  MEDIUM: "Trung bình",
  HIGH: "Cao",
  CRITICAL: "Nghiêm trọng",
};

function formatDate(value: string | null): string {
  if (!value) return "—";
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? value
    : date.toLocaleString("vi-VN");
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [status, setStatus] = useState("");
  const [severity, setSeverity] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [processingId, setProcessingId] = useState<string | null>(null);
  const [role, setRole] = useState<string | null>(null);

  const canAcknowledge =
    role === "Administrator" || role === "Operator";

  const loadAlerts = useCallback(async (signal?: AbortSignal) => {
    setLoading(true);
    setError("");

    try {
      const data = await getAlerts(
        {
          status: status || undefined,
          severity: severity || undefined,
        },
        signal,
      );

      if (!signal?.aborted) {
        setAlerts(data);
        setSelectedAlert((current) =>
          current
            ? data.find((item) => item.id === current.id) ?? null
            : null,
        );
      }
    } catch (err) {
      if (!signal?.aborted) {
        setError(
          err instanceof Error
            ? err.message
            : "Không thể tải danh sách cảnh báo.",
        );
      }
    } finally {
      if (!signal?.aborted) setLoading(false);
    }
  }, [status, severity]);

  useEffect(() => {
    setRole(getUserRole());

    const controller = new AbortController();
    void loadAlerts(controller.signal);

    return () => controller.abort();
  }, [loadAlerts]);

  async function handleAcknowledge(alertId: string) {
    setProcessingId(alertId);
    setError("");

    try {
      const updated = await acknowledgeAlert(alertId);

      setAlerts((current) =>
        current.map((item) => item.id === alertId ? updated : item),
      );

      setSelectedAlert((current) =>
        current?.id === alertId ? updated : current,
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Không thể xác nhận cảnh báo.",
      );
    } finally {
      setProcessingId(null);
    }
  }

  const firingCount = alerts.filter(
    (item) => item.status === "FIRING",
  ).length;

  return (
    <main className="space-y-6 p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Quản lý cảnh báo
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Theo dõi và xử lý các cảnh báo từ hệ thống hạ tầng.
          </p>
        </div>

        <button
          type="button"
          onClick={() => void loadAlerts()}
          disabled={loading}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Đang tải..." : "Tải lại"}
        </button>
      </div>

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="rounded-xl border bg-white p-5 shadow-sm">
          <p className="text-sm text-gray-500">Tổng cảnh báo</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">
            {alerts.length}
          </p>
        </div>

        <div className="rounded-xl border bg-white p-5 shadow-sm">
          <p className="text-sm text-gray-500">Đang phát sinh</p>
          <p className="mt-2 text-3xl font-bold text-red-600">
            {firingCount}
          </p>
        </div>

        <div className="rounded-xl border bg-white p-5 shadow-sm">
          <p className="text-sm text-gray-500">Đã xác nhận</p>
          <p className="mt-2 text-3xl font-bold text-green-600">
            {alerts.filter(
              (item) => item.status === "ACKNOWLEDGED",
            ).length}
          </p>
        </div>
      </section>

      <section className="rounded-xl border bg-white p-5 shadow-sm">
        <div className="mb-4 flex flex-wrap items-center gap-3">
          <h2 className="mr-auto text-lg font-semibold text-gray-900">
            Danh sách cảnh báo
          </h2>

          <select
            value={status}
            onChange={(event) => setStatus(event.target.value)}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm"
            aria-label="Lọc theo trạng thái"
          >
            <option value="">Tất cả trạng thái</option>
            <option value="FIRING">Đang phát sinh</option>
            <option value="ACKNOWLEDGED">Đã xác nhận</option>
            <option value="RECOVERED">Đã khôi phục</option>
          </select>

          <select
            value={severity}
            onChange={(event) => setSeverity(event.target.value)}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm"
            aria-label="Lọc theo mức độ"
          >
            <option value="">Tất cả mức độ</option>
            <option value="LOW">Thấp</option>
            <option value="MEDIUM">Trung bình</option>
            <option value="HIGH">Cao</option>
            <option value="CRITICAL">Nghiêm trọng</option>
          </select>
        </div>

        {error && (
          <div className="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            {error}
          </div>
        )}

        {loading ? (
          <p className="py-10 text-center text-sm text-gray-500">
            Đang tải dữ liệu cảnh báo...
          </p>
        ) : alerts.length === 0 ? (
          <p className="py-10 text-center text-sm text-gray-500">
            Không có cảnh báo phù hợp.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[850px] text-left text-sm">
              <thead className="border-b bg-gray-50 text-gray-600">
                <tr>
                  <th className="px-4 py-3">Nội dung</th>
                  <th className="px-4 py-3">Chỉ số</th>
                  <th className="px-4 py-3">Mức độ</th>
                  <th className="px-4 py-3">Trạng thái</th>
                  <th className="px-4 py-3">Thời gian</th>
                  <th className="px-4 py-3">Thao tác</th>
                </tr>
              </thead>

              <tbody className="divide-y divide-gray-100">
                {alerts.map((alert) => (
                  <tr key={alert.id} className="hover:bg-gray-50">
                    <td className="max-w-xs px-4 py-3 font-medium text-gray-900">
                      {alert.message}
                    </td>
                    <td className="px-4 py-3 text-gray-600">
                      {alert.metric}
                    </td>
                    <td className="px-4 py-3">
                      <span className="rounded-full bg-orange-50 px-2.5 py-1 text-xs font-medium text-orange-700">
                        {severityLabels[alert.severity] ?? alert.severity}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="rounded-full bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-700">
                        {statusLabels[alert.status] ?? alert.status}
                      </span>
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-gray-600">
                      {formatDate(alert.triggered_at)}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => setSelectedAlert(alert)}
                          className="font-medium text-blue-600 hover:underline"
                        >
                          Chi tiết
                        </button>

                        {canAcknowledge && alert.status === "FIRING" && (
                          <button
                            type="button"
                            onClick={() => void handleAcknowledge(alert.id)}
                            disabled={processingId === alert.id}
                            className="rounded-md bg-green-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-green-700 disabled:opacity-50"
                          >
                            {processingId === alert.id
                              ? "Đang xử lý..."
                              : "Xác nhận"}
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {selectedAlert && (
        <section className="rounded-xl border bg-white p-5 shadow-sm">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">
              Chi tiết cảnh báo
            </h2>
            <button
              type="button"
              onClick={() => setSelectedAlert(null)}
              className="text-sm text-gray-500 hover:text-gray-900"
            >
              Đóng
            </button>
          </div>

          <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <dt className="text-sm text-gray-500">Nội dung</dt>
              <dd className="mt-1 font-medium text-gray-900">
                {selectedAlert.message}
              </dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Node ID</dt>
              <dd className="mt-1 break-all text-gray-900">
                {selectedAlert.node_id}
              </dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Chỉ số</dt>
              <dd className="mt-1 text-gray-900">
                {selectedAlert.metric}
              </dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Ngưỡng</dt>
              <dd className="mt-1 text-gray-900">
                {selectedAlert.operator} {selectedAlert.threshold ?? "—"}
              </dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Thời điểm phát sinh</dt>
              <dd className="mt-1 text-gray-900">
                {formatDate(selectedAlert.triggered_at)}
              </dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Thời điểm xác nhận</dt>
              <dd className="mt-1 text-gray-900">
                {formatDate(selectedAlert.acknowledged_at)}
              </dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Thời điểm khôi phục</dt>
              <dd className="mt-1 text-gray-900">
                {formatDate(selectedAlert.recovered_at)}
              </dd>
            </div>
          </dl>
        </section>
      )}
    </main>
  );
}
