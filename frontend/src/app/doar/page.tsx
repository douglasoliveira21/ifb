"use client";

import Link from "next/link";
import { useState } from "react";

export default function DoarPage() {
  const [amount, setAmount] = useState<number | null>(null);
  const [frequency, setFrequency] = useState<"one_time" | "monthly">("one_time");

  const suggestedAmounts = [10, 25, 50, 100, 200, 500];

  return (
    <main className="min-h-screen bg-ifb-gray-light">
      <div className="bg-white border-b border-ifb-gray-medium">
        <div className="max-w-3xl mx-auto px-4 py-8">
          <Link href="/" className="text-sm text-gray-500 hover:text-ifb-black">← Início</Link>
          <h1 className="text-3xl font-bold text-ifb-black mt-4">Apoie o IFB</h1>
          <p className="text-gray-600 mt-2">
            O Instituto Fiscaliza Brasil é independente e só existe com o apoio de pessoas como você.
          </p>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg border border-ifb-gray-medium p-8">
          {/* How resources are used */}
          <div className="mb-8 pb-6 border-b border-ifb-gray-light">
            <h2 className="font-semibold text-ifb-black text-lg mb-3">Para que servem os recursos</h2>
            <ul className="text-sm text-gray-600 space-y-2">
              <li>• Infraestrutura de servidores e banco de dados</li>
              <li>• Custos de inteligência artificial para classificação</li>
              <li>• Equipe de análise e revisão de dados</li>
              <li>• Manutenção e desenvolvimento da plataforma</li>
              <li>• Auditorias e conformidade legal</li>
            </ul>
            <p className="text-xs text-gray-500 mt-3">
              Toda aplicação de recursos é publicada na{" "}
              <Link href="/transparencia" className="underline text-ifb-black">página de transparência</Link>.
            </p>
          </div>

          {/* Frequency */}
          <div className="mb-6">
            <p className="text-sm font-medium text-gray-700 mb-3">Tipo de doação</p>
            <div className="flex gap-3">
              <button
                onClick={() => setFrequency("one_time")}
                className={`flex-1 py-3 rounded-md text-sm font-medium border-2 transition ${
                  frequency === "one_time"
                    ? "border-ifb-yellow bg-ifb-yellow/10 text-ifb-black"
                    : "border-ifb-gray-medium text-gray-600 hover:border-gray-400"
                }`}
              >
                Doação única
              </button>
              <button
                onClick={() => setFrequency("monthly")}
                className={`flex-1 py-3 rounded-md text-sm font-medium border-2 transition ${
                  frequency === "monthly"
                    ? "border-ifb-yellow bg-ifb-yellow/10 text-ifb-black"
                    : "border-ifb-gray-medium text-gray-600 hover:border-gray-400"
                }`}
              >
                Mensal
              </button>
            </div>
          </div>

          {/* Amount */}
          <div className="mb-6">
            <p className="text-sm font-medium text-gray-700 mb-3">Valor</p>
            <div className="grid grid-cols-3 gap-3 mb-3">
              {suggestedAmounts.map((v) => (
                <button
                  key={v}
                  onClick={() => setAmount(v)}
                  className={`py-3 rounded-md text-sm font-medium border-2 transition ${
                    amount === v
                      ? "border-ifb-yellow bg-ifb-yellow/10 text-ifb-black"
                      : "border-ifb-gray-medium text-gray-600 hover:border-gray-400"
                  }`}
                >
                  R$ {v}
                </button>
              ))}
            </div>
            <input
              type="number"
              min="1"
              placeholder="Outro valor (R$)"
              value={amount && !suggestedAmounts.includes(amount) ? amount : ""}
              onChange={(e) => setAmount(Number(e.target.value) || null)}
              className="w-full px-4 py-3 border border-ifb-gray-medium rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ifb-yellow"
            />
          </div>

          {/* Payment methods */}
          <div className="mb-6">
            <p className="text-sm font-medium text-gray-700 mb-3">Forma de pagamento</p>
            <div className="space-y-3">
              <div className="p-4 border border-ifb-gray-medium rounded-md">
                <p className="font-medium text-sm text-ifb-black">Pix</p>
                <p className="text-xs text-gray-500 mt-1">Pagamento instantâneo com QR Code</p>
              </div>
              <div className="p-4 border border-ifb-gray-medium rounded-md">
                <p className="font-medium text-sm text-ifb-black">Cartão de crédito</p>
                <p className="text-xs text-gray-500 mt-1">Processamento seguro via gateway</p>
              </div>
            </div>
          </div>

          {/* CTA */}
          <button
            disabled
            className="w-full bg-ifb-yellow text-ifb-black py-4 rounded-md font-semibold text-lg opacity-50 cursor-not-allowed"
          >
            Continuar para pagamento
          </button>

          <div className="mt-4 p-4 bg-ifb-gray-light rounded-md">
            <p className="text-xs text-gray-600 text-center">
              ⚠️ Sistema de pagamento em fase de homologação.
              Em breve você poderá realizar doações diretamente por esta página.
            </p>
          </div>
        </div>

        {/* Trust indicators */}
        <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
          <div className="bg-white rounded-lg border border-ifb-gray-medium p-4">
            <p className="text-sm font-medium text-ifb-black">100% transparente</p>
            <p className="text-xs text-gray-500 mt-1">Toda receita é publicada</p>
          </div>
          <div className="bg-white rounded-lg border border-ifb-gray-medium p-4">
            <p className="text-sm font-medium text-ifb-black">Apartidário</p>
            <p className="text-xs text-gray-500 mt-1">Nenhum doador influencia conteúdo</p>
          </div>
          <div className="bg-white rounded-lg border border-ifb-gray-medium p-4">
            <p className="text-sm font-medium text-ifb-black">Seguro</p>
            <p className="text-xs text-gray-500 mt-1">Dados protegidos, sem armazenar cartão</p>
          </div>
        </div>
      </div>
    </main>
  );
}
