"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface NewsDetail {
  id: string;
  title: string;
  source_url: string;
  source_domain: string;
  image_url: string | null;
  published_at: string | null;
  category: string;
  reputational_impact: string;
  impact_intensity: number;
  sentiment: string;
  summary: string | null;
  confidence: number;
  fact_type: string;
  politician_name?: string;
  politician_slug?: string;
}

export default function NoticiaDetailPage() {
  const params = useParams();
  const id = params?.id as string;
  const [item, setItem] = useState<NewsDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    fetch(`${API_URL}/api/v1/news/${id}`)
      .then((r) => {
        if (!r.ok) throw new Error(`${r.status}`);
        return r.json();
      })
      .then(setItem)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <main className="min-h-screen bg-[#FAFAFA] flex items-center justify-center">
        <p className="text-[13px] text-[#6B7280]">Carregando...</p>
      </main>
    );
  }

  if (error || !item) {
    return (
      <main className="min-h-screen bg-[#FAFAFA]">
        <div className="max-w-[800px] mx-auto px-6 py-12 text-center">
          <p className="text-[15px] font-bold text-[#111] mb-2">Notícia não encontrada</p>
          <p className="text-[13px] text-[#6B7280] mb-4">A classificação pode não estar aprovada ou o ID é inválido.</p>
          <Link href="/noticias" className="text-[13px] text-[#F4B400] hover:underline">← Voltar para notícias</Link>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#FAFAFA]">
      <div className="bg-white border-b border-[#E5E7EB]">
        <div className="max-w-[800px] mx-auto px-6 lg:px-12 py-6">
          <Link href="/noticias" className="text-[13px] text-[#9CA3AF] hover:text-[#111] transition mb-4 inline-block">← Notícias</Link>
        </div>
      </div>

      <div className="max-w-[800px] mx-auto px-6 lg:px-12 py-8">
        <article className="bg-white border border-[#E5E7EB] rounded-[16px] p-6 lg:p-8">
          {/* Header */}
          <div className="flex items-center gap-2 mb-3">
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-[#F4B400]/15 text-[#92700C]">{item.category?.toUpperCase() || "GERAL"}</span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-[#E9ECEF] text-[#6B7280]">{item.fact_type}</span>
            {item.published_at && <span className="text-[11px] text-[#9CA3AF]">{new Date(item.published_at).toLocaleDateString("pt-BR")}</span>}
          </div>

          <h1 className="text-[20px] font-bold text-[#111] leading-snug mb-4">{item.title}</h1>

          {/* Summary */}
          {item.summary && (
            <div className="bg-[#F6F7F9] border border-[#E9ECEF] rounded-[12px] p-4 mb-6">
              <p className="text-[11px] font-semibold text-[#6B7280] uppercase mb-1">Resumo IFB</p>
              <p className="text-[13px] text-[#374151] leading-relaxed">{item.summary}</p>
            </div>
          )}

          {/* Classification details */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
            <div className="bg-[#F9FAFB] border border-[#E9ECEF] rounded-[10px] p-3 text-center">
              <p className="text-[12px] font-bold text-[#111]">{item.sentiment}</p>
              <p className="text-[10px] text-[#9CA3AF]">Sentimento</p>
            </div>
            <div className="bg-[#F9FAFB] border border-[#E9ECEF] rounded-[10px] p-3 text-center">
              <p className="text-[12px] font-bold text-[#111]">{item.reputational_impact}</p>
              <p className="text-[10px] text-[#9CA3AF]">Impacto</p>
            </div>
            <div className="bg-[#F9FAFB] border border-[#E9ECEF] rounded-[10px] p-3 text-center">
              <p className="text-[12px] font-bold text-[#111]">{(item.confidence * 100).toFixed(0)}%</p>
              <p className="text-[10px] text-[#9CA3AF]">Confiança</p>
            </div>
            <div className="bg-[#F9FAFB] border border-[#E9ECEF] rounded-[10px] p-3 text-center">
              <p className="text-[12px] font-bold text-[#111]">{item.impact_intensity}/10</p>
              <p className="text-[10px] text-[#9CA3AF]">Intensidade</p>
            </div>
          </div>

          {/* Source */}
          <div className="border-t border-[#E9ECEF] pt-5 mt-5">
            <a href={item.source_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 h-[38px] px-5 bg-[#F4B400] hover:bg-[#D9A000] text-[#111] text-[13px] font-semibold rounded-[10px] transition-colors">
              Ler matéria original ↗
            </a>
            <p className="text-[11px] text-[#9CA3AF] mt-3">Fonte: {item.source_domain || "Veículo jornalístico"}</p>
          </div>

          {/* Disclaimer */}
          <div className="bg-[#FFF8E1] border border-[#F4B400]/20 rounded-[10px] p-4 mt-6">
            <p className="text-[12px] text-[#374151] leading-relaxed">
              <strong>Aviso:</strong> Esta classificação foi produzida com auxílio de inteligência artificial e revisada antes da publicação.
              Não representa juízo de valor, condenação ou absolvição. Para metodologia completa, consulte{" "}
              <Link href="/metodologia" className="text-[#F4B400] hover:underline">nossa página de metodologia</Link>.
            </p>
          </div>
        </article>
      </div>
    </main>
  );
}
