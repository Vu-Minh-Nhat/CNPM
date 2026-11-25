import React, { useCallback, useMemo, useRef, useState } from "react";
import { StyleSheet, Text, TextInput, TouchableOpacity, View } from "react-native";
import { useAuth } from "../auth/AuthContext";
import { ArNodeOverlay } from "../components/ArNodeOverlay";
import { useMarkerTelemetry } from "../hooks/useMarkerTelemetry";
import { ArRuntimeConfig } from "../types/ar";
import { MarkerLookupResponse } from "../types/domain";

interface ScannerScreenProps {
  onOpenNode: (lookup: MarkerLookupResponse) => void;
}

const QUICK_MARKERS = ["MKR-NODE-01", "MKR-NODE-02"];

export const ScannerScreen: React.FC<ScannerScreenProps> = ({ onOpenNode }) => {
  const { token, email, logout } = useAuth();
  const [markerCode, setMarkerCode] = useState<string | null>("MKR-NODE-01");
  const [inputCode, setInputCode] = useState<string>("");
  const [cameraReleasedCount, setCameraReleasedCount] = useState<number>(0);
  const cameraActiveRef = useRef<boolean>(true);

  const config: ArRuntimeConfig = useMemo(
    () => ({
      apiBaseUrl: process.env.EXPO_PUBLIC_API_BASE_URL ?? "http://192.168.1.80:5002",
      pollIntervalMs: Number(process.env.EXPO_PUBLIC_POLL_INTERVAL_MS ?? 4000),
      staleThresholdSeconds: Number(process.env.EXPO_PUBLIC_STALE_THRESHOLD_SEC ?? 30),
      allowSimulationFallback:
        (process.env.EXPO_PUBLIC_ALLOW_SIM_FALLBACK ?? "true").toLowerCase() === "true",
      authToken: token ?? undefined,
    }),
    [token]
  );

  const handleReleaseCamera = useCallback(() => {
    cameraActiveRef.current = false;
    setCameraReleasedCount((c) => c + 1);
  }, []);

  const { data, isLoading, isAppActive, error, refreshNow } = useMarkerTelemetry({
    markerCode,
    config,
    onReleaseCamera: handleReleaseCamera,
  });

  const handlePickMarker = (code: string | null) => {
    if (code) cameraActiveRef.current = true;
    setMarkerCode(code ? code.trim().toUpperCase() : null);
  };

  return (
    <View style={styles.root}>
      <View style={[StyleSheet.absoluteFillObject, styles.viewport]}>
        <View style={styles.headerRow}>
          <Text style={styles.headerText}>AR SCANNER • {email ?? "Operator"}</Text>
          <TouchableOpacity style={styles.logoutBtn} onPress={logout}>
            <Text style={styles.logoutText}>Đăng xuất</Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.infoLine}>
          API: {config.apiBaseUrl} • Dọn camera/AR: {cameraReleasedCount}
        </Text>

        <View style={styles.chipRow}>
          {QUICK_MARKERS.map((code) => (
            <TouchableOpacity
              key={code}
              style={[styles.chip, markerCode === code && styles.chipActive]}
              onPress={() => handlePickMarker(code)}
            >
              <Text style={styles.chipText}>{code}</Text>
            </TouchableOpacity>
          ))}
          <TouchableOpacity style={styles.lostChip} onPress={() => handlePickMarker(null)}>
            <Text style={styles.chipText}>Mất dấu</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.searchRow}>
          <TextInput
            style={styles.input}
            value={inputCode}
            onChangeText={setInputCode}
            placeholder="Nhập mã Marker..."
            placeholderTextColor="#64748B"
            autoCapitalize="characters"
          />
          <TouchableOpacity
            style={styles.actionBtn}
            onPress={() => {
              if (!inputCode.trim()) return;
              handlePickMarker(inputCode);
              setInputCode("");
            }}
          >
            <Text style={styles.actionText}>Quét</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.subBtn} onPress={() => void refreshNow()}>
            <Text style={styles.actionText}>Làm mới</Text>
          </TouchableOpacity>
        </View>
      </View>

      <ArNodeOverlay
        markerCode={markerCode}
        snapshot={data}
        isLoading={isLoading}
        isAppActive={isAppActive}
        error={error}
        onOpenDetail={(snap) => onOpenNode(snap)}
        onClearMarker={() => handlePickMarker(null)}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#020617" },
  viewport: { padding: 14 },
  headerRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  headerText: { color: "#F8FAFC", fontSize: 15, fontWeight: "700" },
  logoutBtn: { backgroundColor: "#334155", paddingHorizontal: 10, paddingVertical: 6, borderRadius: 6 },
  logoutText: { color: "#E2E8F0", fontSize: 12, fontWeight: "600" },
  infoLine: { color: "#94A3B8", fontSize: 11, marginTop: 6 },
  chipRow: { flexDirection: "row", flexWrap: "wrap", gap: 8, marginTop: 12 },
  chip: { backgroundColor: "#1E293B", paddingHorizontal: 10, paddingVertical: 6, borderRadius: 8 },
  chipActive: { backgroundColor: "#0369A1" },
  lostChip: { backgroundColor: "#7F1D1D", paddingHorizontal: 10, paddingVertical: 6, borderRadius: 8 },
  chipText: { color: "#F8FAFC", fontSize: 12, fontWeight: "600" },
  searchRow: { flexDirection: "row", gap: 8, marginTop: 10 },
  input: {
    flex: 1,
    backgroundColor: "#0F172A",
    color: "#F8FAFC",
    borderWidth: 1,
    borderColor: "#334155",
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 6,
    fontSize: 13,
  },
  actionBtn: { backgroundColor: "#0284C7", paddingHorizontal: 12, justifyContent: "center", borderRadius: 8 },
  subBtn: { backgroundColor: "#334155", paddingHorizontal: 10, justifyContent: "center", borderRadius: 8 },
  actionText: { color: "#FFFFFF", fontSize: 12, fontWeight: "700" },
});
