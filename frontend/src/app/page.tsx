
"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { login, saveSession } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const submitting = useRef(false);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    if (submitting.current) return;

    setError("");

    if (!email.trim() || !password) {
      setError("Vui lòng nhập đầy đủ email và mật khẩu.");
      return;
    }

    submitting.current = true;
    setLoading(true);

    try {
      const result = await login(email.trim(), password);
      saveSession(result);
      router.replace("/dashboard");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Không thể kết nối máy chủ. Vui lòng thử lại.",
      );
    } finally {
      submitting.current = false;
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen bg-slate-100">
      {/* Left panel */}
      <section className="relative hidden w-1/2 flex-col justify-between overflow-hidden bg-[#071b2b] p-12 text-white lg:flex">
        <div className="absolute inset-0 opacity-20">
          <div className="absolute left-20 top-20 h-64 w-64 rounded-full border border-cyan-400" />
          <div className="absolute left-32 top-32 h-40 w-40 rounded-full border border-cyan-400" />
          <div className="absolute bottom-20 right-10 h-80 w-80 rounded-full border border-cyan-400" />
        </div>

        <div className="relative z-10">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-cyan-500 text-xl font-bold">
              AR
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-wide">AR-IMMS</h1>
              <p className="text-xs tracking-widest text-cyan-300">
                INFRASTRUCTURE INTELLIGENCE
              </p>
            </div>
          </div>
        </div>

        <div className="relative z-10 max-w-lg">
          <div className="mb-8 grid grid-cols-3 gap-3">
            {["SERVER", "NETWORK", "DATABASE"].map((item) => (
              <div
                key={item}
                className="rounded-lg border border-cyan-800 bg-[#102d40] p-4 text-center"
              >
                <div className="mx-auto mb-3 h-8 w-8 rounded-md border-2 border-cyan-400" />
                <p className="text-xs text-cyan-200">{item}</p>
                <span className="mt-2 inline-block h-2 w-2 rounded-full bg-green-400" />
              </div>
            ))}
          </div>

          <h2 className="text-4xl font-bold leading-tight">
            Infrastructure
            <br />
            Monitoring &
            <br />
            Maintenance System
          </h2>
          <p className="mt-5 leading-7 text-slate-300">
            A centralized platform for monitoring, managing and maintaining
            your IT infrastructure.
          </p>
        </div>

        <p className="relative z-10 text-xs text-slate-400">
          © 2026 AR-IMMS. All rights reserved.
        </p>
      </section>

      {/* Right panel */}
      <section className="flex flex-1 items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          <div className="mb-10 lg:hidden">
            <h1 className="text-2xl font-bold text-[#0b2638]">AR-IMMS</h1>
            <p className="text-sm text-slate-500">
              Infrastructure Monitoring System
            </p>
          </div>

          <div className="rounded-2xl bg-white p-8 shadow-xl shadow-slate-200/70 sm:p-10">
            <div className="mb-8">
              <p className="mb-2 text-sm font-semibold uppercase tracking-widest text-cyan-600">
                Welcome back
              </p>
              <h2 className="text-3xl font-bold text-[#102b3d]">
                Sign in
              </h2>
              <p className="mt-2 text-sm text-slate-500">
                Enter your account details to continue.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label
                  htmlFor="email"
                  className="mb-2 block text-sm font-semibold text-slate-700"
                >
                  Email address
                </label>
                <input
                  id="email"
                  type="email"
                  autoComplete="username"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  className="w-full rounded-lg border border-slate-300 px-4 py-3 outline-none transition focus:border-cyan-500 focus:ring-2 focus:ring-cyan-100"
                />
              </div>

              <div>
                <label
                  htmlFor="password"
                  className="mb-2 block text-sm font-semibold text-slate-700"
                >
                  Password
                </label>
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    autoComplete="current-password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    className="w-full rounded-lg border border-slate-300 px-4 py-3 pr-20 outline-none transition focus:border-cyan-500 focus:ring-2 focus:ring-cyan-100"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-sm font-medium text-cyan-700"
                  >
                    {showPassword ? "Hide" : "Show"}
                  </button>
                </div>
              </div>

              {error && (
                <div
                  role="alert"
                  className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
                >
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-lg bg-cyan-700 py-3.5 font-semibold text-white transition hover:bg-cyan-800 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? "Signing in..." : "Sign in"}
              </button>
            </form>
          </div>

          <p className="mt-6 text-center text-xs text-slate-500">
            Secure access to AR-IMMS infrastructure management.
          </p>
        </div>
      </section>
    </main>
  );
}
