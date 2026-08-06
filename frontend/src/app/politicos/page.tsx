"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Politician {
  id: string;
  full_name: string;
  ballot_name: string | null;
  slug: string;
  photo_url: string | null;
  current_status: string;
  current_party: { acronym: string } | null;
  current_position_name: string | null;
  state_code: string | null;
  city_name: string | null;
}

interface ApiResponse {
  items: Politician[];
  total: number;
  page: number;
  pages: number;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function PoliticosPage() {
  const [data, setData] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");

  useEffect(() => {
    fetchPoliticians();
  }, []);

  async function fetchPoliticians(q?: string) {
    setLoading(true);
    setError(null);
    try {
      const params = q ? `?q=${encodeURIComponent(q)}` : "";
      const res = await fetch(`${API_URL}/api/v1/politicians${params}`);
      if (!res.ok) throw new Error(`Erro ${res.status}`);
      const json = await res.json();
      setData(json);
    } catch (e: any) {
      setError(e.message || "Erro ao carregar dados");
    } finally {
      setLoading(false);
    }
  }

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    fetchPoliticians(query);
  }

  return (
    <main className="min-h-screen bg-ifb-gray-light">
      <div className="bg-white border-b border-ifb-gray-medium">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <h1 className="text-3xl font-bold text-ifb-black">Políticos</h1>
          <p className="text-gray-600 mt-2">
            Pesquise e consulte informações públicas sobre políticos brasileiros.
          </p>

          <form onSubmit={handleSearch} className="mt-6 flex flex-col sm:flex-row gap-4">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Pesquisar por nome, partido, cargo..."
              className="flex-1 px-4 py-3 border border-ifb-gray-medium rounded-md focus:outline-none focus:ring-2 focus:ring-ifb-yellow"
              aria-label="Pesquisar político"
            />
            <button
              type="submit"
              className="bg-ifb-yellow text-ifb-black px-6 py-3 rounded-md font-semibold hover:bg-ifb-yellow-light transition"
            >
              Pesquisar
            </button>
          </form>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {loading && (
          <div className="text-center py-16">
            <p className="text-gray-500">Carregando...</p>
          </div>
        )}

        {error && (
          <div className="text-center py-16">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {!loading && !error && data && data.items.length === 0 && (
          <div className="text-center py-16">
            <p className="text-gray-500 text-lg">Nenhum político encontrado.</p>
          </div>
        )}

        {!loading && !error && data && data.items.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.items.map((p) => (
              <Link
                key={p.id}
                href={`/politicos/${p.slug}`}
                className="bg-white rounded-lg border border-ifb-gray-medium p-5 hover:shadow-md transition"
              >
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 bg-ifb-gray-medium rounded-full flex-shrink-0" />
                  <div>
                    <h2 className="font-semibold text-ifb-black">{p.full_name}</h2>
                    <p className="text-sm text-gray-600">
                      {p.ballot_name && p.ballot_name !== p.full_name && (
                        <span>{p.ballot_name} · </span>
                      )}
                      {p.state_code || ""}
                      {p.current_party && ` · ${p.current_party.acronym}`}
                    </p>
                    {p.current_position_name && (
                      <p className="text-xs text-gray-500 mt-1">{p.current_position_name}</p>
                    )}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}

        {data && data.total > 0 && (
          <p className="text-sm text-gray-500 mt-6 text-center">
            {data.total} político(s) encontrado(s)
          </p>
        )}
      </div>
    </main>
  );
}
