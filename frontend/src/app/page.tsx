"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function HomePage() {
  const [stats, setStats] = useState<any>(null);
  useEffect(() => {
    fetch(`${API_URL}/api/v1/politicians?limit=1`).then(r => r.json()).then(d => setStats({ total: d.total })).catch(() => {});
  }, []);

  return (
    <div className="min-h-screen bg-white">
      {/* ===== HEADER ===== */}
      <header className="h-[72px] border-b border-[#E5E7EB] bg-white flex items-center px-6 lg:px-12 sticky top-0 z-50">
        <div className="w-full max-w-[1440px] mx-auto flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-[36px] h-[36px] bg-[#F4B400] rounded-full flex items-center justify-center">
              <span className="text-[#111] font-bold text-[11px] leading-none">IFB</span>
            </div>
            <div className="hidden sm:block leading-tight">
              <span className="text-[13px] font-bold text-[#111] block">Instituto</span>
              <span className="text-[13px] font-bold text-[#111] block">Fiscaliza Brasil</span>
            </div>
          </Link>

          {/* Nav */}
          <nav className="hidden lg:flex items-center gap-7">
            {["Início", "Ranking", "Notícias", "Transparência", "Sobre", "Contato"].map(item => (
              <Link key={item} href={item === "Início" ? "/" : `/${item.toLowerCase()}`} className="text-[14px] font-medium text-[#374151] hover:text-[#111] transition-colors">{item}</Link>
            ))}
          </nav>

          {/* Right */}
          <div className="flex items-center gap-4">
            <button className="w-[36px] h-[36px] flex items-center justify-center text-[#6B7280] hover:text-[#111] transition">
              <svg className="w-[18px] h-[18px]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
            </button>
            <Link href="/login" className="text-[14px] font-medium text-[#374151] hover:text-[#111] transition hidden sm:block">Entrar</Link>
            <Link href="/doar" className="h-[38px] px-5 bg-[#F4B400] hover:bg-[#D9A000] text-[#111] text-[13px] font-semibold rounded-[10px] flex items-center transition-colors">Apoie o IFB</Link>
          </div>
        </div>
      </header>

      {/* ===== HERO ===== */}
      <section className="bg-[#F6F7F9] border-b border-[#E5E7EB] relative overflow-hidden">
        <div className="max-w-[1440px] mx-auto px-6 lg:px-12 py-16 lg:py-[80px]">
          <div className="max-w-[600px]">
            <h1 className="text-[40px] sm:text-[48px] lg:text-[56px] font-bold text-[#111] leading-[1.1] tracking-tight">
              Fiscalizar é um<br/>direito <span className="text-[#F4B400]">seu.</span>
            </h1>
            <p className="mt-4 text-[16px] text-[#6B7280] leading-relaxed max-w-[440px]">
              Informação política de qualidade,<br/>transparente e independente.
            </p>

            {/* Search */}
            <form action="/politicos" className="mt-8">
              <div className="flex items-center bg-white border border-[#E5E7EB] rounded-[14px] overflow-hidden shadow-[0_2px_8px_rgba(0,0,0,0.04)] max-w-[520px]">
                <input
                  type="text"
                  name="q"
                  placeholder="Pesquise por nome, partido, cargo ou Estado..."
                  className="flex-1 h-[52px] px-5 text-[14px] text-[#111] placeholder:text-[#9CA3AF] outline-none bg-transparent"
                />
                <button type="submit" className="w-[52px] h-[52px] bg-[#F4B400] hover:bg-[#D9A000] flex items-center justify-center transition-colors flex-shrink-0">
                  <svg className="w-[20px] h-[20px] text-[#111]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                </button>
              </div>
              <p className="mt-3 text-[12px] text-[#9CA3AF]">Ex: Bolsonaro, Lula, PT, PL, São Paulo...</p>
            </form>
          </div>
        </div>
      </section>

      {/* ===== INDICADORES ===== */}
      <section className="border-b border-[#E5E7EB] bg-white">
        <div className="max-w-[1440px] mx-auto px-6 lg:px-12 py-6">
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-0 divide-x divide-[#E5E7EB]">
            {[
              { value: stats?.total || "594", label: "Políticos\ncadastrados" },
              { value: "10.431", label: "Proposições e\nmatérias" },
              { value: "190", label: "Votações\nregistradas" },
              { value: "2.612", label: "Comissões\nparlamentares" },
              { value: "R$ 932 mi+", label: "Gastos\nparlamentares" },
            ].map((s, i) => (
              <div key={i} className="text-center py-3 px-4">
                <p className="text-[28px] lg:text-[32px] font-bold text-[#111]">{s.value}</p>
                <p className="text-[11px] text-[#6B7280] mt-1 whitespace-pre-line leading-tight">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== GRID PRINCIPAL ===== */}
      <section className="max-w-[1440px] mx-auto px-6 lg:px-12 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Ranking IFB */}
          <div className="bg-white border border-[#E5E7EB] rounded-[16px] p-6">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-[15px] font-bold text-[#111]">Ranking IFB</h2>
              <Link href="/politicos" className="text-[12px] text-[#F4B400] font-medium hover:underline">Ver ranking completo →</Link>
            </div>
            {/* Tabs */}
            <div className="flex gap-4 mb-4 border-b border-[#E9ECEF]">
              {["Geral", "Câmara", "Senado"].map((tab, i) => (
                <button key={tab} className={`pb-2 text-[12px] font-medium border-b-2 transition ${i === 0 ? "border-[#F4B400] text-[#111]" : "border-transparent text-[#9CA3AF]"}`}>{tab}</button>
              ))}
            </div>
            {/* List */}
            <div className="space-y-1">
              {[
                { name: "Adriana Ventura", party: "NOVO / SP", score: 78.6 },
                { name: "Kim Kataguiri", party: "UNIÃO / SP", score: 72.4 },
                { name: "Alan Rick", party: "UNIÃO / AC", score: 71.3 },
                { name: "Rodrigo Moro", party: "PODE / PR", score: 68.9 },
                { name: "Zé Trovão", party: "PL / SC", score: 67.2 },
              ].map((p, i) => (
                <div key={i} className="flex items-center gap-3 py-2.5 px-2 rounded-lg hover:bg-[#F6F7F9] transition">
                  <span className="text-[12px] font-semibold text-[#9CA3AF] w-3">{i + 1}</span>
                  <div className="w-[32px] h-[32px] bg-[#E9ECEF] rounded-full flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-[13px] font-semibold text-[#111] truncate">{p.name}</p>
                    <p className="text-[11px] text-[#9CA3AF]">{p.party}</p>
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="text-[14px] font-bold text-[#F4B400]">{p.score}</span>
                  </div>
                </div>
              ))}
            </div>
            <Link href="/politicos" className="mt-4 block text-center text-[12px] text-[#6B7280] hover:text-[#111] transition">Metodologia do Ranking ↗</Link>
          </div>

          {/* Notícias */}
          <div className="bg-white border border-[#E5E7EB] rounded-[16px] p-6">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-[15px] font-bold text-[#111]">Notícias em destaque</h2>
              <Link href="/politicos" className="text-[12px] text-[#F4B400] font-medium hover:underline">Ver todas →</Link>
            </div>
            <div className="space-y-5">
              {[
                { title: "Câmara aprova projeto que endurece punições para crimes contra o patrimônio público", sub: "Projeto segue agora para análise do Senado Federal." },
                { title: "Senado debate novo marco fiscal em audiência pública nesta terça-feira", sub: "Economistas e especialistas foram convidados para discutir." },
                { title: "Governo envia ao Congresso projeto de lei sobre inteligência artificial", sub: "Texto prevê diretrizes para o uso ético e seguro da IA." },
              ].map((n, i) => (
                <div key={i} className="pb-4 border-b border-[#F6F7F9] last:border-0 last:pb-0">
                  <div className="flex gap-3">
                    <div className="flex-1">
                      <p className="text-[13px] font-semibold text-[#111] leading-snug">{n.title}</p>
                      <p className="text-[11px] text-[#9CA3AF] mt-1.5 leading-relaxed">{n.sub}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Transparência */}
          <div className="bg-white border border-[#E5E7EB] rounded-[16px] p-6">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-[15px] font-bold text-[#111]">Transparência IFB</h2>
            </div>
            <div className="space-y-1">
              {[
                "Receitas e Despesas",
                "Doações Recebidas",
                "Contratos e Serviços",
                "Infraestrutura e Custos",
                "Governança e Equipe",
                "Documentos e Relatórios",
              ].map((item, i) => (
                <Link key={i} href="/transparencia" className="flex items-center gap-3 py-3 px-2 rounded-lg hover:bg-[#F6F7F9] transition">
                  <div className="w-[28px] h-[28px] bg-[#FFF8E1] rounded-[8px] flex items-center justify-center flex-shrink-0">
                    <div className="w-[12px] h-[12px] bg-[#F4B400] rounded-[4px]" />
                  </div>
                  <span className="text-[13px] text-[#374151] font-medium">{item}</span>
                </Link>
              ))}
            </div>
            <Link href="/transparencia" className="mt-4 block w-full text-center h-[38px] border border-[#E5E7EB] rounded-[10px] text-[12px] font-medium text-[#374151] hover:bg-[#F6F7F9] transition leading-[38px]">Ver portal da transparência</Link>
          </div>
        </div>
      </section>

      {/* ===== CTA BANNER ===== */}
      <section className="max-w-[1440px] mx-auto px-6 lg:px-12 pb-12">
        <div className="bg-[#F6F7F9] border border-[#E5E7EB] rounded-[20px] px-8 py-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-[44px] h-[44px] bg-[#F4B400] rounded-full flex items-center justify-center flex-shrink-0">
              <svg className="w-5 h-5 text-[#111]" fill="currentColor" viewBox="0 0 20 20"><path d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z"/></svg>
            </div>
            <div>
              <p className="text-[14px] font-semibold text-[#111]">O IFB é independente e não recebe dinheiro público.</p>
              <p className="text-[12px] text-[#6B7280]">Apoie nossa missão e fortaleça a fiscalização cidadã.</p>
            </div>
          </div>
          <Link href="/doar" className="h-[40px] px-6 bg-[#F4B400] hover:bg-[#D9A000] text-[#111] text-[13px] font-semibold rounded-[10px] flex items-center transition-colors whitespace-nowrap">Apoiar agora</Link>
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
                <span className="text-[12px] font-bold text-[#111]">Instituto<br/>Fiscaliza Brasil</span>
              </div>
              <p className="text-[11px] text-[#9CA3AF] leading-relaxed max-w-[200px]">Promovendo transparência, fiscalização e participação cidadã na política brasileira.</p>
              <div className="flex gap-3 mt-4">
                {["X", "◯", "▢", "in"].map((icon, i) => (
                  <div key={i} className="w-[28px] h-[28px] bg-[#F6F7F9] rounded-[8px] flex items-center justify-center text-[10px] text-[#6B7280]">{icon}</div>
                ))}
              </div>
            </div>
            {[
              { title: "Navegação", links: ["Início", "Ranking", "Notícias", "Transparência", "Sobre", "Contato"] },
              { title: "Políticos", links: ["Deputados", "Senadores", "Partidos", "Estados"] },
              { title: "Institucional", links: ["Quem somos", "Metodologia", "LGPD e Privacidade", "Termos de Uso", "Doações"] },
              { title: "Transparência", links: ["Receitas e Despesas", "Doações", "Contratos", "Relatórios"] },
            ].map((col, i) => (
              <div key={i}>
                <h4 className="text-[12px] font-semibold text-[#111] mb-3">{col.title}</h4>
                <ul className="space-y-2">
                  {col.links.map((link, j) => (
                    <li key={j}><Link href="#" className="text-[11px] text-[#9CA3AF] hover:text-[#111] transition">{link}</Link></li>
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
