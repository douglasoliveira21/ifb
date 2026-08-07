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
      <section className="bg-ifb-black relative overflow-hidden">
        <div className="max-w-ifb mx-auto px-6 lg:px-10 py-16 lg:py-24 relative z-10">
          <div className="max-w-[700px]">
            <h1 className="text-[32px] sm:text-[42px] lg:text-[52px] font-bold uppercase leading-[1.05] tracking-tight">
              <span className="text-ifb-white">POLÍTICA BRASILEIRA,</span><br />
              <span className="text-ifb-white">PELA LUPA DO </span><span className="text-ifb-yellow">DADO.</span><br />
              <span className="text-ifb-yellow">IFB</span><span className="text-ifb-white"> ORGANIZA,</span><br />
              <span className="text-ifb-white">VOCÊ </span><span className="text-ifb-yellow">CONCLUI.</span>
            </h1>
            <p className="mt-6 text-[14px] text-ifb-gray-400 leading-relaxed max-w-[480px]">
              Informação organizada, rastreável e contextualizada sobre políticos e candidatos brasileiros, sem te dizer em quem votar.
            </p>
            <Link href="/politicos" className="btn-outline border-ifb-yellow text-ifb-yellow hover:bg-ifb-yellow hover:text-ifb-black mt-8 inline-block">
              Conheça a Plataforma
            </Link>
          </div>
        </div>
        {/* Geometric accent */}
        <div className="absolute top-0 right-0 w-[400px] h-full hidden lg:block">
          <div className="absolute top-[10%] right-[5%] w-[200px] h-[200px] bg-ifb-yellow/10 skew-x-[-12deg] skew-y-[6deg]" />
          <div className="absolute bottom-[15%] right-[15%] w-[120px] h-[120px] border-2 border-ifb-yellow/30 skew-x-[8deg]" />
          <div className="absolute top-[40%] right-[2%] w-0 h-0 border-l-[60px] border-l-transparent border-b-[100px] border-b-ifb-yellow/20 border-r-[60px] border-r-transparent" />
        </div>
        <img src="/images/congresso-nacional.png" alt="" className="absolute top-0 right-0 h-full w-[45%] object-cover opacity-20 hidden lg:block" />
      </section>

      {/* ===== MÓDULOS ===== */}
      <section className="max-w-ifb mx-auto px-6 lg:px-10 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-0">
          {/* Perfil do Político — destaque */}
          <Link href="/politicos" className="card-ifb-yellow group hover:shadow-ifb-black transition relative overflow-hidden">
            <div className="w-[40px] h-[40px] bg-ifb-black flex items-center justify-center mb-4">
              <svg className="w-5 h-5 text-ifb-yellow" fill="currentColor" viewBox="0 0 20 20"><path d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" /></svg>
            </div>
            <h3 className="text-[15px] font-bold uppercase tracking-wide text-ifb-black mb-2">Perfil do Político</h3>
            <p className="text-[12px] text-ifb-black/70 leading-relaxed">Histórico, Candidaturas, Patrimônio, Projetos, Votações, Gastos, Notícias, Promessas... Tudo de fontes oficiais.</p>
            <div className="absolute top-3 right-3 w-0 h-0 border-l-[16px] border-l-transparent border-t-[16px] border-t-ifb-black" />
          </Link>

          {/* Notícias + IA */}
          <Link href="/noticias" className="card-ifb border-ifb-black group hover:shadow-ifb transition">
            <div className="w-[40px] h-[40px] border-2 border-ifb-black flex items-center justify-center mb-4">
              <svg className="w-5 h-5 text-ifb-black" fill="currentColor" viewBox="0 0 20 20"><path d="M2 5a2 2 0 012-2h8a2 2 0 012 2v10a2 2 0 002 2H4a2 2 0 01-2-2V5zm3 1h6v4H5V6zm6 6H5v2h6v-2z" /><path d="M15 7h1a2 2 0 012 2v5.5a1.5 1.5 0 01-3 0V7z" /></svg>
            </div>
            <h3 className="text-[15px] font-bold uppercase tracking-wide text-ifb-black mb-2">Notícias + IA</h3>
            <p className="text-[12px] text-ifb-gray-600 leading-relaxed">Coleta, classificação e análise de sentimento com Inteligência Artificial, sobreposta por rigorosa revisão humana editorial.</p>
          </Link>

          {/* Indicadores & Ranking */}
          <div className="card-ifb border-ifb-black relative">
            <div className="w-[40px] h-[40px] border-2 border-ifb-black flex items-center justify-center mb-4">
              <svg className="w-5 h-5 text-ifb-black" fill="currentColor" viewBox="0 0 20 20"><path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zm6-4a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zm6-3a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" /></svg>
            </div>
            <h3 className="text-[15px] font-bold uppercase tracking-wide text-ifb-black mb-2">Indicadores & Ranking</h3>
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
                <Link key={n.id} href={`/noticias/${n.id}`} className="card-ifb hover:shadow-ifb transition group">
                  <p className="text-[13px] font-semibold text-ifb-black leading-snug group-hover:text-ifb-yellow transition line-clamp-3">{n.title}</p>
                  <div className="mt-3 flex items-center justify-between">
                    <span className="text-[11px] text-ifb-gray-500">{n.politician_name}</span>
                    {n.published_at && <span className="text-[10px] text-ifb-gray-400">{new Date(n.published_at).toLocaleDateString("pt-BR")}</span>}
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="card-ifb text-center py-8">
              <p className="text-[13px] text-ifb-gray-500">Notícias serão exibidas após coleta, classificação e revisão humana.</p>
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
            <Link key={i} href="/transparencia" className="card-ifb text-center hover:shadow-ifb transition group py-5">
              <span className="text-[20px] block mb-2">{item.icon}</span>
              <span className="text-[11px] font-bold uppercase tracking-wide text-ifb-black group-hover:text-ifb-yellow transition">{item.label}</span>
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
