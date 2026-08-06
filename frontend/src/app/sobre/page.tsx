import Link from "next/link";

export default function SobrePage() {
  return (
    <main className="min-h-screen bg-white">
      {/* Header */}
      <div className="border-b border-ifb-gray-medium">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <Link href="/" className="text-sm text-gray-500 hover:text-ifb-black">← Início</Link>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-12">
        <h1 className="text-3xl font-bold text-ifb-black">Sobre o IFB</h1>

        <section className="mt-8 space-y-6 text-gray-700 leading-relaxed">
          <div>
            <h2 className="text-xl font-semibold text-ifb-black mb-3">Missão</h2>
            <p>
              Transformar dados públicos complexos em informações claras, rastreáveis e
              compreensíveis para qualquer cidadão. O Instituto Fiscaliza Brasil reúne,
              processa, analisa e apresenta informações sobre políticos e agentes públicos
              brasileiros de forma apartidária.
            </p>
          </div>

          <div>
            <h2 className="text-xl font-semibold text-ifb-black mb-3">Princípios</h2>
            <ul className="space-y-2 list-disc list-inside">
              <li><strong>Apartidário</strong> — Não expressa opinião política nem favorece partidos.</li>
              <li><strong>Rastreável</strong> — Toda informação possui fonte, data e método de obtenção.</li>
              <li><strong>Transparente</strong> — Metodologias são públicas e explicáveis.</li>
              <li><strong>Responsável</strong> — Nunca trata investigação como condenação.</li>
              <li><strong>Auditável</strong> — Todas as alterações são registradas com histórico.</li>
              <li><strong>Seguro</strong> — Proteção de dados conforme LGPD.</li>
            </ul>
          </div>

          <div>
            <h2 className="text-xl font-semibold text-ifb-black mb-3">O que fazemos</h2>
            <p>O IFB coleta dados de fontes oficiais públicas e os apresenta de forma acessível:</p>
            <ul className="mt-3 space-y-2 list-disc list-inside">
              <li>Histórico eleitoral e patrimonial</li>
              <li>Atividade parlamentar (projetos, votações, presença)</li>
              <li>Gastos públicos e cota parlamentar</li>
              <li>Promessas de campanha com acompanhamento</li>
              <li>Processos judiciais com contexto (papel, situação, recurso)</li>
              <li>Notícias classificadas com IA e revisão humana</li>
              <li>Indicadores por dimensão com metodologia pública</li>
            </ul>
          </div>

          <div>
            <h2 className="text-xl font-semibold text-ifb-black mb-3">O que NÃO fazemos</h2>
            <ul className="space-y-2 list-disc list-inside text-gray-600">
              <li>Não declaramos culpa pela existência de processo judicial.</li>
              <li>Não criamos ranking geral com nota única arbitrária.</li>
              <li>Não apresentamos opinião como fato.</li>
              <li>Não publicamos classificação automática sem informar uso de IA.</li>
              <li>Não recomendamos voto.</li>
            </ul>
          </div>

          <div>
            <h2 className="text-xl font-semibold text-ifb-black mb-3">Fontes de dados</h2>
            <p>Todas as informações são obtidas de fontes oficiais públicas:</p>
            <ul className="mt-3 space-y-1 text-sm text-gray-600">
              <li>• Tribunal Superior Eleitoral (TSE)</li>
              <li>• Câmara dos Deputados — Dados Abertos</li>
              <li>• Senado Federal — Dados Abertos</li>
              <li>• Portal da Transparência</li>
              <li>• Tribunais — DataJud / CNJ</li>
              <li>• Fontes jornalísticas públicas</li>
            </ul>
          </div>

          <div>
            <h2 className="text-xl font-semibold text-ifb-black mb-3">Uso de Inteligência Artificial</h2>
            <p>
              A IA é utilizada como ferramenta auxiliar para classificar notícias e sugerir
              extração de promessas. Toda análise automatizada é informada ao usuário e
              passa por revisão humana em casos sensíveis. A IA nunca decide culpa,
              publica sozinha ou substitui fonte oficial.
            </p>
          </div>

          <div>
            <h2 className="text-xl font-semibold text-ifb-black mb-3">Financiamento</h2>
            <p>
              O IFB é financiado por doações de pessoas físicas e jurídicas.
              Toda receita e despesa é publicada na página de{" "}
              <Link href="/transparencia" className="text-ifb-black font-medium underline">transparência</Link>.
              Nenhum doador exerce influência sobre o conteúdo editorial.
            </p>
          </div>

          <div>
            <h2 className="text-xl font-semibold text-ifb-black mb-3">Contestação e correção</h2>
            <p>
              Qualquer cidadão pode contestar informações publicadas. Contestações são
              analisadas pela equipe e podem resultar em correção, atualização ou
              manutenção com justificativa. O histórico de alterações é preservado.
            </p>
          </div>
        </section>

        <div className="mt-12 pt-8 border-t border-ifb-gray-medium">
          <p className="text-sm text-gray-500">
            Instituto Fiscaliza Brasil · CNPJ em processo de registro ·{" "}
            <Link href="/contato" className="underline">Contato</Link> ·{" "}
            <Link href="/termos" className="underline">Termos de uso</Link> ·{" "}
            <Link href="/privacidade" className="underline">Política de privacidade</Link>
          </p>
        </div>
      </div>
    </main>
  );
}
