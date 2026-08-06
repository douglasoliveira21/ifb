export default function SessionsPage() {
  return (
    <main className="min-h-screen bg-ifb-gray-light">
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-bold text-ifb-black">Sessões ativas</h1>
          <button className="text-sm text-ifb-red font-medium hover:underline">
            Encerrar todas
          </button>
        </div>

        <div className="bg-white rounded-lg border border-ifb-gray-medium divide-y divide-ifb-gray-medium">
          {/* Session item example */}
          <div className="p-4 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-ifb-black">
                Chrome em Windows
                <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-ifb-green/10 text-ifb-green">
                  Sessão atual
                </span>
              </p>
              <p className="text-xs text-gray-500 mt-1">
                IP: 192.168.1.1 · Último acesso: agora
              </p>
            </div>
          </div>

          <div className="p-4 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-ifb-black">Firefox em Linux</p>
              <p className="text-xs text-gray-500 mt-1">
                IP: 10.0.0.1 · Último acesso: há 2 horas
              </p>
            </div>
            <button className="text-sm text-ifb-red hover:underline">
              Encerrar
            </button>
          </div>
        </div>

        <p className="mt-4 text-xs text-gray-500">
          Se você não reconhece alguma sessão, encerre-a imediatamente e altere sua senha.
        </p>
      </div>
    </main>
  );
}
