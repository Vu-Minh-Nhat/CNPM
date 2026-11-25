import React, { useState } from "react";
import { ActivityIndicator, StyleSheet, View } from "react-native";
import { StatusBar } from "expo-status-bar";
import { AuthProvider, useAuth } from "./src/auth/AuthContext";
import { LoginScreen } from "./src/screens/LoginScreen";
import { ScannerScreen } from "./src/screens/ScannerScreen";
import { NodeDetailScreen } from "./src/screens/NodeDetailScreen";
import { MarkerLookupResponse } from "./src/types/domain";

function ProtectedStack() {
  const { isAuthenticated, isBootstrapping } = useAuth();
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
    <ScannerScreen
      onOpenNode={(lookup) => {
        setSelectedLookup(lookup);
      }}
    />
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
});
