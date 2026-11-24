"use client";

type HeaderProps = {
  email: string;
  role: string;
  onLogout: () => void;
};

const roleLabels: Record<string, string> = {
  Administrator: "Quản trị viên",
  Operator: "Nhân viên vận hành",
  Technician: "Kỹ thuật viên",
};

export default function Header({
  email,
  role,
  onLogout,
}: HeaderProps) {
  return (
    <header className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 bg-white px-4 py-4 sm:px-6">
      <div>
        <p className="text-lg font-semibold text-slate-900">
          Web Management Portal
        </p>

        <p className="mt-1 text-sm text-slate-500">
          Hệ thống quản lý và giám sát hạ tầng
        </p>
      </div>

      <div className="flex min-w-0 flex-wrap items-center gap-4">
        <div className="min-w-0">
          <p className="break-all text-sm font-semibold text-slate-800">
            {email}
          </p>

          <p className="mt-1 text-xs text-slate-500">
            {roleLabels[role] ?? "Chưa xác định vai trò"}
          </p>
        </div>

        <button
          type="button"
          onClick={onLogout}
          className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-red-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600"
        >
          Đăng xuất
        </button>
      </div>
    </header>
  );
}