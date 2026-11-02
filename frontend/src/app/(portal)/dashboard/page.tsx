export default function DashboardPage() {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h1 className="text-2xl font-bold text-slate-900">
        Dashboard
      </h1>

      <p className="mt-3 text-slate-600">
        Chào mừng bạn đến với hệ thống AR-IMMS.
      </p>

      <p className="mt-2 text-sm text-slate-500">
        Thông tin tổng quan về tài sản, telemetry và cảnh báo
        sẽ được tích hợp tại đây.
      </p>
    </section>
  );
}