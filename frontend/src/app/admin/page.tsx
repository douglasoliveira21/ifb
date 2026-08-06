"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface UserMe {
  id: string;
  email: string;
  full_name: string;
  is_verified: boolean;
  mfa_enabled: boolean;
  roles: string[];
}

export default function AdminPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserMe | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/api/v1/users/me`, { credentials: "include" })
      .then((res) => {
        if (res.status === 401) {
          router.push("/login");
          return null;
        }
        if (!res.ok) throw new Error("Erro ao carregar perfil");
        return res.json();
      })
      .then((data) => {
        if (data) setUser(data);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) {
    return (
      <main className="min-h-screen bg-ifb-gray-light flex items-center justify-center">
        <p className="text-gray-500">Carregando...</p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen bg-ifb-gray-light flex items-center justify-center">
        <p className="text-red-600">{error}</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-ifb-gray-light">
      <div className="bg-white border-b border-ifb-gray-medium">
        <div className="max-w-7xl mx-auto px-4 py-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-ifb-black">Painel Administrativo</h1>
            <p className="text-sm text-gray-600 mt-1">
              {user?.full_name} · {user?.email}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className="px-3 py-1 bg-ifb-yellow/20 text-ifb-black text-xs font-medium rounded-full">
              {user?.roles.join(", ")}
            </span>
            <Link href="/" className="text-sm text-gray-600 hover:text-ifb-black">
              Voltar ao site
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Link
            href="/admin/politicos"
            className="bg-white rounded-lg border border-ifb-gray-medium p-6 hover:shadow-md transition"
          >
            <h3 className="font-semibold text-ifb-black text-lg">Políticos</h3>
            <p className="text-sm text-gray-600 mt-2">Gerenciar cadastro, publicar, editar perfis</p>
          </Link>

          <Link
            href="/admin/integracoes"
            className="bg-white rounded-lg border border-ifb-gray-medium p-6 hover:shadow-md transition"
          >
            <h3 className="font-semibold text-ifb-black text-lg">Integrações</h3>
            <p className="text-sm text-gray-600 mt-2">TSE, Câmara, Senado, jobs, conciliação</p>
          </Link>

          <Link
            href="/admin/noticias"
            className="bg-white rounded-lg border border-ifb-gray-medium p-6 hover:shadow-md transition"
          >
            <h3 className="font-semibold text-ifb-black text-lg">Notícias</h3>
            <p className="text-sm text-gray-600 mt-2">Revisão, classificação, fontes, custos de IA</p>
          </Link>

          <Link
            href="/admin/promessas"
            className="bg-white rounded-lg border border-ifb-gray-medium p-6 hover:shadow-md transition"
          >
            <h3 className="font-semibold text-ifb-black text-lg">Promessas</h3>
            <p className="text-sm text-gray-600 mt-2">Extração, revisão, evidências, avaliações</p>
          </Link>

          <Link
            href="/admin/processos"
            className="bg-white rounded-lg border border-ifb-gray-medium p-6 hover:shadow-md transition"
          >
            <h3 className="font-semibold text-ifb-black text-lg">Processos</h3>
            <p className="text-sm text-gray-600 mt-2">Revisão judicial, conciliação, contestações</p>
          </Link>

          <Link
            href="/admin/doacoes"
            className="bg-white rounded-lg border border-ifb-gray-medium p-6 hover:shadow-md transition"
          >
            <h3 className="font-semibold text-ifb-black text-lg">Doações</h3>
            <p className="text-sm text-gray-600 mt-2">Pagamentos, webhooks, recibos, conciliação</p>
          </Link>

          <Link
            href="/admin/transparencia"
            className="bg-white rounded-lg border border-ifb-gray-medium p-6 hover:shadow-md transition"
          >
            <h3 className="font-semibold text-ifb-black text-lg">Transparência</h3>
            <p className="text-sm text-gray-600 mt-2">Receitas, despesas, contratos, documentos</p>
          </Link>

          <Link
            href="/admin/indicadores"
            className="bg-white rounded-lg border border-ifb-gray-medium p-6 hover:shadow-md transition"
          >
            <h3 className="font-semibold text-ifb-black text-lg">Indicadores</h3>
            <p className="text-sm text-gray-600 mt-2">Metodologias, cálculos, rankings</p>
          </Link>

          <Link
            href="/admin/usuarios"
            className="bg-white rounded-lg border border-ifb-gray-medium p-6 hover:shadow-md transition"
          >
            <h3 className="font-semibold text-ifb-black text-lg">Usuários</h3>
            <p className="text-sm text-gray-600 mt-2">Gerenciar contas, roles, permissões</p>
          </Link>
        </div>
      </div>
    </main>
  );
}
