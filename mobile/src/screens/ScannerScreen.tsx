import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { CameraView } from "expo-camera";

import { apiRequest } from "../api/apiClient";
import { useAuth } from "../auth/AuthContext";
import { useMarkerScanner } from "../scanner/useMarkerScanner";
import { MarkerLookupResponse } from "../types/domain";

interface ScannerScreenProps {
  onOpenNode: (lookup: MarkerLookupResponse) => void;
}

interface TelemetryMetrics {
  cpu_percent: number;
  memory_percent: number;
  disk_percent: number;
  measured_at: string;
}

interface LatestTelemetryResponse {
  latest: TelemetryMetrics | null;
  monitoring: {
    connection_status: string;
    data_status: string;
  };
}

export function ScannerScreen({ onOpenNode }: ScannerScreenProps) {
  const { user, logout } = useAuth();

  const [manualCode, setManualCode] = useState("");
  const [scannedNode, setScannedNode] =
    useState<MarkerLookupResponse | null>(null);

  const [telemetry, setTelemetry] =
    useState<LatestTelemetryResponse | null>(null);

  const [telemetryLoading, setTelemetryLoading] = useState(false);
  const [telemetryError, setTelemetryError] = useState("");

  const {
    permission,
    isResolving,
    isNavigating,
    feedback,
    canRetry,
    ensureCameraPermission,
    openDeviceSettings,
    handleBarcodeScanned,
    lookupMarker,
    retryLastScan,
    resumeScanning,
    dismissFeedback,
  } = useMarkerScanner(setScannedNode);

  const nodeId = scannedNode?.node.id;

  useEffect(() => {
    if (!nodeId) {
      setTelemetry(null);
      setTelemetryLoading(false);
      setTelemetryError("");
      return;
    }

    let active = true;
    let timer: ReturnType<typeof setTimeout> | undefined;

    async function loadTelemetry() {
      try {
        const data = await apiRequest<LatestTelemetryResponse>(
          `/telemetry/nodes/${encodeURIComponent(nodeId!)}/latest`,
        );

        if (!active) return;

        setTelemetry(data);
        setTelemetryError("");
      } catch (error) {
        if (!active) return;

        setTelemetryError(
          error instanceof Error
            ? error.message
            : "Không thể cập nhật dữ liệu giám sát.",
        );
      } finally {
        if (active) {
          setTelemetryLoading(false);
          timer = setTimeout(() => void loadTelemetry(), 5000);
        }
      }
    }

    setTelemetry(null);
    setTelemetryError("");
    setTelemetryLoading(true);
    void loadTelemetry();

    return () => {
      active = false;

      if (timer) {
        clearTimeout(timer);
      }
    };
  }, [nodeId]);

  const onBarcodeEvent = useCallback(
    ({ data }: { data?: string }) => {
      if (data) {
        handleBarcodeScanned(data);
      }
    },
    [handleBarcodeScanned],
  );

  const handleManualLookup = () => {
    if (!manualCode.trim()) return;

    void lookupMarker(manualCode);
  };

  const handleScanAnother = () => {
    setScannedNode(null);
    setManualCode("");
    resumeScanning();
  };

  const canShowSettingsButton =
    permission && !permission.granted && permission.canAskAgain === false;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.headerInfo}>
          <Text style={styles.headerTitle}>Quét Marker thiết bị</Text>
          <Text style={styles.headerSub}>
            {user?.email} ({user?.role})
          </Text>
        </View>

        <TouchableOpacity
          style={styles.logoutBtn}
          onPress={() => void logout()}
        >
          <Text style={styles.logoutText}>Đăng xuất</Text>
        </TouchableOpacity>
      </View>

      {permission?.granted ? (
        <View style={styles.cameraWrapper}>
          <CameraView
            style={StyleSheet.absoluteFill}
            facing="back"
            barcodeScannerSettings={{
              barcodeTypes: ["qr", "code128", "code39", "datamatrix"],
            }}
            onBarcodeScanned={
              isResolving || isNavigating ? undefined : onBarcodeEvent
            }
          />

          {scannedNode ? (
            <View style={styles.nodeOverlay}>
              <ScrollView
                style={styles.overlayScroll}
                nestedScrollEnabled
              >
                <Text style={styles.overlayTitle}>
                  {scannedNode.node.code ?? scannedNode.node.name}
                </Text>

                <Text style={styles.overlayText}>
                  {scannedNode.node.site ?? "Chưa có site"} →{" "}
                  {scannedNode.node.room ?? "Chưa có room"} →{" "}
                  {scannedNode.node.rack ?? "Chưa có rack"}
                </Text>

                {telemetryLoading ? (
                  <Text style={styles.overlayText}>
                    Đang tải dữ liệu giám sát...
                  </Text>
                ) : telemetry?.latest ? (
                  <>
                    <Text style={styles.metricsText}>
                      CPU: {telemetry.latest.cpu_percent}% · RAM:{" "}
                      {telemetry.latest.memory_percent}% · Disk:{" "}
                      {telemetry.latest.disk_percent}%
                    </Text>

                    <Text style={styles.overlayText}>
                      Kết nối: {telemetry.monitoring.connection_status}
                      {" · "}Dữ liệu: {telemetry.monitoring.data_status}
                    </Text>
                  </>
                ) : !telemetryError ? (
                  <Text style={styles.overlayText}>
                    Node chưa có mẫu telemetry.
                  </Text>
                ) : null}

                {telemetryError ? (
                  <Text style={styles.overlayError}>
                    {telemetryError}
                    {telemetry ? " Dữ liệu hiển thị có thể đã cũ." : ""}
                  </Text>
                ) : null}

                <View style={styles.overlayActions}>
                  <TouchableOpacity
                    style={styles.overlayPrimaryButton}
                    onPress={() => onOpenNode(scannedNode)}
                  >
                    <Text style={styles.overlayButtonText}>
                      Xem chi tiết
                    </Text>
                  </TouchableOpacity>

                  <TouchableOpacity
                    style={styles.overlaySecondaryButton}
                    onPress={handleScanAnother}
                  >
                    <Text style={styles.overlayButtonText}>
                      Quét mã khác
                    </Text>
                  </TouchableOpacity>
                </View>
              </ScrollView>
            </View>
          ) : (
            <View style={styles.overlayHint}>
              <Text style={styles.hintText}>
                {isResolving
                  ? "Đang tra cứu Marker..."
                  : "Đưa Marker vào khung quét"}
              </Text>
            </View>
          )}
        </View>
      ) : (
        <View style={styles.permissionBox}>
          <Text style={styles.permTitle}>
            Chưa có quyền sử dụng Camera
          </Text>

          <Text style={styles.permDesc}>
            Cấp quyền camera để quét trực tiếp mã trên thiết bị hoặc nhập mã
            thủ công bên dưới.
          </Text>

          <TouchableOpacity
            style={styles.primaryBtn}
            onPress={() => void ensureCameraPermission()}
          >
            <Text style={styles.primaryBtnText}>Xin quyền Camera</Text>
          </TouchableOpacity>

          {canShowSettingsButton ? (
            <TouchableOpacity
              style={styles.secondaryBtn}
              onPress={() => void openDeviceSettings()}
            >
              <Text style={styles.secondaryBtnText}>
                Mở Cài đặt thiết bị
              </Text>
            </TouchableOpacity>
          ) : null}
        </View>
      )}

      {isResolving ? (
        <View style={styles.loadingRow}>
          <ActivityIndicator size="small" color="#0284c7" />
          <Text style={styles.loadingText}>
            Đang kiểm tra thông tin Node...
          </Text>
        </View>
      ) : null}

      {feedback ? (
        <View
          style={[
            styles.feedbackBox,
            feedback.type === "error" ? styles.errBox : styles.warnBox,
          ]}
        >
          <Text style={styles.feedbackTitle}>{feedback.title}</Text>
          <Text style={styles.feedbackMsg}>{feedback.message}</Text>

          <View style={styles.feedbackActions}>
            {canRetry ? (
              <TouchableOpacity
                style={styles.smallBtn}
                onPress={retryLastScan}
              >
                <Text style={styles.smallBtnText}>Thử lại</Text>
              </TouchableOpacity>
            ) : null}

            <TouchableOpacity
              style={styles.smallBtnOutline}
              onPress={dismissFeedback}
            >
              <Text style={styles.smallBtnOutlineText}>
                Quét mã khác
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      ) : null}

      <View style={styles.manualRow}>
        <TextInput
          style={styles.manualInput}
          placeholder="Nhập mã Marker thủ công"
          placeholderTextColor="#94a3b8"
          value={manualCode}
          onChangeText={setManualCode}
          autoCapitalize="characters"
        />

        <TouchableOpacity
          style={styles.manualBtn}
          onPress={handleManualLookup}
          disabled={isResolving || isNavigating}
        >
          <Text style={styles.primaryBtnText}>Tra cứu</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#0f172a",
    padding: 16,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
    marginTop: 24,
    gap: 8,
  },
  headerInfo: {
    flex: 1,
  },
  headerTitle: {
    color: "#f8fafc",
    fontSize: 18,
    fontWeight: "700",
  },
  headerSub: {
    color: "#94a3b8",
    fontSize: 12,
  },
  logoutBtn: {
    backgroundColor: "#334155",
    paddingHorizontal: 12,
    paddingVertical: 7,
    borderRadius: 6,
  },
  logoutText: {
    color: "#f8fafc",
    fontSize: 12,
    fontWeight: "600",
  },
  cameraWrapper: {
    height: 360,
    borderRadius: 12,
    overflow: "hidden",
    backgroundColor: "#000",
    marginBottom: 12,
  },
  overlayHint: {
    position: "absolute",
    bottom: 12,
    alignSelf: "center",
    backgroundColor: "rgba(15,23,42,0.85)",
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 16,
  },
  hintText: {
    color: "#fff",
    fontSize: 12,
    fontWeight: "600",
  },
  nodeOverlay: {
    position: "absolute",
    left: 8,
    right: 8,
    bottom: 8,
    maxHeight: "75%",
    backgroundColor: "rgba(15,23,42,0.92)",
    borderRadius: 12,
    padding: 12,
  },
  overlayScroll: {
    flexGrow: 0,
  },
  overlayTitle: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "700",
    marginBottom: 4,
  },
  overlayText: {
    color: "#e2e8f0",
    fontSize: 12,
    marginBottom: 5,
  },
  metricsText: {
    color: "#7dd3fc",
    fontSize: 13,
    fontWeight: "700",
    marginVertical: 5,
  },
  overlayError: {
    color: "#fca5a5",
    fontSize: 12,
    marginBottom: 5,
  },
  overlayActions: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginTop: 6,
  },
  overlayPrimaryButton: {
    backgroundColor: "#0284c7",
    borderRadius: 6,
    paddingHorizontal: 10,
    paddingVertical: 8,
  },
  overlaySecondaryButton: {
    backgroundColor: "#475569",
    borderRadius: 6,
    paddingHorizontal: 10,
    paddingVertical: 8,
  },
  overlayButtonText: {
    color: "#fff",
    fontSize: 12,
    fontWeight: "700",
  },
  permissionBox: {
    backgroundColor: "#1e293b",
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  permTitle: {
    color: "#f8fafc",
    fontSize: 16,
    fontWeight: "700",
    marginBottom: 6,
  },
  permDesc: {
    color: "#cbd5e1",
    fontSize: 13,
    marginBottom: 12,
  },
  primaryBtn: {
    backgroundColor: "#0284c7",
    paddingVertical: 10,
    paddingHorizontal: 14,
    borderRadius: 8,
    alignItems: "center",
  },
  primaryBtnText: {
    color: "#fff",
    fontWeight: "700",
    fontSize: 13,
  },
  secondaryBtn: {
    marginTop: 8,
    borderWidth: 1,
    borderColor: "#64748b",
    paddingVertical: 9,
    paddingHorizontal: 14,
    borderRadius: 8,
    alignItems: "center",
  },
  secondaryBtnText: {
    color: "#e2e8f0",
    fontSize: 13,
    fontWeight: "600",
  },
  loadingRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginBottom: 10,
  },
  loadingText: {
    color: "#e2e8f0",
    fontSize: 13,
  },
  feedbackBox: {
    borderRadius: 10,
    padding: 12,
    marginBottom: 12,
    borderWidth: 1,
  },
  errBox: {
    backgroundColor: "#450a0a",
    borderColor: "#ef4444",
  },
  warnBox: {
    backgroundColor: "#451a03",
    borderColor: "#f59e0b",
  },
  feedbackTitle: {
    color: "#fff",
    fontWeight: "700",
    fontSize: 14,
    marginBottom: 4,
  },
  feedbackMsg: {
    color: "#e2e8f0",
    fontSize: 13,
  },
  feedbackActions: {
    flexDirection: "row",
    gap: 10,
    marginTop: 10,
  },
  smallBtn: {
    backgroundColor: "#0284c7",
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
  },
  smallBtnText: {
    color: "#fff",
    fontSize: 12,
    fontWeight: "700",
  },
  smallBtnOutline: {
    borderWidth: 1,
    borderColor: "#94a3b8",
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
  },
  smallBtnOutlineText: {
    color: "#f8fafc",
    fontSize: 12,
    fontWeight: "600",
  },
  manualRow: {
    flexDirection: "row",
    gap: 8,
    marginTop: "auto",
  },
  manualInput: {
    flex: 1,
    backgroundColor: "#1e293b",
    color: "#fff",
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 13,
  },
  manualBtn: {
    backgroundColor: "#0284c7",
    justifyContent: "center",
    paddingHorizontal: 14,
    borderRadius: 8,
  },
});