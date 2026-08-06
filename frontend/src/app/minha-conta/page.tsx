export default function MyAccountPage() {
  return (
    <main className="min-h-screen bg-ifb-gray-light">
      <div className="max-w-4xl mx-auto px-4 py-12">
        <h1 className="text-2xl font-bold text-ifb-black mb-8">Minha Conta</h1>

        {/* Profile Section */}
        <section className="bg-white rounded-lg border border-ifb-gray-medium p-6 mb-6">
          <h2 className="text-lg font-semibold text-ifb-black mb-4">Perfil</h2>
          <form className="space-y-4 max-w-md">
            <div>
              <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 mb-1">
                Nome completo
              </label>
              <input
                id="full_name"
                type="text"
                className="w-full px-4 py-3 border border-ifb-gray-medium rounded-md
                         focus:outline-none focus:ring-2 focus:ring-ifb-yellow"
              />
            </div>
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                E-mail
              </label>
              <input
                id="email"
                type="email"
                disabled
                className="w-full px-4 py-3 border border-ifb-gray-medium rounded-md bg-gray-50 text-gray-500"
              />
            </div>
            <button type="submit" className="btn-primary">
              Salvar alterações
            </button>
          </form>
        </section>

        {/* Quick Links */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <a
            href="/minha-conta/seguranca"
            className="bg-white rounded-lg border border-ifb-gray-medium p-6 hover:shadow-sm transition"
          >
            <h3 className="font-semibold text-ifb-black">Segurança</h3>
            <p className="text-sm text-gray-600 mt-1">
              Alterar senha, MFA, sessões ativas
            </p>
          </a>
          <a
            href="/minha-conta/sessoes"
            className="bg-white rounded-lg border border-ifb-gray-medium p-6 hover:shadow-sm transition"
          >
            <h3 className="font-semibold text-ifb-black">Sessões</h3>
            <p className="text-sm text-gray-600 mt-1">
              Ver e encerrar sessões ativas
            </p>
          </a>
        </div>
      </div>
    </main>
  );
}
