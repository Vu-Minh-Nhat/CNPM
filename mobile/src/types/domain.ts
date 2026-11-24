export type UserRole = "TECHNICIAN" | "OPERATOR" | "ADMIN" | string;

export interface UserProfile {
  id: string;
  email: string;
  name?: string;
  role: UserRole;
  allowedNodes?: string[];
  active?: boolean;
}

export type MarkerStatus =
  | "ACTIVE"
  | "DISABLED"
  | "INACTIVE"
  | "REVOKED"
  | string;

export interface NodeInfo {
  id: string;
  code?: string;
  name: string;
  status?: string;
  rack?: string;
  zone?: string;
  ipAddress?: string;
  lastTelemetryAt?: string;
}

export interface MarkerLookupResponse {
  markerCode: string;
  markerStatus: MarkerStatus;
  node: NodeInfo;
}

export type AppErrorKind =
  | "NETWORK"
  | "UNAUTHORIZED"
  | "FORBIDDEN"
  | "NOT_FOUND"
  | "DISABLED_MARKER"
  | "VALIDATION"
  | "SERVER";

export class AppError extends Error {
  kind: AppErrorKind;
  status?: number;

  constructor(kind: AppErrorKind, message: string, status?: number) {
    super(message);
    this.name = "AppError";
    this.kind = kind;
    this.status = status;
  }
}