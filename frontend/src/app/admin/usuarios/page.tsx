"use client";

import { useEffect, useState, useCallback } from "react";
import { AdminGuard, AdminLayout, DataTable, StatusBadge, MetricCard } from "@/components/admin";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface RoleItem {
  id: string;
  name: string;
  description: string | null;
}

export default function AdminUsuariosPage() {
  return (
    <AdminGuard requiredRole="superadmin">
      <AdminLayout title="Usuários e Permissões" description="Gerenciamento de roles, permissões e acesso ao sistema.">
        <UsuariosContent />
      </AdminLayout>
    </AdminGuard>
  );
}

function UsuariosContent() {
  const [roles, setRoles] = useState<RoleItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRoles = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/admin/roles`, { credentials: "include" });
      if (res.ok) {
        const data = await res.json();
        setRoles(data.roles || data || []);
      } else if (res.status === 403) {
        setError("Sem permissão para acessar roles.");
      }
    } catch {
      setError("Erro ao carregar dados.");
    }
    setLoading(false);
  }, []);

  useEffect(() => { fetchRoles(); }, [fetchRoles]);

  if (error) return <div className="text-[13px] text-red-600 py-8 text-center">{error}</div>;

  return (
    <>
      {/* Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-6">
        <MetricCard label="Roles cadastradas" value={roles.length} />
      </div>

      {/* Roles Table */}
      <h2 className="text-[14px] font-bold text-[#111] mb-3">Roles do sistema</h2>
      {loading ? (
        <div className="animate-pulse space-y-3">{[1,2,3].map(i => <div key={i} className="h-10 bg-[#E9ECEF] rounded-[8px]" />)}</div>
      ) : (
        <DataTable
          columns={[
            { key: "name", label: "Nome", render: (item) => <span className="font-medium text-[#111]">{item.name}</span> },
            { key: "description", label: "Descrição", render: (item) => <span className="text-[12px] text-[#6B7280]">{item.description || "—"}</span> },
          ]}
          data={roles}
          keyExtractor={(item) => item.id}
          emptyMessage="Nenhuma role configurada."
        />
      )}

      <div className="mt-8 bg-[#F6F7F9] border border-[#E9ECEF] rounded-[12px] p-5">
        <h3 className="text-[13px] font-semibold text-[#111] mb-2">Gerenciamento de usuários</h3>
        <p className="text-[12px] text-[#6B7280] leading-relaxed">
          Para atribuir ou remover roles de um usuário específico, utilize os endpoints administrativos via CLI ou API diretamente.
          O painel visual de gerenciamento individual de usuários estará disponível na próxima versão.
        </p>
      </div>
    </>
  );
}
