"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { AdminGuard, AdminLayout, DataTable, Pagination, StatusBadge } from "@/components/admin";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface PoliticianAdmin {
  id: string;
  full_name: string;
  ballot_name: string | null;
  slug: string;
  photo_url: string | null;
  state_code: string | null;
  current_status: string;
  is_public: boolean;
  is_verified: boolean;
  current_party: { acronym: string } | null;
  current_position_name: string | null;
  updated_at: string;
}

export default function AdminPoliticosPage() {
  return (
    <AdminGuard requiredRole="superadmin">
      <AdminLayout title="Políticos" description="Gerenciamento do cadastro nacional de políticos.">
        <PoliticosContent />
      </AdminLayout>
    </AdminGuard>
  );
}

function PoliticosContent() {
  const [items, setItems] = useState<PoliticianAdmin[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [stateFilter, setState] = useState("");

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.set("q", search);
      if (stateFilter) params.set("state", stateFilter);
      params.set("page", String(page));
      params.set("limit", "20");
      const res = await fetch(`${API_URL}/api/v1/politicians?${params}`, { credentials: "include" });
      if (res.ok) {
        const data = await res.json();
        setItems(data.items || []);
        setTotal(data.total || 0);
      }
    } catch {}
    setLoading(false);
  }, [page, search, stateFilter]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const totalPages = Math.ceil(total / 20);

  return (
    <>
      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-5">
        <input
          type="text"
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          placeholder="Buscar por nome..."
          className="flex-1 h-[40px] px-4 border border-[#E5E7EB] rounded-[10px] text-[13px] outline-none focus:ring-2 focus:ring-[#F4B400] transition"
        />
        <select value={stateFilter} onChange={(e) => { setState(e.target.value); setPage(1); }} className="h-[40px] px-3 border border-[#E5E7EB] rounded-[10px] text-[13px] bg-white outline-none focus:ring-2 focus:ring-[#F4B400]">
          <option value="">Todos os estados</option>
          {["AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT","PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO"].map(uf => <option key={uf} value={uf}>{uf}</option>)}
        </select>
      </div>

      <p className="text-[12px] text-[#9CA3AF] mb-3">{total} político(s) encontrado(s)</p>

      {loading ? (
        <div className="animate-pulse space-y-3">{[1,2,3,4,5].map(i => <div key={i} className="h-14 bg-[#E9ECEF] rounded-[8px]" />)}</div>
      ) : (
        <DataTable
          columns={[
            { key: "photo", label: "", className: "w-[40px]", render: (item) => (
              <div className="w-[32px] h-[32px] rounded-full bg-[#E9ECEF] overflow-hidden">
                {item.photo_url && <img src={item.photo_url} alt="" className="w-full h-full object-cover" onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />}
              </div>
            )},
            { key: "full_name", label: "Nome", render: (item) => (
              <div>
                <p className="font-medium text-[#111] text-[13px]">{item.full_name}</p>
                {item.ballot_name && item.ballot_name !== item.full_name && <p className="text-[11px] text-[#9CA3AF]">{item.ballot_name}</p>}
              </div>
            )},
            { key: "party", label: "Partido", render: (item) => <span className="text-[12px]">{item.current_party?.acronym || "—"}</span> },
            { key: "state_code", label: "UF", render: (item) => <span className="text-[12px]">{item.state_code || "—"}</span> },
            { key: "position", label: "Cargo", render: (item) => <span className="text-[12px]">{item.current_position_name || "—"}</span> },
            { key: "status", label: "Status", render: (item) => <StatusBadge status={item.is_public ? "active" : "inactive"} /> },
            { key: "actions", label: "", render: (item) => (
              <Link href={`/politicos/${item.slug}`} className="text-[11px] text-[#F4B400] hover:underline">Ver perfil →</Link>
            )},
          ]}
          data={items}
          keyExtractor={(item) => item.id}
          emptyMessage="Nenhum político encontrado."
        />
      )}

      <Pagination page={page} totalPages={totalPages} onChange={setPage} />
    </>
  );
}
