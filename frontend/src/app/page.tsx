"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function HomePage() {
  const [stats, setStats] = useState<{ total: number } | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/api/v1/politicians?limit=1`)
      .then((r) => r.json())
      .then((d) => setStats({ total: d.total }))
      .catch(() => {});
  }, []);

  return (
    <main className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-ifb-gray-medium">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex flex-col leading-tight">
            <span className="text-2xl font-bold tracking-tight text-ifb-black">IFB</span>
            <span className="text-xs text-gray-600 uppercase tracking-widest">Instituto Fiscaliza Brasil</span>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm font-medium">
            <Link href="/politicos" className="hover:text-ifb-yellow transition">Políticos</Link>
            <Link href="/transparencia" className="hover:text-ifb-yellow transition">Transparência</Link>
            <Link href="/login" className="hover:text-ifb-yellow transition">Entrar</Link>
          </nav>
          <Link href="/doar" className="bg-ifb-yellow text-ifb-black px-4 py-2 rounded-md text-sm font-semibold hover:bg-ifb-yellow-light transition">
            Doe agora
          </Link>
        </div>
      </header>

      {/* Hero */}
      <section className="flex-1 flex flex-col items-center justify-center px-4 py-16 sm:py-24">
        <h1 className="text-4xl sm:text-5xl font-bold text-center max-w-3xl leading-tight text-ifb-black">
          Fiscalize quem te representa.
        </h1>
        <p className="mt-4 text-lg text-gray-600 text-center max-w-2xl">
          Plataforma pública e apartidária com dados reais sobre políticos brasileiros.
          Transparência, promessas, gastos, processos e muito mais.
        </p>

        {/* Search */}
        <form
          action="/politicos"
          className="mt-10 w-full max-w-xl"
        >
          <div className="flex gap-2">
            <input
              type="text"
              name="q"
              placeholder="Pesquisar político, partido, cidade..."
              className="flex-1 px-4 py-4 border border-ifb-gray-medium rounded-lg text-base focus:outline-none focus:ring-2 focus:ring-ifb-yellow focus:border-transparent transition"
              aria-label="Pesquisar político"
            />
            <button
              type="submit"
              className="bg-ifb-yellow text-ifb-black px-6 py-4 rounded-lg font-semibold hover:bg-ifb-yellow-light transition"
            >
              Buscar
            </button>
          </div>
        </form>

        {/* Stats */}
        <div className="mt-16 grid grid-cols-2 sm:grid-cols-4 gap-8 text-center">
          <div>
            <p className="text-3xl font-bold text-ifb-black">
              {stats ? stats.total : "—"}
            </p>
            <p className="text-sm text-gray-500 mt-1">Políticos cadastrados</p>
          </div>
          <div>
            <p className="text-3xl font-bold text-ifb-black">513</p>
            <p className="text-sm text-gray-500 mt-1">Deputados</p>
          </div>
          <div>
            <p className="text-3xl font-bold text-ifb-black">81</p>
            <p className="text-sm text-gray-500 mt-1">Senadores</p>
          </div>
          <div>
            <p className="text-3xl font-bold text-ifb-black">27</p>
            <p className="text-sm text-gray-500 mt-1">Estados</p>
          </div>
        </div>

        {/* CTA */}
        <div className="mt-12 flex flex-col sm:flex-row gap-4">
          <Link
            href="/politicos"
            className="bg-ifb-black text-white px-6 py-3 rounded-md font-semibold text-center hover:bg-gray-800 transition"
          >
            Ver todos os políticos
          </Link>
          <Link
            href="/transparencia"
            className="border-2 border-ifb-black text-ifb-black px-6 py-3 rounded-md font-semibold text-center hover:bg-ifb-black hover:text-white transition"
          >
            Transparência do IFB
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="bg-ifb-gray-light border-t border-ifb-gray-medium py-16">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-2xl font-bold text-center text-ifb-black mb-10">O que você encontra aqui</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { title: "Histórico Eleitoral", desc: "Candidaturas, resultados, patrimônio declarado e financiamento de campanha." },
              { title: "Atuação Parlamentar", desc: "Projetos de lei, votações, presença em sessões e gastos." },
              { title: "Notícias Classificadas", desc: "Impacto reputacional com IA e revisão humana. Fonte sempre rastreável." },
              { title: "Promessas de Campanha", desc: "Acompanhamento de cumprimento com evidências e metodologia pública." },
              { title: "Processos Judiciais", desc: "Dados públicos com papel claramente identificado. Processo não é culpa." },
              { title: "Indicadores", desc: "Presença, atividade, gastos — cada dimensão separada, sem nota única arbitrária." },
            ].map((f, i) => (
              <div key={i} className="bg-white p-6 rounded-lg border border-ifb-gray-medium">
                <h3 className="font-semibold text-ifb-black">{f.title}</h3>
                <p className="text-sm text-gray-600 mt-2">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-ifb-gray-medium bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div>
              <p className="text-sm font-semibold text-ifb-black">Instituto Fiscaliza Brasil</p>
              <p className="text-xs text-gray-500 mt-1">Plataforma apartidária. Dados de fontes públicas oficiais.</p>
            </div>
            <div className="flex gap-6 text-sm text-gray-600">
              <Link href="/sobre" className="hover:text-ifb-black">Sobre</Link>
              <Link href="/metodologia" className="hover:text-ifb-black">Metodologia</Link>
              <Link href="/transparencia" className="hover:text-ifb-black">Transparência</Link>
              <Link href="/termos" className="hover:text-ifb-black">Termos</Link>
              <Link href="/privacidade" className="hover:text-ifb-black">Privacidade</Link>
            </div>
          </div>
          <p className="text-xs text-gray-400 text-center mt-6">© 2026 Instituto Fiscaliza Brasil. Todos os direitos reservados.</p>
        </div>
      </footer>
    </main>
  );
}
