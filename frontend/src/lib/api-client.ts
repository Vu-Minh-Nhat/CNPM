import {
  getAccessToken,
  clearSession,
} from "./auth-storage";

const API_URL = (
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:5000"
).replace(/\/+$/, "");

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

type ApiOptions = RequestInit & {
  auth?: boolean;
  clearOn401?: boolean;
};

export async function apiFetch<T>(
  path: string,
  options: ApiOptions = {},
): Promise<T> {
  const {
    auth = true,
    clearOn401 = true,
    headers,
    ...requestOptions
  } = options;

  const token = getAccessToken();

  
let response: Response;

try {
  response = await fetch(`${API_URL}${path}`, {
    ...requestOptions,
    headers: {
      "Content-Type": "application/json",
      ...headers,
      ...(auth && token
        ? { Authorization: `Bearer ${token}` }
        : {}),
    },
    cache: "no-store",
  });
} catch (error) {
  // Không chuyển lỗi hủy request thành lỗi kết nối
  if (error instanceof Error && error.name === "AbortError") {
    throw error;
  }

  throw new Error(
    "Không thể kết nối đến máy chủ. Vui lòng kiểm tra kết nối mạng hoặc trạng thái backend.",
  );
}

const data = await response.json().catch(() => null);


  if (response.status === 401) {
    if (clearOn401) {
      clearSession();

      if (typeof window !== "undefined") {
        window.dispatchEvent(
          new Event("auth:unauthorized"),
        );
      }
    }

    throw new ApiError(
      401,
      "Phiên đăng nhập không hợp lệ hoặc đã hết hạn.",
    );
  }

  if (response.status === 403) {
    throw new ApiError(
      403,
      "Bạn không có quyền thực hiện thao tác này.",
    );
  }

  if (!response.ok) {
    throw new ApiError(
      response.status,
      data?.message || "Có lỗi xảy ra từ máy chủ.",
    );
  }

  return data as T;
}