import Link from "next/link";

export default function ForbiddenPage() {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-8 text-center shadow-sm">
      <p className="text-5xl font-bold text-amber-600">
        403
      </p>

      <h1 className="mt-4 text-2xl font-bold text-slate-900">
        Không có quyền truy cập
      </h1>

      <p className="mt-3 text-slate-600">
        Vai trò hiện tại của bạn không được phép truy cập trang này.
      </p>

      <Link
        href="/dashboard"
        className="mt-6 inline-block rounded-lg bg-cyan-700 px-5 py-3 text-white hover:bg-cyan-800"
      >
        Về Dashboard
      </Link>
    </section>
  );
}