import Link from "next/link";

export default function TermosPage() {
  return (
    <main className="min-h-screen bg-white">
      <div className="border-b border-ifb-gray-medium">
        <div className="max-w-3xl mx-auto px-4 py-6">
          <Link href="/" className="text-sm text-gray-500 hover:text-ifb-black">← Início</Link>
        </div>
      </div>
      <div className="max-w-3xl mx-auto px-4 py-12 prose prose-gray">
        <h1 className="text-3xl font-bold text-ifb-black">Termos de Uso</h1>
        <p className="text-sm text-gray-500">Última atualização: agosto de 2026</p>

        <h2>1. Finalidade</h2>
        <p>O Instituto Fiscaliza Brasil (IFB) é uma plataforma informativa que reúne, processa e apresenta dados públicos sobre políticos e agentes públicos brasileiros. A finalidade é exclusivamente informativa e de interesse público.</p>

        <h2>2. Fontes de dados</h2>
        <p>As informações apresentadas são obtidas de fontes oficiais públicas, incluindo o TSE, Câmara dos Deputados, Senado Federal, Portal da Transparência, tribunais e fontes jornalísticas. Toda informação apresentada possui referência à fonte original.</p>

        <h2>3. Uso de inteligência artificial</h2>
        <p>O IFB utiliza inteligência artificial como ferramenta auxiliar para classificação de notícias e sugestão de extração de promessas. Toda análise automatizada é identificada como tal e pode passar por revisão humana. A IA não é utilizada para determinar culpa, inocência ou mérito de qualquer pessoa.</p>

        <h2>4. Possibilidade de erros</h2>
        <p>Apesar dos esforços de verificação, os dados podem conter imprecisões, atrasos de atualização ou informações incompletas. O IFB não garante a exatidão absoluta das informações e mantém processo de contestação e correção disponível ao público.</p>

        <h2>5. Metodologia</h2>
        <p>Os indicadores, classificações e avaliações seguem metodologias documentadas publicamente. Pesos, fórmulas e critérios são acessíveis na página de metodologia. Alterações metodológicas são versionadas.</p>

        <h2>6. Proibição de uso abusivo</h2>
        <p>É proibido utilizar o IFB para disseminar informações fora de contexto, criar conteúdo difamatório, realizar ataques automatizados, coletar dados em massa para fins comerciais não autorizados ou violar a privacidade de terceiros.</p>

        <h2>7. Propriedade intelectual</h2>
        <p>O código, design, metodologias e textos originais do IFB são de propriedade do instituto. Os dados públicos apresentados permanecem de domínio público conforme sua origem.</p>

        <h2>8. Links externos</h2>
        <p>O IFB pode conter links para fontes externas. Não nos responsabilizamos pelo conteúdo de sites de terceiros.</p>

        <h2>9. Contestação e correção</h2>
        <p>Qualquer cidadão pode contestar informações publicadas. Contestações são analisadas pela equipe editorial e podem resultar em correção, atualização ou manutenção com justificativa documentada.</p>

        <h2>10. Limitação de responsabilidade</h2>
        <p>O IFB não se responsabiliza por decisões tomadas com base nas informações apresentadas. A plataforma não substitui análise profissional, jurídica ou eleitoral.</p>

        <h2>11. Alterações</h2>
        <p>Estes termos podem ser atualizados. Alterações significativas serão comunicadas. A versão vigente estará sempre disponível nesta página.</p>

        <h2>12. Contato</h2>
        <p>Para dúvidas sobre estes termos:<br/>
        E-mail: <span className="text-gray-400">[contato@institutofiscalizabrasil.org — a definir]</span><br/>
        CNPJ: <span className="text-gray-400">[em processo de registro]</span></p>
      </div>
    </main>
  );
}
