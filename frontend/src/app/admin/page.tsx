"use client";

import Link from "next/link";
import { AdminGuard, AdminLayout } from "@/components/admin";

export default function AdminPage() {
  return (
    <AdminGuard>
      <AdminLayout title="Painel Administrativo" description="Gerenciamento do Instituto Fiscaliza Brasil.">
        <AdminDashboard />
      </AdminLayout>
    </AdminGuard>
  );
}

function AdminDashboard() {
  const modules = [
    { label: "Notícias", description: "Revisão, classificação e publicação", href: "/admin/noticias", ready: true },
    { label: "Políticos", description: "Cadastro, edição e publicação de perfis", href: "/admin/politicos", ready: true },
    { label: "Usuários", description: "Roles, permissões e acesso", href: "/admin/usuarios", ready: true },
    { label: "Integrações", description: "Câmara, Senado, TSE, sincronizações", href: "/admin/integracoes", ready: false },
    { label: "Promessas", description: "Extração, revisão e avaliação", href: "/admin/promessas", ready: false },
    { label: "Processos", description: "Revisão judicial e contestações", href: "/admin/processos", ready: false },
    { label: "Doações", description: "Pagamentos e recibos", href: "/admin/doacoes", ready: false },
    { label: "Transparência", description: "Receitas, despesas e contratos", href: "/admin/transparencia", ready: false },
    { label: "Indicadores", description: "Metodologias e rankings", href: "/admin/indicadores", ready: false },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {modules.map((mod) => (
        mod.ready ? (
          <Link key={mod.label} href={mod.href} className="bg-white border border-[#E5E7EB] rounded-[12px] p-5 hover:border-[#F4B400] hover:shadow-sm transition group">
            <h3 className="text-[14px] font-semibold text-[#111] group-hover:text-[#F4B400] transition">{mod.label}</h3>
            <p className="text-[12px] text-[#6B7280] mt-1">{mod.description}</p>
          </Link>
        ) : (
          <div key={mod.label} className="bg-[#F9FAFB] border border-[#E9ECEF] rounded-[12px] p-5 opacity-60">
            <h3 className="text-[14px] font-semibold text-[#374151]">{mod.label}</h3>
            <p className="text-[12px] text-[#9CA3AF] mt-1">{mod.description}</p>
            <span className="inline-block mt-2 text-[10px] text-[#9CA3AF] bg-[#F3F4F6] px-2 py-0.5 rounded">Em preparação</span>
          </div>
        )
      ))}
    </div>
  );
}
