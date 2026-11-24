"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";

import { useRouter } from "next/navigation";

import {
  getCurrentUser,
} from "@/lib/auth";

import {
  getAccessToken,
  clearSession,
} from "@/lib/auth-storage";

type User = {
  id?: number | string;
  email?: string;
  fullName?: string;
  name?: string;
  role?: string;
  [key: string]: unknown;
};

type AuthContextType = {
  user: User | null;
  role: string | null;
  loading: boolean;
  isAuthenticated: boolean;
  refreshUser: () => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(
  undefined,
);

export function AuthProvider({
  children,
}: {
  children: ReactNode;
}) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const logout = () => {
  clearSession();
  setUser(null);
  router.replace("/");
};

  const refreshUser = async () => {
    const token = getAccessToken();

    if (!token) {
      setUser(null);
      return;
    }

    try {
      const data = await getCurrentUser();
      setUser(data as User);
    } catch (error) {
      console.error("Không thể xác minh tài khoản:", error);

      if (
        error instanceof Error &&
        "status" in error &&
        error.status === 401
      ) {
        clearSession();
        setUser(null);
      }

      throw error;
    }
  };

  useEffect(() => {
    let active = true;

    async function initializeAuth() {
      try {
        await refreshUser();
      } catch {
        // Lỗi xác thực đã được xử lý trong refreshUser.
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    initializeAuth();

    const handleUnauthorized = () => {
  if (!active) return;

  setUser(null);
  router.replace("/");
};

    window.addEventListener(
      "auth:unauthorized",
      handleUnauthorized,
    );

    return () => {
      active = false;

      window.removeEventListener(
        "auth:unauthorized",
        handleUnauthorized,
      );
    };
  }, [router]);

  const value: AuthContextType = {
    user,
    role: user?.role ?? null,
    loading,
    isAuthenticated: !!user,
    refreshUser,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth phải được sử dụng bên trong AuthProvider.",
    );
  }

  return context;
}