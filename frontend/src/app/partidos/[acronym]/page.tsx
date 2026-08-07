"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface PartyMember {
  id: string;
  full_name: string;
  ballot_name: string | null;
  slug: string;
  photo_url: string | null;
  state_code: string | null;
  position: string | null;
}

interface PartyDetail {
  id: string;
  name: string;
  acronym: string;
  electoral_number: number | null;
  logo_url: string | null;
  official_url: string | null;
  status: string;
  total_politicians: number;
  deputies: number;
  senators: number;
  members: PartyMember[];
}

export default function PartidoDetailPage() {
  const params = useParams();
  const acronym = (params?.acronym as string)?.toUpperCase();
  const [party, setParty] = useState<PartyDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<"all" | "deputies" | "senators">("all");

  useEffect(() => {
    if (!acronym) return;
    fetch(`${API_URL}/api/v1/parties/${acronym}`)
      .then((r) => { if (!r.ok) throw new Error(`${r.status}`); return r.json(); })
      .then(setParty)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [acronym]);

  if (loading) return <div className="min-h-screen bg-[#FAFAFA] flex items-center justify-center"><p className="text-[13px] text-[#6B7280]">Carregando...</p></div>;
  if (error || !party) return (
    <div className="min-h-screen bg-[#FAFAFA] flex items-center justify-center flex-col gap-3">
      <p className="text-[14px] text-[#111] font-semibold">Partido não encontrado</p>
      <Link href="/partidos" className="text-[13px] text-[#F4B400] hover:underline">← Voltar para partidos</Link>
    </div>
  );

  const filteredMembers = party.members.filter((m) => {
    if (filter === "deputies") return m.position === "Deputado Federal";
    if (filter === "senators") return m.position === "Senador";
    return true;
  });

  return (
    <main className="min-h-screen bg-[#FAFAFA]">
      <div className="bg-white border-b border-[#E5E7EB]">
        <div className="max-w-[1440px] mx-auto px-6 lg:px-12 py-6">
          <Link href="/partidos" className="text-[12px] text-[#9CA3AF] hover:text-[#111] transition mb-3 inline-block">← Partidos</Link>
          <div className="flex items-center gap-4">
            <div className="w-[56px] h-[56px] bg-[#FFF8E1] rounded-full flex items-center justify-center">
              <span className="text-[18px] font-bold text-[#F4B400]">{party.electoral_number || party.acronym.slice(0, 2)}</span>
            </div>
            <div>
              <h1 className="text-[24px] font-bold text-[#111]">{party.acronym}</h1>
              <p className="text-[14px] text-[#6B7280]">{party.name}</p>
            </div>
          </div>

          {/* Stats */}
          <div className="flex items-center gap-6 mt-4 text-[13px]">
            <span className="text-[#374151]"><strong>{party.total_politicians}</strong> parlamentares</span>
            <span className="text-[#374151]"><strong>{party.deputies}</strong> deputados</span>
            <span className="text-[#374151]"><strong>{party.senators}</strong> senadores</span>
            {party.official_url && (
              <a href={party.official_url} target="_blank" rel="noopener noreferrer" className="text-[#F4B400] hover:underline">Site oficial ↗</a>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-[1440px] mx-auto px-6 lg:px-12 py-6">
        {/* Filter tabs */}
        <div className="flex gap-2 mb-5">
          {([["all", "Todos"], ["deputies", "Deputados"], ["senators", "Senadores"]] as const).map(([key, label]) => (
            <button key={key} onClick={() => setFilter(key)} className={`px-4 py-1.5 text-[12px] font-medium rounded-full transition ${filter === key ? "bg-[#F4B400] text-[#111]" : "bg-[#F6F7F9] text-[#6B7280] hover:bg-[#E9ECEF]"}`}>
              {label}
            </button>
          ))}
        </div>

        <p className="text-[12px] text-[#9CA3AF] mb-4">{filteredMembers.length} parlamentar(es)</p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {filteredMembers.map((m) => (
            <Link key={m.id} href={`/politicos/${m.slug}`} className="bg-white border border-[#E5E7EB] rounded-[12px] p-4 hover:border-[#F4B400] hover:shadow-sm transition group">
              <div className="flex items-center gap-3">
                <div className="w-[44px] h-[44px] rounded-full bg-[#E9ECEF] overflow-hidden flex-shrink-0">
                  {m.photo_url && <img src={m.photo_url} alt="" className="w-full h-full object-cover" onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-[13px] font-semibold text-[#111] truncate group-hover:text-[#F4B400] transition">{m.full_name}</p>
                  <p className="text-[11px] text-[#6B7280]">{m.position || "Parlamentar"} · {m.state_code || "—"}</p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </main>
  );
}
