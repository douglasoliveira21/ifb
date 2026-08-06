export default function HomePage() {
  return (
    <main className="min-h-screen flex flex-col">
      <header className="border-b border-ifb-gray-medium">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex flex-col leading-tight">
            <span className="text-2xl font-bold tracking-tight text-ifb-black">IFB</span>
            <span className="text-xs text-gray-600 uppercase tracking-widest">Instituto Fiscaliza Brasil</span>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm font-medium">
            <a href="/politicos" className="hover:text-ifb-yellow transition">Políticos</a>
            <a href="/transparencia" className="hover:text-ifb-yellow transition">Transparência</a>
          </nav>
          <a href="/doar" className="bg-ifb-yellow text-ifb-black px-4 py-2 rounded-md text-sm font-semibold hover:bg-ifb-yellow-light transition">
            Doe agora
          </a>
        </div>
      </header>

      <section className="flex-1 flex flex-col items-center justify-center px-4 py-20">
        <h1 className="text-4xl sm:text-5xl font-bold text-center max-w-3xl leading-tight">
          Fiscalize quem te representa.
        </h1>
        <p className="mt-4 text-lg text-gray-600 text-center max-w-2xl">
          Plataforma pública e apartidária com dados reais sobre políticos brasileiros.
        </p>

        <div className="mt-10 w-full max-w-xl">
          <input
            type="text"
            placeholder="Pesquisar político, partido, cidade..."
            className="w-full px-4 py-4 border border-ifb-gray-medium rounded-lg text-base focus:outline-none focus:ring-2 focus:ring-ifb-yellow focus:border-transparent transition"
            aria-label="Pesquisar político"
          />
        </div>

        <div className="mt-16 grid grid-cols-2 sm:grid-cols-4 gap-8 text-center">
          <div>
            <p className="text-3xl font-bold text-ifb-black">5.570</p>
            <p className="text-sm text-gray-500 mt-1">Municípios</p>
          </div>
          <div>
            <p className="text-3xl font-bold text-ifb-black">513</p>
            <p className="text-sm text-gray-500 mt-1">Deputados</p>
          </div>
          <div>
            <p className="text-3xl font-bold text-ifb-black">81</p>
            <p className="text-sm text-gray-500 mt-1">Senadores</p>
          </div>
          <div>
            <p className="text-3xl font-bold text-ifb-black">27</p>
            <p className="text-sm text-gray-500 mt-1">Governadores</p>
          </div>
        </div>
      </section>

      <footer className="border-t border-ifb-gray-medium bg-ifb-gray-light">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <p className="text-sm text-gray-600 text-center">
            © 2026 Instituto Fiscaliza Brasil. Dados provenientes de fontes públicas oficiais.
          </p>
        </div>
      </footer>
    </main>
  );
}
