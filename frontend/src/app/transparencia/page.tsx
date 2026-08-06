"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function TransparenciaPage() {
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/api/v1/transparency/summary`)
      .then((r) => r.ok ? r.json() : null)
      .then(setSummary)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="min-h-screen bg-ifb-gray-light">
      <div className="bg-white border-b border-ifb-gray-medium">
        <div className="max-w-5xl mx-auto px-4 py-8">
          <Link href="/" className="text-sm text-gray-500 hover:text-ifb-black">← Início</Link>
          <h1 className="text-3xl font-bold text-ifb-black mt-4">Transparência</h1>
          <p className="text-gray-600 mt-2">
            O IFB aplica a si mesmo o padrão de transparência que cobra de políticos.
          </p>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 py-8">
        {/* Summary cards */}
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 animate-pulse">
            {[1,2,3].map(i => <div key={i} className="bg-white rounded-lg border border-ifb-gray-medium p-6 h-24" />)}
          </div>
        ) : summary ? (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg border border-ifb-gray-medium p-6 text-center">
              <p className="text-2xl font-bold text-ifb-green">
                {new Intl.NumberFormat("pt-BR", {style:"currency",currency:"BRL"}).format(summary.total_revenue || 0)}
              </p>
              <p className="text-sm text-gray-600 mt-1">Receitas totais</p>
            </div>
            <div className="bg-white rounded-lg border border-ifb-gray-medium p-6 text-center">
              <p className="text-2xl font-bold text-ifb-red">
                {new Intl.NumberFormat("pt-BR", {style:"currency",currency:"BRL"}).format(summary.total_expenses || 0)}
              </p>
              <p className="text-sm text-gray-600 mt-1">Despesas totais</p>
            </div>
            <div className="bg-white rounded-lg border border-ifb-gray-medium p-6 text-center">
              <p className="text-2xl font-bold text-ifb-black">{summary.active_contracts || 0}</p>
              <p className="text-sm text-gray-600 mt-1">Contratos ativos</p>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg border border-ifb-gray-medium p-6 text-center">
            <p className="text-gray-500">Dados financeiros ainda sendo registrados.</p>
          </div>
        )}

        {/* Sections */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <section className="bg-white rounded-lg border border-ifb-gray-medium p-6">
            <h2 className="font-semibold text-ifb-black text-lg mb-3">Receitas</h2>
            <p className="text-sm text-gray-600">
              Doações, parcerias e outras fontes de recurso do instituto.
            </p>
            <p className="text-xs text-gray-400 mt-3 italic">
              Dados serão publicados conforme receitas forem registradas.
            </p>
          </section>

          <section className="bg-white rounded-lg border border-ifb-gray-medium p-6">
            <h2 className="font-semibold text-ifb-black text-lg mb-3">Despesas</h2>
            <p className="text-sm text-gray-600">
              Custos de infraestrutura, IA, equipe, serviços e operação.
            </p>
            <p className="text-xs text-gray-400 mt-3 italic">
              Dados serão publicados conforme despesas forem registradas.
            </p>
          </section>

          <section className="bg-white rounded-lg border border-ifb-gray-medium p-6">
            <h2 className="font-semibold text-ifb-black text-lg mb-3">Contratos</h2>
            <p className="text-sm text-gray-600">
              Contratos ativos de prestação de serviço ao instituto.
            </p>
            <p className="text-xs text-gray-400 mt-3 italic">
              Nenhum contrato publicado ainda.
            </p>
          </section>

          <section className="bg-white rounded-lg border border-ifb-gray-medium p-6">
            <h2 className="font-semibold text-ifb-black text-lg mb-3">Governança</h2>
            <p className="text-sm text-gray-600">
              Diretoria, conselhos e políticas de independência.
            </p>
            <p className="text-xs text-gray-400 mt-3 italic">
              Estrutura de governança em definição.
            </p>
          </section>
        </div>

        <div className="mt-8 bg-ifb-yellow/10 border border-ifb-yellow/30 rounded-lg p-5">
          <p className="text-sm text-gray-700">
            <strong>Compromisso:</strong> Toda receita e despesa do IFB será publicada aqui com
            data, valor, categoria e responsável. Nenhum doador exerce influência sobre o conteúdo editorial.
          </p>
        </div>
      </div>
    </main>
  );
}
