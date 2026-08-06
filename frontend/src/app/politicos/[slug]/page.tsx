"use client";

export default function PoliticianProfilePage() {
  return (
    <main className="min-h-screen bg-ifb-gray-light">
      <div className="bg-white border-b border-ifb-gray-medium">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row gap-6 items-start">
            <div className="w-24 h-24 bg-ifb-gray-medium rounded-full flex-shrink-0" />
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-ifb-black">Perfil do Político</h1>
              <p className="text-gray-600 mt-1">Dados em carregamento</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <section className="bg-white rounded-lg border border-ifb-gray-medium p-6">
              <h2 className="text-lg font-semibold text-ifb-black mb-4">Biografia</h2>
              <p className="text-gray-600 text-sm">Informação ainda não disponível.</p>
            </section>
          </div>

          <div className="space-y-6">
            <section className="bg-white rounded-lg border border-ifb-gray-medium p-6">
              <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">Informações</h3>
              <p className="text-xs text-gray-500">Dados provenientes de fontes públicas oficiais.</p>
            </section>

            <div className="bg-ifb-yellow/10 border border-ifb-yellow/30 rounded-lg p-4">
              <p className="text-xs text-gray-700">
                <strong>Aviso:</strong> Este perfil está em construção.
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
