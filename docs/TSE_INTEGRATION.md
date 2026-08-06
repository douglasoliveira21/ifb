# Integração TSE — Instituto Fiscaliza Brasil

## Fonte Oficial

- **Portal de Dados Abertos do TSE**: https://dadosabertos.tse.jus.br
- **Tipo**: Dados abertos públicos em formato CSV
- **Licença**: Dados públicos (Lei de Acesso à Informação)

## Datasets Suportados

| Dataset | Descrição | Formato | Periodicidade |
|---------|-----------|---------|---------------|
| Candidatos | Candidaturas registradas | CSV (latin-1, ;) | Por eleição |
| Bens declarados | Patrimônio | CSV | Por eleição |
| Receitas | Receitas de campanha | CSV | Por eleição |
| Despesas | Despesas de campanha | CSV | Por eleição |
| Prestação de contas | Status | CSV | Por eleição |
| Resultados | Votação | CSV | Por eleição |
| Propostas | Planos de governo | PDF | Por eleição |

## Fluxo de Importação

```
1. Descoberta  → Identifica datasets disponíveis
2. Download    → Baixa arquivo via streaming (checksum)
3. Validação   → Verifica encoding, layout, colunas
4. Parsing     → Lê CSV em streaming, normaliza campos
5. Mapeamento  → Converte para formato interno
6. Persistência → Salva no banco (upsert idempotente)
7. Conciliação → Vincula candidatos a políticos existentes
8. Agregação   → Calcula totais e métricas
```

## Encoding e Layout

- Encoding: `latin-1` (ISO-8859-1) — padrão dos arquivos TSE
- Separador: `;` (ponto e vírgula)
- Aspas: `"` (aspas duplas)
- Decimais: vírgula como separador (ex: `1.234,56`)
- Datas: `dd/mm/yyyy`
- Valores nulos: `#NULO#` ou `#NE#`

## Conciliação de Candidatos

Ordem de prioridade:
1. CPF hash (match exato)
2. Sequência TSE (se já importado)
3. Nome + nascimento + UF (match forte)
4. Nome de urna + partido + cargo + eleição (match fraco → revisão manual)

Quando não há match seguro, o candidato permanece como `reconciliation_status=pending`.

## Idempotência

A reimportação do mesmo arquivo NÃO cria duplicatas:
- Constraint única: `(tse_candidate_id, election_id)`
- Checksum do arquivo registrado
- Verificação antes de reprocessar

## Segurança

- CPF: Armazenado apenas como SHA-256 hash
- Documentos de doadores: Hash SHA-256
- Dados pessoais não essenciais: Não expostos na API pública
- Rate limiting: Respeitado na consulta ao portal

## Observabilidade

Métricas exportadas:
- `ifb_tse_download_total`
- `ifb_tse_import_rows_total`
- `ifb_tse_import_errors_total`
- `ifb_tse_reconciliation_pending`

## Limitações Conhecidas

- Layouts de CSV podem variar entre anos eleitorais
- Dados de 2026 podem estar incompletos ou indisponíveis
- Arquivos grandes (>100MB) requerem streaming
- Reconciliação automática tem falsos negativos
