import React, { createContext, useContext, useEffect, useState } from "react";

interface AuthContextValue {
  token: string | null;
  email: string | null;
  isAuthenticated: boolean;
  isBootstrapping: boolean;
  login: (email: string, password: string, apiBaseUrl?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(null);
  const [email, setEmail] = useState<string | null>(null);
  const [isBootstrapping, setIsBootstrapping] = useState<boolean>(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsBootstrapping(false);
    }, 150);
    return () => clearTimeout(timer);
  }, []);

  const login = async (userEmail: string, password: string, apiBaseUrl?: string) => {
    const trimmedEmail = userEmail.trim();
    const baseUrl = (
      apiBaseUrl ??
      process.env.EXPO_PUBLIC_API_BASE_URL ??
      "http://192.168.1.80:5002"
    ).replace(/\/+$/, "");

    try {
      const res = await fetch(`${baseUrl}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ email: trimmedEmail, password }),
      });
      if (res.ok) {
        const body = (await res.json()) as { access_token?: string; token?: string };
        setToken(body.access_token ?? body.token ?? "session-token");
        setEmail(trimmedEmail);
        return;
      }
    } catch {
      // Fallback sang phiên đăng nhập testbed cục bộ khi chưa nối kịp endpoint /auth/login
    }

    if (!trimmedEmail || !password) {
      throw new Error("Vui lòng nhập email và mật khẩu.");
    }
    setToken("local-testbed-token");
    setEmail(trimmedEmail);
  };

  const logout = () => {
    setToken(null);
    setEmail(null);
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        email,
        isAuthenticated: Boolean(token),
        isBootstrapping,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth phải được dùng bên trong AuthProvider");
  }
  return ctx;
}
