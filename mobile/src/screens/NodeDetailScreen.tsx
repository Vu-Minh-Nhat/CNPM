import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";

import { apiRequest } from "../api/apiClient";
import { MarkerLookupResponse } from "../types/domain";

interface NodeDetailScreenProps {
  lookup: MarkerLookupResponse;
  onBackToScanner: () => void;
}

interface LatestTelemetryResponse {
  node_id: string;
  latest: {
    cpu_percent: number;
    memory_percent: number;
    disk_percent: number;
    measured_at: string;
    received_at: string;
  } | null;
  monitoring: {
    connection_status: string;
    data_status: string;
    last_received_at: string | null;
  };
}

interface NodeAlert {
  id: string;
  severity: string;
  message: string;
  triggered_at: string;
}

interface NodeTicket {
  id: string;
  node_id: string;
  title: string;
  status: string;
  progress: number;
  version: number;
  work_notes: string | null;
  evidence: string | null;
}

function formatDate(value: string | null): string {
  if (!value) return "Chưa có";

  const date = new Date(value);

  return Number.isNaN(date.getTime())
    ? value
    : date.toLocaleString("vi-VN");
}

function connectionLabel(status: string): string {
  switch (status) {
    case "online":
      return "Đang kết nối";
    case "offline":
      return "Mất kết nối";
    case "never_seen":
      return "Chưa từng nhận dữ liệu";
    default:
      return status;
  }
}

function dataLabel(status: string): string {
  switch (status) {
    case "fresh":
      return "Dữ liệu còn mới";
    case "stale":
      return "Dữ liệu cũ";
    case "no_data":
      return "Chưa có dữ liệu";
    default:
      return status;
  }
}

function ticketStatusLabel(status: string): string {
  switch (status) {
    case "NEW":
      return "Mới";
    case "ASSIGNED":
      return "Đã phân công";
    case "IN_PROGRESS":
      return "Đang xử lý";
    case "PENDING_APPROVAL":
      return "Chờ duyệt";
    case "CLOSED":
      return "Đã đóng";
    default:
      return status;
  }
}

function TicketWorkForm({ ticket, onUpdated }: {
  ticket: NodeTicket;
  onUpdated: (ticket: NodeTicket) => void;
}) {
  const [progress, setProgress] = useState(String(ticket.progress));
  const [notes, setNotes] = useState(ticket.work_notes ?? "");
  const [evidence, setEvidence] = useState(ticket.evidence ?? "");
  const [result, setResult] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  async function save() {
    const value = Number(progress);
    if (!/^\d+$/.test(progress) || !Number.isInteger(value) || value < 0 || value > 100) {
      setMessage("Tiến độ phải là số nguyên từ 0 đến 100.");
      return;
    }
    setBusy(true);
    setMessage("");
    try {
      const body: { version: number; progress: number; work_notes?: string; evidence?: string } = {
        version: ticket.version, progress: value,
      };
      if (notes.trim()) body.work_notes = notes.trim();
      if (evidence.trim()) body.evidence = evidence.trim();
      const updated = await apiRequest<NodeTicket>(`/tickets/${encodeURIComponent(ticket.id)}/work`, {
        method: "PATCH", body,
      });
      onUpdated(updated);
      setMessage("Đã cập nhật công việc.");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Không thể cập nhật công việc.");
    } finally {
      setBusy(false);
    }
  }

  async function submit() {
    if (!result.trim()) {
      setMessage("Vui lòng nhập kết quả xử lý trước khi gửi duyệt.");
      return;
    }
    setBusy(true);
    setMessage("");
    try {
      const updated = await apiRequest<NodeTicket>(`/tickets/${encodeURIComponent(ticket.id)}/submit`, {
        method: "POST",
        body: { version: ticket.version, result: result.trim() },
      });
      onUpdated(updated);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Không thể gửi duyệt.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <View style={styles.ticket}>
      <Text style={styles.row}>Tiến độ (0–100)</Text>
      <TextInput style={styles.input} keyboardType="numeric" value={progress} onChangeText={setProgress} />
      <Text style={styles.row}>Ghi chú công việc</Text>
      <TextInput style={styles.input} value={notes} onChangeText={setNotes} multiline />
      <Text style={styles.row}>Bằng chứng (văn bản hoặc đường dẫn)</Text>
      <TextInput style={styles.input} value={evidence} onChangeText={setEvidence} multiline />
      <TouchableOpacity style={styles.backBtn} disabled={busy} onPress={() => void save()}>
        <Text style={styles.backText}>{busy ? "Đang lưu..." : "Lưu tiến độ"}</Text>
      </TouchableOpacity>
      <Text style={styles.row}>Kết quả xử lý</Text>
      <TextInput style={styles.input} value={result} onChangeText={setResult} multiline />
      <TouchableOpacity style={styles.backBtn} disabled={busy} onPress={() => void submit()}>
        <Text style={styles.backText}>{busy ? "Đang gửi..." : "Gửi duyệt"}</Text>
      </TouchableOpacity>
      {message ? <Text style={styles.row}>{message}</Text> : null}
    </View>
  );
}

interface TicketHistoryEntry {
  id: string;
  action: string;
  actor_email: string | null;
  actor_id: string;
  created_at: string;
  note: string | null;
}

interface TicketDetail extends NodeTicket {
  description: string;
  result: string | null;
  history: TicketHistoryEntry[];
}

function TicketDetails({ ticketId }: { ticketId: string }) {
  const [detail, setDetail] = useState<TicketDetail | null>(null);
  const [detailError, setDetailError] = useState("");
  const [loadingDetail, setLoadingDetail] = useState(true);

  useEffect(() => {
    let active = true;
    setLoadingDetail(true);
    setDetail(null);
    setDetailError("");
    apiRequest<TicketDetail>(`/tickets/${encodeURIComponent(ticketId)}`)
      .then((data) => { if (active) setDetail(data); })
      .catch((error) => { if (active) setDetailError(error instanceof Error ? error.message : "Không thể tải chi tiết ticket."); })
      .finally(() => { if (active) setLoadingDetail(false); });
    return () => { active = false; };
  }, [ticketId]);

  if (loadingDetail) return <ActivityIndicator size="small" color="#0284c7" />;
  if (detailError) return <Text style={styles.error}>{detailError}</Text>;
  if (!detail) return null;
  return (
    <View style={styles.ticket}>
      <Text style={styles.row}>Mô tả: {detail.description || "Chưa có"}</Text>
      <Text style={styles.row}>Ghi chú: {detail.work_notes || "Chưa có"}</Text>
      <Text style={styles.row}>Bằng chứng: {detail.evidence || "Chưa có"}</Text>
      <Text style={styles.row}>Kết quả: {detail.result || "Chưa có"}</Text>
      <Text style={styles.ticketTitle}>Lịch sử xử lý</Text>
      {detail.history.length === 0 ? <Text style={styles.row}>Chưa có lịch sử.</Text> : detail.history.map((entry) => (
        <View key={entry.id}>
          <Text style={styles.row}>{entry.action} · {entry.actor_email || entry.actor_id}</Text>
          <Text style={styles.hint}>{formatDate(entry.created_at)}</Text>
          {entry.note ? <Text style={styles.row}>Ghi chú: {entry.note}</Text> : null}
        </View>
      ))}
    </View>
  );
}

export function NodeDetailScreen({
  lookup,
  onBackToScanner,
}: NodeDetailScreenProps) {
  const { markerCode, markerStatus, node } = lookup;

  const [telemetry, setTelemetry] =
    useState<LatestTelemetryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [alertCount, setAlertCount] = useState<number | null>(null);
  const [alertError, setAlertError] = useState("");
  const [alerts, setAlerts] = useState<NodeAlert[]>([]);

  const [tickets, setTickets] = useState<NodeTicket[]>([]);
  const [ticketsLoading, setTicketsLoading] = useState(true);
  const [ticketsError, setTicketsError] = useState("");
  const [detailTicketId, setDetailTicketId] = useState<string | null>(null);
  const [startingTicketId, setStartingTicketId] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    let timer: ReturnType<typeof setTimeout> | undefined;

    async function loadTelemetry(): Promise<void> {
      try {
        const data = await apiRequest<LatestTelemetryResponse>(
          `/telemetry/nodes/${encodeURIComponent(node.id)}/latest`,
        );

        if (!active) return;

        setTelemetry(data);
        setError("");
      } catch (loadError) {
        if (!active) return;

        setError(
          loadError instanceof Error
            ? loadError.message
            : "Không thể tải dữ liệu giám sát.",
        );
      } finally {
        if (active) {
          setLoading(false);
          timer = setTimeout(() => void loadTelemetry(), 5000);
        }
      }
    }

    setLoading(true);
    setTelemetry(null);
    setError("");
    void loadTelemetry();
    return () => {
      active = false;
      if (timer) clearTimeout(timer);
    };
  }, [node.id]);

  useEffect(() => {
    let active = true;
    let timer: ReturnType<typeof setTimeout> | undefined;

    async function loadAlerts(): Promise<void> {
      try {
        const data = await apiRequest<{
          items: NodeAlert[];
          pagination: { total: number };
        }>("/alerts", {
          query: {
            node_id: node.id,
            status: "FIRING",
            page: 1,
            page_size: 20,
          },
        });

        if (!active) return;

        setAlertCount(data.pagination.total);
        setAlerts(data.items);
        setAlertError("");
      } catch {
        if (!active) return;

        setAlertError("Không thể tải cảnh báo.");
      } finally {
        if (active) {
          timer = setTimeout(() => void loadAlerts(), 5000);
        }
      }
    }

    setAlertCount(null);
    setAlerts([]);
    setAlertError("");
    void loadAlerts();

    return () => {
      active = false;
      if (timer) clearTimeout(timer);
    };
  }, [node.id]);

  useEffect(() => {
    let active = true;

    async function loadTickets(): Promise<void> {
      try {
        const data = await apiRequest<NodeTicket[]>("/tickets");

        if (!active) return;

        setTickets(data.filter((ticket) => ticket.node_id === node.id));
        setTicketsError("");
      } catch (loadError) {
        if (!active) return;

        setTicketsError(
          loadError instanceof Error
            ? loadError.message
            : "Không thể tải danh sách ticket.",
        );
      } finally {
        if (active) {
          setTicketsLoading(false);
        }
      }
    }

    setTickets([]);
    setTicketsError("");
    setTicketsLoading(true);
    void loadTickets();

    return () => {
      active = false;
    };
  }, [node.id]);

  async function handleStartTicket(ticket: NodeTicket): Promise<void> {
    setStartingTicketId(ticket.id);
    setTicketsError("");

    try {
      await apiRequest(`/tickets/${encodeURIComponent(ticket.id)}/start`, {
        method: "POST",
        body: { version: ticket.version },
      });

      const data = await apiRequest<NodeTicket[]>("/tickets");
      setTickets(data.filter((item) => item.node_id === node.id));
    } catch (startError) {
      setTicketsError(
        startError instanceof Error
          ? startError.message
          : "Không thể bắt đầu xử lý ticket.",
      );

      // Tải lại để hiển thị trạng thái mới nếu ticket đã thay đổi.
      try {
        const data = await apiRequest<NodeTicket[]>("/tickets");
        setTickets(data.filter((item) => item.node_id === node.id));
      } catch {
        // Giữ thông báo lỗi của thao tác ban đầu.
      }
    } finally {
      setStartingTicketId(null);
    }
  }

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
    >
      <Text style={styles.title}>Thông tin Node</Text>

      <Text style={styles.badge}>
        Marker: {markerCode} · Trạng thái: {markerStatus}
      </Text>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Thông tin thiết bị</Text>
        <Text style={styles.row}>Node ID: {node.id}</Text>
        <Text style={styles.row}>Tên Node: {node.name}</Text>

        {node.code ? (
          <Text style={styles.row}>Mã Node: {node.code}</Text>
        ) : null}

        {node.rack ? (
          <Text style={styles.row}>Rack: {node.rack}</Text>
        ) : null}

        <Text style={styles.row}>
          Room: {node.room ?? "Chưa có thông tin"}
        </Text>

        <Text style={styles.row}>
          Site: {node.site ?? "Chưa có thông tin"}
        </Text>

        <Text style={styles.row}>
          Workload:{" "}
          {node.workloads?.length
            ? node.workloads.join(", ")
            : "Chưa có workload"}
        </Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Giám sát Node</Text>

        <Text style={styles.row}>
          Cảnh báo đang phát sinh:{" "}
          {alertCount === null ? "Chưa tải được" : alertCount}
        </Text>

        {alertError ? (
          <Text style={styles.error}>{alertError}</Text>
        ) : null}

        {loading ? (
          <ActivityIndicator size="small" color="#0284c7" />
        ) : null}

        {error ? <Text style={styles.error}>{error}</Text> : null}

        {telemetry ? (
          <>
            <Text style={styles.row}>
              Kết nối:{" "}
              {connectionLabel(telemetry.monitoring.connection_status)}
            </Text>

            <Text style={styles.row}>
              Trạng thái dữ liệu:{" "}
              {dataLabel(telemetry.monitoring.data_status)}
            </Text>

            {telemetry.latest ? (
              <>
                <Text style={styles.row}>
                  CPU: {telemetry.latest.cpu_percent}%
                </Text>

                <Text style={styles.row}>
                  RAM: {telemetry.latest.memory_percent}%
                </Text>

                <Text style={styles.row}>
                  Disk: {telemetry.latest.disk_percent}%
                </Text>

                <Text style={styles.row}>
                  Thời điểm đo: {formatDate(telemetry.latest.measured_at)}
                </Text>
              </>
            ) : (
              <Text style={styles.row}>Node chưa có mẫu telemetry.</Text>
            )}

            <Text style={styles.row}>
              Nhận gần nhất:{" "}
              {formatDate(telemetry.monitoring.last_received_at)}
            </Text>

            {error ? (
              <Text style={styles.warning}>
                Không cập nhật được; dữ liệu trên là lần tải thành công gần
                nhất.
              </Text>
            ) : null}
          </>
        ) : null}

        <Text style={styles.hint}>
          Telemetry và cảnh báo tự cập nhật khoảng 5 giây một lần.
        </Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Cảnh báo đang phát sinh</Text>
        {alertError ? <Text style={styles.error}>{alertError}</Text> : null}
        {alertCount === null ? (
          <Text style={styles.row}>Chưa tải được danh sách cảnh báo.</Text>
        ) : alerts.length === 0 ? (
          <Text style={styles.row}>Không có cảnh báo đang phát sinh.</Text>
        ) : (
          alerts.map((alert) => (
            <View key={alert.id} style={styles.ticket}>
              <Text style={styles.ticketTitle}>Mức độ: {alert.severity}</Text>
              <Text style={styles.row}>{alert.message}</Text>
              <Text style={styles.row}>Phát sinh: {formatDate(alert.triggered_at)}</Text>
            </View>
          ))
        )}
        {alertCount !== null && alertCount > alerts.length ? (
          <Text style={styles.hint}>Hiển thị {alerts.length} / {alertCount} cảnh báo.</Text>
        ) : null}
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Ticket của Node</Text>

        {ticketsLoading ? (
          <ActivityIndicator size="small" color="#0284c7" />
        ) : ticketsError ? (
          <Text style={styles.error}>{ticketsError}</Text>
        ) : tickets.length === 0 ? (
          <Text style={styles.row}>
            Không có ticket được hiển thị cho Node này.
          </Text>
        ) : (
          tickets.map((ticket) => (
            <View key={ticket.id} style={styles.ticket}>
              <Text style={styles.ticketTitle}>{ticket.title}</Text>
              <Text style={styles.row}>
                Trạng thái: {ticketStatusLabel(ticket.status)}
              </Text>
              <Text style={styles.row}>
                Tiến độ: {ticket.progress}%
              </Text>
              <TouchableOpacity style={styles.backBtn} onPress={() => setDetailTicketId(detailTicketId === ticket.id ? null : ticket.id)}>
                <Text style={styles.backText}>{detailTicketId === ticket.id ? "Ẩn chi tiết và lịch sử" : "Xem chi tiết và lịch sử"}</Text>
              </TouchableOpacity>
              {detailTicketId === ticket.id ? <TicketDetails key={`${ticket.id}-${ticket.version}`} ticketId={ticket.id} /> : null}
              {ticket.status === "IN_PROGRESS" ? (
                <TicketWorkForm ticket={ticket} onUpdated={(updated) => {
                  setTickets((current) => current.map((item) => item.id === updated.id ? updated : item));
                }} />
              ) : null}
              {ticket.status === "ASSIGNED" ? (
  <TouchableOpacity
    style={styles.backBtn}
    disabled={startingTicketId !== null}
    onPress={() => void handleStartTicket(ticket)}
  >
    <Text style={styles.backText}>
      {startingTicketId === ticket.id
        ? "Đang xử lý..."
        : "Bắt đầu xử lý"}
    </Text>
  </TouchableOpacity>
) : null}
            </View>
          ))
        )}
      </View>

      <TouchableOpacity
        style={styles.backBtn}
        onPress={onBackToScanner}
      >
        <Text style={styles.backText}>Quét Marker khác</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f8fafc",
  },
  content: {
    padding: 20,
    paddingTop: 40,
    paddingBottom: 40,
  },
  title: {
    fontSize: 22,
    fontWeight: "700",
    color: "#0f172a",
  },
  badge: {
    fontSize: 13,
    color: "#0284c7",
    fontWeight: "600",
    marginTop: 6,
    marginBottom: 16,
  },
  card: {
    backgroundColor: "#fff",
    borderRadius: 10,
    padding: 16,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    gap: 8,
    marginBottom: 16,
  },
  cardTitle: {
    fontSize: 17,
    fontWeight: "700",
    color: "#0f172a",
    marginBottom: 4,
  },
  row: {
    fontSize: 14,
    color: "#1e293b",
  },
  input: { borderWidth: 1, borderColor: "#cbd5e1", borderRadius: 8, padding: 10, color: "#0f172a" },
  ticket: {
    borderTopWidth: 1,
    borderTopColor: "#e2e8f0",
    paddingTop: 10,
    marginTop: 4,
    gap: 4,
  },
  ticketTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: "#0f172a",
  },
  error: {
    color: "#b91c1c",
    fontSize: 14,
  },
  warning: {
    color: "#b45309",
    fontSize: 13,
  },
  hint: {
    color: "#64748b",
    fontSize: 12,
    marginTop: 8,
  },
  backBtn: {
    backgroundColor: "#0284c7",
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: "center",
  },
  backText: {
    color: "#fff",
    fontWeight: "700",
    fontSize: 14,
  },
});