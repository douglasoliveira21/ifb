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

type TabId = "overview" | "propositions" | "votes" | "expenses" | "committees" | "patrimonio" | "electoral" | "news" | "promises" | "judicial";

const TABS: { id: TabId; label: string }[] = [
  { id: "overview", label: "Visão Geral" },
  { id: "propositions", label: "Projetos" },
  { id: "votes", label: "Votações" },
  { id: "expenses", label: "Gastos" },
  { id: "committees", label: "Comissões" },
  { id: "patrimonio", label: "Patrimônio" },
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
  const [patrimonio, setPatrimonio] = useState<number | null>(null);

  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    fetch(`${API_URL}/api/v1/politicians/${slug}`)
      .then((r) => { if (!r.ok) throw new Error(`${r.status}`); return r.json(); })
      .then(setPolitician)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));

    // Fetch patrimônio declarado
    fetch(`${API_URL}/api/v1/politicians/${slug}/assets`)
      .then((r) => r.ok ? r.json() : null)
      .then((d) => {
        if (d?.data?.length) {
          const total = d.data.reduce((s: number, i: any) => s + (i.declared_value || 0), 0);
          setPatrimonio(total);
        }
      })
      .catch(() => {});
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
                {patrimonio !== null && patrimonio > 0 && (
                  <span className="px-3 py-1 text-[11px] font-bold bg-ifb-gray-800 text-ifb-yellow border border-ifb-yellow/40">
                    Patrimônio: {new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 }).format(patrimonio)}
                  </span>
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
        {activeTab === "propositions" && <PropositionsTab slug={slug} />}
        {activeTab === "votes" && <VotesTab slug={slug} />}
        {activeTab === "expenses" && <ExpensesTab slug={slug} />}
        {activeTab === "committees" && <CommitteesTab slug={slug} />}
        {activeTab === "patrimonio" && <PatrimonioTab slug={slug} />}
        {activeTab === "electoral" && <DataTab slug={slug} endpoint="candidacies" title="Histórico Eleitoral" />}
        {activeTab === "news" && <DataTab slug={slug} endpoint="news" title="Notícias" />}
        {activeTab === "promises" && <PromisesTab slug={slug} />}
        {activeTab === "judicial" && <JudicialTab slug={slug} />}
      </div>
    </main>
  );
}

/* ===== OVERVIEW ===== */
function OverviewTab({ politician }: { politician: PoliticianDetail }) {
  const email = politician.social_links.find(s => s.platform === "email");
  const phone = politician.social_links.find(s => s.platform === "phone");
  const nomeCivil = politician.social_links.find(s => s.platform === "nome_civil");
  const otherLinks = politician.social_links.filter(s => !["email", "phone", "nome_civil"].includes(s.platform));

  // Biografia: se começa com "Nome civil:" é o fallback antigo, mostrar como indisponível
  const biographyText = politician.biography && !politician.biography.startsWith("Nome civil:")
    ? politician.biography
    : null;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <div className="lg:col-span-2 space-y-5">
        {/* Biografia */}
        <section className="border border-ifb-gray-800 bg-ifb-black-soft p-6">
          <h2 className="text-[14px] font-bold uppercase tracking-wide text-ifb-yellow mb-3">Biografia</h2>
          <p className="text-[13px] text-ifb-gray-300 leading-relaxed">
            {biographyText || "Biografia ainda não disponível para este político. Os dados pessoais estão na seção ao lado."}
          </p>
        </section>

        {/* Contato */}
        {(email || phone) && (
          <section className="border border-ifb-gray-800 bg-ifb-black-soft p-6">
            <h2 className="text-[14px] font-bold uppercase tracking-wide text-ifb-yellow mb-3">Contato</h2>
            <div className="space-y-2">
              {email && (
                <div className="flex items-center gap-3">
                  <svg className="w-4 h-4 text-ifb-gray-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
                  <a href={email.url} className="text-[13px] text-ifb-gray-200 hover:text-ifb-yellow transition">{email.username || email.url.replace("mailto:", "")}</a>
                </div>
              )}
              {phone && (
                <div className="flex items-center gap-3">
                  <svg className="w-4 h-4 text-ifb-gray-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg>
                  <a href={phone.url} className="text-[13px] text-ifb-gray-200 hover:text-ifb-yellow transition">{phone.username || phone.url.replace("tel:", "")}</a>
                </div>
              )}
            </div>
          </section>
        )}

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

        {/* Redes Sociais */}
        {otherLinks.length > 0 && (
          <section className="border border-ifb-gray-800 bg-ifb-black-soft p-6">
            <h2 className="text-[14px] font-bold uppercase tracking-wide text-ifb-yellow mb-3">Redes Sociais</h2>
            <div className="flex flex-wrap gap-3">
              {otherLinks.map((s, i) => (
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
          <h3 className="text-[12px] font-bold uppercase tracking-wider text-ifb-gray-400 mb-4">Dados Pessoais</h3>
          <dl className="space-y-3">
            {nomeCivil && <InfoRow label="Nome Civil" value={nomeCivil.username} />}
            <InfoRow label="Cargo" value={politician.current_position_name} />
            <InfoRow label="Partido" value={politician.current_party ? `${politician.current_party.name} (${politician.current_party.acronym})` : null} />
            <InfoRow label="Estado" value={politician.state_code} />
            <InfoRow label="Município" value={politician.city_name} />
            <InfoRow label="Nascimento" value={politician.birth_date ? new Date(politician.birth_date + "T00:00:00").toLocaleDateString("pt-BR") : null} />
            {politician.website_url && (
              <div>
                <dt className="text-[11px] text-ifb-gray-500 uppercase">Site</dt>
                <dd><a href={politician.website_url} target="_blank" rel="noopener noreferrer" className="text-[12px] text-ifb-yellow hover:underline break-all">{politician.website_url}</a></dd>
              </div>
            )}
            {email && <InfoRow label="E-mail" value={email.username || email.url.replace("mailto:", "")} />}
            {phone && <InfoRow label="Telefone" value={phone.username || phone.url.replace("tel:", "")} />}
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

/* ===== PATRIMÔNIO TAB ===== */
function PatrimonioTab({ slug }: { slug: string }) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    fetch(`${API_URL}/api/v1/politicians/${slug}/assets`)
      .then((r) => { if (!r.ok) throw new Error(`${r.status}`); return r.json(); })
      .then(setData).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, [slug]);

  if (loading) return <TabSkeleton title="Declaração de Bens" />;
  if (error) return <TabError title="Declaração de Bens" error={error} />;

  const items = data?.data || [];
  const totalValue = items.reduce((sum: number, item: any) => sum + (item.declared_value || 0), 0);

  return (
    <div className="border border-ifb-gray-800 bg-ifb-black-soft p-6">
      <h2 className="text-[14px] font-bold uppercase tracking-wide text-ifb-yellow mb-2">Declaração de Bens</h2>
      <div className="mb-4 p-3 border border-ifb-yellow/30 bg-ifb-yellow/5">
        <p className="text-[11px] text-ifb-gray-300">Valores declarados à Justiça Eleitoral na última eleição em que concorreu. Não representam necessariamente o patrimônio atual.</p>
      </div>

      {items.length === 0 ? <EmptyMsg msg="Nenhuma declaração de bens importada do TSE para este político." /> : (
        <>
          {/* Total */}
          <div className="mb-5">
            <p className="text-[28px] font-bold text-ifb-yellow">{formatCurrency(totalValue)}</p>
            <p className="text-[10px] text-ifb-gray-500 uppercase">Patrimônio total declarado</p>
          </div>

          {/* Items */}
          <div className="overflow-x-auto">
            <table className="w-full text-[12px]">
              <thead><tr className="border-b border-ifb-gray-700">
                <th className="text-left py-2 px-3 text-[10px] font-bold text-ifb-gray-500 uppercase">Ano</th>
                <th className="text-left py-2 px-3 text-[10px] font-bold text-ifb-gray-500 uppercase">Categoria</th>
                <th className="text-left py-2 px-3 text-[10px] font-bold text-ifb-gray-500 uppercase">Descrição</th>
                <th className="text-right py-2 px-3 text-[10px] font-bold text-ifb-gray-500 uppercase">Valor</th>
              </tr></thead>
              <tbody>
                {items.map((item: any, i: number) => (
                  <tr key={i} className="border-b border-ifb-gray-800 hover:bg-ifb-yellow/5 transition">
                    <td className="py-2.5 px-3 text-ifb-gray-400">{item.election_year || "—"}</td>
                    <td className="py-2.5 px-3 text-ifb-gray-300">{item.category || "—"}</td>
                    <td className="py-2.5 px-3 text-ifb-gray-400">{(item.description || "—").slice(0, 50)}</td>
                    <td className="py-2.5 px-3 text-right font-medium text-ifb-yellow">{formatCurrency(item.declared_value)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

/* ===== PROPOSITIONS TAB ===== */
function PropositionsTab({ slug }: { slug: string }) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [yearFilter, setYearFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("");

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (yearFilter) params.set("year", yearFilter);
    if (typeFilter) params.set("type", typeFilter);
    params.set("limit", "100");
    fetch(`${API_URL}/api/v1/politicians/${slug}/propositions?${params}`)
      .then((r) => { if (!r.ok) throw new Error(`${r.status}`); return r.json(); })
      .then(setData).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, [slug, yearFilter, typeFilter]);

  if (loading) return <TabSkeleton title="Projetos de Lei" />;
  if (error) return <TabError title="Projetos de Lei" error={error} />;

  const items = data?.data || [];
  const filtered = items.filter((p: any) => {
    if (!search) return true;
    const text = `${p.title || ""} ${p.summary || ""} ${p.type_acronym || ""} ${p.number || ""}`.toLowerCase();
    return text.includes(search.toLowerCase());
  });

  // Types count
  const types: Record<string, number> = {};
  items.forEach((p: any) => { const t = p.type || p.type_acronym || "Outro"; types[t] = (types[t] || 0) + 1; });

  return (
    <div className="border border-ifb-gray-800 bg-ifb-black-soft p-6">
      <h2 className="text-[14px] font-bold uppercase tracking-wide text-ifb-yellow mb-4">Projetos de Lei</h2>

      {items.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {Object.entries(types).sort((a, b) => b[1] - a[1]).slice(0, 8).map(([t, count]) => (
            <button key={t} onClick={() => setTypeFilter(typeFilter === t ? "" : t)} className={`px-3 py-1 text-[11px] font-medium border transition ${typeFilter === t ? "border-ifb-yellow bg-ifb-yellow/10 text-ifb-yellow" : "border-ifb-gray-700 text-ifb-gray-400 hover:border-ifb-gray-500"}`}>
              {t} ({count})
            </button>
          ))}
        </div>
      )}

      <div className="flex flex-wrap gap-3 mb-4">
        <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Buscar por ementa..." className="flex-1 min-w-[200px] h-[38px] px-3 bg-ifb-black border border-ifb-gray-700 text-[12px] text-ifb-white placeholder:text-ifb-gray-600 outline-none focus:border-ifb-yellow transition" />
        <select value={yearFilter} onChange={(e) => setYearFilter(e.target.value)} className="h-[38px] px-3 bg-ifb-black border border-ifb-gray-700 text-[12px] text-ifb-gray-300 outline-none focus:border-ifb-yellow">
          <option value="">Todos os anos</option>
          {[2026,2025,2024,2023].map(y => <option key={y} value={String(y)}>{y}</option>)}
        </select>
        {(search || yearFilter || typeFilter) && <button onClick={() => { setSearch(""); setYearFilter(""); setTypeFilter(""); }} className="h-[38px] px-3 text-[11px] text-ifb-gray-400 hover:text-ifb-yellow">Limpar</button>}
      </div>

      <p className="text-[11px] text-ifb-gray-500 mb-3">{filtered.length} projeto(s)</p>

      {filtered.length === 0 ? <EmptyMsg msg="Nenhum projeto encontrado." /> : (
        <div className="space-y-2">
          {filtered.slice(0, 50).map((p: any, i: number) => (
            <div key={i} className="border-b border-ifb-gray-800 pb-3 last:border-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="px-2 py-0.5 text-[10px] font-bold bg-ifb-yellow text-ifb-black">{p.type || p.type_acronym || "—"}</span>
                {p.number && <span className="text-[11px] text-ifb-gray-400">Nº {p.number}/{p.year || ""}</span>}
                {p.presentation_date && <span className="text-[10px] text-ifb-gray-500">{new Date(p.presentation_date).toLocaleDateString("pt-BR")}</span>}
              </div>
              <p className="text-[13px] text-ifb-gray-200 leading-snug">{p.title || p.summary || "Sem ementa disponível"}</p>
              {p.status && <p className="text-[11px] text-ifb-gray-500 mt-1">Status: {p.status}</p>}
            </div>
          ))}
          {filtered.length > 50 && <p className="text-[11px] text-ifb-gray-600 text-center mt-2">Mostrando 50 de {filtered.length}</p>}
        </div>
      )}
    </div>
  );
}

/* ===== EXPENSES TAB ===== */
function ExpensesTab({ slug }: { slug: string }) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [yearFilter, setYearFilter] = useState("2026");
  const [search, setSearch] = useState("");

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (yearFilter) params.set("year", yearFilter);
    params.set("limit", "200");
    fetch(`${API_URL}/api/v1/politicians/${slug}/parliamentary-expenses?${params}`)
      .then((r) => { if (!r.ok) throw new Error(`${r.status}`); return r.json(); })
      .then(setData).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, [slug, yearFilter]);

  if (loading) return <TabSkeleton title="Gastos Parlamentares" />;
  if (error) return <TabError title="Gastos Parlamentares" error={error} />;

  const items = data?.data || [];
  const totalNet = data?.aggregates?.total_net_amount || 0;
  const filtered = items.filter((e: any) => {
    if (!search) return true;
    return `${e.category || ""} ${e.supplier_name || ""}`.toLowerCase().includes(search.toLowerCase());
  });

  // Category totals for chart
  const categories: Record<string, number> = {};
  items.forEach((e: any) => { const c = (e.category || "Outros").slice(0, 30); categories[c] = (categories[c] || 0) + (e.net_amount || 0); });
  const topCats = Object.entries(categories).sort((a, b) => b[1] - a[1]).slice(0, 6);

  // Monthly totals for chart
  const monthly: Record<string, number> = {};
  items.forEach((e: any) => {
    const key = `${e.month || 0}`.padStart(2, "0");
    monthly[key] = (monthly[key] || 0) + (e.net_amount || 0);
  });
  const monthlyData = Object.entries(monthly).sort((a, b) => a[0].localeCompare(b[0])).map(([m, v]) => ({
    month: ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"][parseInt(m) - 1] || m,
    valor: v,
  }));

  return (
    <div className="border border-ifb-gray-800 bg-ifb-black-soft p-6">
      <h2 className="text-[14px] font-bold uppercase tracking-wide text-ifb-yellow mb-4">Gastos Parlamentares</h2>

      {/* Summary */}
      <div className="flex items-center gap-6 mb-5">
        <div>
          <p className="text-[24px] font-bold text-ifb-yellow">{formatCurrency(totalNet)}</p>
          <p className="text-[10px] text-ifb-gray-500 uppercase">Total líquido {yearFilter || ""}</p>
        </div>
        <div>
          <p className="text-[18px] font-bold text-ifb-white">{items.length}</p>
          <p className="text-[10px] text-ifb-gray-500 uppercase">Despesas</p>
        </div>
      </div>

      {/* Charts */}
      {items.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
          {/* Monthly bar chart */}
          {monthlyData.length > 1 && (
            <div className="border border-ifb-gray-700 p-4">
              <h3 className="text-[11px] font-bold uppercase text-ifb-gray-400 mb-3">Gastos por Mês</h3>
              <div className="flex items-end gap-1 h-[120px]">
                {monthlyData.map((d, i) => {
                  const maxVal = Math.max(...monthlyData.map(x => x.valor));
                  const height = maxVal > 0 ? (d.valor / maxVal) * 100 : 0;
                  return (
                    <div key={i} className="flex-1 flex flex-col items-center gap-1">
                      <div className="w-full bg-ifb-yellow/80 hover:bg-ifb-yellow transition relative group" style={{ height: `${Math.max(height, 4)}%` }}>
                        <div className="absolute -top-6 left-1/2 -translate-x-1/2 text-[9px] text-ifb-gray-400 opacity-0 group-hover:opacity-100 whitespace-nowrap transition">
                          {formatCurrency(d.valor)}
                        </div>
                      </div>
                      <span className="text-[9px] text-ifb-gray-500">{d.month}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Category breakdown */}
          <div className="border border-ifb-gray-700 p-4">
            <h3 className="text-[11px] font-bold uppercase text-ifb-gray-400 mb-3">Top Categorias</h3>
            <div className="space-y-2">
              {topCats.map(([cat, total], i) => {
                const maxCat = topCats[0][1];
                const pct = maxCat > 0 ? (total / maxCat) * 100 : 0;
                return (
                  <div key={i}>
                    <div className="flex justify-between text-[11px] mb-0.5">
                      <span className="text-ifb-gray-300 truncate max-w-[200px]">{cat}</span>
                      <span className="text-ifb-yellow font-medium">{formatCurrency(total)}</span>
                    </div>
                    <div className="h-[6px] bg-ifb-gray-800 w-full">
                      <div className="h-full bg-ifb-yellow transition-all" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-4">
        <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Buscar por categoria ou fornecedor..." className="flex-1 min-w-[200px] h-[38px] px-3 bg-ifb-black border border-ifb-gray-700 text-[12px] text-ifb-white placeholder:text-ifb-gray-600 outline-none focus:border-ifb-yellow transition" />
        <select value={yearFilter} onChange={(e) => setYearFilter(e.target.value)} className="h-[38px] px-3 bg-ifb-black border border-ifb-gray-700 text-[12px] text-ifb-gray-300 outline-none focus:border-ifb-yellow">
          <option value="">Todos</option>
          {[2026,2025,2024,2023].map(y => <option key={y} value={String(y)}>{y}</option>)}
        </select>
      </div>

      {filtered.length === 0 ? <EmptyMsg msg="Nenhuma despesa encontrada para os filtros selecionados." /> : (
        <div className="overflow-x-auto">
          <table className="w-full text-[12px]">
            <thead><tr className="border-b border-ifb-gray-700">
              <th className="text-left py-2 px-3 text-[10px] font-bold text-ifb-gray-500 uppercase">Mês</th>
              <th className="text-left py-2 px-3 text-[10px] font-bold text-ifb-gray-500 uppercase">Categoria</th>
              <th className="text-left py-2 px-3 text-[10px] font-bold text-ifb-gray-500 uppercase hidden sm:table-cell">Fornecedor</th>
              <th className="text-right py-2 px-3 text-[10px] font-bold text-ifb-gray-500 uppercase">Valor</th>
            </tr></thead>
            <tbody>
              {filtered.slice(0, 50).map((e: any, i: number) => (
                <tr key={i} className="border-b border-ifb-gray-800 hover:bg-ifb-yellow/5 transition">
                  <td className="py-2.5 px-3 text-ifb-gray-400">{e.month || "—"}/{e.year || ""}</td>
                  <td className="py-2.5 px-3 text-ifb-gray-300">{(e.category || "—").slice(0, 35)}</td>
                  <td className="py-2.5 px-3 text-ifb-gray-400 hidden sm:table-cell">{(e.supplier_name || "—").slice(0, 25)}</td>
                  <td className="py-2.5 px-3 text-right font-medium text-ifb-yellow">{formatCurrency(e.net_amount || e.gross_amount)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {filtered.length > 50 && <p className="text-[11px] text-ifb-gray-600 text-center mt-2">Mostrando 50 de {filtered.length}</p>}
        </div>
      )}
    </div>
  );
}

/* ===== COMMITTEES TAB ===== */
function CommitteesTab({ slug }: { slug: string }) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    setLoading(true);
    fetch(`${API_URL}/api/v1/politicians/${slug}/committees`)
      .then((r) => { if (!r.ok) throw new Error(`${r.status}`); return r.json(); })
      .then(setData).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, [slug]);

  if (loading) return <TabSkeleton title="Comissões" />;
  if (error) return <TabError title="Comissões" error={error} />;

  const items = data?.data || [];
  const filtered = items.filter((c: any) => {
    if (!search) return true;
    return `${c.committee_name || ""} ${c.acronym || ""} ${c.role || ""}`.toLowerCase().includes(search.toLowerCase());
  });

  // Roles count
  const roles: Record<string, number> = {};
  items.forEach((c: any) => { const r = c.role || "Membro"; roles[r] = (roles[r] || 0) + 1; });

  return (
    <div className="border border-ifb-gray-800 bg-ifb-black-soft p-6">
      <h2 className="text-[14px] font-bold uppercase tracking-wide text-ifb-yellow mb-4">Comissões</h2>

      {items.length > 0 && (
        <div className="flex items-center gap-4 mb-4">
          <div><p className="text-[20px] font-bold text-ifb-yellow">{items.length}</p><p className="text-[10px] text-ifb-gray-500 uppercase">Total</p></div>
          {Object.entries(roles).map(([role, count]) => (
            <div key={role}><p className="text-[16px] font-bold text-ifb-gray-300">{count}</p><p className="text-[10px] text-ifb-gray-500 uppercase">{role}</p></div>
          ))}
        </div>
      )}

      <div className="mb-4">
        <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Buscar comissão..." className="w-full max-w-[400px] h-[38px] px-3 bg-ifb-black border border-ifb-gray-700 text-[12px] text-ifb-white placeholder:text-ifb-gray-600 outline-none focus:border-ifb-yellow transition" />
      </div>

      {filtered.length === 0 ? <EmptyMsg msg="Nenhuma comissão encontrada." /> : (
        <div className="space-y-2">
          {filtered.map((c: any, i: number) => (
            <div key={i} className="flex items-center justify-between py-3 border-b border-ifb-gray-800 last:border-0">
              <div>
                <p className="text-[13px] text-ifb-gray-200 font-medium">{c.committee_name || "—"}</p>
                {c.acronym && <p className="text-[11px] text-ifb-gray-500">{c.acronym}</p>}
              </div>
              <span className="px-3 py-1 text-[10px] font-bold bg-ifb-gray-800 text-ifb-gray-300 border border-ifb-gray-700">{c.role || "Membro"}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ===== PROMISES TAB ===== */
function PromisesTab({ slug }: { slug: string }) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState("");
  const [search, setSearch] = useState("");

  useEffect(() => {
    setLoading(true);
    fetch(`${API_URL}/api/v1/politicians/${slug}/promises`)
      .then((r) => { if (!r.ok) throw new Error(`${r.status}`); return r.json(); })
      .then(setData).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, [slug]);

  if (loading) return <TabSkeleton title="Promessas de Campanha" />;
  if (error) return <TabError title="Promessas de Campanha" error={error} />;

  const items = data?.data || data?.items || [];
  const filtered = items.filter((p: any) => {
    if (statusFilter && p.status !== statusFilter) return false;
    if (search && !(p.title || "").toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const STATUS_LABELS: Record<string, string> = { fulfilled: "Cumprida", not_fulfilled: "Não cumprida", in_progress: "Em andamento", partially_fulfilled: "Parcialmente", unverifiable: "Não verificável" };
  const STATUS_COLORS: Record<string, string> = { fulfilled: "text-green-400", not_fulfilled: "text-red-400", in_progress: "text-ifb-yellow", partially_fulfilled: "text-orange-400", unverifiable: "text-ifb-gray-500" };

  // Count by status
  const statusCounts: Record<string, number> = {};
  items.forEach((p: any) => { const s = p.status || "unknown"; statusCounts[s] = (statusCounts[s] || 0) + 1; });

  return (
    <div className="border border-ifb-gray-800 bg-ifb-black-soft p-6">
      <h2 className="text-[14px] font-bold uppercase tracking-wide text-ifb-yellow mb-4">Promessas de Campanha</h2>

      {items.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-5">
          {Object.entries(statusCounts).map(([s, count]) => (
            <button key={s} onClick={() => setStatusFilter(statusFilter === s ? "" : s)} className={`px-3 py-1.5 text-[11px] font-medium border transition ${statusFilter === s ? "border-ifb-yellow bg-ifb-yellow/10 text-ifb-yellow" : "border-ifb-gray-700 text-ifb-gray-400 hover:border-ifb-gray-500"}`}>
              {STATUS_LABELS[s] || s} ({count})
            </button>
          ))}
        </div>
      )}

      <div className="flex flex-wrap gap-3 mb-4">
        <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Buscar promessa..." className="flex-1 min-w-[200px] h-[38px] px-3 bg-ifb-black border border-ifb-gray-700 text-[12px] text-ifb-white placeholder:text-ifb-gray-600 outline-none focus:border-ifb-yellow transition" />
        {(search || statusFilter) && <button onClick={() => { setSearch(""); setStatusFilter(""); }} className="h-[38px] px-3 text-[11px] text-ifb-gray-400 hover:text-ifb-yellow">Limpar</button>}
      </div>

      {filtered.length === 0 ? <EmptyMsg msg="Nenhuma promessa registrada ou encontrada com os filtros." /> : (
        <div className="space-y-3">
          {filtered.slice(0, 30).map((p: any, i: number) => (
            <div key={i} className="border-b border-ifb-gray-800 pb-3 last:border-0">
              <div className="flex items-center justify-between mb-1">
                <span className={`text-[12px] font-bold ${STATUS_COLORS[p.status] || "text-ifb-gray-400"}`}>{STATUS_LABELS[p.status] || p.status || "—"}</span>
                {p.progress_percentage != null && <span className="text-[11px] text-ifb-gray-400">{p.progress_percentage}%</span>}
              </div>
              <p className="text-[13px] text-ifb-gray-200 leading-snug">{p.title || "Sem título"}</p>
              {p.category && <p className="text-[11px] text-ifb-gray-500 mt-1">Categoria: {p.category}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ===== JUDICIAL TAB ===== */
function JudicialTab({ slug }: { slug: string }) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  useEffect(() => {
    setLoading(true);
    fetch(`${API_URL}/api/v1/politicians/${slug}/judicial-cases`)
      .then((r) => { if (!r.ok) throw new Error(`${r.status}`); return r.json(); })
      .then(setData).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, [slug]);

  if (loading) return <TabSkeleton title="Processos Judiciais" />;
  if (error) return <TabError title="Processos Judiciais" error={error} />;

  const items = data?.data || [];
  const filtered = items.filter((c: any) => {
    if (statusFilter && (c.normalized_status || c.procedural_status) !== statusFilter) return false;
    if (search && !`${c.tribunal || ""} ${c.case_class || ""} ${c.procedural_status || ""}`.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="border border-ifb-gray-800 bg-ifb-black-soft p-6">
      <h2 className="text-[14px] font-bold uppercase tracking-wide text-ifb-yellow mb-2">Processos Judiciais</h2>
      <div className="mb-4 p-3 border border-ifb-yellow/30 bg-ifb-yellow/5">
        <p className="text-[11px] text-ifb-gray-300">A existência de processo judicial não implica culpa. Investigação não é condenação. Processos podem estar em recurso ou ter sido arquivados.</p>
      </div>

      <div className="flex flex-wrap gap-3 mb-4">
        <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Buscar por tribunal, classe, status..." className="flex-1 min-w-[200px] h-[38px] px-3 bg-ifb-black border border-ifb-gray-700 text-[12px] text-ifb-white placeholder:text-ifb-gray-600 outline-none focus:border-ifb-yellow transition" />
        {(search || statusFilter) && <button onClick={() => { setSearch(""); setStatusFilter(""); }} className="h-[38px] px-3 text-[11px] text-ifb-gray-400 hover:text-ifb-yellow">Limpar</button>}
      </div>

      {filtered.length === 0 ? <EmptyMsg msg="Nenhum processo confirmado e publicado disponível." /> : (
        <div className="overflow-x-auto">
          <table className="w-full text-[12px]">
            <thead><tr className="border-b border-ifb-gray-700">
              <th className="text-left py-2 px-3 text-[10px] font-bold text-ifb-gray-500 uppercase">Tribunal</th>
              <th className="text-left py-2 px-3 text-[10px] font-bold text-ifb-gray-500 uppercase">Classe</th>
              <th className="text-left py-2 px-3 text-[10px] font-bold text-ifb-gray-500 uppercase">Papel</th>
              <th className="text-left py-2 px-3 text-[10px] font-bold text-ifb-gray-500 uppercase">Status</th>
            </tr></thead>
            <tbody>
              {filtered.slice(0, 30).map((c: any, i: number) => (
                <tr key={i} className="border-b border-ifb-gray-800 hover:bg-ifb-yellow/5 transition">
                  <td className="py-2.5 px-3 text-ifb-gray-300">{c.tribunal || "—"}</td>
                  <td className="py-2.5 px-3 text-ifb-gray-300">{c.case_class || "—"}</td>
                  <td className="py-2.5 px-3 text-ifb-gray-400">{c.politician_role || "—"}</td>
                  <td className="py-2.5 px-3 text-ifb-gray-400">{c.procedural_status || c.normalized_status || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

/* ===== SHARED TAB HELPERS ===== */
function TabSkeleton({ title }: { title: string }) {
  return (
    <div className="border border-ifb-gray-800 bg-ifb-black-soft p-6 animate-pulse">
      <div className="h-4 bg-ifb-gray-800 w-1/3 mb-4" />
      <div className="space-y-3">{[1,2,3,4].map(i => <div key={i} className="h-10 bg-ifb-gray-800" />)}</div>
    </div>
  );
}

function TabError({ title, error }: { title: string; error: string }) {
  return (
    <div className="border border-ifb-gray-800 bg-ifb-black-soft p-6">
      <h2 className="text-[14px] font-bold uppercase tracking-wide text-ifb-yellow mb-2">{title}</h2>
      <p className="text-[13px] text-red-400">Erro ao carregar dados ({error})</p>
    </div>
  );
}

function EmptyMsg({ msg }: { msg: string }) {
  return <div className="text-center py-8"><p className="text-[13px] text-ifb-gray-500">{msg}</p></div>;
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
