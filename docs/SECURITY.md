# Segurança — IFB

## Autenticação

- **Senhas**: Argon2id (resistente a GPU attacks)
- **JWT**: Tokens de curta duração (15 minutos padrão)
- **Refresh Token**: Rotação a cada uso, armazenado em cookie HttpOnly
- **Cookies**: HttpOnly + Secure + SameSite=Lax
- **Verificação de e-mail**: Obrigatória
- **MFA**: Obrigatório para roles admin/superadmin
- **Bloqueio**: Após 5 tentativas falhas, conta bloqueada por 15 minutos
- **Sessões**: Por dispositivo, com possibilidade de revogação individual

## Autorização (RBAC)

- 6 perfis: Visitante, Usuário, Analista, Jornalista, Admin, Superadmin
- Permissões granulares por recurso e ação
- Verificação exclusivamente no backend
- Frontend apenas oculta elementos visuais (não valida)

## API

- **Rate limiting**: Por IP e por usuário
- **CORS**: Restritivo (apenas domínios autorizados)
- **Validação**: Pydantic em todas as entradas
- **Headers de segurança**: X-Content-Type-Options, X-Frame-Options, etc.
- **Payload máximo**: 10MB (uploads), 1MB (JSON)
- **Timeout**: 30s para requisições externas
- **Idempotency Key**: Em operações financeiras

## Dados Sensíveis

- **CPF**: Armazenado apenas como hash (nunca em texto claro)
- **Senhas**: Nunca logadas ou retornadas
- **Tokens**: Nunca em localStorage (apenas cookies HttpOnly)
- **Segredos**: Apenas em variáveis de ambiente
- **Logs**: Sanitizados (sem PII)

## LGPD

- Consentimento explícito para dados pessoais
- Minimização de dados (coletar apenas o necessário)
- Direito de exclusão implementado
- Exportação de dados do usuário
- Política de retenção definida
- Canal de privacidade disponível
- Base legal documentada

## Auditoria

- Todas as alterações em dados sensíveis são logadas
- Campos: quem, quando, o quê, antes, depois, justificativa
- Logs de auditoria são imutáveis (não podem ser editados ou excluídos)
- Acesso administrativo requer justificativa

## Proteções Implementadas

- SQL Injection: SQLAlchemy com queries parametrizadas
- XSS: Sanitização de HTML, Content-Security-Policy
- CSRF: SameSite cookies + token CSRF
- SSRF: Validação de URLs em integrações
- Enumeração de usuários: Respostas genéricas em auth
- Path traversal: Validação de paths em uploads
- Mass assignment: Schemas explícitos por operação
