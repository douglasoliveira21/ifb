import Link from "next/link";

export default function ForgotPasswordPage() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-ifb-gray-light px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-ifb-black">IFB</h1>
        </div>

        <div className="bg-white rounded-lg border border-ifb-gray-medium p-8">
          <h2 className="text-xl font-semibold text-ifb-black mb-2">
            Recuperar senha
          </h2>
          <p className="text-sm text-gray-600 mb-6">
            Informe seu e-mail e enviaremos instruções para redefinir sua senha.
          </p>

          <form className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                E-mail
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                required
                className="w-full px-4 py-3 border border-ifb-gray-medium rounded-md
                         focus:outline-none focus:ring-2 focus:ring-ifb-yellow focus:border-transparent"
              />
            </div>

            <button
              type="submit"
              className="w-full bg-ifb-yellow text-ifb-black py-3 rounded-md font-semibold
                       hover:bg-ifb-yellow-light transition-colors"
            >
              Enviar instruções
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-gray-600">
            <Link href="/login" className="font-medium text-ifb-black hover:underline">
              Voltar para login
            </Link>
          </p>
        </div>
      </div>
    </main>
  );
}
