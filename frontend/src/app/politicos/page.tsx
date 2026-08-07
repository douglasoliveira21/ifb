"use client";

import { Suspense, useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Politician {
  id: string;
  full_name: string;
  ballot_name: string | null;
  slug: string;
  photo_url: string | null;
  current_party: { acronym: string; name: string } | null;
  current_position_name: string | null;
  state_code: string | null;
}

interface ApiResponse {
  items: Politician[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

const UF_LIST = ["AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT","PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO"];

const PARTIES = ["MDB","PT","PL","PP","UNIÃO","PSD","REPUBLICANOS","PDT","PODE","PSB","PSOL","PSDB","NOVO","AVANTE","PCdoB","SOLIDARIEDADE","CIDADANIA","PRD","REDE"];

export default function PoliticosPageWrapper() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-[#FAFAFA] flex items-center justify-center"><p className="text-[13px] text-[#6B7280]">Carregando...</p></div>}>
      <PoliticosPage />
    </Suspense>
  );
}

function PoliticosPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [data, setData] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const currentQuery = searchParams?.get("q") || "";
  const currentState = searchParams?.get("state") || "";
  const currentParty = searchParams?.get("party") || "";
  const currentPosition = searchParams?.get("position") || "";
  const currentPage = parseInt(searchParams?.get("page") || "1", 10);

  const [query, setQuery] = useState(currentQuery);
  const [state, setState] = useState(currentState);
  const [party, setParty] = useState(currentParty);
  const [position, setPosition] = useState(currentPosition);

  const fetchData = useCallback(async (q: string, st: string, pt: string, pos: string, page: number) => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (q) params.set("q", q);
      if (st) params.set("state", st);
      if (pt) params.set("party", pt);
      if (pos) params.set("position", pos);
      params.set("page", String(page));
      params.set("limit", "20");
      const res = await fetch(`${API_URL}/api/v1/politicians?${params}`);
      if (!res.ok) throw new Error(`Erro ${res.status}`);
      setData(await res.json());
    } catch (e: any) {
      setError(e.message || "Erro ao carregar dados");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData(currentQuery, currentState, currentParty, currentPosition, currentPage);
  }, [currentQuery, currentState, currentParty, currentPosition, currentPage, fetchData]);

  function updateURL(q: string, st: string, pt: string, pos: string, page: number) {
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (st) params.set("state", st);
    if (pt) params.set("party", pt);
    if (pos) params.set("position", pos);
    if (page > 1) params.set("page", String(page));
    router.push(`/politicos${params.toString() ? `?${params}` : ""}`);
  }

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    updateURL(query, state, party, position, 1);
  }

  function clearFilters() {
    setQuery(""); setState(""); setParty(""); setPosition("");
    router.push("/politicos");
  }

  return (
    <main className="min-h-screen bg-[#FAFAFA]">
      {/* Header */}
      <div className="bg-white border-b border-[#E5E7EB]">
        <div className="max-w-[1440px] mx-auto px-6 lg:px-12 py-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-[24px] font-bold text-[#111]">Políticos</h1>
              <p className="text-[13px] text-[#6B7280] mt-1">Informações públicas sobre parlamentares brasileiros.</p>
            </div>
            <div className="flex items-center gap-3">
              <Link href="/ranking" className="text-[12px] font-medium text-[#F4B400] hover:underline">Ranking →</Link>
              <Link href="/partidos" className="text-[12px] font-medium text-[#F4B400] hover:underline">Partidos →</Link>
            </div>
          </div>

          {/* Filters */}
          <form onSubmit={handleSearch} className="flex flex-wrap gap-3">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Buscar por nome..."
              className="flex-1 min-w-[200px] h-[40px] px-4 border border-[#E5E7EB] rounded-[10px] text-[13px] outline-none focus:ring-2 focus:ring-[#F4B400] transition"
              aria-label="Buscar político"
            />
            <select value={state} onChange={(e) => { setState(e.target.value); updateURL(query, e.target.value, party, position, 1); }} className="h-[40px] px-3 border border-[#E5E7EB] rounded-[10px] text-[13px] bg-white outline-none focus:ring-2 focus:ring-[#F4B400]" aria-label="Estado">
              <option value="">Todos os estados</option>
              {UF_LIST.map(uf => <option key={uf} value={uf}>{uf}</option>)}
            </select>
            <select value={party} onChange={(e) => { setParty(e.target.value); updateURL(query, state, e.target.value, position, 1); }} className="h-[40px] px-3 border border-[#E5E7EB] rounded-[10px] text-[13px] bg-white outline-none focus:ring-2 focus:ring-[#F4B400]" aria-label="Partido">
              <option value="">Todos os partidos</option>
              {PARTIES.map(p => <option key={p} value={p}>{p}</option>)}
            </select>
            <select value={position} onChange={(e) => { setPosition(e.target.value); updateURL(query, state, party, e.target.value, 1); }} className="h-[40px] px-3 border border-[#E5E7EB] rounded-[10px] text-[13px] bg-white outline-none focus:ring-2 focus:ring-[#F4B400]" aria-label="Casa">
              <option value="">Câmara e Senado</option>
              <option value="Deputado Federal">Câmara</option>
              <option value="Senador">Senado</option>
            </select>
            <button type="submit" className="h-[40px] px-5 bg-[#F4B400] hover:bg-[#D9A000] text-[#111] text-[13px] font-semibold rounded-[10px] transition-colors">Buscar</button>
            {(currentQuery || currentState || currentParty || currentPosition) && (
              <button type="button" onClick={clearFilters} className="h-[40px] px-3 text-[12px] text-[#6B7280] hover:text-[#111] transition">Limpar</button>
            )}
          </form>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-[1440px] mx-auto px-6 lg:px-12 py-6">
        {loading && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="bg-white border border-[#E5E7EB] rounded-[12px] p-4 animate-pulse">
                <div className="flex items-center gap-3">
                  <div className="w-[48px] h-[48px] bg-[#E9ECEF] rounded-full" />
                  <div className="flex-1 space-y-2"><div className="h-3 bg-[#E9ECEF] rounded w-3/4" /><div className="h-2.5 bg-[#E9ECEF] rounded w-1/2" /></div>
                </div>
              </div>
            ))}
          </div>
        )}

        {!loading && error && (
          <div className="text-center py-12">
            <p className="text-[14px] text-red-600 mb-3">{error}</p>
            <button onClick={() => fetchData(currentQuery, currentState, currentParty, currentPosition, currentPage)} className="text-[13px] text-[#111] underline">Tentar novamente</button>
          </div>
        )}

        {!loading && !error && data && data.items.length === 0 && (
          <div className="text-center py-16">
            <p className="text-[15px] text-[#6B7280]">Nenhum político encontrado com os filtros selecionados.</p>
            <button onClick={clearFilters} className="mt-3 text-[13px] text-[#F4B400] hover:underline">Limpar filtros</button>
          </div>
        )}

        {!loading && !error && data && data.items.length > 0 && (
          <>
            <p className="text-[12px] text-[#9CA3AF] mb-4">{data.total.toLocaleString("pt-BR")} resultado(s)</p>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {data.items.map((p) => (
                <Link key={p.id} href={`/politicos/${p.slug}`} className="bg-white border border-[#E5E7EB] rounded-[12px] p-4 hover:border-[#F4B400] hover:shadow-sm transition group">
                  <div className="flex items-center gap-3">
                    <div className="w-[48px] h-[48px] rounded-full bg-[#E9ECEF] overflow-hidden flex-shrink-0">
                      {p.photo_url && <img src={p.photo_url} alt="" className="w-full h-full object-cover" onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />}
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-[13px] font-semibold text-[#111] truncate group-hover:text-[#F4B400] transition">{p.full_name}</p>
                      <p className="text-[11px] text-[#6B7280] truncate">
                        {p.current_party?.acronym || "Sem partido"}
                        {p.state_code && ` · ${p.state_code}`}
                      </p>
                      {p.current_position_name && (
                        <p className="text-[10px] text-[#9CA3AF] mt-0.5 truncate">{p.current_position_name}</p>
                      )}
                    </div>
                  </div>
                </Link>
              ))}
            </div>

            {/* Pagination */}
            {data.pages > 1 && (
              <div className="flex justify-center items-center gap-2 mt-8">
                <button onClick={() => updateURL(currentQuery, currentState, currentParty, currentPosition, currentPage - 1)} disabled={currentPage <= 1} className="px-4 py-2 text-[12px] border border-[#E5E7EB] rounded-[8px] disabled:opacity-30 hover:bg-[#F6F7F9] transition">Anterior</button>
                <span className="text-[12px] text-[#6B7280] px-3">{currentPage} de {data.pages}</span>
                <button onClick={() => updateURL(currentQuery, currentState, currentParty, currentPosition, currentPage + 1)} disabled={currentPage >= data.pages} className="px-4 py-2 text-[12px] border border-[#E5E7EB] rounded-[8px] disabled:opacity-30 hover:bg-[#F6F7F9] transition">Próxima</button>
              </div>
            )}
          </>
        )}
      </div>
    </main>
  );
}
