"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getAssets } from "@/lib/assets";
import type { AssetNode } from "@/types/asset";

function displayValue(value?: string | null): string {
  return value?.trim() || "Chưa có thông tin";
}

function getLocation(asset: AssetNode): string {
  const rack = asset.rack;
  const room = rack?.room;
  const site = room?.site;

  return [
    site?.name || site?.code,
    room?.name || room?.code,
    rack?.name || rack?.code,
  ]
    .filter(Boolean)
    .join(" / ") || "Chưa có vị trí";
}

export default function DashboardPage() {
  const [assets, setAssets] = useState<AssetNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [retryCount, setRetryCount] = useState(0);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    async function loadAssets() {
      setLoading(true);
      setError("");

      try {
        const data = await getAssets(controller.signal);

        if (!controller.signal.aborted) {
          setAssets(data);
          setSelectedId(null);
        }
      } catch (err) {
        if (controller.signal.aborted) return;

        setError(
          err instanceof Error
            ? err.message
            : "Không thể tải dữ liệu tài sản.",
        );
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    void loadAssets();

    return () => controller.abort();
  }, [retryCount]);

  const totalNodes = assets.length;

  const totalWorkloads = assets.reduce(
    (total, asset) =>
      total +
      (Array.isArray(asset.workloads) ? asset.workloads.length : 0),
    0,
  );



  return (
    <section className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            Dashboard tổng quan
          </h1>

          <p className="mt-2 text-sm text-slate-600">
            Tổng quan tài sản được cung cấp từ hệ thống AR-IMMS.
          </p>
        </div>

        <Link
          href="/assets"
          className="rounded-lg bg-cyan-700 px-4 py-2 text-sm font-medium text-white hover:bg-cyan-800"
        >
          Xem danh sách tài sản
        </Link>
      </div>

      {loading && (
        <div
          role="status"
          aria-live="polite"
          className="rounded-xl border border-slate-200 bg-white p-6 text-slate-600"
        >
          Đang tải dữ liệu tổng quan từ máy chủ...
        </div>
      )}

      {!loading && error && (
        <div
          role="alert"
          className="rounded-xl border border-red-200 bg-red-50 p-5"
        >
          <h2 className="font-semibold text-red-800">
            Không thể tải Dashboard
          </h2>

          <p className="mt-2 text-sm text-red-700">
            {error}
          </p>

          <button
            type="button"
            onClick={() => setRetryCount((count) => count + 1)}
            className="mt-4 rounded-lg bg-red-700 px-4 py-2 text-sm font-medium text-white hover:bg-red-800"
          >
            Thử tải lại
          </button>
        </div>
      )}

      {!loading && !error && (
        <>
          <div className="grid gap-4 sm:grid-cols-2">
            <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <p className="text-sm font-medium text-slate-500">
                Tổng số Node
              </p>

              <p className="mt-3 text-3xl font-bold text-slate-900">
                {totalNodes}
              </p>

              <p className="mt-2 text-xs text-slate-500">
                Số Node trong phản hồi GET /assets
              </p>
            </article>

            <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <p className="text-sm font-medium text-slate-500">
                Tổng số Workload
              </p>

              <p className="mt-3 text-3xl font-bold text-slate-900">
                {totalWorkloads}
              </p>

              <p className="mt-2 text-xs text-slate-500">
                Tổng Workload thuộc các Node được trả về
              </p>
            </article>
          </div>

          {assets.length === 0 ? (
            <div className="rounded-xl border border-slate-200 bg-white p-8 text-center">
              <h2 className="font-semibold text-slate-800">
                Chưa có dữ liệu tài sản
              </h2>

              <p className="mt-2 text-sm text-slate-500">
                Backend chưa trả về Node nào trong danh sách tài sản.
              </p>

              <Link
                href="/assets"
                className="mt-4 inline-block text-sm font-medium text-cyan-700 hover:underline"
              >
                Đi đến danh sách tài sản
              </Link>
            </div>
          ) : (
            <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h2 className="text-lg font-bold text-slate-900">
                    Danh sách thiết bị
                  </h2>

                  <p className="mt-1 text-sm text-slate-500">
                    Có {totalNodes} Node được trả về từ Backend.
                  </p>
                </div>

                <Link
                  href="/assets"
                  className="text-sm font-medium text-cyan-700 hover:underline"
                >
                  Xem tất cả
                </Link>
              </div>

              <div className="mt-5 space-y-3">
                {assets.map((asset) => (
                  <article
                    key={asset.id}
                    className="rounded-lg border border-slate-200 p-4"
                  >
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div className="min-w-0">
                        <h3 className="break-words font-semibold text-slate-900">
                          {displayValue(asset.name)}
                        </h3>

                        <p className="mt-1 text-sm text-slate-600">
                          Mã Node: {displayValue(asset.code)}
                        </p>

                        <p className="mt-1 text-sm text-slate-600">
                          Serial: {displayValue(asset.serialNumber)}
                        </p>

                        <p className="mt-1 text-sm text-slate-600">
                          Vị trí: {getLocation(asset)}
                        </p>

                        <p className="mt-1 text-sm text-slate-600">
                          Workload:{" "}
                          {Array.isArray(asset.workloads)
                            ? asset.workloads.length
                            : 0}
                        </p>
                      </div>

                      <button
                        type="button"
                        onClick={() =>
                          setSelectedId((current) =>
                            current === asset.id ? null : asset.id,
                          )
                        }
                        aria-expanded={selectedId === asset.id}
                        className="shrink-0 rounded-lg border border-cyan-700 px-3 py-2 text-sm font-medium text-cyan-700 hover:bg-cyan-50"
                      >
                        {selectedId === asset.id
                          ? "Đóng chi tiết"
                          : "Xem chi tiết"}
                      </button>
                    </div>

                    {selectedId === asset.id && (
                      <div className="mt-4 border-t border-slate-200 pt-4">
                        <h4 className="font-semibold text-slate-800">
                          Thông tin chi tiết Node
                        </h4>

                        <dl className="mt-3 grid gap-3 text-sm sm:grid-cols-2">
                          <div>
                            <dt className="text-slate-500">Node ID</dt>
                            <dd className="mt-1 break-all font-medium">
                              {asset.id}
                            </dd>
                          </div>

                          <div>
                            <dt className="text-slate-500">Rack ID</dt>
                            <dd className="mt-1 break-all font-medium">
                              {displayValue(asset.rackId)}
                            </dd>
                          </div>

                          <div>
                            <dt className="text-slate-500">Rack</dt>
                            <dd className="mt-1 font-medium">
                              {displayValue(
                                asset.rack?.name || asset.rack?.code,
                              )}
                            </dd>
                          </div>

                          <div>
                            <dt className="text-slate-500">Room</dt>
                            <dd className="mt-1 font-medium">
                              {displayValue(
                                asset.rack?.room?.name ||
                                asset.rack?.room?.code,
                              )}
                            </dd>
                          </div>

                          <div>
                            <dt className="text-slate-500">Site</dt>
                            <dd className="mt-1 font-medium">
                              {displayValue(
                                asset.rack?.room?.site?.name ||
                                asset.rack?.room?.site?.code,
                              )}
                            </dd>
                          </div>
                        </dl>

                        <h4 className="mt-5 font-semibold text-slate-800">
                          Workload
                        </h4>

                        {!Array.isArray(asset.workloads) ||
                        asset.workloads.length === 0 ? (
                          <p className="mt-2 text-sm text-slate-500">
                            Node chưa có Workload trong dữ liệu trả về.
                          </p>
                        ) : (
                          <ul className="mt-2 divide-y divide-slate-100 rounded-lg border border-slate-200">
                            {asset.workloads.map((workload) => (
                              <li
                                key={workload.id}
                                className="p-3 text-sm"
                              >
                                <p className="font-medium text-slate-800">
                                  {displayValue(workload.name)}
                                </p>

                                <p className="mt-1 text-slate-600">
                                  Mã: {displayValue(workload.code)}
                                </p>

                                <p className="mt-1 break-all text-slate-500">
                                  Runtime ID:{" "}
                                  {displayValue(workload.runtimeId)}
                                </p>
                              </li>
                            ))}
                          </ul>
                        )}

                        <Link
                          href="/assets"
                          className="mt-4 inline-block text-sm font-medium text-cyan-700 hover:underline"
                        >
                          Mở danh sách tài sản để tra cứu thêm
                        </Link>
                      </div>
                    )}
                  </article>
                ))}
              </div>
            </section>
          )}

          <p className="text-xs text-slate-500">
            Số liệu trên Dashboard được tính từ phản hồi GET /assets.
            Dashboard không suy diễn trạng thái online/offline hoặc
            telemetry của thiết bị.
          </p>
        </>
      )}
    </section>
  );
}
