"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getCurrentUser } from "@/lib/auth";
import {
  clearSession,
  getAccessToken,
} from "@/lib/auth-storage";

export default function UsersPage() {
  const router = useRouter();

  const [allowed, setAllowed] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function checkPermission() {
      try {
        const token = getAccessToken();

        if (!token) {
          router.replace("/");
          return;
        }

        const user = await getCurrentUser();

        if (!active) return;

        if (user.role !== "Administrator") {
          router.replace("/forbidden");
          return;
        }

        setAllowed(true);
      } catch (err) {
        if (!active) return;

        const message =
          err instanceof Error
            ? err.message
            : "Không thể kiểm tra quyền truy cập.";

        if (message === "Phiên đăng nhập đã hết hạn.") {
          clearSession();
          router.replace("/");
          return;
        }

        setError(message);
      }
    }

    void checkPermission();

    return () => {
      active = false;
    };
  }, [router]);

  if (error) {
    return (
      <section className="rounded-xl bg-white p-6 shadow-sm">
        <p role="alert" className="text-red-600">
          {error}
        </p>

        <button
          type="button"
          onClick={() => window.location.reload()}
          className="mt-4 rounded-lg bg-cyan-700 px-4 py-2 text-white"
        >
          Thử lại
        </button>
      </section>
    );
  }

  if (!allowed) {
    return <p role="status">Đang kiểm tra quyền truy cập...</p>;
  }

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h1 className="text-2xl font-bold text-slate-900">
        Quản lý tài khoản
      </h1>

      <p className="mt-3 text-slate-600">
        Khu vực dành cho quản trị viên hệ thống.
      </p>

      <p className="mt-2 text-sm text-slate-500">
        Danh sách tài khoản và các thao tác quản trị
        sẽ được tích hợp trong task chức năng tương ứng.
      </p>
    </section>
  );
}