import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { ENV } from "../config/env";
import { apiRequest, registerUnauthorizedHandler } from "../api/apiClient";
import { sessionStorage } from "../storage/sessionStorage";
import { AppError, UserProfile } from "../types/domain";

interface LoginPayload {
  email: string;
  password: string;
}

interface AuthContextValue {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isBootstrapping: boolean;
  isSubmitting: boolean;
  sessionNotice: string | null;
  clearSessionNotice: () => void;
  login: (payload: LoginPayload) => Promise<void>;
  refreshProfile: () => Promise<UserProfile | null>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function extractToken(loginRes: any): string | null {
  return (
    loginRes?.accessToken ||
    loginRes?.access_token ||
    loginRes?.token ||
    loginRes?.data?.accessToken ||
    loginRes?.data?.access_token ||
    null
  );
}

function extractUser(res: any): UserProfile | null {
  const candidate = res?.user ?? res?.data?.user ?? res;
  if (!candidate || (!candidate.email && !candidate.id)) {
    return null;
  }
  return {
    id: String(candidate.id ?? ""),
    email: String(candidate.email ?? ""),
    name: candidate.name ?? candidate.fullName ?? candidate.full_name,
    role: String(candidate.role ?? "TECHNICIAN"),
    allowedNodes: candidate.allowedNodes ?? candidate.allowed_nodes,
    active: candidate.active ?? true,
  };
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isBootstrapping, setIsBootstrapping] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [sessionNotice, setSessionNotice] = useState<string | null>(null);

  const clearSessionNotice = useCallback(() => {
    setSessionNotice(null);
  }, []);

  const logout = useCallback(async () => {
    await sessionStorage.clearSession();
    setUser(null);
  }, []);

  const refreshProfile = useCallback(async (): Promise<UserProfile | null> => {
    const token = await sessionStorage.getToken();
    if (!token) {
      setUser(null);
      return null;
    }
    try {
      const meRes = await apiRequest<any>(ENV.ENDPOINTS.ME, { auth: true });
      const profile = extractUser(meRes);
      if (!profile) {
        await sessionStorage.clearSession();
        setUser(null);
        return null;
      }
      await sessionStorage.setCachedUser(profile);
      setUser(profile);
      return profile;
    } catch (err) {
      if (err instanceof AppError && err.kind === "UNAUTHORIZED") {
        setUser(null);
        setSessionNotice(err.message);
        return null;
      }
      const cached = await sessionStorage.getCachedUser();
      if (cached) {
        setUser(cached);
        return cached;
      }
      setUser(null);
      return null;
    }
  }, []);

  useEffect(() => {
    registerUnauthorizedHandler(async () => {
      setUser(null);
      setSessionNotice("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.");
    });

    void (async () => {
      setIsBootstrapping(true);
      await refreshProfile();
      setIsBootstrapping(false);
    })();

    return () => {
      registerUnauthorizedHandler(null);
    };
  }, [refreshProfile]);

  const login = useCallback(async ({ email, password }: LoginPayload) => {
    setIsSubmitting(true);
    setSessionNotice(null);
    try {
      const trimmedEmail = email.trim().toLowerCase();
      if (!trimmedEmail || !password) {
        throw new AppError(
          "VALIDATION",
          "Vui lòng nhập đầy đủ email và mật khẩu.",
        );
      }

      const res = await apiRequest<any>(ENV.ENDPOINTS.LOGIN, {
        method: "POST",
        body: { email: trimmedEmail, password },
        auth: false,
      });

      const token = extractToken(res);
      if (!token) {
        throw new AppError(
          "SERVER",
          "Phản hồi đăng nhập thiếu token xác thực.",
        );
      }

      await sessionStorage.setToken(token);

      const meRes = await apiRequest<any>(ENV.ENDPOINTS.ME, { auth: true });
      const profile = extractUser(meRes) ?? extractUser(res);
      if (!profile) {
        await sessionStorage.clearSession();
        throw new AppError(
          "SERVER",
          "Không thể lấy thông tin tài khoản sau khi đăng nhập.",
        );
      }

      await sessionStorage.setCachedUser(profile);
      setUser(profile);
    } finally {
      setIsSubmitting(false);
    }
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      isBootstrapping,
      isSubmitting,
      sessionNotice,
      clearSessionNotice,
      login,
      refreshProfile,
      logout,
    }),
    [
      user,
      isBootstrapping,
      isSubmitting,
      sessionNotice,
      clearSessionNotice,
      login,
      refreshProfile,
      logout,
    ],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth phải được dùng bên trong AuthProvider");
  }
  return ctx;
}
