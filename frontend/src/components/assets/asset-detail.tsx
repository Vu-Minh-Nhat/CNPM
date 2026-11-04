"use client";

import type { AssetNode } from "@/types/asset";

type AssetDetailProps = {
  asset: AssetNode;
  onClose: () => void;
};

function displayValue(value?: string | null): string {
  return value?.trim() || "Chưa có thông tin";
}

export default function AssetDetail({
  asset,
  onClose,
}: AssetDetailProps) {
  const rack = asset.rack;
  const room = rack?.room;
  const site = room?.site;

  const locations = [
    { label: "Rack", data: rack },
    { label: "Room", data: room },
    { label: "Site", data: site },
  ];

  return (
    <section
      id="asset-detail"
      aria-labelledby="asset-detail-title"
      className="mt-8 rounded-xl border border-cyan-200 bg-slate-50 p-4 sm:p-6"
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2
          id="asset-detail-title"
          className="text-xl font-bold text-slate-900"
        >
          Chi tiết: {displayValue(asset.code)}
        </h2>

        <button
          type="button"
          onClick={onClose}
          className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100"
        >
          Đóng chi tiết
        </button>
      </div>

      <dl className="mt-5 grid gap-4 sm:grid-cols-2">
        <div>
          <dt className="text-sm text-slate-500">Mã Node</dt>
          <dd className="mt-1 break-words font-medium">
            {displayValue(asset.code)}
          </dd>
        </div>

        <div>
          <dt className="text-sm text-slate-500">Tên Node</dt>
          <dd className="mt-1 break-words font-medium">
            {displayValue(asset.name)}
          </dd>
        </div>

        <div>
          <dt className="text-sm text-slate-500">Serial</dt>
          <dd className="mt-1 break-words font-medium">
            {displayValue(asset.serialNumber)}
          </dd>
        </div>

        <div>
          <dt className="text-sm text-slate-500">ID</dt>
          <dd className="mt-1 break-all text-sm">
            {asset.id}
          </dd>
        </div>
      </dl>

      <h3 className="mt-6 font-semibold text-slate-900">
        Vị trí: Rack → Room → Site
      </h3>

      <div className="mt-3 grid gap-3 lg:grid-cols-3">
        {locations.map(({ label, data }) => (
          <div
            key={label}
            className="rounded-lg border border-slate-200 bg-white p-4"
          >
            <h4 className="font-semibold text-cyan-800">
              {label}
            </h4>

            {data ? (
              <dl className="mt-3 space-y-2 text-sm">
                <div>
                  <dt className="text-slate-500">Mã</dt>
                  <dd className="break-words">
                    {displayValue(data.code)}
                  </dd>
                </div>

                <div>
                  <dt className="text-slate-500">Tên</dt>
                  <dd className="break-words">
                    {displayValue(data.name)}
                  </dd>
                </div>
              </dl>
            ) : (
              <p className="mt-3 text-sm text-slate-500">
                Chưa có thông tin {label}.
              </p>
            )}
          </div>
        ))}
      </div>

      <h3 className="mt-6 font-semibold text-slate-900">
        Workload
      </h3>

      {!Array.isArray(asset.workloads) ? (
        <p className="mt-3 text-sm text-slate-500">
          Chưa có dữ liệu Workload trong phản hồi.
        </p>
      ) : asset.workloads.length === 0 ? (
        <p className="mt-3 text-sm text-slate-500">
          Node chưa có Workload.
        </p>
      ) : (
        <div className="mt-3 overflow-x-auto rounded-lg border border-slate-200 bg-white">
          <table className="w-full min-w-[500px] text-left text-sm">
            <caption className="sr-only">
              Workload thuộc Node {asset.code}
            </caption>

            <thead className="bg-slate-100 text-slate-700">
              <tr>
                <th scope="col" className="px-4 py-3">
                  Mã Workload
                </th>
                <th scope="col" className="px-4 py-3">
                  Tên
                </th>
                <th scope="col" className="px-4 py-3">
                  Runtime ID
                </th>
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-100">
              {asset.workloads.map((workload) => (
                <tr key={workload.id}>
                  <th
                    scope="row"
                    className="px-4 py-3 font-medium"
                  >
                    {displayValue(workload.code)}
                  </th>

                  <td className="px-4 py-3">
                    {displayValue(workload.name)}
                  </td>

                  <td className="break-all px-4 py-3">
                    {displayValue(workload.runtimeId)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}