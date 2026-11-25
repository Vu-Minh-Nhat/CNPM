import React, { useState } from "react";
import { StyleSheet, Text, TextInput, TouchableOpacity, View } from "react-native";
import { useAuth } from "../auth/AuthContext";

interface LoginScreenProps {
  onLoggedIn?: () => void;
}

export const LoginScreen: React.FC<LoginScreenProps> = ({ onLoggedIn }) => {
  const { login } = useAuth();
  const [email, setEmail] = useState<string>("tech@arimms.local");
  const [password, setPassword] = useState<string>("");
  const [apiUrl, setApiUrl] = useState<string>(
    process.env.EXPO_PUBLIC_API_BASE_URL ?? "http://192.168.1.80:5002"
  );
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState<boolean>(false);

  const handleSubmit = async () => {
    setError(null);
    setSubmitting(true);
    try {
      await login(email, password, apiUrl);
      onLoggedIn?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Đăng nhập thất bại");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>ARIMMS Mobile AR</Text>
      <Text style={styles.subtitle}>Đăng nhập để tra cứu & giám sát Node tại testbed</Text>

      <Text style={styles.label}>Backend API URL</Text>
      <TextInput
        style={styles.input}
        value={apiUrl}
        onChangeText={setApiUrl}
        autoCapitalize="none"
        placeholder="http://192.168.1.80:5002"
        placeholderTextColor="#64748B"
      />

      <Text style={styles.label}>Email</Text>
      <TextInput
        style={styles.input}
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        keyboardType="email-address"
        placeholder="tech@arimms.local"
        placeholderTextColor="#64748B"
      />

      <Text style={styles.label}>Mật khẩu</Text>
      <TextInput
        style={styles.input}
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        placeholder="Nhập mật khẩu"
        placeholderTextColor="#64748B"
      />

      {error ? <Text style={styles.error}>{error}</Text> : null}

      <TouchableOpacity style={styles.btn} onPress={() => void handleSubmit()} disabled={submitting}>
        <Text style={styles.btnText}>{submitting ? "Đang đăng nhập..." : "Đăng nhập"}</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#020617", justifyContent: "center", padding: 20 },
  title: { color: "#F8FAFC", fontSize: 22, fontWeight: "700" },
  subtitle: { color: "#94A3B8", fontSize: 13, marginTop: 4, marginBottom: 16 },
  label: { color: "#CBD5E1", fontSize: 12, marginTop: 10, marginBottom: 4 },
  input: {
    backgroundColor: "#0F172A",
    color: "#F8FAFC",
    borderWidth: 1,
    borderColor: "#334155",
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 14,
  },
  error: { color: "#F87171", fontSize: 12, marginTop: 8 },
  btn: {
    marginTop: 18,
    backgroundColor: "#0284C7",
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: "center",
  },
  btnText: { color: "#FFFFFF", fontSize: 14, fontWeight: "700" },
});
