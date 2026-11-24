import Link from "next/link";

export default function NotFound() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-100 px-6 py-12">
      <section className="w-full max-w-lg rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
        <p className="text-6xl font-bold text-cyan-700">
          404
        </p>

        <h1 className="mt-4 text-2xl font-bold text-slate-900">
          Không tìm thấy trang
        </h1>

        <p className="mt-3 text-slate-600">
          Đường dẫn không tồn tại hoặc trang đã được di chuyển.
        </p>

        <div className="mt-6 flex flex-wrap justify-center gap-3">
          <Link
            href="/dashboard"
            className="rounded-lg bg-cyan-700 px-5 py-3 font-medium text-white hover:bg-cyan-800"
          >
            Về Dashboard
          </Link>

          <Link
            href="/"
            className="rounded-lg border border-slate-300 px-5 py-3 font-medium text-slate-700 hover:bg-slate-100"
          >
            Về trang đăng nhập
          </Link>
        </div>
      </section>
    </main>
  );
}