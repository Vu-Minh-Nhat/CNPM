import React from "react";
import { StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { ArMarkerLookupResult, TelemetryFreshnessStatus } from "../types/ar";

interface ArNodeOverlayProps {
  markerCode: string | null;
  snapshot: ArMarkerLookupResult | null;
  isLoading: boolean;
  isAppActive: boolean;
  error: string | null;
  onOpenDetail: (snapshot: ArMarkerLookupResult) => void;
  onClearMarker: () => void;
}

const STATUS_LABELS: Record<TelemetryFreshnessStatus, { text: string; bg: string; fg: string }> = {
  online: { text: "TRỰC TUYẾN • DỮ LIỆU MỚI", bg: "#14532D", fg: "#86EFAC" },
  stale: { text: "DỮ LIỆU CŨ (STALE)", bg: "#713F12", fg: "#FDE047" },
  offline: { text: "MẤT KẾT NỐI", bg: "#7F1D1D", fg: "#FCA5A5" },
  no_data: { text: "CHƯA CÓ DỮ LIỆU", bg: "#1E293B", fg: "#CBD5E1" },
};

function formatTimestamp(isoString: string | null): string {
  if (!isoString) return "Chưa có thời điểm đo";
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) return isoString;
  return date.toLocaleTimeString("vi-VN", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export const ArNodeOverlay: React.FC<ArNodeOverlayProps> = ({
  markerCode,
  snapshot,
  isLoading,
  isAppActive,
  error,
  onOpenDetail,
  onClearMarker,
}) => {
  if (!isAppActive) {
    return (
      <View style={styles.container}>
        <View style={styles.card}>
          <Text style={styles.badgeText}>ỨNG DỤNG ĐANG CHẠY NỀN</Text>
          <Text style={styles.subText}>
            Đã tạm dừng cập nhật telemetry và giải phóng phiên quét để tiết kiệm tài nguyên.
          </Text>
        </View>
      </View>
    );
  }

  if (!markerCode) {
    return (
      <View style={styles.container}>
        <View style={styles.card}>
          <Text style={styles.hintTitle}>Đang tìm Marker trong khung nhìn AR</Text>
          <Text style={styles.subText}>
            Hướng camera tới Marker gắn trên Rack/Node để hiển thị thông tin tài sản và giám sát.
          </Text>
        </View>
      </View>
    );
  }

  if (isLoading && !snapshot) {
    return (
      <View style={styles.container}>
        <View style={styles.card}>
          <Text style={styles.codeText}>MARKER: {markerCode}</Text>
          <Text style={styles.subText}>Đang tra cứu thông tin Node và telemetry mới nhất...</Text>
        </View>
      </View>
    );
  }

  if (!snapshot) {
    return (
      <View style={styles.container}>
        <View style={styles.card}>
          <Text style={styles.codeText}>MARKER: {markerCode}</Text>
          <Text style={styles.errorText}>{error ?? "Không có dữ liệu cho Marker này."}</Text>
          <TouchableOpacity style={styles.secondaryBtn} onPress={onClearMarker}>
            <Text style={styles.secondaryBtnText}>Bỏ khóa Marker</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  const badge = STATUS_LABELS[snapshot.telemetry.status];
  const { node, telemetry, alerts, isSimulated } = snapshot;

  return (
    <View style={styles.container} pointerEvents="box-none">
      <View style={styles.card}>
        <View style={styles.topRow}>
          <View style={[styles.statusBadge, { backgroundColor: badge.bg }]}>
            <Text style={[styles.statusText, { color: badge.fg }]}>{badge.text}</Text>
          </View>
          {isSimulated && (
            <View style={styles.simBadge}>
              <Text style={styles.simText}>DỮ LIỆU MÔ PHỎNG</Text>
            </View>
          )}
        </View>

        <Text style={styles.codeText}>
          {node.code} • {node.name}
        </Text>
        <Text style={styles.metaText}>Serial: {node.serial}</Text>
        <Text style={styles.locationText}>
          Vị trí: {node.location.site} → {node.location.room} → {node.location.rack}
        </Text>

        <View style={styles.metricsRow}>
          {telemetry.status === "no_data" || telemetry.metrics.length === 0 ? (
            <Text style={styles.subText}>Chưa có mẫu telemetry nào được ghi nhận.</Text>
          ) : (
            telemetry.metrics.map((m) => (
              <View key={m.key} style={styles.metricBox}>
                <Text style={styles.metricLabel}>{m.label}</Text>
                <Text style={styles.metricValue}>
                  {m.value ?? "-"}
                  {m.value !== null && m.value !== undefined ? m.unit : ""}
                </Text>
              </View>
            ))
          )}
        </View>

        <Text style={styles.timestampText}>
          Thời điểm đo: {formatTimestamp(telemetry.measuredAt)}
          {telemetry.ageSeconds !== null ? ` (${telemetry.ageSeconds}s trước)` : ""}
        </Text>

        <View style={styles.alertBox}>
          <Text style={styles.alertText}>
            Cảnh báo đang mở: {alerts.activeCount}
            {alerts.highestSeverity ? ` • Mức cao nhất: ${alerts.highestSeverity.toUpperCase()}` : ""}
          </Text>
          {alerts.latestTitle ? (
            <Text style={styles.alertSub} numberOfLines={1}>
              {alerts.latestTitle}
            </Text>
          ) : null}
        </View>

        {error ? <Text style={styles.errorText}>{error}</Text> : null}

        <View style={styles.actionsRow}>
          <TouchableOpacity style={styles.detailBtn} onPress={() => onOpenDetail(snapshot)}>
            <Text style={styles.detailBtnText}>Xem chi tiết Node</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.secondaryBtn} onPress={onClearMarker}>
            <Text style={styles.secondaryBtnText}>Đổi / Mất dấu</Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    position: "absolute",
    left: 12,
    right: 12,
    bottom: 20,
  },
  card: {
    backgroundColor: "rgba(15, 23, 42, 0.90)",
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    borderColor: "rgba(148, 163, 184, 0.35)",
  },
  topRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginBottom: 8,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  statusText: {
    fontSize: 11,
    fontWeight: "700",
  },
  simBadge: {
    backgroundColor: "#312E81",
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  simText: {
    color: "#C7D2FE",
    fontSize: 11,
    fontWeight: "700",
  },
  hintTitle: {
    color: "#F8FAFC",
    fontSize: 15,
    fontWeight: "700",
    marginBottom: 4,
  },
  codeText: {
    color: "#F8FAFC",
    fontSize: 15,
    fontWeight: "700",
  },
  metaText: {
    color: "#CBD5E1",
    fontSize: 12,
    marginTop: 2,
  },
  locationText: {
    color: "#38BDF8",
    fontSize: 12,
    fontWeight: "600",
    marginTop: 4,
  },
  metricsRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginTop: 10,
  },
  metricBox: {
    backgroundColor: "rgba(30, 41, 59, 0.95)",
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 6,
    minWidth: 78,
  },
  metricLabel: {
    color: "#94A3B8",
    fontSize: 11,
  },
  metricValue: {
    color: "#F8FAFC",
    fontSize: 14,
    fontWeight: "700",
    marginTop: 2,
  },
  timestampText: {
    color: "#94A3B8",
    fontSize: 11,
    marginTop: 8,
  },
  alertBox: {
    marginTop: 8,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: "rgba(148, 163, 184, 0.2)",
  },
  alertText: {
    color: "#FBBF24",
    fontSize: 12,
    fontWeight: "600",
  },
  alertSub: {
    color: "#E2E8F0",
    fontSize: 11,
    marginTop: 2,
  },
  subText: {
    color: "#CBD5E1",
    fontSize: 12,
    lineHeight: 17,
  },
  errorText: {
    color: "#F87171",
    fontSize: 12,
    marginTop: 6,
  },
  actionsRow: {
    flexDirection: "row",
    gap: 8,
    marginTop: 12,
  },
  detailBtn: {
    flex: 1,
    backgroundColor: "#0284C7",
    paddingVertical: 10,
    borderRadius: 8,
    alignItems: "center",
  },
  detailBtnText: {
    color: "#FFFFFF",
    fontSize: 13,
    fontWeight: "700",
  },
  secondaryBtn: {
    backgroundColor: "#334155",
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderRadius: 8,
    alignItems: "center",
  },
  secondaryBtnText: {
    color: "#E2E8F0",
    fontSize: 12,
    fontWeight: "600",
  },
});