export type LoginResponse = {
  accessToken: string;
  role: string;
};

export function saveSession(data: LoginResponse): void {
  if (typeof window === "undefined") return;

  sessionStorage.setItem("accessToken", data.accessToken);
  sessionStorage.setItem("role", data.role);
}

export function clearSession(): void {
  if (typeof window === "undefined") return;

  sessionStorage.removeItem("accessToken");
  sessionStorage.removeItem("role");
}

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;

  return sessionStorage.getItem("accessToken");
}