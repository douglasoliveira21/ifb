"use client";

import Link from "next/link";
import { Suspense } from "react";

function VerifyContent() {
  return (
    <div className="bg-white rounded-lg border border-ifb-gray-medium p-8 text-center">
      <h2 className="text-xl font-semibold text-ifb-black mb-2">
        Verifique seu e-mail
      </h2>
      <p className="text-gray-600 text-sm mb-6">
        Enviamos um link de verificação para o seu e-mail.
        Clique no link para ativar sua conta.
      </p>
      <Link
        href="/login"
        className="inline-block bg-ifb-yellow text-ifb-black px-6 py-3 rounded-md font-semibold hover:bg-ifb-yellow-light transition-colors"
      >
        Ir para login
      </Link>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-ifb-gray-light px-4">
      <div className="w-full max-w-md">
        <Suspense fallback={<div>Carregando...</div>}>
          <VerifyContent />
        </Suspense>
      </div>
    </main>
  );
}
