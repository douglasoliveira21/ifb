"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Party {
  id: string;
  name: string;
  acronym: string;
  electoral_number: number | null;
  logo_url: string | null;
  official_url: string | null;
  total_politicians: number;
  deputies: number;
  senators: number;
}

export default function PartidosPage() {
  const [parties, setParties] = useState<Party[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/api/v1/parties`)
      .then((r) => r.json())
      .then((d) => setParties(d.items || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="min-h-screen bg-[#FAFAFA]">
      <div className="bg-white border-b border-[#E5E7EB]">
        <div className="max-w-[1440px] mx-auto px-6 lg:px-12 py-6">
          <div className="flex items-center justify-between">
            <div>
              <Link href="/politicos" className="text-[12px] text-[#9CA3AF] hover:text-[#111] transition mb-2 inline-block">← Políticos</Link>
              <h1 className="text-[24px] font-bold text-[#111]">Partidos Políticos</h1>
              <p className="text-[13px] text-[#6B7280] mt-1">Partidos com representação no Congresso Nacional.</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-[1440px] mx-auto px-6 lg:px-12 py-6">
        {loading && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1,2,3,4,5,6].map(i => (
              <div key={i} className="bg-white border border-[#E5E7EB] rounded-[12px] p-5 animate-pulse">
                <div className="h-5 bg-[#E9ECEF] rounded w-1/3 mb-3" />
                <div className="h-3 bg-[#E9ECEF] rounded w-2/3" />
              </div>
            ))}
          </div>
        )}

        {!loading && parties.length === 0 && (
          <div className="text-center py-16">
            <p className="text-[14px] text-[#6B7280]">Nenhum partido com representação encontrado.</p>
          </div>
        )}

        {!loading && parties.length > 0 && (
          <>
            <p className="text-[12px] text-[#9CA3AF] mb-4">{parties.length} partidos com representação</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {parties.map((p) => (
                <Link key={p.id} href={`/partidos/${p.acronym.toLowerCase()}`} className="bg-white border border-[#E5E7EB] rounded-[12px] p-5 hover:border-[#F4B400] hover:shadow-sm transition group">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h2 className="text-[16px] font-bold text-[#111] group-hover:text-[#F4B400] transition">{p.acronym}</h2>
                      <p className="text-[12px] text-[#6B7280]">{p.name}</p>
                    </div>
                    {p.electoral_number && (
                      <span className="text-[20px] font-bold text-[#E9ECEF]">{p.electoral_number}</span>
                    )}
                  </div>
                  <div className="flex items-center gap-4 text-[12px] text-[#374151]">
                    <span><strong>{p.total_politicians}</strong> parlamentares</span>
                    <span className="text-[#9CA3AF]">•</span>
                    <span>{p.deputies} dep.</span>
                    <span>{p.senators} sen.</span>
                  </div>
                  {p.official_url && (
                    <p className="text-[11px] text-[#9CA3AF] mt-2 truncate">{p.official_url.replace("https://", "").replace("http://", "")}</p>
                  )}
                </Link>
              ))}
            </div>
          </>
        )}
      </div>
    </main>
  );
}
