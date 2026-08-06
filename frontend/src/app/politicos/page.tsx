"use client";

import { Suspense } from "react";
import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Politician {
  id: string;
  full_name: string;
  ballot_name: string | null;
  slug: string;
  photo_url: string | null;
  current_status: string;
  current_party: { acronym: string; name: string } | null;
  current_position_name: string | null;
  state_code: string | null;
  city_name: string | null;
}

interface ApiResponse {
  items: Politician[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

const UF_LIST = [
  "AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT",
  "PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO",
];

export default function PoliticosPageWrapper() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-ifb-gray-light flex items-center justify-center"><p className="text-gray-500">Carregando...</p></div>}>
      <PoliticosPageContent />
    </Suspense>
  );
}

function PoliticosPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [data, setData] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Read filters from URL
  const currentQuery = searchParams?.get("q") || "";
  const currentState = searchParams?.get("state") || "";
  const currentPage = parseInt(searchParams?.get("page") || "1", 10);

  // Local form state
  const [query, setQuery] = useState(currentQuery);
  const [state, setState] = useState(currentState);

  const fetchData = useCallback(async (q: string, st: string, page: number) => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (q) params.set("q", q);
      if (st) params.set("state", st);
      params.set("page", String(page));
      params.set("limit", "18");

      const res = await fetch(`${API_URL}/api/v1/politicians?${params.toString()}`);
      if (!res.ok) throw new Error(`Erro ${res.status}`);
      const json: ApiResponse = await res.json();
      setData(json);
    } catch (e: any) {
      setError(e.message || "Erro ao carregar dados");
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch on mount and when URL params change
  useEffect(() => {
    fetchData(currentQuery, currentState, currentPage);
  }, [currentQuery, currentState, currentPage, fetchData]);

  function updateURL(q: string, st: string, page: number) {
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (st) params.set("state", st);
    if (page > 1) params.set("page", String(page));
    const qs = params.toString();
    router.push(`/politicos${qs ? `?${qs}` : ""}`);
  }

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    updateURL(query, state, 1);
  }

  function handleStateChange(newState: string) {
    setState(newState);
    updateURL(query, newState, 1);
  }

  function goToPage(page: number) {
    updateURL(currentQuery, currentState, page);
  }

  return (
    <main className="min-h-screen bg-ifb-gray-light">
      {/* Header */}
      <div className="bg-white border-b border-ifb-gray-medium">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-ifb-black">Políticos</h1>
              <p className="text-gray-600 mt-1 text-sm">
                Pesquise informações públicas sobre políticos brasileiros.
              </p>
            </div>
            <Link href="/" className="text-sm text-gray-500 hover:text-ifb-black">
              ← Início
            </Link>
          </div>

          {/* Search + Filters */}
          <form onSubmit={handleSearch} className="mt-6 flex flex-col sm:flex-row gap-3">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Nome, partido, cargo..."
              className="flex-1 px-4 py-3 border border-ifb-gray-medium rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ifb-yellow"
              aria-label="Pesquisar político"
            />
            <select
              value={state}
              onChange={(e) => handleStateChange(e.target.value)}
              className="px-4 py-3 border border-ifb-gray-medium rounded-md bg-white text-sm focus:outline-none focus:ring-2 focus:ring-ifb-yellow"
              aria-label="Filtrar por estado"
            >
              <option value="">Todos os estados</option>
              {UF_LIST.map((uf) => (
                <option key={uf} value={uf}>{uf}</option>
              ))}
            </select>
            <button
              type="submit"
              className="bg-ifb-yellow text-ifb-black px-6 py-3 rounded-md text-sm font-semibold hover:bg-ifb-yellow-light transition"
            >
              Pesquisar
            </button>
          </form>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Loading */}
        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-white rounded-lg border border-ifb-gray-medium p-5 animate-pulse">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 bg-gray-200 rounded-full" />
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-gray-200 rounded w-3/4" />
                    <div className="h-3 bg-gray-200 rounded w-1/2" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Error */}
        {!loading && error && (
          <div className="text-center py-16">
            <p className="text-red-600 font-medium">{error}</p>
            <button
              onClick={() => fetchData(currentQuery, currentState, currentPage)}
              className="mt-4 text-sm text-ifb-black underline"
            >
              Tentar novamente
            </button>
          </div>
        )}

        {/* Empty */}
        {!loading && !error && data && data.items.length === 0 && (
          <div className="text-center py-16">
            <p className="text-gray-500 text-lg">Nenhum político encontrado.</p>
            {(currentQuery || currentState) && (
              <button
                onClick={() => { setQuery(""); setState(""); updateURL("", "", 1); }}
                className="mt-4 text-sm text-ifb-black underline"
              >
                Limpar filtros
              </button>
            )}
          </div>
        )}

        {/* Results */}
        {!loading && !error && data && data.items.length > 0 && (
          <>
            <p className="text-sm text-gray-500 mb-4">
              {data.total} resultado(s) encontrado(s)
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {data.items.map((p) => (
                <Link
                  key={p.id}
                  href={`/politicos/${p.slug}`}
                  className="bg-white rounded-lg border border-ifb-gray-medium p-5 hover:shadow-md transition group"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-14 h-14 bg-ifb-gray-medium rounded-full flex-shrink-0 overflow-hidden">
                      {p.photo_url && (
                        <img src={p.photo_url} alt="" className="w-full h-full object-cover" />
                      )}
                    </div>
                    <div className="min-w-0">
                      <h2 className="font-semibold text-ifb-black truncate group-hover:text-ifb-yellow transition">
                        {p.full_name}
                      </h2>
                      <p className="text-sm text-gray-600 truncate">
                        {p.current_party?.acronym || "Sem partido"}
                        {p.state_code && ` · ${p.state_code}`}
                      </p>
                      {p.current_position_name && (
                        <p className="text-xs text-gray-500 mt-0.5 truncate">
                          {p.current_position_name}
                        </p>
                      )}
                    </div>
                  </div>
                </Link>
              ))}
            </div>

            {/* Pagination */}
            {data.pages > 1 && (
              <div className="flex justify-center items-center gap-2 mt-8">
                <button
                  onClick={() => goToPage(currentPage - 1)}
                  disabled={currentPage <= 1}
                  className="px-4 py-2 text-sm border border-ifb-gray-medium rounded-md disabled:opacity-30 hover:bg-ifb-gray-light transition"
                >
                  Anterior
                </button>
                <span className="text-sm text-gray-600 px-3">
                  {currentPage} de {data.pages}
                </span>
                <button
                  onClick={() => goToPage(currentPage + 1)}
                  disabled={currentPage >= data.pages}
                  className="px-4 py-2 text-sm border border-ifb-gray-medium rounded-md disabled:opacity-30 hover:bg-ifb-gray-light transition"
                >
                  Próxima
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </main>
  );
}