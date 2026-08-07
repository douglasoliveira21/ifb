"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface PlatformStats {
  politicians: number;
  propositions: number;
  votes: number;
  committees: number;
  expenses_total: number;
}

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

export default function HomePage() {
  const [stats, setStats] = useState<PlatformStats | null>(null);
  const [news, setNews] = useState<NewsItem[]>([]);

  useEffect(() => {
    fetch(`${API_URL}/api/v1/stats`).then(r => r.json()).then(setStats).catch(() => {});
    fetch(`${API_URL}/api/v1/news/latest?limit=3`).then(r => r.json()).then(d => setNews(d.items || [])).catch(() => {});
  }, []);

  return (
    <div className="min-h-screen bg-ifb-white">
      {/* ===== HEADER ===== */}
      <header className="bg-ifb-black sticky top-0 z-50">
        <div className="max-w-ifb mx-auto px-6 lg:px-10 h-[64px] flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-[32px] h-[32px] bg-ifb-yellow flex items-center justify-center skew-x-[-6deg]">
              <span className="text-ifb-black font-bold text-[12px] skew-x-[6deg]">IFB</span>
            </div>
          </Link>

          <nav className="hidden lg:flex items-center gap-6">
            {[
              { label: "Pesquisar Político", href: "/politicos" },
              { label: "Dados Abertos", href: "/transparencia" },
              { label: "Metodologia", href: "/metodologia" },
              { label: "Sobre Nós", href: "/sobre" },
            ].map((item) => (
              <Link key={item.href} href={item.href} className="text-[13px] font-medium text-ifb-white/80 hover:text-ifb-white transition uppercase tracking-wide">
                {item.label}
              </Link>
            ))}
          </nav>

          <Link href="/doar" className="btn-primary text-[12px] py-2 px-4 border-ifb-yellow">
            Faça uma Doação
          </Link>
        </div>

        {/* Search Bar */}
        <div className="border-t border-ifb-gray-800">
          <div className="max-w-ifb mx-auto px-6 lg:px-10 py-3">
            <form action="/politicos" className="flex items-center bg-ifb-white border-2 border-ifb-gray-300 max-w-[600px]">
              <svg className="w-5 h-5 text-ifb-gray-400 ml-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
              <input type="text" name="q" placeholder="Nome, partido, cargo ou UF..." className="flex-1 h-[44px] px-3 text-[14px] text-ifb-black outline-none bg-transparent" />
              <button type="submit" className="h-[44px] px-5 bg-ifb-yellow text-ifb-black font-bold text-[12px] uppercase tracking-wide hover:bg-ifb-yellow-hover transition border-l-2 border-ifb-gray-300">Buscar</button>
            </form>
          </div>
        </div>
      </header>

      {/* ===== HERO ===== */}
      <section className="bg-ifb-black relative overflow-hidden min-h-[520px]">
        <div className="max-w-ifb mx-auto px-6 lg:px-10 py-20 lg:py-28 relative z-10">
          <div className="max-w-[720px]">
            <h1 className="text-[36px] sm:text-[48px] lg:text-[60px] font-black uppercase leading-[1.02] tracking-tighter">
              <span className="text-ifb-white">POLÍTICA BRASILEIRA,</span><br />
              <span className="text-ifb-white">PELA LUPA DO </span><span className="text-ifb-yellow">DADO.</span><br />
              <span className="text-ifb-yellow">IFB</span><span className="text-ifb-white"> ORGANIZA,</span><br />
              <span className="text-ifb-white">VOCÊ </span><span className="text-ifb-yellow">CONCLUI.</span>
            </h1>
            <p className="mt-6 text-[15px] text-ifb-gray-400 leading-relaxed max-w-[500px]">
              Informação organizada, rastreável e contextualizada sobre políticos e candidatos brasileiros, sem te dizer em quem votar.
            </p>
            <Link href="/politicos" className="mt-10 inline-block bg-ifb-yellow text-ifb-black font-bold text-[13px] uppercase tracking-wide px-8 py-4 border-2 border-ifb-yellow hover:bg-ifb-yellow-hover transition-all">
              Conheça a Plataforma
            </Link>
          </div>
        </div>

        {/* Right geometric composition */}
        <div className="absolute top-0 right-0 w-[50%] h-full hidden lg:block pointer-events-none">
          {/* Large triangle */}
          <div className="absolute top-[8%] right-[8%] w-0 h-0 border-l-[120px] border-l-transparent border-b-[200px] border-b-ifb-yellow border-r-[120px] border-r-transparent opacity-90" />
          {/* Skewed block */}
          <div className="absolute top-[25%] right-[20%] w-[180px] h-[180px] bg-ifb-yellow/15 skew-x-[-12deg] skew-y-[4deg]" />
          {/* Angular frame */}
          <div className="absolute bottom-[12%] right-[10%] w-[140px] h-[140px] border-[3px] border-ifb-yellow skew-x-[8deg] skew-y-[-4deg]" />
          {/* Small arrow shape */}
          <div className="absolute top-[55%] right-[35%] w-0 h-0 border-l-[40px] border-l-transparent border-t-[70px] border-t-ifb-yellow/40 border-r-[40px] border-r-transparent" />
          {/* Diagonal line */}
          <div className="absolute top-[15%] right-[3%] w-[3px] h-[200px] bg-ifb-yellow/50 rotate-[25deg] origin-top" />
          {/* Congress image with clip mask */}
          <img src="/images/congresso-nacional.png" alt="" className="absolute bottom-0 right-0 h-[70%] w-[80%] object-cover opacity-15" style={{ clipPath: "polygon(30% 0, 100% 0, 100% 100%, 0 100%)" }} />
        </div>
      </section>

      {/* ===== MÓDULOS ===== */}
      <section className="max-w-ifb mx-auto px-6 lg:px-10 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-0">
          {/* Perfil do Político — destaque */}
          <Link href="/politicos" className="bg-ifb-yellow border-2 border-ifb-black p-6 group hover:shadow-ifb-black transition relative overflow-hidden">
            <div className="w-[44px] h-[44px] bg-ifb-black flex items-center justify-center mb-4 skew-x-[-4deg]">
              <svg className="w-5 h-5 text-ifb-yellow skew-x-[4deg]" fill="currentColor" viewBox="0 0 20 20"><path d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" /></svg>
            </div>
            <h3 className="text-[16px] font-black uppercase tracking-wide text-ifb-black mb-2">Perfil do Político</h3>
            <p className="text-[12px] text-ifb-black/70 leading-relaxed">Histórico, Candidaturas, Patrimônio, Projetos, Votações, Gastos, Notícias, Promessas... Tudo de fontes oficiais.</p>
            {/* Corner geometric cut */}
            <div className="absolute top-0 right-0 w-[48px] h-[48px] bg-ifb-black" style={{ clipPath: "polygon(100% 0, 0 0, 100% 100%)" }} />
            <div className="absolute bottom-0 left-0 w-[24px] h-[24px] bg-ifb-black/20" style={{ clipPath: "polygon(0 100%, 100% 100%, 0 0)" }} />
          </Link>

          {/* Notícias + IA */}
          <Link href="/noticias" className="bg-ifb-white border-2 border-ifb-black p-6 group hover:shadow-ifb transition">
            <div className="w-[44px] h-[44px] border-2 border-ifb-black flex items-center justify-center mb-4">
              <svg className="w-5 h-5 text-ifb-black" fill="currentColor" viewBox="0 0 20 20"><path d="M2 5a2 2 0 012-2h8a2 2 0 012 2v10a2 2 0 002 2H4a2 2 0 01-2-2V5zm3 1h6v4H5V6zm6 6H5v2h6v-2z" /><path d="M15 7h1a2 2 0 012 2v5.5a1.5 1.5 0 01-3 0V7z" /></svg>
            </div>
            <h3 className="text-[16px] font-black uppercase tracking-wide text-ifb-black mb-2">Notícias + IA</h3>
            <p className="text-[12px] text-ifb-gray-600 leading-relaxed">Coleta, classificação e análise de sentimento com Inteligência Artificial, sobreposta por rigorosa revisão humana editorial.</p>
          </Link>

          {/* Indicadores & Ranking */}
          <div className="bg-ifb-white border-2 border-ifb-black p-6 relative">
            <div className="w-[44px] h-[44px] border-2 border-ifb-black flex items-center justify-center mb-4">
              <svg className="w-5 h-5 text-ifb-black" fill="currentColor" viewBox="0 0 20 20"><path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zm6-4a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zm6-3a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" /></svg>
            </div>
            <h3 className="text-[16px] font-black uppercase tracking-wide text-ifb-black mb-2">Indicadores & Ranking</h3>
            <span className="tag-preparation">Em Preparação</span>
            <p className="text-[12px] text-ifb-gray-600 leading-relaxed mt-3">Metodologias transparentes e dados consolidados. Rankings sérios, quando houver base sólida.</p>
          </div>
        </div>
      </section>

      {/* ===== ÚLTIMAS ATUALIZAÇÕES ===== */}
      <section className="bg-ifb-gray-50 border-y-2 border-ifb-gray-200">
        <div className="max-w-ifb mx-auto px-6 lg:px-10 py-10">
          <h2 className="section-title mb-6">Últimas Atualizações</h2>

          {news.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {news.map((n) => (
                <Link key={n.id} href={`/noticias/${n.id}`} className="bg-ifb-white border-2 border-ifb-black p-5 hover:shadow-ifb transition group">
                  <p className="text-[13px] font-bold text-ifb-black leading-snug group-hover:text-ifb-yellow transition line-clamp-3">{n.title}</p>
                  <div className="mt-3 flex items-center justify-between">
                    <span className="text-[11px] text-ifb-gray-500 font-medium">{n.politician_name}</span>
                    {n.published_at && <span className="text-[10px] text-ifb-gray-400">{new Date(n.published_at).toLocaleDateString("pt-BR")}</span>}
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="border-2 border-ifb-black p-5 relative">
                  <div className="h-3 bg-ifb-gray-200 w-full mb-3" />
                  <div className="h-3 bg-ifb-gray-200 w-4/5 mb-3" />
                  <div className="h-3 bg-ifb-gray-200 w-3/5 mb-5" />
                  <div className="flex justify-between items-center">
                    <div className="h-2.5 bg-ifb-gray-200 w-24" />
                    <div className="h-2.5 bg-ifb-gray-200 w-16" />
                  </div>
                  {/* Yellow accent line */}
                  <div className="absolute bottom-0 left-0 w-full h-[3px] bg-ifb-yellow" />
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* ===== TRANSPARÊNCIA IFB ===== */}
      <section className="max-w-ifb mx-auto px-6 lg:px-10 py-12">
        <h2 className="section-title mb-6">Transparência IFB</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          {[
            { label: "Nossas Receitas e Despesas", icon: "📊" },
            { label: "Governança", icon: "🏛" },
            { label: "Tecnologia e Custos", icon: "🖥" },
            { label: "Contratos", icon: "📄" },
            { label: "Doações", icon: "🤝" },
          ].map((item, i) => (
            <Link key={i} href="/transparencia" className="border border-ifb-black bg-ifb-white text-center py-6 px-3 hover:bg-ifb-yellow hover:border-ifb-black transition-all group">
              <span className="text-[32px] block mb-3">{item.icon}</span>
              <span className="text-[11px] font-bold uppercase tracking-wide text-ifb-black group-hover:text-ifb-black transition">{item.label}</span>
            </Link>
          ))}
        </div>
      </section>

      {/* ===== INDICADORES ===== */}
      <section className="bg-ifb-black">
        <div className="max-w-ifb mx-auto px-6 lg:px-10 py-10">
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
            {[
              { value: stats ? stats.politicians.toLocaleString("pt-BR") : "—", label: "Políticos" },
              { value: stats ? stats.propositions.toLocaleString("pt-BR") : "—", label: "Proposições" },
              { value: stats ? stats.votes.toLocaleString("pt-BR") : "—", label: "Votações" },
              { value: stats ? stats.committees.toLocaleString("pt-BR") : "—", label: "Comissões" },
              { value: stats?.expenses_total ? `R$ ${(stats.expenses_total / 1_000_000).toFixed(0)}mi` : "—", label: "Gastos" },
            ].map((s, i) => (
              <div key={i} className="text-center py-3">
                <p className="text-[28px] lg:text-[34px] font-bold text-ifb-yellow">{s.value}</p>
                <p className="text-[11px] text-ifb-gray-400 uppercase tracking-wide mt-1">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== FONTES DE DADOS ===== */}
      <section className="bg-ifb-black-soft border-t border-ifb-gray-800">
        <div className="max-w-ifb mx-auto px-6 lg:px-10 py-8">
          <h3 className="text-[12px] font-bold uppercase tracking-wider text-ifb-gray-400 mb-4">Fontes de Dados Verificáveis</h3>
          <div className="flex flex-wrap items-center gap-6 text-[12px] text-ifb-gray-500">
            <span className="font-medium text-ifb-white/70">TSE</span>
            <span className="font-medium text-ifb-white/70">Câmara dos Deputados</span>
            <span className="font-medium text-ifb-white/70">Senado Federal</span>
            <span className="font-medium text-ifb-white/70">Google News</span>
            <span className="font-medium text-ifb-white/70">Portal da Transparência</span>
          </div>
        </div>
      </section>

      {/* ===== FOOTER ===== */}
      <footer className="bg-ifb-black">
        <div className="max-w-ifb mx-auto px-6 lg:px-10 py-10">
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-5 gap-8">
            <div className="col-span-2 sm:col-span-4 lg:col-span-1">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-[28px] h-[28px] bg-ifb-yellow flex items-center justify-center skew-x-[-6deg]">
                  <span className="text-ifb-black font-bold text-[9px] skew-x-[6deg]">IFB</span>
                </div>
                <span className="text-[12px] font-bold text-ifb-white">Instituto Fiscaliza Brasil</span>
              </div>
              <p className="text-[11px] text-ifb-gray-500 leading-relaxed">CNPJ: Em registro</p>
            </div>
            {[
              { title: "Pesquisar", links: [{ l: "Políticos", h: "/politicos" }, { l: "Partidos", h: "/partidos" }, { l: "Dados Abertos", h: "/transparencia" }] },
              { title: "Institucional", links: [{ l: "Metodologia", h: "/metodologia" }, { l: "Sobre Nós", h: "/sobre" }, { l: "Contato", h: "/contato" }] },
              { title: "Legal", links: [{ l: "Termos", h: "/termos" }, { l: "Privacidade", h: "/privacidade" }, { l: "Doações", h: "/doar" }] },
            ].map((col, i) => (
              <div key={i}>
                <h4 className="text-[11px] font-bold uppercase tracking-wider text-ifb-gray-400 mb-3">{col.title}</h4>
                <ul className="space-y-2">
                  {col.links.map((link, j) => (
                    <li key={j}><Link href={link.h} className="text-[12px] text-ifb-gray-500 hover:text-ifb-white transition">{link.l}</Link></li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          <div className="mt-8 pt-5 border-t border-ifb-gray-800 text-center">
            <p className="text-[11px] text-ifb-gray-600">© 2026 Instituto Fiscaliza Brasil — Todos os direitos reservados.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
