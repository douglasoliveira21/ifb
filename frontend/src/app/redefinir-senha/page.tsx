"use client";

import { useSearchParams } from "next/navigation";
import Link from "next/link";

export default function ResetPasswordPage() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  if (!token) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-ifb-gray-light px-4">
        <div className="bg-white rounded-lg border border-ifb-gray-medium p-8 text-center max-w-md">
          <h2 className="text-xl font-semibold text-ifb-red mb-2">Link inválido</h2>
          <p className="text-gray-600 text-sm mb-4">
            Este link de redefinição é inválido ou expirou.
          </p>
          <Link href="/esqueci-minha-senha" className="text-ifb-black font-medium hover:underline">
            Solicitar novo link
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-ifb-gray-light px-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-lg border border-ifb-gray-medium p-8">
          <h2 className="text-xl font-semibold text-ifb-black mb-6">
            Nova senha
          </h2>

          <form className="space-y-4">
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Nova senha (mínimo 10 caracteres)
              </label>
              <input
                id="password"
                type="password"
                autoComplete="new-password"
                required
                minLength={10}
                className="w-full px-4 py-3 border border-ifb-gray-medium rounded-md
                         focus:outline-none focus:ring-2 focus:ring-ifb-yellow focus:border-transparent"
              />
            </div>

            <div>
              <label htmlFor="confirm" className="block text-sm font-medium text-gray-700 mb-1">
                Confirmar nova senha
              </label>
              <input
                id="confirm"
                type="password"
                autoComplete="new-password"
                required
                minLength={10}
                className="w-full px-4 py-3 border border-ifb-gray-medium rounded-md
                         focus:outline-none focus:ring-2 focus:ring-ifb-yellow focus:border-transparent"
              />
            </div>

            <button
              type="submit"
              className="w-full bg-ifb-yellow text-ifb-black py-3 rounded-md font-semibold
                       hover:bg-ifb-yellow-light transition-colors"
            >
              Redefinir senha
            </button>
          </form>
        </div>
      </div>
    </main>
  );
}
