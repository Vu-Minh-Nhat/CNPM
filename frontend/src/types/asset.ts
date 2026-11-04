export type AssetSite = {
  id: string;
  code: string;
  name: string;
};

export type AssetRoom = {
  id: string;
  siteId: string;
  code: string;
  name: string;
  site?: AssetSite | null;
};

export type AssetRack = {
  id: string;
  roomId: string;
  code: string;
  name: string;
  capacityU: number;
  room?: AssetRoom | null;
};

export type AssetWorkload = {
  id: string;
  nodeId: string;
  code: string;
  name: string;
  runtimeId: string | null;
};

export type AssetNode = {
  id: string;
  rackId: string;
  code: string;
  name: string;
  serialNumber: string | null;
  rack?: AssetRack | null;
  workloads?: AssetWorkload[] | null;
};