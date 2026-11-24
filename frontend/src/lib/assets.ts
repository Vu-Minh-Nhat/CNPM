import { apiFetch } from "@/lib/api-client";
import type { AssetNode } from "@/types/asset";

export async function getAssets(
  signal?: AbortSignal,
): Promise<AssetNode[]> {
  const data = await apiFetch<AssetNode[]>("/assets", {
    method: "GET",
    signal,
  });

  if (!Array.isArray(data)) {
    throw new Error("Dữ liệu danh sách tài sản không hợp lệ.");
  }

  return data;
}