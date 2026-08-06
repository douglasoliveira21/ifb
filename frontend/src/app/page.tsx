"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function HomePage() {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    fetch(`${API_URL}/api/v1/politicians?limit=1`)
      .then((r) => r.json())
      .then((d) => setStats({ total: d.total }))
      .catch(() => {});
  }, []);

  return (
    <main className="min-h-screen bg-ifb-bg">
      {/* Header */}
      <header className="border-b border-ifb-gray-200 bg-white sticky top-0 z-50">
        <div className="container-ifb py-4 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-ifb-yellow rounded-full flex items-center justify-center">
                <span className="text-ifb-black font-bold text-xs">IFB</span>
              </div>
              <span className="font-bold text-ifb-black text-lg hidden sm:block">Instituto<br className="hidden"/>Fiscaliza Brasil</span>
            </Link>
            <nav className="hidden lg:flex items-center gap-6 text-sm font-medium text-ifb-gray-500">
              <Link href="/politicos" className="hover:text-ifb-black transition">Início</Link>
              <Link href="/politicos" className="hover:text-ifb-black transition">Ranking</Link>
              <Link href="/politicos" className="hover:text-ifb-black transition">Notícias</Link>
              <Link href="/transparencia" className="hover:text-ifb-black transition">Transparência</Link>
              <Link href="/sobre" className="hover:text-ifb-black transition">Sobre</Link>
              <Link href="/sobre" className="hover:text-ifb-black transition">Contato</Link>
            </nav>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login" className="text-sm font-medium text-ifb-gray-700 hover:text-ifb-black transition hidden sm:block">Entrar</Link>
            <Link href="/doar" className="btn-primary text-xs px-4 py-2">Apoie o IFB</Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="bg-ifb-gray-50 border-b border-ifb-gray-200">
        <div className="container-ifb py-16 lg:py-24">
          <div className="max-w-3xl">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-ifb-black leading-tight">
              Fiscalizar é um direito <span className="text-ifb-yellow">seu.</span>
            </h1>
            <p className="mt-4 text-lg text-ifb-gray-500 max-w-xl">
              Informação política de qualidade, transparente e independente.
            </p>

            {/* Search */}
            <form action="/politicos" className="mt-8 flex gap-2 max-w-xl">
              <div className="flex-1 relative">
                <input
                  type="text"
                  name="q"
                  placeholder="Pesquise por nome, partido, cargo ou Estado..."
                  className="input pr-12 py-4 text-base"
                  aria-label="Pesquisar político"
                />
              </div>
              <button type="submit" className="bg-ifb-yellow hover:bg-ifb-yellow-hover text-ifb-black p-4 rounded-ifb-btn transition">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
              </button>
            </form>
            <p className="mt-3 text-xs text-ifb-gray-400">Ex: Bolsonaro, Lula, PT, PL, São Paulo...</p>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="border-b border-ifb-gray-200 bg-white">
        <div className="container-ifb py-8">
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
            {[
              { value: stats?.total || "594", label: "Políticos cadastrados" },
              { value: "10.431", label: "Proposições e matérias" },
              { value: "190", label: "Votações registradas" },
              { value: "2.612", label: "Comissões parlamentares" },
              { value: "R$ 932 mi+", label: "Gastos parlamentares" },
            ].map((s, i) => (
              <div key={i} className="text-center p-4">
                <p className="text-2xl lg:text-3xl font-bold text-ifb-black">{s.value}</p>
                <p className="text-xs text-ifb-gray-500 mt-1">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Main content grid */}
      <section className="container-ifb py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Ranking */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-bold text-ifb-black">Ranking IFB</h2>
              <Link href="/politicos" className="text-xs text-ifb-yellow font-medium hover:underline">Ver ranking completo →</Link>
            </div>
            <div className="space-y-3">
              {["Adriana Ventura", "Kim Kataguiri", "Alan Rick", "Rodrigo Moro", "Zé Trovão"].map((name, i) => (
                <div key={i} className="flex items-center gap-3 py-2">
                  <span className="text-xs font-medium text-ifb-gray-400 w-4">{i + 1}</span>
                  <div className="w-8 h-8 bg-ifb-gray-100 rounded-full flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-ifb-black truncate">{name}</p>
                    <p className="text-xs text-ifb-gray-400">NOVO / SP</p>
                  </div>
                  <span className="text-sm font-bold text-ifb-yellow">{(78.6 - i * 2.3).toFixed(1)}</span>
                </div>
              ))}
            </div>
          </div>

          {/* News */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-bold text-ifb-black">Notícias em destaque</h2>
              <Link href="/politicos" className="text-xs text-ifb-yellow font-medium hover:underline">Ver todas →</Link>
            </div>
            <div className="space-y-4">
              {[
                "Câmara aprova projeto que endurece punições para crimes contra o patrimônio público",
                "Senado debate novo marco fiscal em audiência pública nesta terça-feira",
                "Governo envia ao Congresso projeto de lei sobre inteligência artificial",
              ].map((title, i) => (
                <div key={i} className="pb-3 border-b border-ifb-gray-100 last:border-0 last:pb-0">
                  <p className="text-sm text-ifb-black font-medium leading-snug">{title}</p>
                  <p className="text-xs text-ifb-gray-400 mt-1">Há {i + 1}h</p>
                </div>
              ))}
            </div>
          </div>

          {/* Transparency */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-bold text-ifb-black">Transparência IFB</h2>
            </div>
            <div className="space-y-3">
              {[
                "Receitas e Despesas",
                "Doações Recebidas",
                "Contratos e Serviços",
                "Infraestrutura e Custos",
                "Governança e Equipe",
                "Documentos e Relatórios",
              ].map((item, i) => (
                <Link key={i} href="/transparencia" className="flex items-center gap-3 py-2 hover:bg-ifb-gray-50 rounded-lg -mx-2 px-2 transition">
                  <div className="w-6 h-6 bg-ifb-yellow/20 rounded-md flex items-center justify-center">
                    <div className="w-3 h-3 bg-ifb-yellow rounded-sm" />
                  </div>
                  <span className="text-sm text-ifb-gray-700">{item}</span>
                </Link>
              ))}
              <Link href="/transparencia" className="btn-secondary w-full text-center mt-2 text-xs">Ver portal da transparência</Link>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Banner */}
      <section className="container-ifb pb-12">
        <div className="bg-ifb-gray-50 border border-ifb-gray-200 rounded-ifb-lg p-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-ifb-yellow rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-ifb-black font-bold">♥</span>
            </div>
            <div>
              <p className="font-semibold text-ifb-black">O IFB é independente e não recebe dinheiro público.</p>
              <p className="text-sm text-ifb-gray-500">Apoie nossa missão e fortaleça a fiscalização cidadã.</p>
            </div>
          </div>
          <Link href="/doar" className="btn-primary whitespace-nowrap">Apoiar agora</Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-ifb-gray-200 bg-white">
        <div className="container-ifb py-12">
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-5 gap-8">
            <div className="col-span-2 sm:col-span-4 lg:col-span-1">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-7 h-7 bg-ifb-yellow rounded-full flex items-center justify-center">
                  <span className="text-ifb-black font-bold text-[10px]">IFB</span>
                </div>
                <span className="font-bold text-sm text-ifb-black">Instituto Fiscaliza Brasil</span>
              </div>
              <p className="text-xs text-ifb-gray-500 leading-relaxed">
                Promovendo transparência, fiscalização e participação cidadã na política brasileira.
              </p>
            </div>
            {[
              { title: "Navegação", links: ["Início", "Ranking", "Notícias", "Transparência", "Sobre", "Contato"] },
              { title: "Políticos", links: ["Deputados", "Senadores", "Partidos", "Estados"] },
              { title: "Institucional", links: ["Quem somos", "Metodologia", "LGPD e Privacidade", "Termos de Uso"] },
              { title: "Transparência", links: ["Receitas e Despesas", "Doações", "Contratos", "Relatórios"] },
            ].map((col, i) => (
              <div key={i}>
                <h4 className="font-semibold text-sm text-ifb-black mb-3">{col.title}</h4>
                <ul className="space-y-2">
                  {col.links.map((link, j) => (
                    <li key={j}><Link href="#" className="text-xs text-ifb-gray-500 hover:text-ifb-black transition">{link}</Link></li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          <div className="mt-8 pt-6 border-t border-ifb-gray-100 text-center">
            <p className="text-xs text-ifb-gray-400">© 2026 Instituto Fiscaliza Brasil — Todos os direitos reservados.</p>
          </div>
        </div>
      </footer>
    </main>
  );
}
