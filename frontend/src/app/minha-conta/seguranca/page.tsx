export default function SecurityPage() {
  return (
    <main className="min-h-screen bg-ifb-gray-light">
      <div className="max-w-4xl mx-auto px-4 py-12">
        <h1 className="text-2xl font-bold text-ifb-black mb-8">Segurança</h1>

        {/* Change Password */}
        <section className="bg-white rounded-lg border border-ifb-gray-medium p-6 mb-6">
          <h2 className="text-lg font-semibold text-ifb-black mb-4">Alterar senha</h2>
          <form className="space-y-4 max-w-md">
            <div>
              <label htmlFor="current" className="block text-sm font-medium text-gray-700 mb-1">
                Senha atual
              </label>
              <input
                id="current"
                type="password"
                autoComplete="current-password"
                required
                className="w-full px-4 py-3 border border-ifb-gray-medium rounded-md
                         focus:outline-none focus:ring-2 focus:ring-ifb-yellow"
              />
            </div>
            <div>
              <label htmlFor="new_password" className="block text-sm font-medium text-gray-700 mb-1">
                Nova senha (mínimo 10 caracteres)
              </label>
              <input
                id="new_password"
                type="password"
                autoComplete="new-password"
                required
                minLength={10}
                className="w-full px-4 py-3 border border-ifb-gray-medium rounded-md
                         focus:outline-none focus:ring-2 focus:ring-ifb-yellow"
              />
            </div>
            <button type="submit" className="btn-primary">
              Alterar senha
            </button>
          </form>
        </section>

        {/* MFA */}
        <section className="bg-white rounded-lg border border-ifb-gray-medium p-6 mb-6">
          <h2 className="text-lg font-semibold text-ifb-black mb-2">
            Autenticação em dois fatores (MFA)
          </h2>
          <p className="text-sm text-gray-600 mb-4">
            Proteja sua conta com autenticação TOTP usando aplicativos como
            Google Authenticator ou Authy.
          </p>
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
              Desativado
            </span>
            <button className="btn-primary text-sm py-2 px-4">
              Ativar MFA
            </button>
          </div>
        </section>

        {/* Danger Zone */}
        <section className="bg-white rounded-lg border border-ifb-red/20 p-6">
          <h2 className="text-lg font-semibold text-ifb-red mb-2">Zona de risco</h2>
          <p className="text-sm text-gray-600 mb-4">
            Ações irreversíveis. Tenha certeza antes de prosseguir.
          </p>
          <button className="border-2 border-ifb-red text-ifb-red px-4 py-2 rounded-md text-sm font-medium hover:bg-ifb-red hover:text-white transition">
            Excluir minha conta
          </button>
        </section>
      </div>
    </main>
  );
}
