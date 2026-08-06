"use client";

export default function PoliticosPage() {
  return (
    <main className="min-h-screen bg-ifb-gray-light">
      <div className="bg-white border-b border-ifb-gray-medium">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <h1 className="text-3xl font-bold text-ifb-black">Políticos</h1>
          <p className="text-gray-600 mt-2">
            Pesquise e consulte informações públicas sobre políticos brasileiros.
          </p>

          <div className="mt-6 flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <input
                type="text"
                placeholder="Pesquisar por nome, partido, cargo..."
                className="w-full pl-4 pr-4 py-3 border border-ifb-gray-medium rounded-md focus:outline-none focus:ring-2 focus:ring-ifb-yellow"
                aria-label="Pesquisar político"
              />
            </div>
            <select
              className="px-4 py-3 border border-ifb-gray-medium rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-ifb-yellow"
              aria-label="Filtrar por estado"
            >
              <option value="">Todos os estados</option>
              <option value="SP">São Paulo</option>
              <option value="RJ">Rio de Janeiro</option>
              <option value="MG">Minas Gerais</option>
            </select>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center py-16">
          <p className="text-gray-500 text-lg">Nenhum político encontrado.</p>
          <p className="text-gray-400 text-sm mt-2">
            Dados em fase de importação.
          </p>
        </div>
      </div>
    </main>
  );
}
