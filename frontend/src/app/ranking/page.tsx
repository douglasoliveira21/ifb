"use client";

import Link from "next/link";

export default function RankingPage() {
  return (
    <main className="min-h-screen bg-[#FAFAFA]">
      <div className="bg-white border-b border-[#E5E7EB]">
        <div className="max-w-[1440px] mx-auto px-6 lg:px-12 py-8">
          <Link href="/" className="text-[13px] text-[#9CA3AF] hover:text-[#111] transition mb-4 inline-block">← Início</Link>
          <h1 className="text-[28px] font-bold text-[#111]">Ranking IFB</h1>
          <p className="text-[14px] text-[#6B7280] mt-2 max-w-[600px]">
            Avaliação objetiva e transparente dos parlamentares brasileiros com base em indicadores públicos e metodologia aberta.
          </p>
        </div>
      </div>

      <div className="max-w-[1440px] mx-auto px-6 lg:px-12 py-12">
        <div className="bg-white border border-[#E5E7EB] rounded-[16px] p-8 max-w-[640px] mx-auto text-center">
          <div className="w-[64px] h-[64px] bg-[#FFF8E1] rounded-full flex items-center justify-center mx-auto mb-5">
            <svg className="w-8 h-8 text-[#F4B400]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
          </div>
          <h2 className="text-[20px] font-bold text-[#111] mb-3">Ranking em preparação</h2>
          <p className="text-[14px] text-[#6B7280] leading-relaxed mb-6 max-w-[440px] mx-auto">
            Estamos finalizando a metodologia pública de avaliação dos parlamentares. O ranking será publicado somente após validação completa dos critérios, indicadores e pesos utilizados no cálculo.
          </p>
          <div className="bg-[#F6F7F9] border border-[#E9ECEF] rounded-[12px] p-5 text-left mb-6">
            <h3 className="text-[13px] font-semibold text-[#111] mb-3">O que será considerado:</h3>
            <ul className="space-y-2 text-[13px] text-[#374151]">
              <li className="flex items-start gap-2"><span className="text-[#F4B400] mt-0.5">•</span>Atividade legislativa (proposições, votações, comissões)</li>
              <li className="flex items-start gap-2"><span className="text-[#F4B400] mt-0.5">•</span>Transparência e prestação de contas</li>
              <li className="flex items-start gap-2"><span className="text-[#F4B400] mt-0.5">•</span>Cumprimento de promessas de campanha</li>
              <li className="flex items-start gap-2"><span className="text-[#F4B400] mt-0.5">•</span>Processos judiciais confirmados</li>
              <li className="flex items-start gap-2"><span className="text-[#F4B400] mt-0.5">•</span>Gastos parlamentares relativos</li>
            </ul>
          </div>
          <Link href="/metodologia" className="inline-flex items-center gap-2 h-[40px] px-6 bg-[#F4B400] hover:bg-[#D9A000] text-[#111] text-[13px] font-semibold rounded-[10px] transition-colors">
            Conheça a metodologia
          </Link>
        </div>
      </div>
    </main>
  );
}
