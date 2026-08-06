"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState, ReactNode } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/* ===== Auth Guard ===== */
interface AdminGuardProps {
  children: ReactNode;
  requiredRole?: string;
}

export function AdminGuard({ children, requiredRole = "superadmin" }: AdminGuardProps) {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [status, setStatus] = useState<"loading" | "ok" | "denied">("loading");

  useEffect(() => {
    fetch(`${API_URL}/api/v1/users/me`, { credentials: "include" })
      .then((r) => {
        if (r.status === 401) { router.push("/login"); return null; }
        if (!r.ok) throw new Error("Erro");
        return r.json();
      })
      .then((data) => {
        if (!data) return;
        const roles: string[] = data.roles || [];
        if (roles.includes("superadmin") || roles.includes(requiredRole)) {
          setUser(data);
          setStatus("ok");
        } else {
          setStatus("denied");
        }
      })
      .catch(() => router.push("/login"));
  }, [router, requiredRole]);

  if (status === "loading") return <AdminLoading />;
  if (status === "denied") return <AdminDenied />;
  return <>{children}</>;
}

/* ===== Layout ===== */
export function AdminLayout({ children, title, description }: { children: ReactNode; title: string; description?: string }) {
  return (
    <div className="min-h-screen bg-[#F9FAFB]">
      <AdminHeader />
      <div className="max-w-[1440px] mx-auto px-6 lg:px-10 py-6">
        <div className="mb-6">
          <h1 className="text-[22px] font-bold text-[#111]">{title}</h1>
          {description && <p className="text-[13px] text-[#6B7280] mt-1">{description}</p>}
        </div>
        {children}
      </div>
    </div>
  );
}

/* ===== Header ===== */
function AdminHeader() {
  return (
    <header className="h-[56px] bg-white border-b border-[#E5E7EB] flex items-center px-6 lg:px-10 sticky top-0 z-50">
      <div className="w-full max-w-[1440px] mx-auto flex items-center justify-between">
        <div className="flex items-center gap-6">
          <Link href="/admin" className="flex items-center gap-2">
            <div className="w-[28px] h-[28px] bg-[#F4B400] rounded-full flex items-center justify-center">
              <span className="text-[#111] font-bold text-[8px]">IFB</span>
            </div>
            <span className="text-[13px] font-bold text-[#111]">Admin</span>
          </Link>
          <nav className="hidden md:flex items-center gap-4">
            {[
              { label: "Notícias", href: "/admin/noticias" },
              { label: "Políticos", href: "/admin/politicos" },
              { label: "Usuários", href: "/admin/usuarios" },
            ].map((item) => (
              <Link key={item.href} href={item.href} className="text-[12px] font-medium text-[#6B7280] hover:text-[#111] transition">
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
        <Link href="/" className="text-[12px] text-[#9CA3AF] hover:text-[#111] transition">← Voltar ao site</Link>
      </div>
    </header>
  );
}

/* ===== Metric Card ===== */
export function MetricCard({ label, value, highlight }: { label: string; value: string | number; highlight?: boolean }) {
  return (
    <div className={`rounded-[12px] border px-4 py-3 ${highlight ? "border-[#F4B400] bg-[#FFFDF5]" : "border-[#E5E7EB] bg-white"}`}>
      <p className="text-[20px] font-bold text-[#111]">{value}</p>
      <p className="text-[11px] text-[#6B7280] mt-0.5">{label}</p>
    </div>
  );
}

/* ===== Data Table ===== */
interface Column<T> {
  key: string;
  label: string;
  render?: (item: T) => ReactNode;
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyExtractor: (item: T) => string;
  onRowClick?: (item: T) => void;
  emptyMessage?: string;
}

export function DataTable<T>({ columns, data, keyExtractor, onRowClick, emptyMessage }: DataTableProps<T>) {
  if (data.length === 0) return <EmptyState message={emptyMessage || "Nenhum registro encontrado."} />;
  return (
    <div className="overflow-x-auto border border-[#E5E7EB] rounded-[12px] bg-white">
      <table className="w-full text-[13px]">
        <thead>
          <tr className="border-b border-[#E9ECEF] bg-[#F9FAFB]">
            {columns.map((col) => (
              <th key={col.key} className={`text-left px-4 py-2.5 text-[11px] font-semibold text-[#6B7280] uppercase tracking-wide ${col.className || ""}`}>{col.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((item) => (
            <tr
              key={keyExtractor(item)}
              onClick={() => onRowClick?.(item)}
              className={`border-b border-[#F3F4F6] last:border-0 ${onRowClick ? "cursor-pointer hover:bg-[#F9FAFB]" : ""} transition`}
            >
              {columns.map((col) => (
                <td key={col.key} className={`px-4 py-3 text-[#374151] ${col.className || ""}`}>
                  {col.render ? col.render(item) : (item as any)[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/* ===== Pagination ===== */
export function Pagination({ page, totalPages, onChange }: { page: number; totalPages: number; onChange: (p: number) => void }) {
  if (totalPages <= 1) return null;
  return (
    <div className="flex items-center justify-center gap-2 mt-5">
      <button onClick={() => onChange(page - 1)} disabled={page <= 1} className="px-3 py-1.5 text-[12px] border border-[#E5E7EB] rounded-[8px] disabled:opacity-30 hover:bg-[#F6F7F9] transition">Anterior</button>
      <span className="text-[12px] text-[#6B7280] px-2">{page} de {totalPages}</span>
      <button onClick={() => onChange(page + 1)} disabled={page >= totalPages} className="px-3 py-1.5 text-[12px] border border-[#E5E7EB] rounded-[8px] disabled:opacity-30 hover:bg-[#F6F7F9] transition">Próxima</button>
    </div>
  );
}

/* ===== Empty State ===== */
export function EmptyState({ message, icon }: { message: string; icon?: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      {icon || <div className="w-[40px] h-[40px] bg-[#F6F7F9] rounded-full flex items-center justify-center mb-3"><span className="text-[16px]">📭</span></div>}
      <p className="text-[13px] text-[#6B7280]">{message}</p>
    </div>
  );
}

/* ===== Error State ===== */
export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <p className="text-[13px] text-red-600 mb-3">{message}</p>
      {onRetry && <button onClick={onRetry} className="text-[12px] text-[#111] underline">Tentar novamente</button>}
    </div>
  );
}

/* ===== Confirm Dialog ===== */
export function ConfirmDialog({ open, title, description, confirmLabel, danger, onConfirm, onCancel }: {
  open: boolean; title: string; description: string; confirmLabel?: string; danger?: boolean; onConfirm: () => void; onCancel: () => void;
}) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/30" onClick={onCancel}>
      <div className="bg-white rounded-[16px] border border-[#E5E7EB] p-6 max-w-[400px] w-full mx-4 shadow-lg" onClick={(e) => e.stopPropagation()}>
        <h3 className="text-[16px] font-bold text-[#111] mb-2">{title}</h3>
        <p className="text-[13px] text-[#6B7280] mb-5">{description}</p>
        <div className="flex gap-3 justify-end">
          <button onClick={onCancel} className="px-4 py-2 text-[13px] text-[#374151] border border-[#E5E7EB] rounded-[8px] hover:bg-[#F6F7F9] transition">Cancelar</button>
          <button onClick={onConfirm} className={`px-4 py-2 text-[13px] font-semibold rounded-[8px] transition ${danger ? "bg-red-600 text-white hover:bg-red-700" : "bg-[#F4B400] text-[#111] hover:bg-[#D9A000]"}`}>
            {confirmLabel || "Confirmar"}
          </button>
        </div>
      </div>
    </div>
  );
}

/* ===== Status Badge ===== */
export function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    approved: "bg-green-50 text-green-700 border-green-200",
    auto_approved: "bg-green-50 text-green-700 border-green-200",
    pending: "bg-yellow-50 text-yellow-700 border-yellow-200",
    rejected: "bg-red-50 text-red-700 border-red-200",
    collected: "bg-blue-50 text-blue-700 border-blue-200",
    active: "bg-green-50 text-green-700 border-green-200",
    inactive: "bg-gray-50 text-gray-600 border-gray-200",
  };
  const cls = styles[status] || "bg-gray-50 text-gray-600 border-gray-200";
  return <span className={`inline-block px-2 py-0.5 text-[10px] font-semibold rounded border ${cls}`}>{status}</span>;
}

/* ===== Loading ===== */
function AdminLoading() {
  return (
    <div className="min-h-screen bg-[#F9FAFB] flex items-center justify-center">
      <p className="text-[13px] text-[#6B7280]">Carregando...</p>
    </div>
  );
}

function AdminDenied() {
  return (
    <div className="min-h-screen bg-[#F9FAFB] flex items-center justify-center">
      <div className="text-center">
        <p className="text-[15px] font-bold text-[#111] mb-2">Acesso negado</p>
        <p className="text-[13px] text-[#6B7280]">Você não possui permissão para acessar esta página.</p>
        <Link href="/" className="mt-4 inline-block text-[13px] text-[#F4B400] hover:underline">Voltar ao site</Link>
      </div>
    </div>
  );
}
