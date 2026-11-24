
"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { getUserRole } from "@/lib/auth-storage";
import {
  createAlertRule,
  getAlertRules,
  setAlertRuleActive,
  updateAlertRule,
  type AlertRuleInput,
} from "@/lib/alerts";
import type { AlertRule, AlertSeverity } from "@/types/alert";

const METRICS = [
  { value: "cpu_percent", label: "CPU (%)" },
  { value: "memory_percent", label: "RAM (%)" },
  { value: "disk_percent", label: "Ổ đĩa (%)" },
] as const;

const OPERATORS = [">", ">=", "<", "<="] as const;

const SEVERITIES: AlertSeverity[] = [
  "LOW",
  "MEDIUM",
  "HIGH",
  "CRITICAL",
];

const emptyForm = {
  metric: "cpu_percent" as AlertRuleInput["metric"],
  operator: ">=" as AlertRuleInput["operator"],
  threshold: "80",
  severity: "HIGH" as AlertSeverity,
  recovery_operator: "<=" as AlertRuleInput["operator"],
  recovery_threshold: "",
};

export default function AlertRulesPage() {
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [role, setRole] = useState<string | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingActive, setEditingActive] = useState(true);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const isAdmin = role === "Administrator";

  const loadRules = useCallback(async (signal?: AbortSignal) => {
    try {
      setLoading(true);
      setError("");
      const data = await getAlertRules(signal);
      setRules(data);
    } catch (err) {
      if (err instanceof Error && err.name === "AbortError") return;
      setError(
        err instanceof Error
          ? err.message
          : "Không thể tải danh sách quy tắc cảnh báo.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    setRole(getUserRole());

    const controller = new AbortController();
    void loadRules(controller.signal);

    return () => controller.abort();
  }, [loadRules]);

  function resetForm() {
    setForm(emptyForm);
    setEditingId(null);
    setEditingActive(true);
  }

  function startEditing(rule: AlertRule) {
    setEditingId(rule.id);
    setEditingActive(rule.is_active);
    setForm({
      metric: rule.metric as AlertRuleInput["metric"],
      operator: rule.operator as AlertRuleInput["operator"],
      threshold: String(rule.threshold),
      severity: rule.severity,
      recovery_operator:
        (rule.recovery_operator as AlertRuleInput["operator"]) ?? "<=",
      recovery_threshold:
        rule.recovery_threshold === null
          ? ""
          : String(rule.recovery_threshold),
    });
    setError("");
    setMessage("");
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const threshold = Number(form.threshold);
    const recoveryThreshold =
      form.recovery_threshold.trim() === ""
        ? null
        : Number(form.recovery_threshold);

    if (
      !Number.isFinite(threshold) ||
      threshold < 0 ||
      threshold > 100
    ) {
      setError("Ngưỡng cảnh báo phải nằm trong khoảng 0 đến 100.");
      return;
    }

    if (
      recoveryThreshold !== null &&
      (!Number.isFinite(recoveryThreshold) ||
        recoveryThreshold < 0 ||
        recoveryThreshold > 100)
    ) {
      setError("Ngưỡng khôi phục phải nằm trong khoảng 0 đến 100.");
      return;
    }

    const payload: AlertRuleInput = {
      metric: form.metric,
      operator: form.operator,
      threshold,
      severity: form.severity,
      recovery_operator:
        recoveryThreshold === null ? null : form.recovery_operator,
      recovery_threshold: recoveryThreshold,
    };

    try {
      setSaving(true);
      setError("");
      setMessage("");

      if (editingId) {
        await updateAlertRule(editingId, {
          ...payload,
          is_active: editingActive,
        });
        setMessage("Đã cập nhật quy tắc cảnh báo.");
      } else {
        await createAlertRule(payload);
        setMessage("Đã tạo quy tắc cảnh báo.");
      }

      resetForm();
      await loadRules();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Không thể lưu quy tắc cảnh báo.",
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleToggle(rule: AlertRule) {
    try {
      setError("");
      setMessage("");
      await setAlertRuleActive(rule.id, !rule.is_active);
      setMessage(
        rule.is_active
          ? "Đã tắt quy tắc cảnh báo."
          : "Đã bật quy tắc cảnh báo.",
      );
      await loadRules();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Không thể thay đổi trạng thái quy tắc.",
      );
    }
  }

  function metricLabel(metric: string) {
    return METRICS.find((item) => item.value === metric)?.label ?? metric;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Cấu hình cảnh báo
        </h1>
        <p className="mt-1 text-sm text-slate-600">
          Quản lý các quy tắc giám sát CPU, RAM và dung lượng ổ đĩa.
        </p>
      </div>

      {error && (
        <div
          role="alert"
          className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700"
        >
          {error}
        </div>
      )}

      {message && (
        <div
          role="status"
          className="rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-700"
        >
          {message}
        </div>
      )}

      {isAdmin && (
        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-slate-900">
            {editingId ? "Chỉnh sửa quy tắc" : "Tạo quy tắc mới"}
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <label className="block text-sm font-medium text-slate-700">
                Chỉ số giám sát
                <select
                  value={form.metric}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      metric: e.target.value as AlertRuleInput["metric"],
                    })
                  }
                  className="mt-1 w-full rounded-lg border border-slate-300 p-2.5"
                >
                  {METRICS.map((item) => (
                    <option key={item.value} value={item.value}>
                      {item.label}
                    </option>
                  ))}
                </select>
              </label>

              <label className="block text-sm font-medium text-slate-700">
                Mức độ cảnh báo
                <select
                  value={form.severity}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      severity: e.target.value as AlertSeverity,
                    })
                  }
                  className="mt-1 w-full rounded-lg border border-slate-300 p-2.5"
                >
                  {SEVERITIES.map((severity) => (
                    <option key={severity} value={severity}>
                      {severity}
                    </option>
                  ))}
                </select>
              </label>

              <label className="block text-sm font-medium text-slate-700">
                Toán tử cảnh báo
                <select
                  value={form.operator}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      operator: e.target.value as AlertRuleInput["operator"],
                    })
                  }
                  className="mt-1 w-full rounded-lg border border-slate-300 p-2.5"
                >
                  {OPERATORS.map((operator) => (
                    <option key={operator} value={operator}>
                      {operator}
                    </option>
                  ))}
                </select>
              </label>

              <label className="block text-sm font-medium text-slate-700">
                Ngưỡng cảnh báo (0–100)
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  required
                  value={form.threshold}
                  onChange={(e) =>
                    setForm({ ...form, threshold: e.target.value })
                  }
                  className="mt-1 w-full rounded-lg border border-slate-300 p-2.5"
                />
              </label>

              <label className="block text-sm font-medium text-slate-700">
                Toán tử khôi phục
                <select
                  value={form.recovery_operator}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      recovery_operator:
                        e.target.value as AlertRuleInput["operator"],
                    })
                  }
                  className="mt-1 w-full rounded-lg border border-slate-300 p-2.5"
                >
                  {OPERATORS.map((operator) => (
                    <option key={operator} value={operator}>
                      {operator}
                    </option>
                  ))}
                </select>
              </label>

              <label className="block text-sm font-medium text-slate-700">
                Ngưỡng khôi phục (để trống nếu không dùng)
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  value={form.recovery_threshold}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      recovery_threshold: e.target.value,
                    })
                  }
                  className="mt-1 w-full rounded-lg border border-slate-300 p-2.5"
                />
              </label>
            </div>

            {editingId && (
              <label className="flex items-center gap-2 text-sm text-slate-700">
                <input
                  type="checkbox"
                  checked={editingActive}
                  onChange={(e) => setEditingActive(e.target.checked)}
                />
                Quy tắc đang hoạt động
              </label>
            )}

            <div className="flex flex-wrap gap-3">
              <button
                type="submit"
                disabled={saving}
                className="rounded-lg bg-cyan-700 px-5 py-2.5 text-sm font-semibold text-white hover:bg-cyan-800 disabled:opacity-50"
              >
                {saving
                  ? "Đang lưu..."
                  : editingId
                    ? "Lưu thay đổi"
                    : "Tạo quy tắc"}
              </button>

              {editingId && (
                <button
                  type="button"
                  onClick={resetForm}
                  className="rounded-lg border border-slate-300 px-5 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
                >
                  Hủy chỉnh sửa
                </button>
              )}
            </div>
          </form>
        </section>
      )}

      <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-200 p-5">
          <h2 className="text-lg font-semibold text-slate-900">
            Danh sách quy tắc
          </h2>
        </div>

        {loading ? (
          <p className="p-5 text-sm text-slate-500">
            Đang tải quy tắc cảnh báo...
          </p>
        ) : rules.length === 0 ? (
          <p className="p-5 text-sm text-slate-500">
            Chưa có quy tắc cảnh báo nào.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[850px] text-left text-sm">
              <thead className="bg-slate-50 text-slate-600">
                <tr>
                  <th className="px-5 py-3">Chỉ số</th>
                  <th className="px-5 py-3">Điều kiện</th>
                  <th className="px-5 py-3">Mức độ</th>
                  <th className="px-5 py-3">Khôi phục</th>
                  <th className="px-5 py-3">Trạng thái</th>
                  {isAdmin && <th className="px-5 py-3">Thao tác</th>}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {rules.map((rule) => (
                  <tr key={rule.id}>
                    <td className="px-5 py-4 font-medium text-slate-900">
                      {metricLabel(rule.metric)}
                    </td>
                    <td className="px-5 py-4 text-slate-700">
                      {rule.operator} {rule.threshold}%
                    </td>
                    <td className="px-5 py-4">{rule.severity}</td>
                    <td className="px-5 py-4 text-slate-700">
                      {rule.recovery_operator &&
                      rule.recovery_threshold !== null
                        ? `${rule.recovery_operator} ${rule.recovery_threshold}%`
                        : "Không cấu hình"}
                    </td>
                    <td className="px-5 py-4">
                      <span
                        className={
                          rule.is_active
                            ? "rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-700"
                            : "rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600"
                        }
                      >
                        {rule.is_active ? "Đang bật" : "Đã tắt"}
                      </span>
                    </td>
                    {isAdmin && (
                      <td className="px-5 py-4">
                        <div className="flex gap-3">
                          <button
                            type="button"
                            onClick={() => startEditing(rule)}
                            className="font-medium text-cyan-700 hover:underline"
                          >
                            Sửa
                          </button>
                          <button
                            type="button"
                            onClick={() => void handleToggle(rule)}
                            className="font-medium text-slate-700 hover:underline"
                          >
                            {rule.is_active ? "Tắt" : "Bật"}
                          </button>
                        </div>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
