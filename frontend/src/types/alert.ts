export type AlertStatus =
  | "FIRING"
  | "ACKNOWLEDGED"
  | "RECOVERED";

export type AlertSeverity =
  | "LOW"
  | "MEDIUM"
  | "HIGH"
  | "CRITICAL";

export interface Alert {
  id: string;
  node_id: string;
  rule_id: string | null;
  metric: string;
  operator: string;
  threshold: number | null;
  severity: AlertSeverity;
  status: AlertStatus;
  message: string;
  triggered_at: string;
  acknowledged_at: string | null;
  recovered_at: string | null;
}

export interface AlertRule {
  id: string;
  metric: string;
  operator: string;
  threshold: number;
  severity: AlertSeverity;
  recovery_operator: string | null;
  recovery_threshold: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
