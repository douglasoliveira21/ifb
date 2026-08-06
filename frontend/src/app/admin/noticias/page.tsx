"use client";

import { useEffect, useState, useCallback } from "react";
import { AdminGuard, AdminLayout, MetricCard, DataTable, Pagination, StatusBadge, ConfirmDialog } from "@/components/admin";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ClassificationItem {
  classification_id: string;
  article_title: string;
  article_url: string;
  category: string;
  impact: string;
  intensity: number;
  confidence: number;
  summary: string | null;
  justification: string | null;
  review_reasons: string[] | null;
  created_at: string | null;
}

export default function AdminNoticiasPage() {
  return (
    <AdminGuard requiredRole="analyst">
      <AdminLayout title="Notícias" description="Revisão e aprovação de classificações de notícias.">
        <NoticiasContent />
      </AdminLayout>
    </AdminGuard>
  );
}

function NoticiasContent() {
  const [items, setItems] = useState<ClassificationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState<ClassificationItem | null>(null);
  const [confirmAction, setConfirmAction] = useState<{ id: string; action: "approve" | "reject" } | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  const fetchQueue = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/admin/news/review-queue?page=${page}&limit=20`, { credentials: "include" });
      if (res.ok) {
        const data = await res.json();
        setItems(data.data || []);
      }
    } catch {}
    setLoading(false);
  }, [page]);

  useEffect(() => { fetchQueue(); }, [fetchQueue]);

  async function handleAction(id: string, action: "approve" | "reject") {
    setActionLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/admin/news/${id}/${action}`, {
        method: "POST", credentials: "include",
      });
      if (res.ok) {
        setItems((prev) => prev.filter((i) => i.classification_id !== id));
        setSelected(null);
        setConfirmAction(null);
      }
    } catch {}
    setActionLoading(false);
  }

  return (
    <>
      {/* Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
        <MetricCard label="Pendentes" value={items.length} highlight />
        <MetricCard label="Página atual" value={page} />
      </div>

      {/* Table */}
      {loading ? (
        <div className="animate-pulse space-y-3">{[1,2,3,4,5].map(i => <div key={i} className="h-12 bg-[#E9ECEF] rounded-[8px]" />)}</div>
      ) : (
        <DataTable
          columns={[
            { key: "article_title", label: "Título", render: (item) => <span className="font-medium line-clamp-1 max-w-[240px] block">{item.article_title}</span> },
            { key: "category", label: "Categoria", render: (item) => <StatusBadge status={item.category} /> },
            { key: "impact", label: "Impacto", render: (item) => <span className="text-[12px]">{item.impact}</span> },
            { key: "confidence", label: "Confiança", render: (item) => <span className="text-[12px]">{(item.confidence * 100).toFixed(0)}%</span> },
            { key: "created_at", label: "Data", render: (item) => <span className="text-[11px] text-[#9CA3AF]">{item.created_at ? new Date(item.created_at).toLocaleDateString("pt-BR") : "—"}</span> },
            { key: "actions", label: "Ações", render: (item) => (
              <div className="flex gap-2">
                <button onClick={(e) => { e.stopPropagation(); setConfirmAction({ id: item.classification_id, action: "approve" }); }} className="px-2 py-1 text-[11px] font-medium bg-green-50 text-green-700 border border-green-200 rounded-[6px] hover:bg-green-100 transition">Aprovar</button>
                <button onClick={(e) => { e.stopPropagation(); setConfirmAction({ id: item.classification_id, action: "reject" }); }} className="px-2 py-1 text-[11px] font-medium bg-red-50 text-red-700 border border-red-200 rounded-[6px] hover:bg-red-100 transition">Rejeitar</button>
              </div>
            )},
          ]}
          data={items}
          keyExtractor={(item) => item.classification_id}
          onRowClick={setSelected}
          emptyMessage="Nenhuma notícia aguardando revisão."
        />
      )}

      <Pagination page={page} totalPages={10} onChange={setPage} />

      {/* Detail Drawer */}
      {selected && (
        <div className="fixed inset-0 z-[90] flex justify-end bg-black/20" onClick={() => setSelected(null)}>
          <div className="w-full max-w-[520px] bg-white h-full overflow-y-auto border-l border-[#E5E7EB] p-6" onClick={(e) => e.stopPropagation()}>
            <button onClick={() => setSelected(null)} className="text-[12px] text-[#9CA3AF] hover:text-[#111] mb-4">← Fechar</button>
            <h2 className="text-[16px] font-bold text-[#111] mb-2 leading-snug">{selected.article_title}</h2>
            <a href={selected.article_url} target="_blank" rel="noopener noreferrer" className="text-[12px] text-[#F4B400] hover:underline block mb-4">Ver matéria original ↗</a>

            <div className="space-y-3 text-[13px]">
              <Detail label="Categoria" value={selected.category} />
              <Detail label="Impacto" value={selected.impact} />
              <Detail label="Intensidade" value={String(selected.intensity)} />
              <Detail label="Confiança" value={`${(selected.confidence * 100).toFixed(1)}%`} />
              {selected.summary && <Detail label="Resumo" value={selected.summary} />}
              {selected.justification && <Detail label="Justificativa IA" value={selected.justification} />}
              {selected.review_reasons && selected.review_reasons.length > 0 && (
                <Detail label="Motivos da revisão" value={selected.review_reasons.join(", ")} />
              )}
            </div>

            <div className="flex gap-3 mt-6 pt-4 border-t border-[#E9ECEF]">
              <button onClick={() => setConfirmAction({ id: selected.classification_id, action: "approve" })} className="flex-1 h-[38px] bg-green-600 text-white text-[13px] font-semibold rounded-[8px] hover:bg-green-700 transition">Aprovar</button>
              <button onClick={() => setConfirmAction({ id: selected.classification_id, action: "reject" })} className="flex-1 h-[38px] bg-red-600 text-white text-[13px] font-semibold rounded-[8px] hover:bg-red-700 transition">Rejeitar</button>
            </div>
          </div>
        </div>
      )}

      {/* Confirm */}
      <ConfirmDialog
        open={!!confirmAction}
        title={confirmAction?.action === "approve" ? "Aprovar classificação?" : "Rejeitar classificação?"}
        description={confirmAction?.action === "approve" ? "A notícia será publicada no perfil do político." : "A notícia não será exibida publicamente."}
        confirmLabel={confirmAction?.action === "approve" ? "Aprovar" : "Rejeitar"}
        danger={confirmAction?.action === "reject"}
        onConfirm={() => confirmAction && handleAction(confirmAction.id, confirmAction.action)}
        onCancel={() => setConfirmAction(null)}
      />
    </>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-[11px] text-[#9CA3AF] font-medium uppercase tracking-wide">{label}</dt>
      <dd className="text-[#374151] mt-0.5">{value}</dd>
    </div>
  );
}
