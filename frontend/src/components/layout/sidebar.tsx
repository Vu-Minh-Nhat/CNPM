"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

type SidebarProps = {
  role: string;
};

const menuItems = [
  {
    label: "Dashboard",
    href: "/dashboard",
    roles: ["Administrator", "Operator", "Technician"],
  },
  {
    label: "Tài sản",
    href: "/assets",
    roles: ["Administrator", "Operator", "Technician"],
  },
  {
    label: "Quản lý tài khoản",
    href: "/users",
    roles: ["Administrator"],
  },
];

export default function Sidebar({ role }: SidebarProps) {
  const pathname = usePathname();

  const visibleItems = menuItems.filter((item) =>
    item.roles.includes(role),
  );

  return (
    <aside className="w-full shrink-0 bg-[#071b2b] text-white md:w-64">
      <div className="border-b border-slate-700 px-6 py-6">
        <Link
          href="/dashboard"
          className="text-2xl font-bold tracking-wide"
        >
          AR-IMMS
        </Link>

        <p className="mt-2 text-xs text-slate-400">
          Quản lý và giám sát hạ tầng
        </p>
      </div>

      <nav aria-label="Điều hướng chính" className="space-y-2 p-4">
        {visibleItems.map((item) => {
          const isActive =
            pathname === item.href ||
            pathname.startsWith(`${item.href}/`);

          return (
            <Link
              key={item.href}
              href={item.href}
              aria-current={isActive ? "page" : undefined}
              className={[
                "block rounded-lg px-4 py-3 text-sm font-medium",
                "transition-colors",
                "focus-visible:outline-2 focus-visible:outline-offset-2",
                "focus-visible:outline-cyan-300",
                isActive
                  ? "bg-cyan-700 text-white"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white",
              ].join(" ")}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}