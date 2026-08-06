"use client";

import Link from "next/link";

export default function PoliticianProfilePage({
  params,
}: {
  params: { slug: string };
}) {
  return (
    <main className="min-h-screen bg-ifb-gray-light">
      {/* Profile Header */}
      <div className="bg-white border-b border-ifb-gray-medium">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row gap-6 items-start">
            {/* Photo placeholder */}
            <div className="w-24 h-24 bg-ifb-gray-medium rounded-full flex-shrink-0" />

            <div className="flex-1">
              <h1 className="text-2xl font-bold text-ifb-black">
                Carregando...
              </h1>
              <p className="text-gray-600 mt-1">
                Dados em carregamento
              </p>
              <div className="flex flex-wrap gap-2 mt-3">
                <span className="px-3 py-1 bg-ifb-gray-light rounded-full text-xs font-medium text-gray-700">
                  Perfil em construção
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Biography */}
            <section className="bg-white rounded-lg border border-ifb-gray-medium p-6">
              <h2 className="text-lg font-semibold text-ifb-black mb-4">Biografia</h2>
              <p className="text-gray-600 text-sm">
                Informação ainda não disponível.
              </p>
            </section>

            {/* Mandates */}
            <section className="bg-white rounded-lg border border-ifb-gray-medium p-6">
              <h2 className="text-lg font-semibold text-ifb-black mb-4">Mandatos</h2>
              <p className="text-gray-500 text-sm italic">Em preparação</p>
            </section>

            {/* Party History */}
            <section className="bg-white rounded-lg border border-ifb-gray-medium p-6">
              <h2 className="text-lg font-semibold text-ifb-black mb-4">Histórico Partidário</h2>
              <p className="text-gray-500 text-sm italic">Em preparação</p>
            </section>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick info */}
            <section className="bg-white rounded-lg border border-ifb-gray-medium p-6">
              <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">
                Informações
              </h3>
              <dl className="space-y-3 text-sm">
                <div>
                  <dt className="text-gray-500">Cargo atual</dt>
                  <dd className="text-ifb-black font-medium">—</dd>
                </div>
                <div>
                  <dt className="text-gray-500">Partido</dt>
                  <dd className="text-ifb-black font-medium">—</dd>
                </div>
                <div>
                  <dt className="text-gray-500">Estado</dt>
                  <dd className="text-ifb-black font-medium">—</dd>
                </div>
              </dl>
            </section>

            {/* Sources */}
            <section className="bg-white rounded-lg border border-ifb-gray-medium p-6">
              <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
                Fontes
              </h3>
              <p className="text-xs text-gray-500">
                Dados provenientes de fontes públicas oficiais. Última atualização: —
              </p>
            </section>

            {/* Disclaimer */}
            <div className="bg-ifb-yellow/10 border border-ifb-yellow/30 rounded-lg p-4">
              <p className="text-xs text-gray-700">
                <strong>Aviso:</strong> Este perfil está em construção.
                As informações serão importadas de fontes públicas oficiais nas próximas etapas.
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
