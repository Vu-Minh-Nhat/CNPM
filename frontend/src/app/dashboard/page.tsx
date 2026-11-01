"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  clearSession,
  getAccessToken,
  getCurrentUser,
} from "@/lib/auth";

export default function DashboardPage() {
  const router = useRouter();

  const [checking, setChecking] = useState(true);
  const [role, setRole] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function checkAuthentication() {
      const token = getAccessToken();

      // Không có token: quay về Login
      if (!token) {
        router.replace("/");
        return;
      }

      try {
        // Xác minh token trực tiếp với backend
        const user = await getCurrentUser(token);

        if (!active) return;

        setRole(user.role ?? "");
        setChecking(false);
      } catch (err) {
        if (!active) return;

        const message =
          err instanceof Error ? err.message : "Có lỗi xảy ra.";

        // Token không hợp lệ hoặc đã hết hạn
        if (message === "Phiên đăng nhập đã hết hạn.") {
          clearSession();
          router.replace("/");
          return;
        }

        // Lỗi kết nối: không cho hiển thị Dashboard
        setError(message);
        setChecking(false);
      }
    }

    checkAuthentication();

    return () => {
      active = false;
    };
  }, [router]);

  function handleLogout() {
    clearSession();
    router.replace("/");
  }

  if (checking) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p>Đang xác minh phiên đăng nhập...</p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-4">
        <p className="text-red-600">{error}</p>

        <button
          onClick={() => window.location.reload()}
          className="rounded-lg bg-blue-600 px-5 py-2 text-white"
        >
          Thử lại
        </button>

        <button
          onClick={handleLogout}
          className="rounded-lg bg-slate-600 px-5 py-2 text-white"
        >
          Quay về đăng nhập
        </button>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-100">
      <header className="flex items-center justify-between bg-[#071b2b] px-8 py-5 text-white">
        <h1 className="text-xl font-bold">
          AR-IMMS Dashboard
        </h1>

        <button
          onClick={handleLogout}
          className="rounded-lg bg-red-600 px-5 py-2 font-semibold hover:bg-red-700"
        >
          Logout
        </button>
      </header>

      <section className="p-8">
        <div className="rounded-xl bg-white p-8 shadow">
          <h2 className="text-2xl font-bold text-slate-800">
            Welcome to AR-IMMS
          </h2>

          <p className="mt-3 text-slate-600">
            You have successfully logged in.
          </p>

          <p className="mt-2 text-sm text-slate-500">
            Role: {role}
          </p>
        </div>
      </section>
    </main>
  );
}