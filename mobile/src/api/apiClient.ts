import { ENV } from "../config/env";
import { sessionStorage } from "../storage/sessionStorage";
import { AppError } from "../types/domain";

type UnauthorizedHandler = () => void | Promise<void>;

let onUnauthorizedCallback: UnauthorizedHandler | null = null;
let handlingUnauthorized = false;

export function registerUnauthorizedHandler(
  handler: UnauthorizedHandler | null,
): void {
  onUnauthorizedCallback = handler;
}

async function triggerUnauthorizedOnce(): Promise<void> {
  if (handlingUnauthorized) {
    return;
  }
  handlingUnauthorized = true;
  try {
    await sessionStorage.clearSession();
    if (onUnauthorizedCallback) {
      await onUnauthorizedCallback();
    }
  } finally {
    setTimeout(() => {
      handlingUnauthorized = false;
    }, 500);
  }
}

interface RequestOptions {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  body?: unknown;
  query?: Record<string, string | number | undefined>;
  auth?: boolean;
  timeoutMs?: number;
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const {
    method = "GET",
    body,
    query,
    auth = true,
    timeoutMs = ENV.REQUEST_TIMEOUT_MS,
  } = options;

  const url = new URL(`${ENV.API_BASE_URL}${path}`);
  if (query) {
    Object.entries(query).forEach(([key, value]) => {
      if (value !== undefined && value !== "") {
        url.searchParams.set(key, String(value));
      }
    });
  }

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (auth) {
    const token = await sessionStorage.getToken();
    if (!token) {
      throw new AppError(
        "UNAUTHORIZED",
        "Bạn chưa đăng nhập hoặc phiên làm việc đã kết thúc.",
        401,
      );
    }
    headers.Authorization = `Bearer ${token}`;
  }

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  let response: Response;
  try {
    response = await fetch(url.toString(), {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    });
  } catch (err) {
    clearTimeout(timer);
    const isAbort = err instanceof Error && err.name === "AbortError";
    throw new AppError(
      "NETWORK",
      isAbort
        ? "Kết nối tới máy chủ quá thời gian chờ. Vui lòng kiểm tra mạng và thử lại."
        : "Không thể kết nối đến máy chủ. Vui lòng kiểm tra kết nối mạng.",
    );
  } finally {
    clearTimeout(timer);
  }

  const payload = await response.json().catch(() => null);
  const serverMessage: string | undefined =
    payload?.message || payload?.error || payload?.detail;

  if (!response.ok) {
    if (response.status === 401) {
      if (auth) {
        await triggerUnauthorizedOnce();
      }
      throw new AppError(
        "UNAUTHORIZED",
        serverMessage || "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.",
        401,
      );
    }
    if (response.status === 403) {
      throw new AppError(
        "FORBIDDEN",
        serverMessage || "Tài khoản không có quyền thực hiện thao tác này.",
        403,
      );
    }
    if (response.status === 404) {
      throw new AppError(
        "NOT_FOUND",
        serverMessage || "Không tìm thấy Marker hoặc thiết bị tương ứng.",
        404,
      );
    }
    if (response.status === 422 || response.status === 400) {
      throw new AppError(
        "VALIDATION",
        serverMessage || "Dữ liệu không hợp lệ.",
        response.status,
      );
    }
    throw new AppError(
      "SERVER",
      serverMessage || "Có lỗi xảy ra từ máy chủ. Vui lòng thử lại sau.",
      response.status,
    );
  }

  return payload as T;
}
