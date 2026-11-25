import { useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import { AuthProvider, useAuth } from "./src/auth/AuthContext";
import { LoginScreen } from "./src/screens/LoginScreen";
import { OverviewScreen } from "./src/screens/OverviewScreen";
import { ScannerScreen } from "./src/screens/ScannerScreen";
import { NodeDetailScreen } from "./src/screens/NodeDetailScreen";
import { AssetOverviewItem } from "./src/services/assetsService";
import { MarkerLookupResponse } from "./src/types/domain";

type ActiveTab = "overview" | "scanner";

function buildLookupFromAsset(item: AssetOverviewItem): MarkerLookupResponse {
  return {
    markerCode: item.code ?? item.id,
    node: {
      id: item.id,
      code: item.code ?? item.id,
      name: item.name,
      serialNumber: item.serialNumber ?? null,
    },
    location: {
      site: item.location.siteName ?? item.location.siteCode ?? undefined,
      room: item.location.roomName ?? item.location.roomCode ?? undefined,
      rack: item.location.rackName ?? item.location.rackCode ?? undefined,
    },
    workloads: item.workloads.map((w) => ({
      id: w.id,
      code: w.code ?? w.id,
      name: w.name ?? w.code ?? w.id,
    })),
    telemetry: null,
    alerts: [],
    isSimulated: false,
    fetchedAt: new Date().toISOString(),
  } as unknown as MarkerLookupResponse;
}

function ProtectedStack() {
  const { token, isAuthenticated, isBootstrapping } = useAuth();
  const [activeTab, setActiveTab] = useState<ActiveTab>("overview");
  const [selectedLookup, setSelectedLookup] =
    useState<MarkerLookupResponse | null>(null);

  if (isBootstrapping) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#0284c7" />
      </View>
    );
  }

  if (!isAuthenticated) {
    return <LoginScreen />;
  }

  if (selectedLookup) {
    return (
      <NodeDetailScreen
        lookup={selectedLookup}
        onBackToScanner={() => setSelectedLookup(null)}
      />
    );
  }

  return (
    <View style={styles.screenContainer}>
      <View style={styles.tabBar}>
        <Pressable
          style={[styles.tabBtn, activeTab === "overview" && styles.tabBtnActive]}
          onPress={() => setActiveTab("overview")}
        >
          <Text
            style={[
              styles.tabText,
              activeTab === "overview" && styles.tabTextActive,
            ]}
          >
            Tong quan
          </Text>
        </Pressable>
        <Pressable
          style={[styles.tabBtn, activeTab === "scanner" && styles.tabBtnActive]}
          onPress={() => setActiveTab("scanner")}
        >
          <Text
            style={[
              styles.tabText,
              activeTab === "scanner" && styles.tabTextActive,
            ]}
          >
            Quet AR
          </Text>
        </Pressable>
      </View>

      {activeTab === "overview" ? (
        <OverviewScreen
          accessToken={token}
          onOpenAssetList={() => setActiveTab("scanner")}
          onOpenAssetDetail={(assetId) => {
            setSelectedLookup(
              buildLookupFromAsset({
                id: assetId,
                name: assetId,
                assetKind: "node",
                workloadCount: 0,
                workloads: [],
                location: {},
              })
            );
          }}
        />
      ) : (
        <ScannerScreen
          onOpenNode={(lookup) => {
            setSelectedLookup(lookup);
          }}
        />
      )}
    </View>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <StatusBar style="auto" />
      <ProtectedStack />
    </AuthProvider>
  );
}

const styles = StyleSheet.create({
  center: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#f8fafc",
  },
  screenContainer: {
    flex: 1,
    backgroundColor: "#f8fafc",
  },
  tabBar: {
    flexDirection: "row",
    paddingHorizontal: 16,
    paddingTop: 12,
    gap: 8,
    backgroundColor: "#ffffff",
    borderBottomWidth: 1,
    borderBottomColor: "#e2e8f0",
  },
  tabBtn: {
    paddingVertical: 10,
    paddingHorizontal: 14,
    borderBottomWidth: 2,
    borderBottomColor: "transparent",
  },
  tabBtnActive: {
    borderBottomColor: "#0284c7",
  },
  tabText: {
    fontSize: 13,
    fontWeight: "600",
    color: "#64748b",
  },
  tabTextActive: {
    color: "#0284c7",
  },
});
