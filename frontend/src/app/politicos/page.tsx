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
    <Suspense fallback={<div className="min-h-screen bg-ifb-black flex items-center justify-center"><p className="text-ifb-gray-400 text-sm">Carregando...</p></div>}>
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

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (currentQuery) params.set("q", currentQuery);
      if (currentState) params.set("state", currentState);
      if (currentParty) params.set("party", currentParty);
      if (currentPosition) params.set("position", currentPosition);
      params.set("page", String(currentPage));
      params.set("limit", "18");
      const res = await fetch(`${API_URL}/api/v1/politicians?${params}`);
      if (!res.ok) throw new Error(`Erro ${res.status}`);
      setData(await res.json());
    } catch (e: any) {
      setError(e.message || "Erro ao carregar");
    } finally {
      setLoading(false);
    }
  }, [currentQuery, currentState, currentParty, currentPosition, currentPage]);

  useEffect(() => { fetchData(); }, [fetchData]);
  useEffect(() => { setQuery(currentQuery); }, [currentQuery]);

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
    updateURL(query, currentState, currentParty, currentPosition, 1);
  }

  function setFilter(key: string, value: string) {
    const st = key === "state" ? value : currentState;
    const pt = key === "party" ? value : currentParty;
    const pos = key === "position" ? value : currentPosition;
    updateURL(currentQuery, st, pt, pos, 1);
  }

  const positionLabel = currentPosition === "Deputado Federal" ? "Deputados" : currentPosition === "Senador" ? "Senadores" : "Políticos";

  return (
    <main className="min-h-screen bg-ifb-black">
      {/* ===== HEADER ===== */}
      <div className="border-b border-ifb-gray-800">
        <div className="max-w-ifb mx-auto px-6 lg:px-10 py-8">
          <div className="flex items-center gap-3 mb-1">
            <div className="w-[4px] h-[28px] bg-ifb-yellow" />
            <h1 className="text-[24px] sm:text-[32px] font-black uppercase tracking-tight text-ifb-white">
              Mockup da Interface de Pesquisa
            </h1>
          </div>
        </div>
      </div>

      {/* ===== SEARCH + FILTERS ===== */}
      <div className="border-b border-ifb-gray-800">
        <div className="max-w-ifb mx-auto px-6 lg:px-10 py-5">
          <form onSubmit={handleSearch} className="flex flex-col lg:flex-row gap-4">
            {/* Search input */}
            <div className="flex items-center flex-1 bg-ifb-black-soft border border-ifb-gray-700 px-4 gap-3">
              <svg className="w-5 h-5 text-ifb-gray-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder='Buscar por nome, CPF ou palavra-chave (ex: "Deputado federal SP")...'
                className="flex-1 h-[48px] text-[14px] text-ifb-white placeholder:text-ifb-gray-500 bg-transparent outline-none"
              />
              <button type="submit" className="text-ifb-yellow font-bold text-[12px] uppercase tracking-wide hover:text-ifb-yellow-hover transition hidden sm:block">Buscar</button>
            </div>

            {/* Filter pills */}
            <div className="flex flex-wrap gap-2">
              <FilterPill
                icon={<svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" /></svg>}
                label="Todos os Cargos"
                value={currentPosition}
                options={[{ v: "", l: "Todos os Cargos" }, { v: "Deputado Federal", l: "Deputado Federal" }, { v: "Senador", l: "Senador" }]}
                onChange={(v) => setFilter("position", v)}
              />
              <FilterPill
                icon={<svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" /></svg>}
                label="Estado (UF)"
                value={currentState}
                options={[{ v: "", l: "Estado (UF)" }, ...UF_LIST.map(uf => ({ v: uf, l: uf }))]}
                onChange={(v) => setFilter("state", v)}
              />
              <FilterPill
                icon={<svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M3 6a3 3 0 013-3h10a1 1 0 01.8 1.6L14.25 8l2.55 3.4A1 1 0 0116 13H6a1 1 0 00-1 1v3a1 1 0 11-2 0V6z" /></svg>}
                label="Partido"
                value={currentParty}
                options={[{ v: "", l: "Partido" }, ...PARTIES.map(p => ({ v: p, l: p }))]}
                onChange={(v) => setFilter("party", v)}
              />
            </div>
          </form>
        </div>
      </div>

      {/* ===== RESULTS ===== */}
      <div className="max-w-ifb mx-auto px-6 lg:px-10 py-6">
        {/* Results header */}
        <div className="flex items-center justify-between mb-5">
          <p className="text-[14px] text-ifb-gray-400">
            Exibindo <span className="text-ifb-yellow font-bold">{data?.total?.toLocaleString("pt-BR") || "—"} {positionLabel}</span> encontrados
          </p>
          <div className="hidden sm:block text-[12px] text-ifb-gray-500 border border-ifb-gray-700 px-3 py-1.5">
            Ordenar por: Maior Presença em Sessões ▼
          </div>
        </div>

        {/* Yellow divider */}
        <div className="h-[3px] bg-ifb-yellow mb-6" />

        {/* Loading */}
        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="border border-ifb-gray-700 bg-ifb-black-soft p-5 animate-pulse">
                <div className="flex gap-4">
                  <div className="w-[72px] h-[72px] bg-ifb-gray-800" />
                  <div className="flex-1 space-y-2"><div className="h-4 bg-ifb-gray-800 w-3/4" /><div className="h-3 bg-ifb-gray-800 w-1/2" /></div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Error */}
        {!loading && error && (
          <div className="text-center py-12">
            <p className="text-red-500 text-[14px] mb-3">{error}</p>
            <button onClick={fetchData} className="text-ifb-yellow text-[13px] font-bold uppercase hover:underline">Tentar novamente</button>
          </div>
        )}

        {/* Empty */}
        {!loading && !error && data && data.items.length === 0 && (
          <div className="text-center py-16">
            <p className="text-ifb-gray-400 text-[15px]">Nenhum político encontrado com os filtros selecionados.</p>
            <button onClick={() => updateURL("", "", "", "", 1)} className="mt-3 text-ifb-yellow text-[13px] font-bold uppercase hover:underline">Limpar filtros</button>
          </div>
        )}

        {/* Grid */}
        {!loading && !error && data && data.items.length > 0 && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {data.items.map((p) => (
                <PoliticianCard key={p.id} politician={p} />
              ))}
            </div>

            {/* Pagination */}
            {data.pages > 1 && (
              <div className="flex justify-center items-center gap-3 mt-8">
                <button
                  onClick={() => updateURL(currentQuery, currentState, currentParty, currentPosition, currentPage - 1)}
                  disabled={currentPage <= 1}
                  className="px-4 py-2 text-[12px] font-bold uppercase text-ifb-white border border-ifb-gray-700 disabled:opacity-30 hover:border-ifb-yellow hover:text-ifb-yellow transition"
                >
                  Anterior
                </button>
                <span className="text-[12px] text-ifb-gray-400">{currentPage} de {data.pages}</span>
                <button
                  onClick={() => updateURL(currentQuery, currentState, currentParty, currentPosition, currentPage + 1)}
                  disabled={currentPage >= data.pages}
                  className="px-4 py-2 text-[12px] font-bold uppercase text-ifb-white border border-ifb-gray-700 disabled:opacity-30 hover:border-ifb-yellow hover:text-ifb-yellow transition"
                >
                  Próxima
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </main>
  );
}

/* ===== POLITICIAN CARD ===== */
function PoliticianCard({ politician: p }: { politician: Politician }) {
  return (
    <div className="border border-ifb-gray-700 bg-ifb-black-soft relative group hover:border-ifb-yellow transition-all">
      {/* Yellow top line */}
      <div className="h-[3px] bg-ifb-yellow" />

      {/* Main content */}
      <div className="p-5">
        <div className="flex gap-4 items-start">
          {/* Photo */}
          <div className="w-[72px] h-[72px] bg-ifb-gray-800 flex-shrink-0 overflow-hidden border border-ifb-gray-700">
            {p.photo_url ? (
              <img src={p.photo_url} alt="" className="w-full h-full object-cover" onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-ifb-gray-600">
                <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20"><path d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" /></svg>
              </div>
            )}
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0">
            <h3 className="text-[16px] font-bold text-ifb-white truncate">{p.full_name}</h3>
            <div className="flex flex-wrap gap-1.5 mt-2">
              {p.current_party?.acronym && (
                <span className="px-2 py-0.5 text-[10px] font-bold bg-ifb-yellow text-ifb-black">{p.current_party.acronym}</span>
              )}
              {p.state_code && (
                <span className="px-2 py-0.5 text-[10px] font-bold bg-ifb-gray-800 text-ifb-gray-300 border border-ifb-gray-700">{p.state_code}</span>
              )}
              {p.current_position_name && (
                <span className="px-2 py-0.5 text-[10px] font-medium bg-ifb-gray-800 text-ifb-gray-400 border border-ifb-gray-700">
                  {p.current_position_name === "Deputado Federal" ? "Dep. Federal" : p.current_position_name}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Metrics row */}
        <div className="grid grid-cols-3 gap-2 mt-4 pt-4 border-t border-ifb-gray-800">
          <Metric label="PRESENÇA" value="—" />
          <Metric label="PROCESSOS" value="—" />
          <Metric label="EMENDAS" value="—" />
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between mt-4 pt-3 border-t border-ifb-gray-800">
          <span className="text-[11px] text-ifb-gray-500 flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-ifb-gray-600" />
            Dados em processamento
          </span>
          <Link
            href={`/politicos/${p.slug}`}
            className="text-[11px] font-bold uppercase tracking-wide text-ifb-yellow border border-ifb-yellow px-3 py-1.5 hover:bg-ifb-yellow hover:text-ifb-black transition"
          >
            Ver Perfil →
          </Link>
        </div>
      </div>
    </div>
  );
}

/* ===== METRIC ===== */
function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="text-center">
      <p className="text-[16px] font-bold text-ifb-yellow">{value}</p>
      <p className="text-[9px] text-ifb-gray-500 uppercase tracking-wider mt-0.5">{label}</p>
    </div>
  );
}

/* ===== FILTER PILL ===== */
function FilterPill({ icon, label, value, options, onChange }: {
  icon: React.ReactNode;
  label: string;
  value: string;
  options: { v: string; l: string }[];
  onChange: (v: string) => void;
}) {
  return (
    <div className={`flex items-center gap-2 px-4 py-2 border text-[12px] font-medium cursor-pointer transition ${value ? "border-ifb-yellow bg-ifb-yellow/10 text-ifb-yellow" : "border-ifb-gray-600 text-ifb-gray-300 hover:border-ifb-gray-400"}`}>
      {icon}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="bg-transparent outline-none cursor-pointer text-current appearance-none"
        style={{ WebkitAppearance: "none" }}
      >
        {options.map((opt) => (
          <option key={opt.v} value={opt.v} className="bg-ifb-black text-ifb-white">{opt.l}</option>
        ))}
      </select>
    </div>
  );
}
