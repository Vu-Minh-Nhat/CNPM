import { apiFetch } from "@/lib/api-client";
import type { Alert, AlertRule, AlertSeverity } from "@/types/alert";

export interface AlertFilters {
  status?: string;
  severity?: string;
}

export async function getAlerts(
  filters: AlertFilters = {},
  signal?: AbortSignal,
): Promise<Alert[]> {
  const params = new URLSearchParams();

  if (filters.status) params.set("status", filters.status);
  if (filters.severity) params.set("severity", filters.severity);

  const query = params.toString();
  const data = await apiFetch<Alert[]>(
    `/alerts${query ? `?${query}` : ""}`,
    { method: "GET", signal },
  );

  if (!Array.isArray(data)) {
    throw new Error("Dữ liệu danh sách cảnh báo không hợp lệ.");
  }

  return data;
}

export async function getAlert(
  alertId: string,
  signal?: AbortSignal,
): Promise<Alert> {
  return apiFetch<Alert>(`/alerts/${encodeURIComponent(alertId)}`, {
    method: "GET",
    signal,
  });
}

export async function acknowledgeAlert(
  alertId: string,
): Promise<Alert> {
  return apiFetch<Alert>(
    `/alerts/${encodeURIComponent(alertId)}/acknowledge`,
    { method: "PATCH" },
  );
}

export interface AlertRuleInput {
  metric: "cpu_percent" | "memory_percent" | "disk_percent";
  operator: ">" | ">=" | "<" | "<=";
  threshold: number;
  severity: AlertSeverity;
  recovery_operator?: ">" | ">=" | "<" | "<=" | null;
  recovery_threshold?: number | null;
}

export async function getAlertRules(
  signal?: AbortSignal,
): Promise<AlertRule[]> {
  const data = await apiFetch<AlertRule[]>("/alerts/rules", {
    method: "GET",
    signal,
  });

  if (!Array.isArray(data)) {
    throw new Error("Dữ liệu quy tắc cảnh báo không hợp lệ.");
  }

  return data;
}

export async function createAlertRule(
  payload: AlertRuleInput,
): Promise<AlertRule> {
  return apiFetch<AlertRule>("/alerts/rules", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateAlertRule(
  ruleId: string,
  payload: AlertRuleInput & { is_active: boolean },
): Promise<AlertRule> {
  return apiFetch<AlertRule>(
    `/alerts/rules/${encodeURIComponent(ruleId)}`,
    {
      method: "PUT",
      body: JSON.stringify(payload),
    },
  );
}

export async function setAlertRuleActive(
  ruleId: string,
  isActive: boolean,
): Promise<AlertRule> {
  return apiFetch<AlertRule>(
    `/alerts/rules/${encodeURIComponent(ruleId)}/active`,
    {
      method: "PATCH",
      body: JSON.stringify({ is_active: isActive }),
    },
  );
}