# Roadmap — Instituto Fiscaliza Brasil

## Fases de Desenvolvimento

| Fase | Descrição | Status |
|------|-----------|--------|
| 0 | Planejamento e arquitetura | ✅ Concluída |
| 1 | Fundação técnica | 🔄 Em andamento |
| 2 | Autenticação e RBAC | ⏳ Próxima |
| 3 | Cadastro de políticos | ⏳ Planejada |
| 4 | Integração TSE | ⏳ Planejada |
| 5 | Câmara e Senado | ⏳ Planejada |
| 6 | Notícias e IA | ⏳ Planejada |
| 7 | Promessas de campanha | ⏳ Planejada |
| 8 | Processos judiciais | ⏳ Planejada |
| 9 | Ranking IFB | ⏳ Planejada |
| 10 | Doações | ⏳ Planejada |
| 11 | Transparência institucional | ⏳ Planejada |
| 12 | Produção e monitoramento | ⏳ Planejada |

## Detalhamento

### Fase 2 — Autenticação
- Cadastro com verificação de e-mail
- Login / logout
- Refresh token rotativo
- Recuperação de senha
- RBAC com 6 perfis
- MFA para administradores
- Auditoria de login
- Bloqueio por tentativas

### Fase 3 — Políticos
- CRUD administrativo
- Pesquisa por nome, partido, estado
- Perfil público
- Aliases e nomes de urna
- Fontes e rastreabilidade
- Histórico de alterações

### Fase 4 — TSE
- Importação de candidaturas
- Dados eleitorais
- Patrimônio declarado
- Receitas e despesas de campanha
- Plano de governo

### Fase 5 — Câmara e Senado
- Projetos de lei
- Votações nominais
- Presença em sessões
- Gastos parlamentares (cota)
- Emendas

### Fase 6 — Notícias e IA
- Coleta automatizada de notícias
- Deduplicação
- Confirmação de identidade do político
- Classificação de impacto (IA)
- Fila de revisão humana
- Justificativa e confiança

### Fase 7 — Promessas
- Extração de promessas (IA + humano)
- Cadastro e categorização
- Evidências de cumprimento
- Percentual de execução
- Histórico

### Fase 8 — Processos
- Modelo completo (tribunal, classe, assunto)
- Importação
- Movimentações
- Status jurídicos corretos
- Revisão obrigatória para processos criminais

### Fase 9 — Ranking
- Metodologia pública
- Pesos justificados
- Cálculo transparente
- Histórico de scores
- Explicação individual

### Fase 10 — Doações
- PIX, cartão, boleto
- Recorrência
- Webhooks
- Recibos
- Gateway abstrato

### Fase 11 — Transparência
- Receitas e despesas do IFB
- Documentos institucionais
- Relatórios anuais
- Prestação de contas pública

### Fase 12 — Produção
- EasyPanel configurado
- SSL/HTTPS
- Backup automático
- Monitoramento (Sentry, Prometheus, Grafana)
- Testes de carga
- Revisão de segurança
