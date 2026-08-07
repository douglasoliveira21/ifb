"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface PoliticianDetail {
  id: string;
  full_name: string;
  ballot_name: string | null;
  slug: string;
  biography: string | null;
  birth_date: string | null;
  photo_url: string | null;
  current_status: string;
  current_party: { name: string; acronym: string } | null;
  current_position_name: string | null;
  state_code: string | null;
  city_name: string | null;
  website_url: string | null;
  is_verified: boolean;
  aliases: { alias: string; alias_type: string }[];
  social_links: { platform: string; url: string }[];
  updated_at: string;
  source_url: string | null;
}

type TabId = "overview" | "propositions" | "votes" | "expenses" | "committees" | "electoral" | "news" | "promises" | "judicial";

const TABS: { id: TabId; label: string }[] = [
  { id: "overview", label: "Visão Geral" },
  { id: "propositions", label: "Projetos" },
  { id: "votes", label: "Votações" },
  { id: "expenses", label: "Gastos" },
  { id: "committees", label: "Comissões" },
  { id: "electoral", label: "Eleições" },
  { id: "news", label: "Notícias" },
  { id: "promises", label: "Promessas" },
  { id: "judicial", label: "Processos" },
];

export default function PoliticianProfilePage() {
  const params = useParams();
  const slug = params?.slug as string;

  const [politician, setPolitician] = useState<PoliticianDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabId>("overview");

  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    fetch(`${API_URL}/api/v1/politicians/${slug}`)
      .then((r) => { if (!r.ok) throw new Error(`${r.status}`); return r.json(); })
      .then(setPolitician)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [slug]);

  if (loading) return <LoadingSkeleton />;
  if (error || !politician) return <ErrorState error={error} />;

  return (
    <main className="min-h-screen bg-ifb-black">
      {/* ===== PROFILE HEADER ===== */}
      <div className="border-b border-ifb-gray-800">
        <div className="max-w-ifb mx-auto px-6 lg:px-10 py-6">
          <Link href="/politicos" className="text-[12px] text-ifb-gray-500 hover:text-ifb-yellow transition uppercase tracking-wide mb-4 inline-block">
            ← Voltar para pesquisa
          </Link>

          <div className="flex flex-col sm:flex-row gap-5 items-start">
            {/* Photo */}
            <div className="w-[96px] h-[96px] bg-ifb-gray-800 flex-shrink-0 overflow-hidden border-2 border-ifb-gray-700">
              {politician.photo_url ? (
                <img src={politician.photo_url} alt="" className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <svg className="w-10 h-10 text-ifb-gray-600" fill="currentColor" viewBox="0 0 20 20"><path d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" /></svg>
                </div>
              )}
            </div>

            {/* Info */}
            <div className="flex-1 min-w-0">
              <h1 className="text-[24px] sm:text-[28px] font-black text-ifb-white uppercase tracking-tight truncate">{politician.full_name}</h1>
              <div className="flex flex-wrap gap-2 mt-2">
                {politician.current_party?.acronym && (
                  <span className="px-3 py-1 text-[11px] font-bold bg-ifb-yellow text-ifb-black">{politician.current_party.acronym}</span>
                )}
                {politician.state_code && (
                  <span className="px-3 py-1 text-[11px] font-bold bg-ifb-gray-800 text-ifb-gray-300 border border-ifb-gray-700">{politician.state_code}</span>
                )}
                {politician.current_position_name && (
                  <span className="px-3 py-1 text-[11px] font-medium bg-ifb-gray-800 text-ifb-gray-400 border border-ifb-gray-700">{politician.current_position_name}</span>
                )}
                {politician.is_verified && (
                  <span className="px-3 py-1 text-[11px] font-bold bg-green-900/50 text-green-400 border border-green-700">✓ Verificado</span>
                )}
              </div>
              {politician.source_url && (
                <p className="text-[11px] text-ifb-gray-500 mt-2">Fonte: <a href={politician.source_url} target="_blank" rel="noopener noreferrer" className="text-ifb-yellow hover:underline">Dados oficiais ↗</a></p>
              )}
            </div>
          </div>

          {/* Tabs */}
          <div className="mt-6 flex gap-0 overflow-x-auto scrollbar-hide" style={{ WebkitOverflowScrolling: "touch" }}>
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2.5 text-[12px] font-bold uppercase tracking-wide whitespace-nowrap transition flex-shrink-0 border-b-[3px] ${
                  activeTab === tab.id
                    ? "border-ifb-yellow text-ifb-yellow bg-ifb-yellow/5"
                    : "border-transparent text-ifb-gray-500 hover:text-ifb-gray-300"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ===== TAB CONTENT ===== */}
      <div className="max-w-ifb mx-auto px-6 lg:px-10 py-6">
        {activeTab === "overview" && <OverviewTab politician={politician} />}
        {activeTab === "propositions" && <DataTab slug={slug} endpoint="propositions" title="Projetos de Lei" />}
        {activeTab === "votes" && <VotesTab slug={slug} />}
        {activeTab === "expenses" && <DataTab slug={slug} endpoint="parliamentary-expenses" title="Gastos Parlamentares" />}
        {activeTab === "committees" && <DataTab slug={slug} endpoint="committees" title="Comissões" />}
        {activeTab === "electoral" && <DataTab slug={slug} endpoint="candidacies" title="Histórico Eleitoral" />}
        {activeTab === "news" && <DataTab slug={slug} endpoint="news" title="Notícias" />}
        {activeTab === "promises" && <DataTab slug={slug} endpoint="promises" title="Promessas de Campanha" />}
        {activeTab === "judicial" && <DataTab slug={slug} endpoint="judicial-cases" title="Processos Judiciais" disclaimer="A existência de processo não implica culpa." />}
      </div>
    </main>
  );
}

/* ===== OVERVIEW ===== */
function OverviewTab({ politician }: { politician: PoliticianDetail }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <div className="lg:col-span-2 space-y-5">
        {/* Biografia */}
        <section className="border border-ifb-gray-800 bg-ifb-black-soft p-6">
          <h2 className="text-[14px] font-bold uppercase tracking-wide text-ifb-yellow mb-3">Biografia</h2>
          <p className="text-[13px] text-ifb-gray-300 leading-relaxed">
            {politician.biography || "Informação ainda não disponível para este político."}
          </p>
        </section>

        {/* Aliases */}
        {politician.aliases.length > 0 && (
          <section className="border border-ifb-gray-800 bg-ifb-black-soft p-6">
            <h2 className="text-[14px] font-bold uppercase tracking-wide text-ifb-yellow mb-3">Nomes Conhecidos</h2>
            <div className="flex flex-wrap gap-2">
              {politician.aliases.map((a, i) => (
                <span key={i} className="px-3 py-1 text-[12px] text-ifb-gray-300 bg-ifb-gray-800 border border-ifb-gray-700">{a.alias}</span>
              ))}
            </div>
          </section>
        )}

        {/* Social links */}
        {politician.social_links.length > 0 && (
          <section className="border border-ifb-gray-800 bg-ifb-black-soft p-6">
            <h2 className="text-[14px] font-bold uppercase tracking-wide text-ifb-yellow mb-3">Redes Sociais</h2>
            <div className="flex flex-wrap gap-3">
              {politician.social_links.map((s, i) => (
                <a key={i} href={s.url} target="_blank" rel="noopener noreferrer" className="text-[12px] text-ifb-gray-400 hover:text-ifb-yellow transition border border-ifb-gray-700 px-3 py-1.5">
                  {s.platform} ↗
                </a>
              ))}
            </div>
          </section>
        )}
      </div>

      {/* Sidebar */}
      <div className="space-y-5">
        <section className="border border-ifb-gray-800 bg-ifb-black-soft p-6">
          <h3 className="text-[12px] font-bold uppercase tracking-wider text-ifb-gray-400 mb-4">Dados</h3>
          <dl className="space-y-3">
            <InfoRow label="Cargo" value={politician.current_position_name} />
            <InfoRow label="Partido" value={politician.current_party ? `${politician.current_party.name} (${politician.current_party.acronym})` : null} />
            <InfoRow label="Estado" value={politician.state_code} />
            <InfoRow label="Município" value={politician.city_name} />
            <InfoRow label="Nascimento" value={politician.birth_date} />
            {politician.website_url && (
              <div>
                <dt className="text-[11px] text-ifb-gray-500 uppercase">Site</dt>
                <dd><a href={politician.website_url} target="_blank" rel="noopener noreferrer" className="text-[12px] text-ifb-yellow hover:underline break-all">{politician.website_url}</a></dd>
              </div>
            )}
          </dl>
        </section>

        <section className="border border-ifb-gray-800 bg-ifb-black-soft p-6">
          <h3 className="text-[12px] font-bold uppercase tracking-wider text-ifb-gray-400 mb-3">Fontes e Atualização</h3>
          <p className="text-[11px] text-ifb-gray-500 leading-relaxed">
            Dados de fontes públicas oficiais (Câmara, Senado, TSE).<br />
            Atualizado: {new Date(politician.updated_at).toLocaleDateString("pt-BR")}
          </p>
        </section>
      </div>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string | null | undefined }) {
  return (
    <div>
      <dt className="text-[11px] text-ifb-gray-500 uppercase">{label}</dt>
      <dd className="text-[13px] text-ifb-white font-medium">{value || "—"}</dd>
    </div>
  );
}

/* ===== VOTES TAB (dedicated with filters) ===== */
function VotesTab({ slug }: { slug: string }) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [voteFilter, setVoteFilter] = useState("");
  const [yearFilter, setYearFilter] = useState("");

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (yearFilter) params.set("year", yearFilter);
    params.set("limit", "100");
    fetch(`${API_URL}/api/v1/politicians/${slug}/votes?${params}`)
      .then((r) => { if (!r.ok) throw new Error(`${r.status}`); return r.json(); })
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [slug, yearFilter]);

  const VOTE_LABELS: Record<string, string> = {
    yes: "Sim", no: "Não", abstention: "Abstenção", obstruction: "Obstrução",
    art17: "Art. 17", president: "Presidente", absent: "Ausente", other: "Outro",
  };

  const VOTE_COLORS: Record<string, string> = {
    yes: "text-green-400", no: "text-red-400", abstention: "text-ifb-gray-400",
    obstruction: "text-orange-400", absent: "text-ifb-gray-600", president: "text-ifb-yellow",
    art17: "text-blue-400", other: "text-ifb-gray-500",
  };

  if (loading) return (
    <div className="border border-ifb-gray-800 bg-ifb-black-soft p-6 animate-pulse">
      <div className="h-4 bg-ifb-gray-800 w-1/3 mb-4" />
      <div className="space-y-3">{[1,2,3,4,5].map(i => <div key={i} className="h-12 bg-ifb-gray-800" />)}</div>
    </div>
  );

  if (error) return (
    <div className="border border-ifb-gray-800 bg-ifb-black-soft p-6">
      <h2 className="text-[14px] font-bold uppercase tracking-wide text-ifb-yellow mb-2">Votações</h2>
      <p className="text-[13px] text-red-400">Erro ao carregar dados ({error})</p>
    </div>
  );

  const items = data?.data || [];

  // Apply client-side filters
  const filtered = items.filter((v: any) => {
    if (voteFilter && v.vote !== voteFilter && v.normalized_vote !== voteFilter) return false;
    if (search) {
      const desc = (v.description || "").toLowerCase();
      if (!desc.includes(search.toLowerCase())) return false;
    }
    return true;
  });

  // Count by vote type
  const counts: Record<string, number> = {};
  items.forEach((v: any) => {
    const key = v.vote || v.normalized_vote || "other";
    counts[key] = (counts[key] || 0) + 1;
  });

  return (
    <div className="border border-ifb-gray-800 bg-ifb-black-soft p-6">
      <h2 className="text-[14px] font-bold uppercase tracking-wide text-ifb-yellow mb-4">Votações</h2>

      {/* Summary counters */}
      {items.length > 0 && (
        <div className="grid grid-cols-3 sm:grid-cols-6 gap-2 mb-5">
          {Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 6).map(([key, count]) => (
            <button
              key={key}
              onClick={() => setVoteFilter(voteFilter === key ? "" : key)}
              className={`text-center py-2 border transition ${voteFilter === key ? "border-ifb-yellow bg-ifb-yellow/10" : "border-ifb-gray-700 hover:border-ifb-gray-500"}`}
            >
              <p className={`text-[16px] font-bold ${VOTE_COLORS[key] || "text-ifb-gray-400"}`}>{count}</p>
              <p className="text-[9px] text-ifb-gray-500 uppercase">{VOTE_LABELS[key] || key}</p>
            </button>
          ))}
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-4">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar por descrição da votação..."
          className="flex-1 min-w-[200px] h-[38px] px-3 bg-ifb-black border border-ifb-gray-700 text-[12px] text-ifb-white placeholder:text-ifb-gray-600 outline-none focus:border-ifb-yellow transition"
        />
        <select
          value={yearFilter}
          onChange={(e) => setYearFilter(e.target.value)}
          className="h-[38px] px-3 bg-ifb-black border border-ifb-gray-700 text-[12px] text-ifb-gray-300 outline-none focus:border-ifb-yellow"
        >
          <option value="">Todos os anos</option>
          <option value="2026">2026</option>
          <option value="2025">2025</option>
          <option value="2024">2024</option>
          <option value="2023">2023</option>
        </select>
        <select
          value={voteFilter}
          onChange={(e) => setVoteFilter(e.target.value)}
          className="h-[38px] px-3 bg-ifb-black border border-ifb-gray-700 text-[12px] text-ifb-gray-300 outline-none focus:border-ifb-yellow"
        >
          <option value="">Todos os votos</option>
          <option value="yes">Sim</option>
          <option value="no">Não</option>
          <option value="abstention">Abstenção</option>
          <option value="obstruction">Obstrução</option>
          <option value="absent">Ausente</option>
        </select>
        {(search || voteFilter || yearFilter) && (
          <button onClick={() => { setSearch(""); setVoteFilter(""); setYearFilter(""); }} className="h-[38px] px-3 text-[11px] text-ifb-gray-400 hover:text-ifb-yellow transition">Limpar</button>
        )}
      </div>

      {/* Results count */}
      <p className="text-[11px] text-ifb-gray-500 mb-3">
        {filtered.length} votação(ões) {voteFilter && `(${VOTE_LABELS[voteFilter] || voteFilter})`} {search && `contendo "${search}"`}
      </p>

      {/* Table */}
      {filtered.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-[13px] text-ifb-gray-500">Nenhuma votação encontrada com os filtros selecionados.</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-[12px]">
            <thead>
              <tr className="border-b border-ifb-gray-700">
                <th className="text-left py-2 px-3 text-[10px] font-bold text-ifb-gray-500 uppercase w-[90px]">Data</th>
                <th className="text-left py-2 px-3 text-[10px] font-bold text-ifb-gray-500 uppercase">Descrição</th>
                <th className="text-left py-2 px-3 text-[10px] font-bold text-ifb-gray-500 uppercase w-[100px]">Voto</th>
                <th className="text-left py-2 px-3 text-[10px] font-bold text-ifb-gray-500 uppercase w-[100px]">Resultado</th>
              </tr>
            </thead>
            <tbody>
              {filtered.slice(0, 50).map((v: any, i: number) => {
                const voteKey = v.vote || v.normalized_vote || "other";
                return (
                  <tr key={i} className="border-b border-ifb-gray-800 hover:bg-ifb-yellow/5 transition">
                    <td className="py-3 px-3 text-ifb-gray-400 whitespace-nowrap">
                      {v.date ? new Date(v.date).toLocaleDateString("pt-BR") : "—"}
                    </td>
                    <td className="py-3 px-3 text-ifb-gray-300 leading-snug">
                      {v.description || "Sem descrição"}
                    </td>
                    <td className="py-3 px-3">
                      <span className={`font-bold ${VOTE_COLORS[voteKey] || "text-ifb-gray-400"}`}>
                        {v.original_vote || VOTE_LABELS[voteKey] || voteKey}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-ifb-gray-400">
                      {v.result === "true" || v.result === "1" ? "Aprovado" : v.result === "false" || v.result === "0" ? "Rejeitado" : v.result || "—"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {filtered.length > 50 && <p className="text-[11px] text-ifb-gray-600 mt-3 text-center">Mostrando 50 de {filtered.length} votações</p>}
        </div>
      )}
    </div>
  );
}

/* ===== GENERIC DATA TAB ===== */
function DataTab({ slug, endpoint, title, disclaimer }: { slug: string; endpoint: string; title: string; disclaimer?: string }) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch(`${API_URL}/api/v1/politicians/${slug}/${endpoint}`)
      .then((r) => { if (!r.ok) throw new Error(`${r.status}`); return r.json(); })
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [slug, endpoint]);

  if (loading) return (
    <div className="border border-ifb-gray-800 bg-ifb-black-soft p-6 animate-pulse">
      <div className="h-4 bg-ifb-gray-800 w-1/3 mb-4" />
      <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="h-10 bg-ifb-gray-800" />)}</div>
    </div>
  );

  if (error) return (
    <div className="border border-ifb-gray-800 bg-ifb-black-soft p-6">
      <h2 className="text-[14px] font-bold uppercase tracking-wide text-ifb-yellow mb-2">{title}</h2>
      <p className="text-[13px] text-red-400">Erro ao carregar dados ({error})</p>
    </div>
  );

  const items = data?.data || data?.items || [];
  const isEmpty = Array.isArray(items) && items.length === 0;

  return (
    <div className="border border-ifb-gray-800 bg-ifb-black-soft p-6">
      <h2 className="text-[14px] font-bold uppercase tracking-wide text-ifb-yellow mb-4">{title}</h2>

      {disclaimer && (
        <div className="mb-4 p-3 border border-ifb-yellow/30 bg-ifb-yellow/5">
          <p className="text-[11px] text-ifb-gray-300">{disclaimer}</p>
        </div>
      )}

      {isEmpty ? (
        <div className="text-center py-10">
          <p className="text-[13px] text-ifb-gray-500">{getEmptyMessage(endpoint)}</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-[12px]">
            <thead>
              <tr className="border-b border-ifb-gray-700">
                {getTableHeaders(endpoint).map((h, i) => (
                  <th key={i} className="text-left py-2 px-3 text-[10px] font-bold text-ifb-gray-500 uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {items.slice(0, 30).map((item: any, i: number) => (
                <tr key={i} className="border-b border-ifb-gray-800 hover:bg-ifb-yellow/5 transition">
                  {getTableCells(endpoint, item).map((cell, j) => (
                    <td key={j} className="py-2.5 px-3 text-ifb-gray-300">{cell}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          {items.length > 30 && <p className="text-[11px] text-ifb-gray-600 mt-3 text-center">Mostrando 30 de {items.length}</p>}
        </div>
      )}

      {data?.summary && (
        <div className="mt-4 pt-4 border-t border-ifb-gray-800 grid grid-cols-2 sm:grid-cols-4 gap-3">
          {Object.entries(data.summary).filter(([k]) => k !== "methodology_url").map(([key, val]) => (
            <div key={key} className="text-center">
              <p className="text-[18px] font-bold text-ifb-yellow">{String(val ?? "—")}</p>
              <p className="text-[10px] text-ifb-gray-500 uppercase tracking-wide">{formatLabel(key)}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ===== HELPERS ===== */
function getEmptyMessage(endpoint: string): string {
  const messages: Record<string, string> = {
    candidacies: "Dados eleitorais ainda não importados para este político.",
    assets: "Patrimônio declarado ainda não disponível.",
    "election-results": "Resultados eleitorais ainda não importados.",
    propositions: "Nenhuma proposição sincronizada para este mandato.",
    votes: "Registros de votações em processamento.",
    attendance: "Dados de presença não disponíveis via API oficial.",
    "parliamentary-expenses": "Nenhuma despesa parlamentar encontrada.",
    committees: "Nenhuma comissão vinculada.",
    news: "Nenhuma notícia revisada publicada para este político.",
    promises: "Promessas de campanha ainda não avaliadas.",
    "judicial-cases": "Nenhum processo confirmado e publicado.",
  };
  return messages[endpoint] || "Dados ainda não disponíveis.";
}

function getTableHeaders(endpoint: string): string[] {
  const headers: Record<string, string[]> = {
    candidacies: ["Ano", "Cargo", "Partido", "Nº", "UF", "Status"],
    assets: ["Ano", "Categoria", "Descrição", "Valor"],
    propositions: ["Tipo", "Nº", "Ano", "Ementa", "Status"],
    votes: ["Data", "Descrição", "Voto", "Resultado"],
    "parliamentary-expenses": ["Mês", "Categoria", "Fornecedor", "Valor"],
    committees: ["Comissão", "Sigla", "Papel"],
    news: ["Data", "Título", "Impacto", "Confiança"],
    promises: ["Promessa", "Categoria", "Status", "Progresso"],
    "judicial-cases": ["Tribunal", "Classe", "Papel", "Status"],
  };
  return headers[endpoint] || ["Dados"];
}

function getTableCells(endpoint: string, item: any): string[] {
  switch (endpoint) {
    case "candidacies": return [item.election_year, item.position || "—", item.party_acronym || "—", item.ballot_number || "—", item.state_code || "—", item.status || "—"];
    case "assets": return [item.election_year, item.category || "—", (item.description || "").slice(0, 40), formatCurrency(item.declared_value)];
    case "propositions": return [item.type || item.type_acronym || "—", item.number || "—", item.year || "—", (item.title || item.summary || "").slice(0, 50), item.status || "—"];
    case "votes": return [item.date?.slice(0, 10) || "—", (item.description || "").slice(0, 40), item.vote || item.normalized_vote || "—", item.result || "—"];
    case "parliamentary-expenses": return [item.month || "—", (item.category || "").slice(0, 25), (item.supplier_name || "—").slice(0, 20), formatCurrency(item.net_amount || item.gross_amount)];
    case "committees": return [item.committee_name || "—", item.acronym || "—", item.role || "Membro"];
    case "news": return [item.published_at?.slice(0, 10) || "—", (item.title || "").slice(0, 40), item.reputational_impact || "—", item.confidence ? `${Math.round(item.confidence * 100)}%` : "—"];
    case "promises": return [item.title?.slice(0, 40) || "—", item.category || "—", item.status || "—", item.progress_percentage != null ? `${item.progress_percentage}%` : "—"];
    case "judicial-cases": return [item.tribunal || "—", item.case_class || "—", item.politician_role || "—", item.procedural_status || item.normalized_status || "—"];
    default: return [JSON.stringify(item).slice(0, 80)];
  }
}

function formatCurrency(value: any): string {
  if (value == null) return "—";
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(Number(value));
}

function formatLabel(key: string): string {
  const labels: Record<string, string> = {
    total_sessions: "Sessões", present: "Presenças", absent: "Ausências",
    attendance_rate: "% Presença", total_articles: "Notícias", positive: "Positivas",
    negative: "Negativas", neutral: "Neutras", total_promises: "Promessas",
    fulfilled: "Cumpridas", in_progress: "Em andamento", total_confirmed_cases: "Processos",
  };
  return labels[key] || key.replace(/_/g, " ");
}

/* ===== STATES ===== */
function LoadingSkeleton() {
  return (
    <main className="min-h-screen bg-ifb-black">
      <div className="max-w-ifb mx-auto px-6 lg:px-10 py-10">
        <div className="animate-pulse space-y-4">
          <div className="flex gap-5">
            <div className="w-[96px] h-[96px] bg-ifb-gray-800" />
            <div className="flex-1 space-y-3"><div className="h-6 bg-ifb-gray-800 w-1/2" /><div className="h-4 bg-ifb-gray-800 w-1/3" /></div>
          </div>
          <div className="h-[3px] bg-ifb-gray-800 mt-6" />
          <div className="h-[200px] bg-ifb-gray-800 mt-4" />
        </div>
      </div>
    </main>
  );
}

function ErrorState({ error }: { error: string | null }) {
  return (
    <main className="min-h-screen bg-ifb-black flex items-center justify-center">
      <div className="text-center">
        <p className="text-[16px] font-bold text-ifb-white mb-2">Político não encontrado</p>
        <p className="text-[13px] text-ifb-gray-400 mb-4">{error || "Verifique o endereço e tente novamente."}</p>
        <Link href="/politicos" className="text-[13px] font-bold uppercase text-ifb-yellow hover:underline">← Voltar para pesquisa</Link>
      </div>
    </main>
  );
}
