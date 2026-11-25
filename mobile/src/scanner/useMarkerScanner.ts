import { useCallback, useEffect, useRef, useState } from "react";
import { Linking } from "react-native";
import { useCameraPermissions } from "expo-camera";
import { ENV } from "../config/env";
import { apiRequest } from "../api/apiClient";
import { AppError, MarkerLookupResponse } from "../types/domain";

const MARKER_PATTERN = /^[A-Za-z0-9_-]{3,64}$/;

export type ScanFeedback =
  | { type: "info"; title: string; message: string }
  | { type: "warning"; title: string; message: string }
  | { type: "error"; title: string; message: string; canRetry?: boolean };

export function useMarkerScanner(
  onNodeResolved: (result: MarkerLookupResponse) => void,
) {
  const [permission, requestPermission] = useCameraPermissions();
  const [isResolving, setIsResolving] = useState(false);
  const [isNavigating, setIsNavigating] = useState(false);
  const [feedback, setFeedback] = useState<ScanFeedback | null>(null);
  const [lastRetryCode, setLastRetryCode] = useState<string | null>(null);

  const lastCodeRef = useRef<string | null>(null);
  const lastScanTimestampRef = useRef<number>(0);
  const resolvingRef = useRef<boolean>(false);
  const navigatingRef = useRef<boolean>(false);

  const ensureCameraPermission = useCallback(async (): Promise<boolean> => {
    setFeedback(null);
    if (permission?.granted) {
      return true;
    }

    const res = await requestPermission();
    if (res.granted) {
      return true;
    }

    if (!res.canAskAgain) {
      setFeedback({
        type: "warning",
        title: "Quyền camera bị từ chối vĩnh viễn",
        message:
          "Vui lòng mở Cài đặt thiết bị → ứng dụng AR-IMMS Technician → bật Camera để quét mã thiết bị.",
      });
    } else {
      setFeedback({
        type: "warning",
        title: "Cần quyền truy cập camera",
        message: "Ứng dụng cần quyền camera để quét Marker trên thiết bị/node.",
      });
    }
    return false;
  }, [permission?.granted, requestPermission]);

  useEffect(() => {
    if (!permission) {
      void requestPermission();
    }
  }, [permission, requestPermission]);

  const openDeviceSettings = useCallback(async () => {
    await Linking.openSettings();
  }, []);

  const lookupMarker = useCallback(
    async (rawCode: string) => {
      const code = rawCode.trim();
      if (!MARKER_PATTERN.test(code)) {
        setFeedback({
          type: "error",
          title: "Mã Marker không hợp lệ",
          message: `Định dạng mã "${code}" không khớp chuẩn Marker hệ thống.`,
        });
        return;
      }

      resolvingRef.current = true;
      setIsResolving(true);
      setFeedback(null);
      setLastRetryCode(null);

      try {
        const res = await apiRequest<any>(ENV.ENDPOINTS.MARKER_LOOKUP, {
          method: "GET",
          query: {
          marker_type: "QR",
          identifier: code,
      },
          auth: true,
        });

        const markerStatus = String(
          res?.markerStatus ?? res?.marker_status ?? res?.status ?? "ACTIVE",
        ).toUpperCase();

        const rawNode = res?.node ?? res?.data?.node ?? res;
        if (!rawNode || !rawNode.id) {
          throw new AppError(
            "NOT_FOUND",
            "Marker chưa được liên kết với Node nào.",
            404,
          );
        }

        const normalized: MarkerLookupResponse = {
          markerCode: String(res?.markerCode ?? res?.marker_code ?? code),
          markerStatus,
          node: {
            id: String(rawNode.id),
            code: rawNode.code ? String(rawNode.code) : undefined,
            name: String(rawNode.name ?? rawNode.hostname ?? rawNode.id),
            status: rawNode.status ? String(rawNode.status) : undefined,
            rack: rawNode.rack?.name ?? rawNode.rack?.code ?? undefined,
            room:
  rawNode.rack?.room?.name ??
  rawNode.rack?.room?.code ??
  undefined,

site:
  rawNode.rack?.room?.site?.name ??
  rawNode.rack?.room?.site?.code ??
  undefined,

workloads: Array.isArray(rawNode.workloads)
  ? rawNode.workloads.map(
      (workload: { name?: string; code?: string }) =>
        workload.name ?? workload.code ?? "Không có tên",
    )
  : [],
            zone: rawNode.zone ? String(rawNode.zone) : undefined,
            ipAddress: rawNode.ipAddress ?? rawNode.ip_address,
            lastTelemetryAt: rawNode.lastTelemetryAt ?? rawNode.last_telemetry_at,
          },
        };

        if (
          markerStatus === "DISABLED" ||
          markerStatus === "INACTIVE" ||
          markerStatus === "REVOKED"
        ) {
          setFeedback({
            type: "warning",
            title: "Marker đã bị vô hiệu hóa",
            message: `Marker "${normalized.markerCode}" hiện không còn hiệu lực trên Node ${normalized.node.name}.`,
          });
          return;
        }

        navigatingRef.current = true;
        setIsNavigating(true);
        onNodeResolved(normalized);
      } catch (err) {
        if (err instanceof AppError) {
          if (err.kind === "UNAUTHORIZED") {
            return;
          }
          if (err.kind === "NETWORK") {
            setLastRetryCode(code);
            setFeedback({
              type: "error",
              title: "Mất kết nối mạng",
              message: err.message,
              canRetry: true,
            });
            return;
          }
          if (err.kind === "NOT_FOUND") {
            setFeedback({
              type: "error",
              title: "Không tìm thấy Marker",
              message: `Mã "${code}" không tồn tại trong hệ thống.`,
            });
            return;
          }
          setFeedback({
            type: "error",
            title: "Không thể tra cứu Marker",
            message: err.message,
            canRetry: err.kind === "SERVER",
          });
          return;
        }

        setLastRetryCode(code);
        setFeedback({
          type: "error",
          title: "Lỗi không xác định",
          message: "Đã xảy ra lỗi khi xử lý mã quét. Vui lòng thử lại.",
          canRetry: true,
        });
      } finally {
        resolvingRef.current = false;
        setIsResolving(false);
      }
    },
    [onNodeResolved],
  );

  const handleBarcodeScanned = useCallback(
    (rawValue: string) => {
      if (resolvingRef.current || navigatingRef.current) {
        return;
      }

      const normalized = rawValue.trim();
      if (!normalized) {
        return;
      }

      const now = Date.now();
      const isSameCodeInCooldown =
        lastCodeRef.current === normalized &&
        now - lastScanTimestampRef.current < ENV.SCAN_COOLDOWN_MS;

      if (isSameCodeInCooldown) {
        return;
      }

      lastCodeRef.current = normalized;
      lastScanTimestampRef.current = now;
      void lookupMarker(normalized);
    },
    [lookupMarker],
  );

  const retryLastScan = useCallback(() => {
    if (!lastRetryCode) {
      return;
    }
    void lookupMarker(lastRetryCode);
  }, [lastRetryCode, lookupMarker]);

  const resumeScanning = useCallback(() => {
    navigatingRef.current = false;
    setIsNavigating(false);
    lastScanTimestampRef.current = Date.now();
    setFeedback(null);
  }, []);

  const dismissFeedback = useCallback(() => {
    setFeedback(null);
    lastCodeRef.current = null;
  }, []);

  return {
    permission,
    isResolving,
    isNavigating,
    feedback,
   canRetry: Boolean(
  lastRetryCode &&
  feedback?.type === "error" &&
  feedback.canRetry
 ),
    ensureCameraPermission,
    openDeviceSettings,
    handleBarcodeScanned,
    lookupMarker,
    retryLastScan,
    resumeScanning,
    dismissFeedback,
  };
}
