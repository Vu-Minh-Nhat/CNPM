
const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3000";

export type LoginResponse = {
  accessToken: string;
  role: string;
};

export async function login(
  email: string,
  password: string,
): Promise<LoginResponse> {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(
      data?.message || "Đăng nhập thất bại. Vui lòng kiểm tra lại.",
    );
  }

  if (!data?.accessToken || !data?.role) {
    throw new Error("Dữ liệu phản hồi từ máy chủ không hợp lệ.");
  }

  return data as LoginResponse;
}

export function saveSession(data: LoginResponse): void {
  sessionStorage.setItem("accessToken", data.accessToken);
  sessionStorage.setItem("role", data.role);
}

export function clearSession(): void {
  sessionStorage.removeItem("accessToken");
  sessionStorage.removeItem("role");
}

export function getAccessToken(): string | null {
  return sessionStorage.getItem("accessToken");
}
export async function getCurrentUser(token: string) {
  const response = await fetch(`${API_URL}/auth/me`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(
      response.status === 401
        ? "Phiên đăng nhập đã hết hạn."
        : "Không thể xác minh phiên đăng nhập.",
    );
  }

  return response.json();
}
