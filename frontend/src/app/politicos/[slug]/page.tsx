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

type TabId = "overview" | "electoral" | "assets" | "campaign" | "results" |
  "propositions" | "votes" | "attendance" | "expenses" | "committees" | "news" | "promises" | "judicial";

const TABS: { id: TabId; label: string }[] = [
  { id: "overview", label: "Visão geral" },
  { id: "electoral", label: "Eleições" },
  { id: "assets", label: "Bens" },
  { id: "campaign", label: "Campanhas" },
  { id: "results", label: "Resultados" },
  { id: "propositions", label: "Projetos" },
  { id: "votes", label: "Votações" },
  { id: "attendance", label: "Presença" },
  { id: "expenses", label: "Gastos" },
  { id: "committees", label: "Comissões" },
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
    <main className="min-h-screen bg-ifb-gray-light">
      {/* Header */}
      <div className="bg-white border-b border-ifb-gray-medium">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <Link href="/politicos" className="text-sm text-gray-500 hover:text-ifb-black mb-4 inline-block">
            ← Voltar para lista
          </Link>
          <div className="flex flex-col sm:flex-row gap-5 items-start">
            <div className="w-20 h-20 bg-ifb-gray-medium rounded-full flex-shrink-0 overflow-hidden">
              {politician.photo_url && <img src={politician.photo_url} alt="" className="w-full h-full object-cover" />}
            </div>
            <div className="flex-1 min-w-0">
              <h1 className="text-2xl font-bold text-ifb-black truncate">{politician.full_name}</h1>
              <p className="text-gray-600 mt-1 text-sm">
                {politician.current_party?.acronym || "Sem partido"}
                {politician.state_code && ` · ${politician.state_code}`}
                {politician.current_position_name && ` · ${politician.current_position_name}`}
              </p>
              {politician.is_verified && (
                <span className="inline-block mt-2 px-2 py-0.5 bg-ifb-green/10 text-ifb-green text-xs font-medium rounded">Verificado</span>
              )}
            </div>
          </div>

          {/* Tabs */}
          <div className="mt-6 -mb-px flex gap-1 overflow-x-auto pb-px scrollbar-hide" style={{WebkitOverflowScrolling: "touch"}}>
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-3 py-2 text-sm font-medium whitespace-nowrap border-b-2 transition flex-shrink-0 ${
                  activeTab === tab.id
                    ? "border-ifb-yellow text-ifb-black"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Tab Content */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        {activeTab === "overview" && <OverviewTab politician={politician} />}
        {activeTab === "electoral" && <ApiTab slug={slug} endpoint="candidacies" title="Histórico Eleitoral" />}
        {activeTab === "assets" && <ApiTab slug={slug} endpoint="assets" title="Bens Declarados" disclaimer="Valores declarados à Justiça Eleitoral. Não representam necessariamente o patrimônio atual." />}
        {activeTab === "campaign" && <CampaignTab slug={slug} />}
        {activeTab === "results" && <ApiTab slug={slug} endpoint="election-results" title="Resultados Eleitorais" />}
        {activeTab === "propositions" && <ApiTab slug={slug} endpoint="propositions" title="Projetos de Lei" />}
        {activeTab === "votes" && <ApiTab slug={slug} endpoint="votes" title="Votações" />}
        {activeTab === "attendance" && <ApiTab slug={slug} endpoint="attendance" title="Presença" />}
        {activeTab === "expenses" && <ExpensesTab slug={slug} />}
        {activeTab === "committees" && <ApiTab slug={slug} endpoint="committees" title="Comissões" />}
        {activeTab === "news" && <ApiTab slug={slug} endpoint="news" title="Notícias" />}
        {activeTab === "promises" && <ApiTab slug={slug} endpoint="promises" title="Promessas de Campanha" />}
        {activeTab === "judicial" && <ApiTab slug={slug} endpoint="judicial-cases" title="Processos Judiciais" disclaimer="A existência de processo não implica culpa." />}
      </div>
    </main>
  );
}

/* --- Sub-components --- */

function OverviewTab({ politician }: { politician: PoliticianDetail }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-6">
        <section className="bg-white rounded-lg border border-ifb-gray-medium p-6">
          <h2 className="text-lg font-semibold text-ifb-black mb-3">Biografia</h2>
          <p className="text-gray-600 text-sm leading-relaxed">
            {politician.biography || "Informação ainda não disponível."}
          </p>
        </section>

        {politician.aliases.length > 0 && (
          <section className="bg-white rounded-lg border border-ifb-gray-medium p-6">
            <h2 className="text-lg font-semibold text-ifb-black mb-3">Nomes conhecidos</h2>
            <div className="flex flex-wrap gap-2">
              {politician.aliases.map((a, i) => (
                <span key={i} className="px-3 py-1 bg-ifb-gray-light rounded-full text-sm text-gray-700">
                  {a.alias}
                </span>
              ))}
            </div>
          </section>
        )}
      </div>

      <div className="space-y-6">
        <section className="bg-white rounded-lg border border-ifb-gray-medium p-6">
          <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">Dados</h3>
          <dl className="space-y-3 text-sm">
            <DL label="Cargo" value={politician.current_position_name} />
            <DL label="Partido" value={politician.current_party ? `${politician.current_party.name} (${politician.current_party.acronym})` : null} />
            <DL label="Estado" value={politician.state_code} />
            <DL label="Município" value={politician.city_name} />
            <DL label="Nascimento" value={politician.birth_date} />
            {politician.website_url && (
              <div><dt className="text-gray-500">Site</dt><dd><a href={politician.website_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline text-xs break-all">{politician.website_url}</a></dd></div>
            )}
          </dl>
        </section>

        <section className="bg-white rounded-lg border border-ifb-gray-medium p-6">
          <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">Fontes</h3>
          <p className="text-xs text-gray-500">
            Dados de fontes públicas oficiais.<br />
            Atualizado: {new Date(politician.updated_at).toLocaleDateString("pt-BR")}
          </p>
        </section>
      </div>
    </div>
  );
}

function DL({ label, value }: { label: string; value: string | null | undefined }) {
  return (
    <div>
      <dt className="text-gray-500">{label}</dt>
      <dd className="text-ifb-black font-medium">{value || "—"}</dd>
    </div>
  );
}

function ApiTab({ slug, endpoint, title, disclaimer }: { slug: string; endpoint: string; title: string; disclaimer?: string }) {
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

  if (loading) return <div className="bg-white rounded-lg border border-ifb-gray-medium p-6 animate-pulse"><div className="h-4 bg-gray-200 rounded w-1/3 mb-4" /><div className="h-3 bg-gray-200 rounded w-full mb-2" /><div className="h-3 bg-gray-200 rounded w-2/3" /></div>;

  if (error) return (
    <div className="bg-white rounded-lg border border-ifb-gray-medium p-6">
      <h2 className="text-lg font-semibold text-ifb-black mb-2">{title}</h2>
      <p className="text-sm text-red-600">Erro ao carregar dados ({error})</p>
    </div>
  );

  const items = data?.data || data?.items || [];
  const isEmpty = Array.isArray(items) && items.length === 0;

  return (
    <div className="bg-white rounded-lg border border-ifb-gray-medium p-6">
      <h2 className="text-lg font-semibold text-ifb-black mb-4">{title}</h2>
      {disclaimer && (
        <div className="mb-4 p-3 bg-ifb-yellow/10 border border-ifb-yellow/30 rounded-md">
          <p className="text-xs text-gray-700">{disclaimer}</p>
        </div>
      )}

      {isEmpty ? (
        <div className="text-center py-8">
          <p className="text-gray-500">{getEmptyMessage(endpoint)}</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-ifb-gray-medium">
                {getTableHeaders(endpoint).map((h, i) => (
                  <th key={i} className="text-left py-2 px-3 text-xs font-semibold text-gray-600 uppercase">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {items.slice(0, 30).map((item: any, i: number) => (
                <tr key={i} className="border-b border-ifb-gray-light hover:bg-ifb-gray-light/50 transition">
                  {getTableCells(endpoint, item).map((cell, j) => (
                    <td key={j} className="py-2.5 px-3 text-gray-700">{cell}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          {items.length > 30 && (
            <p className="text-xs text-gray-400 mt-3 text-center">Mostrando 30 de {items.length} registros</p>
          )}
        </div>
      )}

      {data?.metadata && (
        <p className="text-xs text-gray-400 mt-4 pt-3 border-t border-ifb-gray-light">
          Fonte: {data.metadata.source || "Dados públicos oficiais"}
        </p>
      )}
      {data?.summary && (
        <div className="mt-4 pt-3 border-t border-ifb-gray-light grid grid-cols-2 sm:grid-cols-4 gap-3">
          {Object.entries(data.summary).filter(([k]) => k !== "methodology_url").map(([key, val]) => (
            <div key={key} className="text-center">
              <p className="text-lg font-bold text-ifb-black">{String(val ?? "—")}</p>
              <p className="text-xs text-gray-500">{formatLabel(key)}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function getEmptyMessage(endpoint: string): string {
  switch (endpoint) {
    case "candidacies": return "Os dados eleitorais deste perfil ainda não foram importados do TSE.";
    case "assets": return "O patrimônio declarado ainda não foi importado para este político.";
    case "campaign/revenues": return "As receitas de campanha ainda não foram importadas.";
    case "campaign/expenses": return "As despesas de campanha ainda não foram importadas.";
    case "election-results": return "Os resultados eleitorais ainda não foram importados.";
    case "propositions": return "Nenhuma proposição foi sincronizada para este mandato.";
    case "votes": return "Os registros de votações ainda estão em processamento.";
    case "attendance": return "A API oficial da Câmara não disponibiliza dados individuais de presença em formato importável. Este dado será adicionado quando uma fonte adequada estiver disponível.";
    case "parliamentary-expenses": return "Nenhuma despesa parlamentar encontrada para este político.";
    case "news": return "Nenhuma notícia revisada foi publicada para este político.";
    case "promises": return "As promessas de campanha ainda não foram avaliadas.";
    case "judicial-cases": return "Nenhum processo confirmado e publicado está disponível.";
    default: return "Dados ainda não disponíveis.";
  }
}

function getTableHeaders(endpoint: string): string[] {
  switch (endpoint) {
    case "candidacies": return ["Ano", "Cargo", "Partido", "Nº", "UF", "Status"];
    case "assets": return ["Ano", "Categoria", "Descrição", "Valor"];
    case "campaign/revenues": return ["Ano", "Doador", "Tipo", "Valor"];
    case "campaign/expenses": return ["Ano", "Fornecedor", "Tipo", "Valor"];
    case "election-results": return ["Ano", "Turno", "Votos", "%", "Resultado"];
    case "propositions": return ["Tipo", "Nº", "Ano", "Ementa", "Status"];
    case "votes": return ["Data", "Descrição", "Voto", "Resultado"];
    case "attendance": return ["Data", "Tipo", "Status", "Justificativa"];
    case "parliamentary-expenses": return ["Ano", "Mês", "Categoria", "Fornecedor", "Valor"];
    case "committees": return ["Comissão", "Sigla", "Papel"];
    case "news": return ["Data", "Título", "Impacto", "Confiança"];
    case "promises": return ["Promessa", "Categoria", "Status", "Progresso"];
    case "judicial-cases": return ["Tribunal", "Classe", "Papel", "Status"];
    default: return ["Dados"];
  }
}

function getTableCells(endpoint: string, item: any): string[] {
  switch (endpoint) {
    case "candidacies":
      return [item.election_year, item.position || "—", item.party_acronym || "—", item.ballot_number || "—", item.state_code || "—", item.status || "—"];
    case "assets":
      return [item.election_year, item.category || "—", (item.description || "").slice(0, 40), formatCurrency(item.declared_value)];
    case "campaign/revenues":
      return [item.election_year, (item.donor_name || "Não informado").slice(0, 30), item.revenue_type || "—", formatCurrency(item.amount)];
    case "campaign/expenses":
      return [item.election_year, (item.supplier_name || "—").slice(0, 30), item.expense_type || "—", formatCurrency(item.amount)];
    case "election-results":
      return [item.election_year, `${item.round}º`, item.votes?.toLocaleString("pt-BR") || "0", item.vote_percentage ? `${item.vote_percentage}%` : "—", item.elected ? "✓ Eleito" : item.result_status || "—"];
    case "propositions":
      return [item.type || item.type_acronym || "—", item.number || "—", item.year || "—", (item.title || item.summary || "").slice(0, 50), item.status || "—"];
    case "votes":
      return [item.date?.slice(0, 10) || "—", (item.description || "").slice(0, 40), item.vote || item.normalized_vote || "—", item.result || "—"];
    case "attendance":
      return [item.date?.slice(0, 10) || item.session_date || "—", item.session_type || "—", item.status || item.attendance_status || "—", item.justification || "—"];
    case "parliamentary-expenses":
      return [item.year, item.month, (item.category || "").slice(0, 25), (item.supplier_name || "—").slice(0, 20), formatCurrency(item.net_amount || item.gross_amount)];
    case "committees":
      return [item.committee_name || "—", item.acronym || "—", item.role || "Membro"];
    case "news":
      return [item.published_at?.slice(0, 10) || "—", (item.title || "").slice(0, 40), item.reputational_impact || "—", item.confidence ? `${Math.round(item.confidence * 100)}%` : "—"];
    case "promises":
      return [item.title?.slice(0, 40) || "—", item.category || "—", item.status || "—", item.progress_percentage != null ? `${item.progress_percentage}%` : "—"];
    case "judicial-cases":
      return [item.tribunal || "—", item.case_class || "—", item.politician_role || "—", item.procedural_status || item.normalized_status || "—"];
    default:
      return [JSON.stringify(item).slice(0, 80)];
  }
}

function formatCurrency(value: any): string {
  if (value == null) return "—";
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(Number(value));
}

function formatLabel(key: string): string {
  const labels: Record<string, string> = {
    total_sessions: "Sessões", present: "Presenças", absent: "Ausências",
    absent_justified: "Just.", attendance_rate: "% Presença",
    total_articles: "Notícias", positive: "Positivas", negative: "Negativas",
    neutral: "Neutras", total_promises: "Promessas", fulfilled: "Cumpridas",
    not_fulfilled: "Não cumpridas", in_progress: "Em andamento",
    total_confirmed_cases: "Processos",
  };
  return labels[key] || key.replace(/_/g, " ");
}

function CampaignTab({ slug }: { slug: string }) {
  const [revenues, setRevenues] = useState<any>(null);
  const [expenses, setExpenses] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch(`${API_URL}/api/v1/politicians/${slug}/campaign/revenues`).then(r => r.ok ? r.json() : null),
      fetch(`${API_URL}/api/v1/politicians/${slug}/campaign/expenses`).then(r => r.ok ? r.json() : null),
    ]).then(([rev, exp]) => { setRevenues(rev); setExpenses(exp); })
      .finally(() => setLoading(false));
  }, [slug]);

  if (loading) return <div className="bg-white rounded-lg border border-ifb-gray-medium p-6 animate-pulse"><div className="h-4 bg-gray-200 rounded w-1/3 mb-4" /></div>;

  const revItems = revenues?.data || [];
  const expItems = expenses?.data || [];
  const totalRev = revItems.reduce((s: number, r: any) => s + (r.amount || 0), 0);
  const totalExp = expItems.reduce((s: number, e: any) => s + (e.amount || 0), 0);

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg border border-ifb-gray-medium p-4 text-center">
          <p className="text-lg font-bold text-ifb-green">{formatCurrency(totalRev)}</p>
          <p className="text-xs text-gray-500">Total de receitas</p>
        </div>
        <div className="bg-white rounded-lg border border-ifb-gray-medium p-4 text-center">
          <p className="text-lg font-bold text-ifb-red">{formatCurrency(totalExp)}</p>
          <p className="text-xs text-gray-500">Total de despesas</p>
        </div>
        <div className="bg-white rounded-lg border border-ifb-gray-medium p-4 text-center">
          <p className={`text-lg font-bold ${totalRev - totalExp >= 0 ? 'text-ifb-black' : 'text-ifb-red'}`}>
            {formatCurrency(totalRev - totalExp)}
          </p>
          <p className="text-xs text-gray-500">Saldo</p>
        </div>
      </div>

      {/* Revenues */}
      <div className="bg-white rounded-lg border border-ifb-gray-medium p-6">
        <h3 className="text-lg font-semibold text-ifb-black mb-4">Receitas de Campanha</h3>
        {revItems.length === 0 ? (
          <p className="text-sm text-gray-500">Nenhuma receita importada para esta eleição.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b border-ifb-gray-medium text-left">
                <th className="py-2 px-2 text-xs font-semibold text-gray-600">Origem</th>
                <th className="py-2 px-2 text-xs font-semibold text-gray-600">Tipo</th>
                <th className="py-2 px-2 text-xs font-semibold text-gray-600 text-right">Valor</th>
              </tr></thead>
              <tbody>
                {revItems.map((r: any, i: number) => (
                  <tr key={i} className="border-b border-ifb-gray-light">
                    <td className="py-2 px-2 text-gray-700">{r.donor_name || '—'}</td>
                    <td className="py-2 px-2 text-gray-600">{r.revenue_type || '—'}</td>
                    <td className="py-2 px-2 text-right font-medium">{formatCurrency(r.amount)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Expenses */}
      <div className="bg-white rounded-lg border border-ifb-gray-medium p-6">
        <h3 className="text-lg font-semibold text-ifb-black mb-4">Despesas de Campanha</h3>
        {expItems.length === 0 ? (
          <p className="text-sm text-gray-500">Nenhuma despesa importada para esta eleição.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b border-ifb-gray-medium text-left">
                <th className="py-2 px-2 text-xs font-semibold text-gray-600">Categoria</th>
                <th className="py-2 px-2 text-xs font-semibold text-gray-600 hidden sm:table-cell">Fornecedor</th>
                <th className="py-2 px-2 text-xs font-semibold text-gray-600 text-right">Valor</th>
              </tr></thead>
              <tbody>
                {expItems.map((e: any, i: number) => (
                  <tr key={i} className="border-b border-ifb-gray-light">
                    <td className="py-2 px-2 text-gray-700">{e.expense_type || '—'}</td>
                    <td className="py-2 px-2 text-gray-600 hidden sm:table-cell">{e.supplier_name || '—'}</td>
                    <td className="py-2 px-2 text-right font-medium">{formatCurrency(e.amount)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Disclaimer */}
      <div className="bg-ifb-yellow/10 border border-ifb-yellow/30 rounded-lg p-4">
        <p className="text-xs text-gray-700">
          Os valores apresentados correspondem à prestação de contas eleitoral disponibilizada pelo TSE para a eleição selecionada.
          A ausência de registros não significa ausência de movimentação financeira.
        </p>
      </div>
      <p className="text-xs text-gray-400">Fonte: Tribunal Superior Eleitoral — Dados Abertos</p>
    </div>
  );
}

function ExpensesTab({ slug }: { slug: string }) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [year, setYear] = useState<string>("2026");
  const [month, setMonth] = useState<string>("");
  const [category, setCategory] = useState<string>("");
  const [page, setPage] = useState(1);

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (year) params.set("year", year);
    if (month) params.set("month", month);
    if (category) params.set("category", category);
    params.set("page", String(page));
    params.set("limit", "25");

    fetch(`${API_URL}/api/v1/politicians/${slug}/parliamentary-expenses?${params}`)
      .then((r) => { if (!r.ok) throw new Error(`${r.status}`); return r.json(); })
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [slug, year, month, category, page]);

  const items = data?.data || [];
  const totalNet = data?.aggregates?.total_net_amount || 0;

  // Compute stats from current page items
  const categories = items.reduce((acc: Record<string, number>, e: any) => {
    const cat = e.category || "Outros";
    acc[cat] = (acc[cat] || 0) + (e.net_amount || 0);
    return acc;
  }, {} as Record<string, number>);

  const topCategories = Object.entries(categories)
    .sort(([,a], [,b]) => (b as number) - (a as number))
    .slice(0, 5);

  function clearFilters() { setYear("2026"); setMonth(""); setCategory(""); setPage(1); }

  const months = ["","01","02","03","04","05","06","07","08","09","10","11","12"];

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-white rounded-lg border border-ifb-gray-medium p-4">
        <div className="flex flex-wrap gap-3 items-end">
          <div>
            <label className="text-xs text-gray-500 block mb-1">Ano</label>
            <select value={year} onChange={e => { setYear(e.target.value); setPage(1); }}
              className="px-3 py-2 border border-ifb-gray-medium rounded text-sm">
              <option value="2026">2026</option>
              <option value="2025">2025</option>
              <option value="2024">2024</option>
              <option value="2023">2023</option>
              <option value="">Todos</option>
            </select>
          </div>
          <div>
            <label className="text-xs text-gray-500 block mb-1">Mês</label>
            <select value={month} onChange={e => { setMonth(e.target.value); setPage(1); }}
              className="px-3 py-2 border border-ifb-gray-medium rounded text-sm">
              <option value="">Todos</option>
              {months.slice(1).map(m => <option key={m} value={m}>{ ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"][parseInt(m)-1] }</option>)}
            </select>
          </div>
          <div className="flex-1 min-w-[150px]">
            <label className="text-xs text-gray-500 block mb-1">Categoria</label>
            <input type="text" value={category} onChange={e => { setCategory(e.target.value); setPage(1); }}
              placeholder="Filtrar por categoria..."
              className="w-full px-3 py-2 border border-ifb-gray-medium rounded text-sm" />
          </div>
          <button onClick={clearFilters} className="px-3 py-2 text-xs text-gray-500 hover:text-ifb-black underline">
            Limpar
          </button>
        </div>
      </div>

      {/* Summary */}
      {!loading && !error && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="bg-white rounded-lg border border-ifb-gray-medium p-4 text-center">
            <p className="text-lg font-bold text-ifb-black">{formatCurrency(totalNet)}</p>
            <p className="text-xs text-gray-500">Total líquido{year ? ` (${year})` : ""}</p>
          </div>
          <div className="bg-white rounded-lg border border-ifb-gray-medium p-4 text-center">
            <p className="text-lg font-bold text-ifb-black">{items.length}</p>
            <p className="text-xs text-gray-500">Despesas na página</p>
          </div>
          {topCategories.length > 0 && (
            <div className="bg-white rounded-lg border border-ifb-gray-medium p-4 text-center col-span-2">
              <p className="text-xs text-gray-500 mb-1">Principal categoria</p>
              <p className="text-sm font-medium text-ifb-black truncate">{topCategories[0][0]}</p>
              <p className="text-xs text-gray-400">{formatCurrency(topCategories[0][1] as number)}</p>
            </div>
          )}
        </div>
      )}

      {/* Table */}
      <div className="bg-white rounded-lg border border-ifb-gray-medium p-4">
        <h2 className="text-lg font-semibold text-ifb-black mb-4">Gastos Parlamentares</h2>

        {loading && <div className="animate-pulse space-y-2">{[1,2,3,4,5].map(i => <div key={i} className="h-8 bg-gray-100 rounded"/>)}</div>}

        {error && <p className="text-red-600 text-sm">Erro ao carregar: {error}</p>}

        {!loading && !error && items.length === 0 && (
          <p className="text-gray-500 text-sm py-4 text-center">
            Não há despesas importadas para os filtros selecionados.
          </p>
        )}

        {!loading && !error && items.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b border-ifb-gray-medium text-left">
                <th className="py-2 px-2 text-xs font-semibold text-gray-600">Mês</th>
                <th className="py-2 px-2 text-xs font-semibold text-gray-600">Categoria</th>
                <th className="py-2 px-2 text-xs font-semibold text-gray-600 hidden sm:table-cell">Fornecedor</th>
                <th className="py-2 px-2 text-xs font-semibold text-gray-600 text-right">Valor líquido</th>
                <th className="py-2 px-2 text-xs font-semibold text-gray-600 text-right hidden md:table-cell">Bruto</th>
                <th className="py-2 px-2 text-xs font-semibold text-gray-600 hidden lg:table-cell">Doc</th>
              </tr></thead>
              <tbody>
                {items.map((e: any, i: number) => (
                  <tr key={i} className="border-b border-ifb-gray-light hover:bg-ifb-gray-light/50">
                    <td className="py-2 px-2 text-gray-700">{e.month}/{e.year}</td>
                    <td className="py-2 px-2 text-gray-700 max-w-[200px] truncate">{e.category}</td>
                    <td className="py-2 px-2 text-gray-600 max-w-[150px] truncate hidden sm:table-cell">{e.supplier_name || "—"}</td>
                    <td className="py-2 px-2 text-right font-medium text-ifb-black">{formatCurrency(e.net_amount)}</td>
                    <td className="py-2 px-2 text-right text-gray-500 hidden md:table-cell">{formatCurrency(e.gross_amount)}</td>
                    <td className="py-2 px-2 hidden lg:table-cell">
                      {e.document_url ? <a href={e.document_url} target="_blank" rel="noopener" className="text-blue-600 text-xs hover:underline">Ver</a> : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {!loading && items.length > 0 && (
          <div className="flex justify-between items-center mt-4 pt-3 border-t border-ifb-gray-light">
            <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page <= 1}
              className="px-3 py-1.5 text-xs border border-ifb-gray-medium rounded disabled:opacity-30">
              Anterior
            </button>
            <span className="text-xs text-gray-500">Página {page}</span>
            <button onClick={() => setPage(page + 1)} disabled={items.length < 25}
              className="px-3 py-1.5 text-xs border border-ifb-gray-medium rounded disabled:opacity-30">
              Próxima
            </button>
          </div>
        )}

        {/* Source */}
        <p className="text-xs text-gray-400 mt-4 pt-3 border-t border-ifb-gray-light">
          Fonte: Câmara dos Deputados — Dados Abertos (CEAP) · Valores em reais (R$) · Valor líquido = valor reembolsado ao parlamentar
        </p>
      </div>

      {/* Category distribution */}
      {topCategories.length > 1 && (
        <div className="bg-white rounded-lg border border-ifb-gray-medium p-4">
          <h3 className="text-sm font-semibold text-ifb-black mb-3">Distribuição por categoria (página atual)</h3>
          <div className="space-y-2">
            {topCategories.map(([cat, val]) => {
              const pct = totalNet > 0 ? ((val as number) / totalNet * 100) : 0;
              return (
                <div key={cat}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-gray-700 truncate max-w-[70%]">{cat}</span>
                    <span className="text-gray-500">{formatCurrency(val as number)}</span>
                  </div>
                  <div className="h-2 bg-ifb-gray-light rounded-full overflow-hidden">
                    <div className="h-full bg-ifb-yellow rounded-full" style={{ width: `${Math.min(pct, 100)}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <main className="min-h-screen bg-ifb-gray-light">
      <div className="bg-white border-b border-ifb-gray-medium">
        <div className="max-w-7xl mx-auto px-4 py-6 animate-pulse">
          <div className="flex gap-5"><div className="w-20 h-20 bg-gray-200 rounded-full" /><div className="flex-1 space-y-3"><div className="h-6 bg-gray-200 rounded w-1/3" /><div className="h-4 bg-gray-200 rounded w-1/4" /></div></div>
        </div>
      </div>
    </main>
  );
}

function ErrorState({ error }: { error: string | null }) {
  return (
    <main className="min-h-screen bg-ifb-gray-light flex items-center justify-center">
      <div className="text-center">
        <p className="text-red-600 font-medium">{error === "404" ? "Político não encontrado." : `Erro: ${error}`}</p>
        <Link href="/politicos" className="mt-4 inline-block text-sm text-ifb-black underline">Voltar para lista</Link>
      </div>
    </main>
  );
}
