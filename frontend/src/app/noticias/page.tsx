"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface NewsItem {
  id: string;
  title: string;
  source_url: string;
  category: string;
  published_at: string | null;
  politician_name: string;
  politician_slug: string;
  summary: string | null;
}

export default function NoticiasPage() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/api/v1/news/latest?limit=20`)
      .then((r) => r.json())
      .then((d) => setNews(d.items || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="min-h-screen bg-[#FAFAFA]">
      <div className="bg-white border-b border-[#E5E7EB]">
        <div className="max-w-[1440px] mx-auto px-6 lg:px-12 py-8">
          <Link href="/" className="text-[13px] text-[#9CA3AF] hover:text-[#111] transition mb-4 inline-block">← Início</Link>
          <h1 className="text-[28px] font-bold text-[#111]">Notícias</h1>
          <p className="text-[14px] text-[#6B7280] mt-2 max-w-[600px]">
            Notícias coletadas, classificadas por inteligência artificial e revisadas antes da publicação.
          </p>
        </div>
      </div>

      <div className="max-w-[1440px] mx-auto px-6 lg:px-12 py-8">
        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="bg-white border border-[#E5E7EB] rounded-[12px] p-5 animate-pulse">
                <div className="h-3 bg-[#E9ECEF] rounded w-1/4 mb-3" />
                <div className="h-4 bg-[#E9ECEF] rounded w-full mb-2" />
                <div className="h-4 bg-[#E9ECEF] rounded w-2/3" />
              </div>
            ))}
          </div>
        )}

        {!loading && news.length === 0 && (
          <div className="bg-white border border-[#E5E7EB] rounded-[16px] p-10 max-w-[540px] mx-auto text-center">
            <div className="w-[56px] h-[56px] bg-[#FFF8E1] rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-7 h-7 text-[#F4B400]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" /></svg>
            </div>
            <h2 className="text-[18px] font-bold text-[#111] mb-2">Nenhuma notícia publicada ainda</h2>
            <p className="text-[13px] text-[#6B7280] leading-relaxed max-w-[380px] mx-auto">
              As notícias são coletadas automaticamente, classificadas por IA e só são publicadas após revisão humana. Nenhuma notícia foi aprovada para exibição até o momento.
            </p>
          </div>
        )}

        {!loading && news.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {news.map((n) => (
              <article key={n.id} className="bg-white border border-[#E5E7EB] rounded-[12px] p-5 hover:shadow-sm transition">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-[#F4B400]/15 text-[#92700C]">
                    {n.category?.toUpperCase() || "GERAL"}
                  </span>
                  {n.published_at && (
                    <span className="text-[11px] text-[#9CA3AF]">{new Date(n.published_at).toLocaleDateString("pt-BR")}</span>
                  )}
                </div>
                <a href={n.source_url} target="_blank" rel="noopener noreferrer" className="text-[14px] font-semibold text-[#111] leading-snug hover:text-[#F4B400] transition line-clamp-2 block">
                  {n.title}
                </a>
                {n.summary && (
                  <p className="text-[12px] text-[#6B7280] mt-2 line-clamp-2 leading-relaxed">{n.summary}</p>
                )}
                <div className="mt-3 flex items-center justify-between">
                  <Link href={`/politicos/${n.politician_slug}`} className="text-[12px] text-[#374151] hover:text-[#F4B400] font-medium transition">
                    {n.politician_name}
                  </Link>
                  <a href={n.source_url} target="_blank" rel="noopener noreferrer" className="text-[11px] text-[#9CA3AF] hover:text-[#111] transition">
                    Ver matéria original ↗
                  </a>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
