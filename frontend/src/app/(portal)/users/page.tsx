
"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ApiError, apiFetch } from "@/lib/api-client";
import { getCurrentUser } from "@/lib/auth";
import {
  clearSession,
  getAccessToken,
} from "@/lib/auth-storage";

type Role = "Administrator" | "Operator" | "Technician";

type Account = {
  id: string;
  email: string;
  role: Role;
  isActive: boolean;
  createdAt: string;
};

const ROLES: Role[] = [
  "Administrator",
  "Operator",
  "Technician",
];

const ROLE_LABELS: Record<Role, string> = {
  Administrator: "Quản trị viên",
  Operator: "Nhân viên vận hành",
  Technician: "Kỹ thuật viên",
};

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return "Đã xảy ra lỗi không xác định.";
}

export default function UsersPage() {
  const router = useRouter();

  const [allowed, setAllowed] = useState(false);
  const [checking, setChecking] = useState(true);

  const [accounts, setAccounts] = useState<Account[]>([]);
  const [currentEmail, setCurrentEmail] = useState("");

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<Role>("Operator");

  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [savingId, setSavingId] = useState("");

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleError = useCallback(
    (err: unknown) => {
      if (err instanceof ApiError && err.status === 401) {
        clearSession();
        router.replace("/");
        return;
      }

      if (err instanceof ApiError && err.status === 403) {
        router.replace("/forbidden");
        return;
      }

      setError(getErrorMessage(err));
    },
    [router],
  );

  const loadAccounts = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const data = await apiFetch<Account[]>("/users", {
        method: "GET",
      });

      setAccounts(data);
    } catch (err) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }, [handleError]);

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

        setCurrentEmail(user.email);
        setAllowed(true);

        const data = await apiFetch<Account[]>("/users", {
          method: "GET",
        });

        if (active) {
          setAccounts(data);
        }
      } catch (err) {
        if (!active) return;
        handleError(err);
      } finally {
        if (active) {
          setChecking(false);
        }
      }
    }

    void checkPermission();

    return () => {
      active = false;
    };
  }, [router, handleError]);

  async function handleCreate(
    event: React.FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setError("");
    setSuccess("");
    setSubmitting(true);

    try {
      await apiFetch<Account>("/users", {
        method: "POST",
        body: JSON.stringify({
          email,
          password,
          role,
        }),
      });

      setEmail("");
      setPassword("");
      setRole("Operator");

      setSuccess("Tạo tài khoản thành công.");

      await loadAccounts();
    } catch (err) {
      handleError(err);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleRoleChange(
    account: Account,
    newRole: Role,
  ) {
    if (account.role === newRole) return;

    setError("");
    setSuccess("");
    setSavingId(account.id);

    try {
      const updated = await apiFetch<Account>(
        `/users/${account.id}/role`,
        {
          method: "PATCH",
          body: JSON.stringify({
            role: newRole,
          }),
        },
      );

      if (
        account.email.toLowerCase() ===
        currentEmail.toLowerCase()
      ) {
        const currentUser = await getCurrentUser();

        if (currentUser.role !== "Administrator") {
          router.replace("/forbidden");
          return;
        }
      }

      setAccounts((previous) =>
        previous.map((item) =>
          item.id === updated.id ? updated : item,
        ),
      );

      setSuccess("Cập nhật vai trò thành công.");
    } catch (err) {
      handleError(err);
    } finally {
      setSavingId("");
    }
  }

  if (checking) {
    return (
      <p role="status">
        Đang kiểm tra quyền truy cập...
      </p>
    );
  }

  if (!allowed) {
    return null;
  }

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Quản lý tài khoản
        </h1>

        <p className="mt-2 text-sm text-slate-600">
          Quản lý danh sách tài khoản và phân quyền người dùng.
        </p>
      </div>

      {error && (
        <div
          role="alert"
          className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700"
        >
          {error}
        </div>
      )}

      {success && (
        <div
          role="status"
          className="rounded-lg border border-green-200 bg-green-50 p-4 text-sm text-green-700"
        >
          {success}
        </div>
      )}

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="mb-5 text-lg font-semibold text-slate-900">
          Tạo tài khoản mới
        </h2>

        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label
              htmlFor="email"
              className="mb-2 block text-sm font-medium text-slate-700"
            >
              Email
            </label>

            <input
              id="email"
              type="email"
              required
              maxLength={254}
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
              placeholder="example@email.com"
              className="w-full rounded-lg border border-slate-300 px-4 py-2.5 outline-none focus:border-cyan-600"
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="mb-2 block text-sm font-medium text-slate-700"
            >
              Mật khẩu
            </label>

            <input
              id="password"
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              placeholder="Ít nhất 8 ký tự"
              className="w-full rounded-lg border border-slate-300 px-4 py-2.5 outline-none focus:border-cyan-600"
            />

            <p className="mt-1 text-xs text-slate-500">
              Mật khẩu phải có ít nhất 8 ký tự.
            </p>
          </div>

          <div>
            <label
              htmlFor="role"
              className="mb-2 block text-sm font-medium text-slate-700"
            >
              Vai trò
            </label>

            <select
              id="role"
              value={role}
              onChange={(event) =>
                setRole(event.target.value as Role)
              }
              className="w-full rounded-lg border border-slate-300 bg-white px-4 py-2.5 outline-none focus:border-cyan-600"
            >
              {ROLES.map((item) => (
                <option key={item} value={item}>
                  {ROLE_LABELS[item]}
                </option>
              ))}
            </select>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="rounded-lg bg-cyan-700 px-5 py-2.5 font-medium text-white hover:bg-cyan-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {submitting ? "Đang tạo..." : "Tạo tài khoản"}
          </button>
        </form>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">
              Danh sách tài khoản
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Tổng số: {accounts.length} tài khoản
            </p>
          </div>

          <button
            type="button"
            onClick={() => void loadAccounts()}
            disabled={loading}
            className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-60"
          >
            {loading ? "Đang tải..." : "Làm mới"}
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[700px] border-collapse text-left text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                <th className="px-4 py-3 font-semibold text-slate-700">
                  Email
                </th>

                <th className="px-4 py-3 font-semibold text-slate-700">
                  Vai trò
                </th>

                <th className="px-4 py-3 font-semibold text-slate-700">
                  Trạng thái
                </th>

                <th className="px-4 py-3 font-semibold text-slate-700">
                  Ngày tạo
                </th>
              </tr>
            </thead>

            <tbody>
              {accounts.map((account) => (
                <tr
                  key={account.id}
                  className="border-b border-slate-100 hover:bg-slate-50"
                >
                  <td className="px-4 py-3 text-slate-800">
                    {account.email}
                    {account.email.toLowerCase() ===
                      currentEmail.toLowerCase() && (
                      <span className="ml-2 text-xs text-cyan-700">
                        (Bạn)
                      </span>
                    )}
                  </td>

                  <td className="px-4 py-3">
                    <select
                      aria-label={`Vai trò của ${account.email}`}
                      value={account.role}
                      disabled={savingId === account.id}
                      onChange={(event) =>
                        void handleRoleChange(
                          account,
                          event.target.value as Role,
                        )
                      }
                      className="rounded-lg border border-slate-300 bg-white px-3 py-2 disabled:opacity-60"
                    >
                      {ROLES.map((item) => (
                        <option key={item} value={item}>
                          {ROLE_LABELS[item]}
                        </option>
                      ))}
                    </select>

                    {savingId === account.id && (
                      <span className="ml-2 text-xs text-slate-500">
                        Đang lưu...
                      </span>
                    )}
                  </td>

                  <td className="px-4 py-3">
                    {account.isActive ? (
                      <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-700">
                        Hoạt động
                      </span>
                    ) : (
                      <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                        Không hoạt động
                      </span>
                    )}
                  </td>

                  <td className="px-4 py-3 text-slate-600">
                    {account.createdAt
                      ? new Date(
                          account.createdAt,
                        ).toLocaleString("vi-VN")
                      : "—"}
                  </td>
                </tr>
              ))}

              {!loading && accounts.length === 0 && (
                <tr>
                  <td
                    colSpan={4}
                    className="px-4 py-8 text-center text-slate-500"
                  >
                    Chưa có tài khoản nào.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
