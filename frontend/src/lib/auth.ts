import { apiFetch, ApiError } from "./api-client";
import type { LoginResponse } from "./auth-storage";

export type { LoginResponse } from "./auth-storage";

// Đăng nhập
export async function login(
  email: string,
  password: string,
): Promise<LoginResponse> {
  try {
    const data = await apiFetch<LoginResponse>(
      "/auth/login",
      {
        method: "POST",
        auth: false,
        clearOn401: false,
        body: JSON.stringify({ email, password }),
      },
    );

    if (!data?.accessToken || !data?.role) {
      throw new Error(
        "Dữ liệu phản hồi từ máy chủ không hợp lệ.",
      );
    }

    return data;
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      throw new Error("Email hoặc mật khẩu không chính xác.");
    }

    throw error;
  }
}

// Kiểu dữ liệu người dùng hiện tại
export type CurrentUser = {
  email: string;
  role: string;
};

// Lấy thông tin người dùng hiện tại
export async function getCurrentUser(): Promise<CurrentUser> {
  return apiFetch<CurrentUser>("/auth/me", {
    method: "GET",
  });
}