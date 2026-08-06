"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface PoliticianDetail {
  id: string;
  full_name: string;
  ballot_name: string | null;
  slug: string;
  biography: string | null;
  birth_date: string | null;
  photo_url: string | null;
  current_status: string;
  current_party: { name: string; acronym: string } | null;
  current_position_name: string | null;
  state_code: string | null;
  city_name: string | null;
  website_url: string | null;
  is_verified: boolean;
  aliases: { alias: string; alias_type: string }[];
  social_links: { platform: string; url: string }[];
  updated_at: string;
  source_url: string | null;
}

export default function PoliticianProfilePage() {
  const params = useParams();
  const slug = params?.slug as string;
  const [data, setData] = useState<PoliticianDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!slug) return;
    fetch(`${API_URL}/api/v1/politicians/${slug}`)
      .then((res) => {
        if (!res.ok) throw new Error(`Erro ${res.status}`);
        return res.json();
      })
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [slug]);

  if (loading) {
    return (
      <main className="min-h-screen bg-ifb-gray-light flex items-center justify-center">
        <p className="text-gray-500">Carregando perfil...</p>
      </main>
    );
  }

  if (error || !data) {
    return (
      <main className="min-h-screen bg-ifb-gray-light flex items-center justify-center">
        <p className="text-red-600">{error || "Político não encontrado"}</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-ifb-gray-light">
      <div className="bg-white border-b border-ifb-gray-medium">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row gap-6 items-start">
            <div className="w-24 h-24 bg-ifb-gray-medium rounded-full flex-shrink-0 overflow-hidden">
              {data.photo_url && (
                <img src={data.photo_url} alt={data.full_name} className="w-full h-full object-cover" />
              )}
            </div>
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-ifb-black">{data.full_name}</h1>
              <p className="text-gray-600 mt-1">
                {data.ballot_name && data.ballot_name !== data.full_name && `${data.ballot_name} · `}
                {data.current_party ? data.current_party.acronym : "Sem partido"}
                {data.state_code && ` · ${data.state_code}`}
              </p>
              {data.current_position_name && (
                <p className="text-sm text-gray-500 mt-1">{data.current_position_name}</p>
              )}
              <div className="flex flex-wrap gap-2 mt-3">
                {data.is_verified && (
                  <span className="px-3 py-1 bg-ifb-green/10 text-ifb-green rounded-full text-xs font-medium">
                    Verificado
                  </span>
                )}
                <span className="px-3 py-1 bg-ifb-gray-light rounded-full text-xs font-medium text-gray-700">
                  {data.current_status === "unknown" ? "Status não definido" : data.current_status}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <section className="bg-white rounded-lg border border-ifb-gray-medium p-6">
              <h2 className="text-lg font-semibold text-ifb-black mb-4">Biografia</h2>
              <p className="text-gray-600 text-sm">
                {data.biography || "Informação ainda não disponível."}
              </p>
            </section>

            {data.aliases.length > 0 && (
              <section className="bg-white rounded-lg border border-ifb-gray-medium p-6">
                <h2 className="text-lg font-semibold text-ifb-black mb-4">Nomes conhecidos</h2>
                <ul className="space-y-2">
                  {data.aliases.map((a, i) => (
                    <li key={i} className="text-sm text-gray-700">
                      {a.alias} <span className="text-gray-400">({a.alias_type})</span>
                    </li>
                  ))}
                </ul>
              </section>
            )}
          </div>

          <div className="space-y-6">
            <section className="bg-white rounded-lg border border-ifb-gray-medium p-6">
              <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">Informações</h3>
              <dl className="space-y-3 text-sm">
                <div>
                  <dt className="text-gray-500">Cargo atual</dt>
                  <dd className="text-ifb-black font-medium">{data.current_position_name || "—"}</dd>
                </div>
                <div>
                  <dt className="text-gray-500">Partido</dt>
                  <dd className="text-ifb-black font-medium">
                    {data.current_party ? `${data.current_party.name} (${data.current_party.acronym})` : "—"}
                  </dd>
                </div>
                <div>
                  <dt className="text-gray-500">Estado</dt>
                  <dd className="text-ifb-black font-medium">{data.state_code || "—"}</dd>
                </div>
                {data.city_name && (
                  <div>
                    <dt className="text-gray-500">Município</dt>
                    <dd className="text-ifb-black font-medium">{data.city_name}</dd>
                  </div>
                )}
              </dl>
            </section>

            <section className="bg-white rounded-lg border border-ifb-gray-medium p-6">
              <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">Fontes</h3>
              <p className="text-xs text-gray-500">
                Dados provenientes de fontes públicas oficiais.
                <br />Última atualização: {new Date(data.updated_at).toLocaleDateString("pt-BR")}
              </p>
              {data.source_url && (
                <a href={data.source_url} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-600 hover:underline mt-2 block">
                  Ver fonte
                </a>
              )}
            </section>
          </div>
        </div>
      </div>
    </main>
  );
}
