"use client";

import { useEffect, useState, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import Header from "@/components/layout/header";
import Sidebar from "@/components/layout/sidebar";
import {
  clearSession,
  getAccessToken,
  getCurrentUser,
} from "@/lib/auth";

type CurrentUser = {
  email: string;
  role: string;
};

const supportedRoles = [
  "Administrator",
  "Operator",
  "Technician",
];

export default function PortalLayout({
  children,
}: {
  children: ReactNode;
}) {
  const router = useRouter();

  const [user, setUser] = useState<CurrentUser | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadUser() {
      try {
        const token = getAccessToken();

        if (!token) {
          router.replace("/");
          return;
        }

        const currentUser = await getCurrentUser(token);

        if (!active) return;

        if (
          typeof currentUser?.email !== "string" ||
          !supportedRoles.includes(currentUser?.role)
        ) {
          throw new Error("Thông tin tài khoản không hợp lệ.");
        }

        setUser({
          email: currentUser.email,
          role: currentUser.role,
        });
      } catch (err) {
        if (!active) return;

        const message =
          err instanceof Error
            ? err.message
            : "Không thể xác minh phiên đăng nhập.";

        if (message === "Phiên đăng nhập đã hết hạn.") {
          clearSession();
          router.replace("/");
          return;
        }

        setError(message);
      }
    }

    void loadUser();

    return () => {
      active = false;
    };
  }, [router]);

  function handleLogout() {
    clearSession();
    router.replace("/");
  }

  if (error) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-4 px-6">
        <h1 className="text-xl font-semibold text-slate-900">
          Không thể mở Web Portal
        </h1>

        <p role="alert" className="text-center text-red-600">
          {error}
        </p>

        <div className="flex flex-wrap justify-center gap-3">
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="rounded-lg bg-cyan-700 px-4 py-2 text-white hover:bg-cyan-800"
          >
            Thử lại
          </button>

          <button
            type="button"
            onClick={handleLogout}
            className="rounded-lg bg-slate-700 px-4 py-2 text-white hover:bg-slate-800"
          >
            Về trang đăng nhập
          </button>
        </div>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="flex min-h-screen items-center justify-center px-6">
        <p role="status">Đang xác minh phiên đăng nhập...</p>
      </main>
    );
  }

  return (
    <div className="flex min-h-screen flex-col bg-slate-100 md:flex-row">
      <Sidebar role={user.role} />

      <div className="flex min-w-0 flex-1 flex-col">
        <Header
          email={user.email}
          role={user.role}
          onLogout={handleLogout}
        />

        <main className="min-w-0 flex-1 p-4 sm:p-6">
          {children}
        </main>
      </div>
    </div>
  );
}