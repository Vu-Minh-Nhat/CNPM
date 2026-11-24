import { StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { MarkerLookupResponse } from "../types/domain";

interface NodeDetailScreenProps {
  lookup: MarkerLookupResponse;
  onBackToScanner: () => void;
}

export function NodeDetailScreen({
  lookup,
  onBackToScanner,
}: NodeDetailScreenProps) {
  const { markerCode, markerStatus, node } = lookup;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Thông tin Node</Text>
      <Text style={styles.badge}>
        Marker: {markerCode} · Trạng thái: {markerStatus}
      </Text>

      <View style={styles.card}>
        <Text style={styles.row}>Node ID: {node.id}</Text>
        <Text style={styles.row}>Tên Node: {node.name}</Text>
        {node.code ? <Text style={styles.row}>Mã Node: {node.code}</Text> : null}
        {node.status ? (
          <Text style={styles.row}>Trạng thái Node: {node.status}</Text>
        ) : null}
        {node.rack ? <Text style={styles.row}>Rack: {node.rack}</Text> : null}
        {node.zone ? <Text style={styles.row}>Khu vực: {node.zone}</Text> : null}
        {node.ipAddress ? (
          <Text style={styles.row}>IP: {node.ipAddress}</Text>
        ) : null}
        {node.lastTelemetryAt ? (
          <Text style={styles.row}>
            Telemetry gần nhất: {node.lastTelemetryAt}
          </Text>
        ) : null}
      </View>

      <TouchableOpacity style={styles.backBtn} onPress={onBackToScanner}>
        <Text style={styles.backText}>Quét Marker khác</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f8fafc",
    padding: 20,
    paddingTop: 40,
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
  },
  row: {
    fontSize: 14,
    color: "#1e293b",
  },
  backBtn: {
    marginTop: 24,
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
