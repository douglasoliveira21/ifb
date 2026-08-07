"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const HERO_IMAGE = "/images/congresso-nacional.png";

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
  const [newsLoading, setNewsLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/api/v1/stats`)
      .then((r) => r.json())
      .then(setStats)
      .catch(() => {});

    fetch(`${API_URL}/api/v1/news/latest?limit=3`)
      .then((r) => r.json())
      .then((d) => setNews(d.items || []))
      .catch(() => {})
      .finally(() => setNewsLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-[#FAFAFA]">
      {/* ===== HEADER ===== */}
      <header className="h-[72px] border-b border-[#E5E7EB] bg-white flex items-center px-6 lg:px-12 sticky top-0 z-50">
        <div className="w-full max-w-[1440px] mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-[36px] h-[36px] bg-[#F4B400] rounded-full flex items-center justify-center">
              <span className="text-[#111] font-bold text-[11px] leading-none">IFB</span>
            </div>
            <div className="hidden sm:block leading-tight">
              <span className="text-[13px] font-bold text-[#111] block">Instituto</span>
              <span className="text-[13px] font-bold text-[#111] block">Fiscaliza Brasil</span>
            </div>
          </Link>

          <nav className="hidden lg:flex items-center gap-7">
            {[
              { label: "Início", href: "/" },
              { label: "Ranking", href: "/ranking" },
              { label: "Notícias", href: "/noticias" },
              { label: "Políticos", href: "/politicos" },
              { label: "Transparência", href: "/transparencia" },
              { label: "Sobre", href: "/sobre" },
              { label: "Contato", href: "/contato" },
            ].map((item) => (
              <Link key={item.label} href={item.href} className="text-[14px] font-medium text-[#374151] hover:text-[#111] transition-colors">
                {item.label}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-3">
            <Link href="/politicos" className="w-[36px] h-[36px] flex items-center justify-center text-[#6B7280] hover:text-[#111] transition" aria-label="Buscar">
              <svg className="w-[18px] h-[18px]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
            </Link>
            <Link href="/login" className="text-[14px] font-medium text-[#374151] hover:text-[#111] transition hidden sm:block">Entrar</Link>
            <Link href="/doar" className="h-[38px] px-5 bg-[#F4B400] hover:bg-[#D9A000] text-[#111] text-[13px] font-semibold rounded-[10px] flex items-center gap-1.5 transition-colors">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" /></svg>
              Apoie o IFB
            </Link>
          </div>
        </div>
      </header>

      {/* ===== HERO ===== */}
      <section className="relative overflow-hidden bg-gradient-to-r from-[#FFFDF5] via-[#FFF9E6] to-[#FFF3CC]">
        <div className="max-w-[1440px] mx-auto px-6 lg:px-12 relative">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-0 items-center min-h-[420px]">
            <div className="py-14 lg:py-20 relative z-10">
              <h1 className="text-[38px] sm:text-[46px] lg:text-[52px] font-bold text-[#111] leading-[1.1] tracking-tight">
                Fiscalizar é um<br />direito <span className="text-[#F4B400]">seu.</span>
              </h1>
              <p className="mt-4 text-[15px] text-[#6B7280] leading-relaxed max-w-[400px]">
                Informação política de qualidade,<br />transparente e independente.
              </p>
              <form action="/politicos" className="mt-8">
                <div className="flex items-center bg-white border border-[#E5E7EB] rounded-[12px] overflow-hidden shadow-[0_2px_8px_rgba(0,0,0,0.06)] max-w-[480px]">
                  <input type="text" name="q" placeholder="Pesquise por nome, partido, cargo ou Estado..." className="flex-1 h-[50px] px-5 text-[14px] text-[#111] placeholder:text-[#9CA3AF] outline-none bg-transparent" />
                  <button type="submit" className="w-[50px] h-[50px] bg-[#F4B400] hover:bg-[#D9A000] flex items-center justify-center transition-colors flex-shrink-0">
                    <svg className="w-[18px] h-[18px] text-[#111]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
                  </button>
                </div>
                <p className="mt-3 text-[12px] text-[#9CA3AF]">Ex: Bolsonaro, Lula, PT, PL, São Paulo...</p>
              </form>
            </div>
            <div className="hidden lg:block relative h-[420px]">
              <div className="absolute inset-0 overflow-hidden rounded-bl-[60px]">
                <img src={HERO_IMAGE} alt="Congresso Nacional, Brasília" className="w-full h-full object-cover object-center" />
                <div className="absolute inset-0 bg-gradient-to-l from-transparent to-[#FFF9E6]/80" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== INDICADORES (API real) ===== */}
      <section className="bg-white border-y border-[#E5E7EB] -mt-[1px]">
        <div className="max-w-[1440px] mx-auto px-6 lg:px-12 py-5">
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
            {[
              { value: stats ? stats.politicians.toLocaleString("pt-BR") : "—", label: "Políticos\ncadastrados", icon: "👤" },
              { value: stats ? stats.propositions.toLocaleString("pt-BR") : "—", label: "Proposições e\nmatérias", icon: "📋" },
              { value: stats ? stats.votes.toLocaleString("pt-BR") : "—", label: "Votações\nregistradas", icon: "✓" },
              { value: stats ? stats.committees.toLocaleString("pt-BR") : "—", label: "Comissões\nparlamentares", icon: "🏛" },
              { value: stats?.expenses_total ? `R$ ${(stats.expenses_total / 1_000_000).toFixed(0)} mi+` : "—", label: "Gastos\nparlamentares", icon: "💰" },
            ].map((s, i) => (
              <div key={i} className="flex items-center gap-3 bg-[#FAFAFA] border border-[#E9ECEF] rounded-[12px] px-4 py-3">
                <div className="w-[36px] h-[36px] bg-[#FFF8E1] rounded-full flex items-center justify-center flex-shrink-0 text-[14px]">{s.icon}</div>
                <div>
                  <p className="text-[20px] lg:text-[22px] font-bold text-[#111] leading-tight">{s.value}</p>
                  <p className="text-[11px] text-[#6B7280] whitespace-pre-line leading-tight">{s.label}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== GRID PRINCIPAL ===== */}
      <section className="max-w-[1440px] mx-auto px-6 lg:px-12 py-10">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* === Ranking — Em preparação === */}
          <div className="bg-white border border-[#E5E7EB] rounded-[16px] p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-[15px] font-bold text-[#111]">Ranking IFB</h2>
            </div>
            <div className="flex flex-col items-center justify-center py-10 text-center">
              <div className="w-[48px] h-[48px] bg-[#FFF8E1] rounded-full flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-[#F4B400]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
              </div>
              <p className="text-[14px] font-semibold text-[#111] mb-1">Ranking em preparação</p>
              <p className="text-[12px] text-[#6B7280] max-w-[220px] leading-relaxed">
                Estamos finalizando a metodologia pública de avaliação dos parlamentares.
              </p>
              <Link href="/metodologia" className="mt-4 text-[12px] text-[#F4B400] font-medium hover:underline">
                Conheça a metodologia →
              </Link>
            </div>
          </div>

          {/* === Notícias (API real) === */}
          <div className="bg-white border border-[#E5E7EB] rounded-[16px] p-6">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-[15px] font-bold text-[#111]">Notícias recentes</h2>
            </div>

            {newsLoading && (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="animate-pulse flex gap-3">
                    <div className="w-[60px] h-[60px] bg-[#E9ECEF] rounded-[8px]" />
                    <div className="flex-1 space-y-2 py-1">
                      <div className="h-3 bg-[#E9ECEF] rounded w-full" />
                      <div className="h-3 bg-[#E9ECEF] rounded w-2/3" />
                    </div>
                  </div>
                ))}
              </div>
            )}

            {!newsLoading && news.length === 0 && (
              <div className="flex flex-col items-center justify-center py-10 text-center">
                <div className="w-[48px] h-[48px] bg-[#FFF8E1] rounded-full flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-[#F4B400]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" /></svg>
                </div>
                <p className="text-[14px] font-semibold text-[#111] mb-1">Notícias em processamento</p>
                <p className="text-[12px] text-[#6B7280] max-w-[220px] leading-relaxed">
                  As notícias serão publicadas após coleta, classificação e revisão humana.
                </p>
              </div>
            )}

            {!newsLoading && news.length > 0 && (
              <div className="space-y-4">
                {news.map((n) => (
                  <div key={n.id} className="pb-4 border-b border-[#F3F4F6] last:border-0 last:pb-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-[#F4B400]/15 text-[#92700C]">{n.category?.toUpperCase() || "GERAL"}</span>
                      {n.published_at && (
                        <span className="text-[10px] text-[#9CA3AF]">{new Date(n.published_at).toLocaleDateString("pt-BR")}</span>
                      )}
                    </div>
                    <Link href={`/noticias/${n.id}`} className="text-[13px] font-semibold text-[#111] leading-snug hover:text-[#F4B400] transition line-clamp-2 block">
                      {n.title}
                    </Link>
                    <p className="text-[11px] text-[#9CA3AF] mt-1">
                      <Link href={`/politicos/${n.politician_slug}`} className="hover:text-[#111] transition">{n.politician_name}</Link>
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* === Transparência === */}
          <div className="bg-white border border-[#E5E7EB] rounded-[16px] p-6">
            <h2 className="text-[15px] font-bold text-[#111] mb-5">Transparência IFB</h2>
            <div className="space-y-1">
              {[
                { label: "Receitas e Despesas", icon: "📊" },
                { label: "Doações Recebidas", icon: "🤝" },
                { label: "Contratos e Serviços", icon: "📄" },
                { label: "Infraestrutura e Custos", icon: "🖥" },
                { label: "Governança e Equipe", icon: "👥" },
                { label: "Documentos e Relatórios", icon: "📁" },
              ].map((item, i) => (
                <Link key={i} href="/transparencia" className="flex items-center justify-between py-3 px-3 rounded-[10px] hover:bg-[#F6F7F9] transition group">
                  <div className="flex items-center gap-3">
                    <div className="w-[28px] h-[28px] bg-[#FFF8E1] rounded-[8px] flex items-center justify-center text-[13px] flex-shrink-0">{item.icon}</div>
                    <span className="text-[13px] text-[#374151] font-medium">{item.label}</span>
                  </div>
                  <svg className="w-4 h-4 text-[#9CA3AF] group-hover:text-[#F4B400] transition" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
                </Link>
              ))}
            </div>
            <Link href="/transparencia" className="mt-5 block w-full text-center h-[40px] bg-[#F4B400] hover:bg-[#D9A000] text-[#111] rounded-[10px] text-[13px] font-semibold leading-[40px] transition-colors">
              Ver portal da transparência
            </Link>
          </div>
        </div>
      </section>

      {/* ===== CTA BANNER ===== */}
      <section className="max-w-[1440px] mx-auto px-6 lg:px-12 pb-12">
        <div className="bg-white border border-[#E5E7EB] rounded-[20px] px-8 py-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-[48px] h-[48px] bg-[#FFF8E1] rounded-full flex items-center justify-center flex-shrink-0">
              <svg className="w-6 h-6 text-[#F4B400]" fill="currentColor" viewBox="0 0 20 20"><path d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" /></svg>
            </div>
            <div>
              <p className="text-[15px] font-bold text-[#111]">O IFB é independente e não recebe dinheiro público.</p>
              <p className="text-[13px] text-[#6B7280]">Apoie nossa missão e fortaleça a fiscalização cidadã.</p>
            </div>
          </div>
          <Link href="/doar" className="h-[42px] px-7 bg-[#F4B400] hover:bg-[#D9A000] text-[#111] text-[13px] font-semibold rounded-[10px] flex items-center gap-2 transition-colors whitespace-nowrap">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" /></svg>
            Apoiar agora
          </Link>
        </div>
      </section>

      {/* ===== FOOTER ===== */}
      <footer className="border-t border-[#E5E7EB] bg-white">
        <div className="max-w-[1440px] mx-auto px-6 lg:px-12 py-12">
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-8 lg:gap-12">
            <div className="col-span-2 sm:col-span-3 lg:col-span-1">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-[28px] h-[28px] bg-[#F4B400] rounded-full flex items-center justify-center">
                  <span className="text-[#111] font-bold text-[9px]">IFB</span>
                </div>
                <span className="text-[12px] font-bold text-[#111] leading-tight">Instituto<br />Fiscaliza Brasil</span>
              </div>
              <p className="text-[11px] text-[#9CA3AF] leading-relaxed max-w-[200px]">Promovendo transparência, fiscalização e participação cidadã na política brasileira.</p>
            </div>
            {[
              { title: "Navegação", links: [{ l: "Início", h: "/" }, { l: "Ranking", h: "/ranking" }, { l: "Notícias", h: "/noticias" }, { l: "Políticos", h: "/politicos" }, { l: "Transparência", h: "/transparencia" }, { l: "Sobre", h: "/sobre" }, { l: "Contato", h: "/contato" }] },
              { title: "Políticos", links: [{ l: "Deputados", h: "/politicos?position=Deputado+Federal" }, { l: "Senadores", h: "/politicos?position=Senador" }, { l: "Partidos", h: "/partidos" }, { l: "Todos", h: "/politicos" }] },
              { title: "Institucional", links: [{ l: "Quem somos", h: "/sobre" }, { l: "Metodologia", h: "/metodologia" }, { l: "Privacidade", h: "/privacidade" }, { l: "Termos de Uso", h: "/termos" }, { l: "Doações", h: "/doar" }] },
              { title: "Transparência", links: [{ l: "Receitas e Despesas", h: "/transparencia" }, { l: "Doações", h: "/transparencia" }, { l: "Contratos", h: "/transparencia" }, { l: "Relatórios", h: "/transparencia" }] },
            ].map((col, i) => (
              <div key={i}>
                <h4 className="text-[12px] font-semibold text-[#111] mb-3">{col.title}</h4>
                <ul className="space-y-2">
                  {col.links.map((link, j) => (
                    <li key={j}><Link href={link.h} className="text-[11px] text-[#9CA3AF] hover:text-[#111] transition">{link.l}</Link></li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          <div className="mt-10 pt-5 border-t border-[#E9ECEF]">
            <p className="text-[11px] text-[#9CA3AF]">© 2026 Instituto Fiscaliza Brasil — Todos os direitos reservados.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
