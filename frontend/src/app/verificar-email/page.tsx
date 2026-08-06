"use client";

import { useSearchParams } from "next/navigation";
import Link from "next/link";

export default function VerifyEmailPage() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  return (
    <main className="min-h-screen flex items-center justify-center bg-ifb-gray-light px-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-lg border border-ifb-gray-medium p-8 text-center">
          {token ? (
            <>
              <div className="w-16 h-16 bg-ifb-yellow rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-ifb-black" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-ifb-black mb-2">
                Verificando e-mail...
              </h2>
              <p className="text-gray-600 text-sm">
                Aguarde enquanto verificamos seu e-mail.
              </p>
            </>
          ) : (
            <>
              <h2 className="text-xl font-semibold text-ifb-black mb-2">
                Verifique seu e-mail
              </h2>
              <p className="text-gray-600 text-sm mb-6">
                Enviamos um link de verificação para o seu e-mail.
                Clique no link para ativar sua conta.
              </p>
              <Link
                href="/login"
                className="inline-block bg-ifb-yellow text-ifb-black px-6 py-3 rounded-md font-semibold
                         hover:bg-ifb-yellow-light transition-colors"
              >
                Ir para login
              </Link>
            </>
          )}
        </div>
      </div>
    </main>
  );
}
