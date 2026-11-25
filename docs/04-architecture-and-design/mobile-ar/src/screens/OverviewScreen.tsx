import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import {
  AssetsOverviewData,
  fetchAssetsOverview,
} from "../services/assetsService";

interface OverviewScreenProps {
  accessToken?: string | null;
  onOpenAssetList?: () => void;
  onOpenAssetDetail?: (assetId: string) => void;
}

export function OverviewScreen({
  accessToken,
  onOpenAssetList,
  onOpenAssetDetail,
}: OverviewScreenProps) {
  const [data, setData] = useState<AssetsOverviewData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadOverview = useCallback(
    async (signal?: AbortSignal) => {
      setLoading(true);
      setError(null);
      try {
        const result = await fetchAssetsOverview(accessToken, signal);
        setData(result);
      } catch (err) {
        if ((err as Error)?.name === "AbortError") return;
        setError(
          err instanceof Error
            ? err.message
            : "Khong the tai du lieu tu GET /assets."
        );
      } finally {
        if (!signal?.aborted) {
          setLoading(false);
        }
      }
    },
    [accessToken]
  );

  useEffect(() => {
    const controller = new AbortController();
    void loadOverview(controller.signal);
    return () => controller.abort();
  }, [loadOverview]);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <View style={styles.headerText}>
          <Text style={styles.title}>Tong quan tai san</Text>
          <Text style={styles.subtitle}>Du lieu tu GET /assets sau dang nhap</Text>
        </View>
        <View style={styles.actions}>
          <Pressable style={styles.secondaryBtn} onPress={() => void loadOverview()}>
            <Text style={styles.secondaryBtnText}>Lam moi</Text>
          </Pressable>
          {onOpenAssetList && (
            <Pressable style={styles.primaryBtn} onPress={onOpenAssetList}>
              <Text style={styles.primaryBtnText}>Danh sach</Text>
            </Pressable>
          )}
        </View>
      </View>

      {loading && (
        <View style={styles.card}>
          <ActivityIndicator size="small" color="#0284c7" />
          <Text style={styles.infoText}>Dang tai du lieu tai san...</Text>
        </View>
      )}

      {!loading && error && (
        <View style={[styles.card, styles.errorCard]}>
          <Text style={styles.errorTitle}>Loi goi API GET /assets</Text>
          <Text style={styles.errorText}>{error}</Text>
          <Pressable style={styles.retryBtn} onPress={() => void loadOverview()}>
            <Text style={styles.primaryBtnText}>Thu lai</Text>
          </Pressable>
        </View>
      )}

      {!loading && !error && data && data.items.length === 0 && (
        <View style={styles.card}>
          <Text style={styles.emptyTitle}>Khong co du lieu tai san</Text>
          <Text style={styles.infoText}>
            GET /assets hien khong tra ve ban ghi tai san nao.
          </Text>
        </View>
      )}

      {!loading && !error && data && data.items.length > 0 && (
        <>
          <View style={styles.statsRow}>
            <View style={styles.statBox}>
              <Text style={styles.statLabel}>So Node</Text>
              <Text style={styles.statValue}>{data.nodeCount}</Text>
            </View>
            <View style={styles.statBox}>
              <Text style={styles.statLabel}>So Workload</Text>
              <Text style={styles.statValue}>{data.workloadCount}</Text>
            </View>
          </View>

          <View style={styles.card}>
            <Text style={styles.statLabel}>Vi tri (Site / Room / Rack)</Text>
            <Text style={styles.locationValue}>
              {data.siteCount} Site · {data.roomCount} Room · {data.rackCount} Rack
            </Text>
            <Text style={styles.noteText}>
              Chi tinh cac vi tri xuat hien trong du lieu Node tra ve tu /assets.
            </Text>
          </View>

          <View style={styles.card}>
            <Text style={styles.sectionTitle}>
              Tom tat thiet bi ({data.items.length})
            </Text>
            {data.items.map((item) => (
              <View key={item.id} style={styles.itemRow}>
                <View style={styles.itemInfo}>
                  <Text style={styles.itemTitle}>
                    {item.code ? `${item.code} - ` : ""}
                    {item.name}
                  </Text>
                  <Text style={styles.itemMeta}>
                    ID: {item.id} · Workload: {item.workloadCount}
                    {item.location.formatted
                      ? ` · Vi tri: ${item.location.formatted}`
                      : ""}
                  </Text>
                </View>
                {onOpenAssetDetail && (
                  <Pressable
                    style={styles.detailBtn}
                    onPress={() => onOpenAssetDetail(item.id)}
                  >
                    <Text style={styles.secondaryBtnText}>Chi tiet</Text>
                  </Pressable>
                )}
              </View>
            ))}
          </View>
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc" },
  content: { padding: 16, gap: 12 },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 8,
  },
  headerText: { flex: 1 },
  title: { fontSize: 20, fontWeight: "700", color: "#0f172a" },
  subtitle: { fontSize: 12, color: "#475569", marginTop: 2 },
  actions: { flexDirection: "row", gap: 8 },
  primaryBtn: {
    backgroundColor: "#0284c7",
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
  },
  primaryBtnText: { color: "#ffffff", fontWeight: "600", fontSize: 12 },
  secondaryBtn: {
    backgroundColor: "#ffffff",
    borderWidth: 1,
    borderColor: "#cbd5e1",
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
  },
  secondaryBtnText: { color: "#1e293b", fontWeight: "600", fontSize: 12 },
  detailBtn: {
    backgroundColor: "#ffffff",
    borderWidth: 1,
    borderColor: "#cbd5e1",
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
  },
  card: {
    backgroundColor: "#ffffff",
    borderWidth: 1,
    borderColor: "#e2e8f0",
    borderRadius: 12,
    padding: 14,
    gap: 6,
  },
  errorCard: { backgroundColor: "#fef2f2", borderColor: "#fecaca" },
  errorTitle: { color: "#991b1b", fontWeight: "700", fontSize: 14 },
  errorText: { color: "#991b1b", fontSize: 12 },
  retryBtn: {
    alignSelf: "flex-start",
    backgroundColor: "#b91c1c",
    paddingHorizontal: 12,
    paddingVertical: 7,
    borderRadius: 8,
    marginTop: 4,
  },
  emptyTitle: { fontSize: 15, fontWeight: "700", color: "#0f172a" },
  infoText: { fontSize: 13, color: "#475569" },
  statsRow: { flexDirection: "row", gap: 12 },
  statBox: {
    flex: 1,
    backgroundColor: "#ffffff",
    borderWidth: 1,
    borderColor: "#e2e8f0",
    borderRadius: 12,
    padding: 14,
  },
  statLabel: { fontSize: 11, fontWeight: "700", color: "#64748b" },
  statValue: { fontSize: 26, fontWeight: "700", color: "#0f172a", marginTop: 4 },
  locationValue: { fontSize: 15, fontWeight: "700", color: "#0f172a" },
  noteText: { fontSize: 11, color: "#64748b" },
  sectionTitle: { fontSize: 15, fontWeight: "700", color: "#0f172a" },
  itemRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 8,
    borderTopWidth: 1,
    borderTopColor: "#f1f5f9",
    gap: 8,
  },
  itemInfo: { flex: 1 },
  itemTitle: { fontSize: 13, fontWeight: "700", color: "#0f172a" },
  itemMeta: { fontSize: 11, color: "#64748b", marginTop: 2 },
});

