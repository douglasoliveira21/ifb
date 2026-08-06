import Link from "next/link";

export default function MetodologiaPage() {
  return (
    <main className="min-h-screen bg-[#FAFAFA]">
      <div className="bg-white border-b border-[#E5E7EB]">
        <div className="max-w-[1440px] mx-auto px-6 lg:px-12 py-8">
          <Link href="/" className="text-[13px] text-[#9CA3AF] hover:text-[#111] transition mb-4 inline-block">← Início</Link>
          <h1 className="text-[28px] font-bold text-[#111]">Metodologia</h1>
          <p className="text-[14px] text-[#6B7280] mt-2 max-w-[600px]">
            Transparência total sobre como os dados são obtidos, processados e apresentados pelo IFB.
          </p>
        </div>
      </div>

      <div className="max-w-[800px] mx-auto px-6 lg:px-12 py-10 space-y-10">
        <Section title="Princípios">
          <p>O Instituto Fiscaliza Brasil opera sob cinco princípios fundamentais:</p>
          <ul className="list-disc pl-5 space-y-1 mt-2">
            <li><strong>Apartidário</strong> — Não expressa opinião política nem favorece partidos</li>
            <li><strong>Rastreável</strong> — Toda informação possui fonte e data de coleta</li>
            <li><strong>Transparente</strong> — Metodologias são públicas e explicáveis</li>
            <li><strong>Responsável</strong> — Nunca trata investigação como condenação</li>
            <li><strong>Auditável</strong> — Todas as alterações são registradas</li>
          </ul>
        </Section>

        <Section title="Fontes de dados">
          <p>Os dados utilizados são exclusivamente de fontes públicas oficiais:</p>
          <ul className="list-disc pl-5 space-y-1 mt-2">
            <li>Câmara dos Deputados — Dados Abertos (proposições, votações, despesas, comissões)</li>
            <li>Senado Federal — Dados Abertos (matérias, votações, comissões, discursos)</li>
            <li>Tribunal Superior Eleitoral — Dados Abertos (candidaturas, bens, prestação de contas)</li>
            <li>Fontes jornalísticas públicas (notícias coletadas via RSS)</li>
          </ul>
        </Section>

        <Section title="Dados legislativos">
          <p>Proposições, votações, comissões e gastos parlamentares são sincronizados diretamente das APIs oficiais da Câmara e do Senado. Cada registro mantém:</p>
          <ul className="list-disc pl-5 space-y-1 mt-2">
            <li>Identificador externo original</li>
            <li>Data e hora da coleta</li>
            <li>URL da fonte original</li>
            <li>Vínculo com o parlamentar via perfil legislativo confirmado</li>
          </ul>
        </Section>

        <Section title="Dados eleitorais">
          <p>Candidaturas, patrimônio declarado, receitas e despesas de campanha são provenientes do Portal de Dados Abertos do TSE. A importação registra:</p>
          <ul className="list-disc pl-5 space-y-1 mt-2">
            <li>Ano eleitoral e tipo de eleição</li>
            <li>Status de conciliação (matched, pending, rejected)</li>
            <li>Data de coleta e origem</li>
          </ul>
        </Section>

        <Section title="Notícias e Inteligência Artificial">
          <p>O ciclo de vida de uma notícia no IFB:</p>
          <ol className="list-decimal pl-5 space-y-2 mt-2">
            <li><strong>Coleta</strong> — Artigos são coletados via Google News RSS e outras fontes públicas</li>
            <li><strong>Deduplicação</strong> — URLs canônicas são resolvidas e duplicatas descartadas</li>
            <li><strong>Classificação automática</strong> — IA classifica sentimento, categoria e identifica o político. Esta classificação NÃO é publicação</li>
            <li><strong>Revisão humana</strong> — Toda notícia com categoria sensível, confiança insuficiente ou identidade incerta passa por revisão</li>
            <li><strong>Publicação</strong> — Somente após aprovação a notícia aparece no perfil público</li>
          </ol>
          <div className="bg-[#FFF8E1] border border-[#F4B400]/30 rounded-[10px] p-4 mt-4">
            <p className="text-[13px] text-[#374151]">
              <strong>Importante:</strong> A classificação de impacto é auxiliada por IA mas não representa juízo de valor, condenação ou absolvição. É uma categorização para organização da informação.
            </p>
          </div>
        </Section>

        <Section title="Promessas de campanha">
          <p>Promessas são extraídas de planos de governo registrados no TSE e de declarações públicas documentadas. O acompanhamento segue critérios objetivos:</p>
          <ul className="list-disc pl-5 space-y-1 mt-2">
            <li>Cumprida — Evidência documental de realização</li>
            <li>Em andamento — Ação iniciada mas não concluída</li>
            <li>Não cumprida — Prazo esgotado sem evidência de ação</li>
            <li>Impossível de verificar — Sem indicador público mensurável</li>
          </ul>
        </Section>

        <Section title="Processos judiciais">
          <p>Processos são registrados exclusivamente a partir de fontes judiciais públicas. Regras:</p>
          <ul className="list-disc pl-5 space-y-1 mt-2">
            <li>Investigação NÃO equivale a culpa</li>
            <li>Absolvição é registrada como informação positiva</li>
            <li>Somente processos confirmados em fontes oficiais são publicados</li>
            <li>Toda publicação passa por revisão humana</li>
          </ul>
        </Section>

        <Section title="Indicadores e Ranking">
          <p>O Ranking IFB está em desenvolvimento. Quando publicado, utilizará exclusivamente indicadores baseados em dados verificáveis:</p>
          <ul className="list-disc pl-5 space-y-1 mt-2">
            <li>Atividade legislativa quantificável</li>
            <li>Transparência e prestação de contas</li>
            <li>Cumprimento de promessas</li>
            <li>Regularidade judicial</li>
            <li>Uso da cota parlamentar</li>
          </ul>
          <p className="mt-2">Nenhum ranking será publicado antes da validação completa da metodologia e dos pesos utilizados.</p>
        </Section>

        <Section title="Diferença entre Dado, Cálculo, Classificação e Análise">
          <div className="overflow-x-auto mt-2">
            <table className="w-full text-[13px] border border-[#E5E7EB] rounded-[8px] overflow-hidden">
              <thead className="bg-[#F6F7F9]">
                <tr>
                  <th className="text-left px-4 py-2 font-semibold text-[#111]">Tipo</th>
                  <th className="text-left px-4 py-2 font-semibold text-[#111]">Definição</th>
                  <th className="text-left px-4 py-2 font-semibold text-[#111]">Exemplo</th>
                </tr>
              </thead>
              <tbody className="text-[#374151]">
                <tr className="border-t border-[#E9ECEF]"><td className="px-4 py-2 font-medium">Dado</td><td className="px-4 py-2">Informação bruta de fonte oficial</td><td className="px-4 py-2">Deputado votou &quot;Sim&quot; no PL 1234/2026</td></tr>
                <tr className="border-t border-[#E9ECEF]"><td className="px-4 py-2 font-medium">Cálculo</td><td className="px-4 py-2">Operação aritmética sobre dados</td><td className="px-4 py-2">Total de gastos CEAP no ano: R$ 150.000</td></tr>
                <tr className="border-t border-[#E9ECEF]"><td className="px-4 py-2 font-medium">Classificação</td><td className="px-4 py-2">Categorização automática por IA</td><td className="px-4 py-2">Notícia classificada como &quot;legislativo&quot;</td></tr>
                <tr className="border-t border-[#E9ECEF]"><td className="px-4 py-2 font-medium">Análise humana</td><td className="px-4 py-2">Decisão editorial após revisão</td><td className="px-4 py-2">Aprovação de notícia sensível para publicação</td></tr>
              </tbody>
            </table>
          </div>
        </Section>

        <Section title="Contestação">
          <p>Qualquer cidadão pode contestar uma classificação, indicador ou informação publicada. O processo:</p>
          <ol className="list-decimal pl-5 space-y-1 mt-2">
            <li>Usuário registra contestação com justificativa</li>
            <li>Equipe de revisão analisa a contestação</li>
            <li>Decisão é registrada com auditoria completa</li>
            <li>Usuário é notificado do resultado</li>
          </ol>
        </Section>

        <Section title="Atualizações">
          <p>Esta metodologia é um documento vivo e será atualizada conforme o sistema evolui. Todas as versões anteriores serão mantidas para auditoria.</p>
          <p className="text-[12px] text-[#9CA3AF] mt-3">Última atualização: Agosto 2026</p>
        </Section>
      </div>
    </main>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="bg-white border border-[#E5E7EB] rounded-[16px] p-6">
      <h2 className="text-[17px] font-bold text-[#111] mb-3">{title}</h2>
      <div className="text-[13px] text-[#374151] leading-relaxed">{children}</div>
    </section>
  );
}
