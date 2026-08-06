import Link from "next/link";

export default function PrivacidadePage() {
  return (
    <main className="min-h-screen bg-white">
      <div className="border-b border-ifb-gray-medium">
        <div className="max-w-3xl mx-auto px-4 py-6">
          <Link href="/" className="text-sm text-gray-500 hover:text-ifb-black">← Início</Link>
        </div>
      </div>
      <div className="max-w-3xl mx-auto px-4 py-12 prose prose-gray">
        <h1 className="text-3xl font-bold text-ifb-black">Política de Privacidade</h1>
        <p className="text-sm text-gray-500">Última atualização: agosto de 2026</p>

        <h2>1. Dados coletados</h2>
        <p>O IFB coleta apenas os dados necessários para o funcionamento da plataforma:</p>
        <ul>
          <li><strong>Cadastro:</strong> nome, e-mail e senha (armazenada como hash irreversível).</li>
          <li><strong>Autenticação:</strong> sessão, IP, user-agent (para segurança).</li>
          <li><strong>Doações:</strong> nome, e-mail e dados necessários para processamento pelo gateway de pagamento.</li>
          <li><strong>Contestações:</strong> conteúdo da contestação vinculado ao usuário.</li>
          <li><strong>Navegação:</strong> logs técnicos para segurança e performance.</li>
        </ul>

        <h2>2. Cookies</h2>
        <p>Utilizamos cookies HttpOnly para autenticação de sessão. Não utilizamos cookies de rastreamento publicitário. Cookies de sessão são removidos ao fazer logout.</p>

        <h2>3. Segurança</h2>
        <p>Senhas são armazenadas com Argon2id. Tokens de acesso possuem expiração curta. Comunicação é protegida por HTTPS. Dados sensíveis são criptografados em repouso quando necessário.</p>

        <h2>4. Doações</h2>
        <p>O IFB não armazena dados completos de cartão de crédito. O processamento de pagamentos é realizado por gateway certificado (PCI-DSS). Armazenamos apenas identificadores de transação para conciliação e recibos.</p>

        <h2>5. Retenção</h2>
        <p>Dados de conta são mantidos enquanto a conta estiver ativa. Dados de auditoria são mantidos conforme obrigações legais. Dados de doação são mantidos para prestação de contas.</p>

        <h2>6. Compartilhamento</h2>
        <p>Não vendemos dados pessoais. Compartilhamos dados apenas com:</p>
        <ul>
          <li>Gateway de pagamento (para processar doações)</li>
          <li>Provedor de e-mail (para comunicações transacionais)</li>
          <li>Autoridades (quando exigido por lei)</li>
        </ul>

        <h2>7. Direitos do titular (LGPD)</h2>
        <p>Você tem direito a:</p>
        <ul>
          <li>Acessar seus dados pessoais</li>
          <li>Corrigir dados incorretos</li>
          <li>Solicitar exclusão da conta</li>
          <li>Exportar seus dados</li>
          <li>Revogar consentimento</li>
          <li>Solicitar informação sobre compartilhamento</li>
        </ul>

        <h2>8. Exclusão de conta</h2>
        <p>Você pode solicitar exclusão da conta a qualquer momento. Dados vinculados a obrigações legais (como registros de doação) serão mantidos pelo prazo exigido e depois anonimizados.</p>

        <h2>9. Dados públicos de agentes políticos</h2>
        <p>As informações sobre políticos e agentes públicos apresentadas no IFB são dados públicos obtidos de fontes oficiais. O tratamento desses dados tem base legal no interesse público e no exercício da liberdade de expressão e informação (Art. 7º, IX da LGPD).</p>

        <h2>10. Base legal</h2>
        <p>O tratamento de dados pessoais no IFB tem como bases legais:</p>
        <ul>
          <li>Consentimento (cadastro voluntário)</li>
          <li>Execução de contrato (doações)</li>
          <li>Interesse legítimo (segurança, auditoria)</li>
          <li>Cumprimento de obrigação legal (fiscal)</li>
          <li>Exercício regular de direitos (informação pública)</li>
        </ul>

        <h2>11. Alterações</h2>
        <p>Esta política pode ser atualizada. Alterações significativas serão comunicadas aos usuários cadastrados.</p>

        <h2>12. Contato — Encarregado (DPO)</h2>
        <p>Para exercer seus direitos ou esclarecer dúvidas sobre privacidade:<br/>
        E-mail: <span className="text-gray-400">[privacidade@institutofiscalizabrasil.org — a definir]</span><br/>
        Encarregado: <span className="text-gray-400">[a ser designado]</span><br/>
        CNPJ: <span className="text-gray-400">[em processo de registro]</span><br/>
        Endereço: <span className="text-gray-400">[a definir]</span></p>
      </div>
    </main>
  );
}
