export interface AssetLocationSummary {
  siteCode?: string | null;
  siteName?: string | null;
  roomCode?: string | null;
  roomName?: string | null;
  rackCode?: string | null;
  rackName?: string | null;
  formatted?: string | null;
}

export interface WorkloadSummary {
  id: string;
  code?: string;
  name?: string;
  nodeId?: string;
  runtimeId?: string | null;
}

export interface AssetOverviewItem {
  id: string;
  code?: string;
  name: string;
  assetKind: "node" | "workload";
  serialNumber?: string | null;
  workloadCount: number;
  workloads: WorkloadSummary[];
  location: AssetLocationSummary;
}

export interface AssetsOverviewData {
  nodeCount: number;
  workloadCount: number;
  siteCount: number;
  roomCount: number;
  rackCount: number;
  items: AssetOverviewItem[];
}

function getApiBaseUrl(): string {
  return (
    process.env.EXPO_PUBLIC_API_BASE_URL ??
    process.env.NEXT_PUBLIC_API_BASE_URL ??
    "http://127.0.0.1:5002"
  ).replace(/\/+$/, "");
}

function extractRawEntries(payload: unknown): Record<string, unknown>[] {
  if (!payload || typeof payload !== "object") return [];
  if (Array.isArray(payload)) {
    return payload.filter(
      (item): item is Record<string, unknown> =>
        Boolean(item && typeof item === "object")
    );
  }

  const obj = payload as Record<string, unknown>;
  for (const key of ["assets", "nodes", "items", "data"]) {
    if (Array.isArray(obj[key])) {
      return (obj[key] as unknown[]).filter(
        (item): item is Record<string, unknown> =>
          Boolean(item && typeof item === "object")
      );
    }
  }

  return [obj];
}

function parseLocation(rawNode: Record<string, unknown>): AssetLocationSummary {
  const rack =
    rawNode.rack && typeof rawNode.rack === "object"
      ? (rawNode.rack as Record<string, unknown>)
      : null;
  const room =
    rack && rack.room && typeof rack.room === "object"
      ? (rack.room as Record<string, unknown>)
      : null;
  const site =
    room && room.site && typeof room.site === "object"
      ? (room.site as Record<string, unknown>)
      : null;

  const siteCode =
    typeof site?.code === "string" && site.code.trim() ? site.code.trim() : null;
  const siteName =
    typeof site?.name === "string" && site.name.trim() ? site.name.trim() : null;
  const roomCode =
    typeof room?.code === "string" && room.code.trim() ? room.code.trim() : null;
  const roomName =
    typeof room?.name === "string" && room.name.trim() ? room.name.trim() : null;
  const rackCode =
    typeof rack?.code === "string" && rack.code.trim() ? rack.code.trim() : null;
  const rackName =
    typeof rack?.name === "string" && rack.name.trim() ? rack.name.trim() : null;

  const parts = [
    siteCode ?? siteName,
    roomCode ?? roomName,
    rackCode ?? rackName,
  ].filter((part): part is string => Boolean(part));

  return {
    siteCode,
    siteName,
    roomCode,
    roomName,
    rackCode,
    rackName,
    formatted: parts.length > 0 ? parts.join(" -> ") : null,
  };
}

function parseWorkloads(rawNode: Record<string, unknown>): WorkloadSummary[] {
  if (!Array.isArray(rawNode.workloads)) return [];
  return rawNode.workloads
    .filter(
      (w): w is Record<string, unknown> => Boolean(w && typeof w === "object")
    )
    .map((w, idx) => ({
      id: String(w.id ?? `workload-${idx + 1}`),
      code: typeof w.code === "string" ? w.code : undefined,
      name: typeof w.name === "string" ? w.name : undefined,
      nodeId: typeof w.nodeId === "string" ? w.nodeId : undefined,
      runtimeId:
        typeof w.runtimeId === "string" || w.runtimeId === null
          ? (w.runtimeId as string | null)
          : undefined,
    }));
}

export async function fetchAssetsOverview(
  accessToken?: string | null,
  signal?: AbortSignal
): Promise<AssetsOverviewData> {
  const baseUrl = getApiBaseUrl();
  const headers: Record<string, string> = {
    Accept: "application/json",
  };
  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
  }

  const response = await fetch(`${baseUrl}/assets`, {
    method: "GET",
    headers,
    signal,
  });

  if (!response.ok) {
    let message = `Loi goi GET /assets (HTTP ${response.status})`;
    try {
      const errJson = (await response.json()) as {
        message?: string;
        error?: string;
      };
      message = errJson.message ?? errJson.error ?? message;
    } catch {
      // Bo qua neu body loi khong phai JSON
    }
    throw new Error(message);
  }

  const payload = (await response.json()) as unknown;
  const rawEntries = extractRawEntries(payload);

  const sites = new Set<string>();
  const rooms = new Set<string>();
  const racks = new Set<string>();

  let nodeCount = 0;
  let workloadCount = 0;
  const items: AssetOverviewItem[] = [];

  rawEntries.forEach((raw, idx) => {
    const id = String(raw.id ?? `node-${idx + 1}`);
    const code = typeof raw.code === "string" ? raw.code : undefined;
    const name =
      typeof raw.name === "string" && raw.name.trim()
        ? raw.name.trim()
        : code ?? id;
    const serialNumber =
      typeof raw.serialNumber === "string" || raw.serialNumber === null
        ? (raw.serialNumber as string | null)
        : null;

    const workloads = parseWorkloads(raw);
    const location = parseLocation(raw);

    nodeCount += 1;
    workloadCount += workloads.length;

    const siteKey = location.siteCode ?? location.siteName;
    const roomKey = location.roomCode ?? location.roomName;
    const rackKey = location.rackCode ?? location.rackName;

    if (siteKey) sites.add(siteKey);
    if (roomKey) rooms.add(roomKey);
    if (rackKey) racks.add(rackKey);

    items.push({
      id,
      code,
      name,
      assetKind: "node",
      serialNumber,
      workloadCount: workloads.length,
      workloads,
      location,
    });
  });

  return {
    nodeCount,
    workloadCount,
    siteCount: sites.size,
    roomCount: rooms.size,
    rackCount: racks.size,
    items,
  };
}
