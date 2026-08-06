"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/* Foto oficial do Congresso Nacional — asset local */
const HERO_IMAGE = "/images/congresso-nacional.png";

/* Fotos placeholder dos políticos do ranking (API da Câmara) */
const RANKING_PHOTOS: Record<string, string> = {
  "Adriana Ventura": "https://www.camara.leg.br/internet/deputado/bandep/204554.jpg",
  "Kim Kataguiri": "https://www.camara.leg.br/internet/deputado/bandep/204374.jpg",
  "Alan Rick": "https://www.camara.leg.br/internet/deputado/bandep/160518.jpg",
  "Rodrigo Maia": "https://www.camara.leg.br/internet/deputado/bandep/74693.jpg",
  "Zé Trovão": "https://www.camara.leg.br/internet/deputado/bandep/220596.jpg",
};

/* Thumbnails de notícias — fotos editoriais do Congresso (Wikimedia Commons, CC-BY) */
const NEWS_THUMBS = [
  "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Fachada_do_Congresso_Nacional_%2848079561026%29.jpg/320px-Fachada_do_Congresso_Nacional_%2848079561026%29.jpg",
  "https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/Congresso_Nacional_%2824858405017%29.jpg/320px-Congresso_Nacional_%2824858405017%29.jpg",
  "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Palacio_do_Planalto.jpg/320px-Palacio_do_Planalto.jpg",
];

export default function HomePage() {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    fetch(`${API_URL}/api/v1/stats`)
      .then((r) => r.json())
      .then(setStats)
      .catch(() => {});
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
            <button className="w-[36px] h-[36px] flex items-center justify-center text-[#6B7280] hover:text-[#111] transition" aria-label="Buscar">
              <svg className="w-[18px] h-[18px]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
            </button>
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
            {/* Left — Text */}
            <div className="py-14 lg:py-20 relative z-10">
              <h1 className="text-[38px] sm:text-[46px] lg:text-[52px] font-bold text-[#111] leading-[1.1] tracking-tight">
                Fiscalizar é um<br />direito <span className="text-[#F4B400]">seu.</span>
              </h1>
              <p className="mt-4 text-[15px] text-[#6B7280] leading-relaxed max-w-[400px]">
                Informação política de qualidade,<br />transparente e independente.
              </p>

              <form action="/politicos" className="mt-8">
                <div className="flex items-center bg-white border border-[#E5E7EB] rounded-[12px] overflow-hidden shadow-[0_2px_8px_rgba(0,0,0,0.06)] max-w-[480px]">
                  <input
                    type="text"
                    name="q"
                    placeholder="Pesquise por nome, partido, cargo ou Estado..."
                    className="flex-1 h-[50px] px-5 text-[14px] text-[#111] placeholder:text-[#9CA3AF] outline-none bg-transparent"
                  />
                  <button type="submit" className="w-[50px] h-[50px] bg-[#F4B400] hover:bg-[#D9A000] flex items-center justify-center transition-colors flex-shrink-0">
                    <svg className="w-[18px] h-[18px] text-[#111]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
                  </button>
                </div>
                <p className="mt-3 text-[12px] text-[#9CA3AF]">Ex: Bolsonaro, Lula, PT, PL, São Paulo...</p>
              </form>
            </div>

            {/* Right — Image */}
            <div className="hidden lg:block relative h-[420px]">
              <div className="absolute inset-0 overflow-hidden rounded-bl-[60px]">
                <img
                  src={HERO_IMAGE}
                  alt="Congresso Nacional, Brasília"
                  className="w-full h-full object-cover object-center"
                />
                <div className="absolute inset-0 bg-gradient-to-l from-transparent to-[#FFF9E6]/80" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== INDICADORES ===== */}
      <section className="bg-white border-y border-[#E5E7EB] -mt-[1px]">
        <div className="max-w-[1440px] mx-auto px-6 lg:px-12 py-5">
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
            {[
              { value: stats?.politicians?.toLocaleString("pt-BR") || "—", label: "Políticos\ncadastrados", icon: "👤" },
              { value: stats?.propositions?.toLocaleString("pt-BR") || "—", label: "Proposições e\nmatérias", icon: "📋" },
              { value: stats?.votes?.toLocaleString("pt-BR") || "—", label: "Votações\nregistradas", icon: "✓" },
              { value: stats?.committees?.toLocaleString("pt-BR") || "—", label: "Comissões\nparlamentares", icon: "🏛" },
              { value: stats?.expenses_total ? `R$ ${(stats.expenses_total / 1_000_000).toFixed(0)} mi+` : "—", label: "Gastos\nparlamentares", icon: "💰" },
            ].map((s, i) => (
              <div key={i} className="flex items-center gap-3 bg-[#FAFAFA] border border-[#E9ECEF] rounded-[12px] px-4 py-3">
                <div className="w-[36px] h-[36px] bg-[#FFF8E1] rounded-full flex items-center justify-center flex-shrink-0 text-[14px]">
                  {s.icon}
                </div>
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

          {/* === Ranking IFB === */}
          <div className="bg-white border border-[#E5E7EB] rounded-[16px] p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-[15px] font-bold text-[#111]">Ranking IFB</h2>
              <Link href="/ranking" className="text-[12px] text-[#F4B400] font-medium hover:underline">Ver ranking completo →</Link>
            </div>

            {/* Tabs */}
            <div className="flex gap-0 mb-5">
              {["Geral", "Câmara", "Senado"].map((tab, i) => (
                <button
                  key={tab}
                  className={`px-4 py-1.5 text-[12px] font-medium rounded-full transition ${
                    i === 0
                      ? "bg-[#F4B400] text-[#111]"
                      : "bg-[#F6F7F9] text-[#6B7280] hover:bg-[#E9ECEF]"
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>

            {/* List */}
            <div className="space-y-0.5">
              {[
                { name: "Adriana Ventura", party: "NOVO / SP", score: 78.6 },
                { name: "Kim Kataguiri", party: "UNIÃO / SP", score: 72.4 },
                { name: "Alan Rick", party: "UNIÃO / AC", score: 71.3 },
                { name: "Rodrigo Maia", party: "PODE / PR", score: 68.9 },
                { name: "Zé Trovão", party: "PL / SC", score: 67.2 },
              ].map((p, i) => (
                <div key={i} className="flex items-center gap-3 py-2.5 px-2 rounded-[10px] hover:bg-[#F6F7F9] transition">
                  <span className="text-[12px] font-bold text-[#9CA3AF] w-[14px] text-right">{i + 1}</span>
                  <div className="w-[34px] h-[34px] rounded-full overflow-hidden flex-shrink-0 bg-[#E9ECEF]">
                    <img
                      src={RANKING_PHOTOS[p.name] || ""}
                      alt={p.name}
                      className="w-full h-full object-cover"
                      onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-[13px] font-semibold text-[#111] truncate">{p.name}</p>
                    <p className="text-[11px] text-[#9CA3AF]">{p.party}</p>
                  </div>
                  <span className="text-[15px] font-bold text-[#F4B400]">{p.score}</span>
                </div>
              ))}
            </div>

            <Link href="/metodologia" className="mt-5 flex items-center justify-center gap-1 text-[12px] text-[#6B7280] hover:text-[#111] transition">
              Metodologia do Ranking
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            </Link>
          </div>

          {/* === Notícias === */}
          <div className="bg-white border border-[#E5E7EB] rounded-[16px] p-6">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-[15px] font-bold text-[#111]">Notícias em destaque</h2>
              <Link href="/noticias" className="text-[12px] text-[#F4B400] font-medium hover:underline">Ver todas →</Link>
            </div>
            <div className="space-y-4">
              {[
                { tag: "CÂMARA", tagColor: "#2563EB", date: "há 2 horas", title: "Câmara aprova projeto que endurece punições para crimes contra o patrimônio público", sub: "Projeto segue agora para análise do Senado Federal." },
                { tag: "SENADO", tagColor: "#16A34A", date: "há 4 horas", title: "Senado debate novo marco fiscal em audiência pública nesta terça-feira", sub: "Economistas e especialistas foram convidados para discutir o impacto da proposta." },
                { tag: "POLÍTICA", tagColor: "#DC2626", date: "há 6 horas", title: "Governo envia ao Congresso projeto de lei sobre inteligência artificial", sub: "Texto prevê diretrizes para o uso ético e seguro da IA no Brasil." },
              ].map((n, i) => (
                <div key={i} className="flex gap-3 pb-4 border-b border-[#F3F4F6] last:border-0 last:pb-0">
                  <div className="w-[80px] h-[80px] rounded-[10px] overflow-hidden flex-shrink-0 bg-[#E9ECEF]">
                    <img src={NEWS_THUMBS[i]} alt="" className="w-full h-full object-cover" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[10px] font-bold px-1.5 py-0.5 rounded" style={{ backgroundColor: n.tagColor + "15", color: n.tagColor }}>{n.tag}</span>
                      <span className="text-[10px] text-[#9CA3AF]">{n.date}</span>
                    </div>
                    <p className="text-[13px] font-semibold text-[#111] leading-snug line-clamp-2">{n.title}</p>
                    <p className="text-[11px] text-[#9CA3AF] mt-1 leading-relaxed line-clamp-2">{n.sub}</p>
                  </div>
                </div>
              ))}
            </div>
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
                    <div className="w-[28px] h-[28px] bg-[#FFF8E1] rounded-[8px] flex items-center justify-center text-[13px] flex-shrink-0">
                      {item.icon}
                    </div>
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
              { title: "Navegação", links: [{ l: "Início", h: "/" }, { l: "Ranking", h: "/ranking" }, { l: "Notícias", h: "/noticias" }, { l: "Transparência", h: "/transparencia" }, { l: "Sobre", h: "/sobre" }, { l: "Contato", h: "/contato" }] },
              { title: "Políticos", links: [{ l: "Deputados", h: "/politicos?position=deputado" }, { l: "Senadores", h: "/politicos?position=senador" }, { l: "Partidos", h: "/politicos" }, { l: "Estados", h: "/politicos" }] },
              { title: "Institucional", links: [{ l: "Quem somos", h: "/sobre" }, { l: "Metodologia", h: "/metodologia" }, { l: "LGPD e Privacidade", h: "/privacidade" }, { l: "Termos de Uso", h: "/termos" }, { l: "Doações", h: "/doar" }] },
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
