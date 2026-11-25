import React from "react";
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { MarkerLookupResponse } from "../types/domain";

interface NodeDetailScreenProps {
  lookup: MarkerLookupResponse | null;
  onBackToScanner: () => void;
}

export const NodeDetailScreen: React.FC<NodeDetailScreenProps> = ({ lookup, onBackToScanner }) => {
  if (!lookup) {
    return (
      <View style={styles.container}>
        <Text style={styles.title}>Không có dữ liệu Node</Text>
        <TouchableOpacity style={styles.btn} onPress={onBackToScanner}>
          <Text style={styles.btnText}>Quay lại AR</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const { node, telemetry, alerts, isSimulated } = lookup;

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>
        {node.code} • {node.name}
      </Text>
      {isSimulated ? <Text style={styles.simLabel}>DỮ LIỆU MÔ PHỎNG</Text> : null}

      <Text style={styles.line}>ID: {node.id}</Text>
      <Text style={styles.line}>Serial: {node.serial}</Text>
      <Text style={styles.line}>
        Vị trí: {node.location.site} → {node.location.room} → {node.location.rack}
      </Text>
      <Text style={styles.line}>Trạng thái dữ liệu: {telemetry.status}</Text>
      <Text style={styles.line}>Thời điểm đo: {telemetry.measuredAt ?? "Chưa có"}</Text>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Telemetry mới nhất</Text>
        {telemetry.metrics.length === 0 ? (
          <Text style={styles.line}>Chưa có mẫu telemetry.</Text>
        ) : (
          telemetry.metrics.map((m) => (
            <Text key={m.key} style={styles.line}>
              • {m.label}: {m.value ?? "-"} {m.unit}
            </Text>
          ))
        )}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Cảnh báo</Text>
        <Text style={styles.line}>Đang mở: {alerts.activeCount}</Text>
        <Text style={styles.line}>Mức cao nhất: {alerts.highestSeverity ?? "Không có"}</Text>
        {alerts.latestTitle ? <Text style={styles.line}>Gần nhất: {alerts.latestTitle}</Text> : null}
      </View>

      <TouchableOpacity style={styles.btn} onPress={onBackToScanner}>
        <Text style={styles.btnText}>Quay lại khung nhìn AR</Text>
      </TouchableOpacity>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#020617" },
  content: { padding: 18 },
  title: { color: "#F8FAFC", fontSize: 20, fontWeight: "700" },
  simLabel: { color: "#C7D2FE", fontSize: 12, fontWeight: "700", marginTop: 6 },
  line: { color: "#E2E8F0", fontSize: 13, marginTop: 6 },
  section: {
    marginTop: 14,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: "rgba(148, 163, 184, 0.25)",
  },
  sectionTitle: { color: "#38BDF8", fontSize: 15, fontWeight: "700", marginBottom: 4 },
  btn: {
    marginTop: 20,
    backgroundColor: "#0284C7",
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: "center",
  },
  btnText: { color: "#FFFFFF", fontSize: 14, fontWeight: "700" },
});
