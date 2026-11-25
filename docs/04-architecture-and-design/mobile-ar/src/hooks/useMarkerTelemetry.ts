import { useCallback, useEffect, useRef, useState } from "react";
import { AppState, AppStateStatus } from "react-native";
import { lookupMarkerSnapshot } from "../services/arApiService";
import { ArMarkerLookupResult, ArRuntimeConfig } from "../types/ar";

interface UseMarkerTelemetryParams {
  markerCode: string | null;
  config: ArRuntimeConfig;
  onReleaseCamera?: () => void;
}

interface UseMarkerTelemetryState {
  data: ArMarkerLookupResult | null;
  isLoading: boolean;
  isAppActive: boolean;
  error: string | null;
  refreshNow: () => Promise<void>;
}

export function useMarkerTelemetry({
  markerCode,
  config,
  onReleaseCamera,
}: UseMarkerTelemetryParams): UseMarkerTelemetryState {
  const [data, setData] = useState<ArMarkerLookupResult | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isAppActive, setIsAppActive] = useState<boolean>(AppState.currentState === "active");
  const [error, setError] = useState<string | null>(null);

  const activeMarkerRef = useRef<string | null>(markerCode);
  const isAppActiveRef = useRef<boolean>(AppState.currentState === "active");
  const abortControllerRef = useRef<AbortController | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const releaseCameraRef = useRef<(() => void) | undefined>(onReleaseCamera);

  releaseCameraRef.current = onReleaseCamera;

  const clearPollingTimer = useCallback(() => {
    if (intervalRef.current !== null) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const abortInFlightRequest = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  }, []);

  const executeFetch = useCallback(
    async (targetCode: string, showSpinner: boolean) => {
      if (!isAppActiveRef.current || activeMarkerRef.current !== targetCode) {
        return;
      }

      abortInFlightRequest();
      const controller = new AbortController();
      abortControllerRef.current = controller;

      if (showSpinner) {
        setIsLoading(true);
      }
      setError(null);

      try {
        const result = await lookupMarkerSnapshot(targetCode, config, controller.signal);

        if (!isAppActiveRef.current || activeMarkerRef.current !== targetCode) {
          return;
        }

        setData(result);
        setError(result.telemetry.status === "offline" ? result.telemetry.statusReason ?? "Mất kết nối" : null);
      } catch (err) {
        if (err instanceof Error && err.name === "AbortError") {
          return;
        }
        if (activeMarkerRef.current === targetCode) {
          setError(err instanceof Error ? err.message : "Không thể tải dữ liệu telemetry");
        }
      } finally {
        if (abortControllerRef.current === controller) {
          abortControllerRef.current = null;
        }
        if (activeMarkerRef.current === targetCode) {
          setIsLoading(false);
        }
      }
    },
    [abortInFlightRequest, config]
  );

  const refreshNow = useCallback(async () => {
    if (!activeMarkerRef.current || !isAppActiveRef.current) return;
    await executeFetch(activeMarkerRef.current, true);
  }, [executeFetch]);

  useEffect(() => {
    const handleAppStateChange = (nextState: AppStateStatus) => {
      const nowActive = nextState === "active";
      isAppActiveRef.current = nowActive;
      setIsAppActive(nowActive);

      if (!nowActive) {
        clearPollingTimer();
        abortInFlightRequest();
        setIsLoading(false);
      } else if (activeMarkerRef.current) {
        void executeFetch(activeMarkerRef.current, false);
        clearPollingTimer();
        const intervalMs = Math.max(1000, config.pollIntervalMs);
        intervalRef.current = setInterval(() => {
          if (activeMarkerRef.current && isAppActiveRef.current) {
            void executeFetch(activeMarkerRef.current, false);
          }
        }, intervalMs);
      }
    };

    const subscription = AppState.addEventListener("change", handleAppStateChange);
    return () => {
      subscription.remove();
    };
  }, [abortInFlightRequest, clearPollingTimer, config.pollIntervalMs, executeFetch]);

  useEffect(() => {
    activeMarkerRef.current = markerCode;
    clearPollingTimer();
    abortInFlightRequest();

    setData(null);
    setError(null);
    setIsLoading(false);

    if (!markerCode) {
      return;
    }

    if (isAppActiveRef.current) {
      void executeFetch(markerCode, true);
      const intervalMs = Math.max(1000, config.pollIntervalMs);
      intervalRef.current = setInterval(() => {
        if (activeMarkerRef.current === markerCode && isAppActiveRef.current) {
          void executeFetch(markerCode, false);
        }
      }, intervalMs);
    }

    return () => {
      clearPollingTimer();
      abortInFlightRequest();
    };
  }, [markerCode, config.pollIntervalMs, abortInFlightRequest, clearPollingTimer, executeFetch]);

  useEffect(() => {
    return () => {
      activeMarkerRef.current = null;
      clearPollingTimer();
      abortInFlightRequest();
      releaseCameraRef.current?.();
    };
  }, [abortInFlightRequest, clearPollingTimer]);

  return {
    data,
    isLoading,
    isAppActive,
    error,
    refreshNow,
  };
}
