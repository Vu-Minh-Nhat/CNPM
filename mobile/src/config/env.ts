export const ENV = {
  API_BASE_URL: (
    process.env.EXPO_PUBLIC_API_BASE_URL ?? "http://192.168.1.80:5002"
  ).replace(/\/+$/, ""),
  SCAN_COOLDOWN_MS: Number(process.env.EXPO_PUBLIC_SCAN_COOLDOWN_MS ?? 2000),
  REQUEST_TIMEOUT_MS: Number(
    process.env.EXPO_PUBLIC_REQUEST_TIMEOUT_MS ?? 8000,
  ),
  ENDPOINTS: {
    LOGIN: "/auth/login",
    ME: "/auth/me",
    MARKER_LOOKUP: "/markers/lookup",
  },
};