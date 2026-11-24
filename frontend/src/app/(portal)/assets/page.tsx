"use client";

import { useEffect, useState } from "react";
import { getAssets } from "@/lib/assets";
import type { AssetNode } from "@/types/asset";
import AssetDetail from "@/components/assets/asset-detail";

function displayValue(value?: string | null): string {
  return value?.trim() || "Chưa có thông tin";
}

function getLocation(asset: AssetNode): string {
  const rack = asset.rack;
  const room = rack?.room;
  const site = room?.site;

  return (
    [
      site?.name || site?.code,
      room?.name || room?.code,
      rack?.name || rack?.code,
    ]
      .filter(Boolean)
      .join(" / ") || "Chưa có vị trí"
  );
}

export default function AssetsPage() {
  const [assets, setAssets] = useState<AssetNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [siteId, setSiteId] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    async function loadAssets() {
      try {
        const data = await getAssets(controller.signal);

        if (!controller.signal.aborted) {
          setAssets(data);
        }
      } catch (err) {
        if (controller.signal.aborted) return;

        setError(
          err instanceof Error
            ? err.message
            : "Không thể tải danh sách tài sản.",
        );
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    void loadAssets();

    return () => controller.abort();
  }, []);

  const normalizedSearch = search.trim().toLocaleLowerCase("vi");

  const sites = Array.from(
    new Map(
      assets.flatMap((asset) => {
        const site = asset.rack?.room?.site;

        return site ? [[site.id, site] as const] : [];
      }),
    ).values(),
  ).sort((first, second) =>
    first.name.localeCompare(second.name, "vi"),
  );

  const filteredAssets = assets.filter((asset) => {
    const assetSiteId = asset.rack?.room?.site?.id;
    const matchesSite = !siteId || assetSiteId === siteId;

    const searchableText = [
      asset.code,
      asset.name,
      asset.serialNumber,
      getLocation(asset),
    ]
      .filter(Boolean)
      .join(" ")
      .toLocaleLowerCase("vi");

    return matchesSite && searchableText.includes(normalizedSearch);
  });
  const selectedAsset = assets.find((asset) => asset.id === selectedId);

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:p-6">
      <h1 className="text-2xl font-bold text-slate-900">
        Danh sách tài sản
      </h1>

      <p className="mt-2 text-sm text-slate-600">
        Tra cứu Node/Server và vị trí trong cây tài sản.
      </p>

      <div className="mt-6 grid gap-4 md:grid-cols-[minmax(0,1fr)_240px_auto] md:items-end">
        <div>
          <label
            htmlFor="asset-search"
            className="mb-2 block text-sm font-medium text-slate-700"
          >
            Tìm tài sản
          </label>

          <input
            id="asset-search"
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Nhập mã, tên, serial hoặc vị trí..."
            disabled={loading || !!error}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-cyan-600 focus:ring-2 focus:ring-cyan-100 disabled:bg-slate-100"
          />
        </div>

        <div>
          <label
            htmlFor="asset-site"
            className="mb-2 block text-sm font-medium text-slate-700"
          >
            Site
          </label>

          <select
            id="asset-site"
            value={siteId}
            onChange={(event) => setSiteId(event.target.value)}
            disabled={loading || !!error}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 disabled:bg-slate-100"
          >
            <option value="">Tất cả Site</option>

            {sites.map((site) => (
              <option key={site.id} value={site.id}>
                {site.name || site.code}
              </option>
            ))}
          </select>
        </div>

        <button
          type="button"
          onClick={() => {
            setSearch("");
            setSiteId("");
          }}
          disabled={!search && !siteId}
          className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Xóa bộ lọc
        </button>
      </div>

      {!loading && !error && assets.length > 0 && (
        <p role="status" className="mt-4 text-sm text-slate-500">
          Hiển thị {filteredAssets.length} / {assets.length} tài sản.
        </p>
      )}

      {loading && (
        <p role="status" className="mt-6 text-slate-600">
          Đang tải danh sách tài sản...
        </p>
      )}

      {!loading && error && (
        <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4">
          <p role="alert" className="text-red-700">
            {error}
          </p>

          <button
            type="button"
            onClick={() => window.location.reload()}
            className="mt-3 rounded-lg bg-red-700 px-4 py-2 text-sm font-medium text-white hover:bg-red-800"
          >
            Thử lại
          </button>
        </div>
      )}

      {!loading && !error && assets.length === 0 && (
        <p role="status" className="mt-6 text-slate-600">
          Chưa có tài sản trong hệ thống.
        </p>
      )}

      {!loading &&
        !error &&
        assets.length > 0 &&
        filteredAssets.length === 0 && (
          <p role="status" className="mt-6 text-slate-600">
            Không tìm thấy tài sản phù hợp. Hãy đổi từ khóa hoặc bộ lọc.
          </p>
        )}

      {!loading && !error && filteredAssets.length > 0 && (
        <div className="mt-6 overflow-x-auto">
          <table className="w-full min-w-[700px] text-left text-sm">
            <caption className="sr-only">
              Danh sách Node và Server
            </caption>

            <thead className="border-b border-slate-200 bg-slate-50 text-slate-700">
              <tr>
                <th scope="col" className="px-4 py-3">
                  Mã Node
                </th>
                <th scope="col" className="px-4 py-3">
                  Tên
                </th>
                <th scope="col" className="px-4 py-3">
                  Serial
                </th>
                <th scope="col" className="px-4 py-3">
                  Vị trí
                </th>
                <th scope="col" className="px-4 py-3">
                  Chi tiết
                </th>
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-100">
              {filteredAssets.map((asset) => (
                <tr key={asset.id} className="hover:bg-slate-50">
                  <th
                    scope="row"
                    className="px-4 py-4 font-semibold text-slate-900"
                  >
                    {displayValue(asset.code)}
                  </th>

                  <td className="px-4 py-4 text-slate-700">
                    {displayValue(asset.name)}
                  </td>

                  <td className="px-4 py-4 text-slate-700">
                    {displayValue(asset.serialNumber)}
                  </td>

                  <td className="px-4 py-4 text-slate-700">
                    {getLocation(asset)}
                    <td className="px-4 py-4">
                  <button
                    type="button"
                    onClick={() => setSelectedId(asset.id)}
                    aria-expanded={selectedId === asset.id}
                    aria-controls={
                    selectedId === asset.id ? "asset-detail" : undefined
                    }
                    className="rounded-lg bg-cyan-700 px-3 py-2 text-sm font-medium text-white hover:bg-cyan-800"
                    >
                  Xem chi tiết
                  </button>
                  </td>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {!loading && !error && selectedAsset && (
      <AssetDetail
        asset={selectedAsset}
        onClose={() => setSelectedId(null)}
      />
)}
    </section>
  );
}