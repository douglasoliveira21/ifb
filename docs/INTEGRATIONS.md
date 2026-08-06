# Integrações Externas — IFB

## Arquitetura de Integrações

Cada integração é isolada em um módulo com:
- `client.py` — Cliente HTTP com retries e circuit breaker
- `schemas.py` — Schemas de entrada/saída da API externa
- `mapper.py` — Mapeamento para modelos internos
- `service.py` — Lógica de negócio da integração
- `exceptions.py` — Exceções específicas
- `tests/` — Testes unitários e de integração

## Fontes de Dados

### TSE (Tribunal Superior Eleitoral)
- **URL base**: `https://divulgacandcontas.tse.jus.br/divulga/rest/v1`
- **Dados**: Candidaturas, resultados, prestação de contas
- **Rate limit**: Respeitar headers da API
- **Cache**: 24h para dados eleitorais passados

### Câmara dos Deputados
- **URL base**: `https://dadosabertos.camara.leg.br/api/v2`
- **Dados**: Deputados, proposições, votações, despesas
- **Documentação**: https://dadosabertos.camara.leg.br/swagger/api.html
- **Rate limit**: 50 req/min
- **Cache**: 1h para dados atuais

### Senado Federal
- **URL base**: `https://legis.senado.leg.br/dadosabertos`
- **Dados**: Senadores, matérias, votações, comissões
- **Rate limit**: Não documentado (respeitar 30 req/min)
- **Cache**: 1h para dados atuais

### Portal da Transparência
- **URL base**: `https://api.portaldatransparencia.gov.br/api-de-dados`
- **Dados**: Servidores, gastos, emendas, convênios
- **Autenticação**: Chave de API obrigatória
- **Rate limit**: 30 req/min
- **Cache**: 6h

### CGU (Controladoria-Geral da União)
- **Dados**: CEIS, CEPIM, CNEP, acordos de leniência
- **Cache**: 24h

### TCU (Tribunal de Contas da União)
- **Dados**: Contas públicas, julgamentos
- **Cache**: 24h

### IBGE
- **URL base**: `https://servicodados.ibge.gov.br/api/v1`
- **Dados**: Municípios, estados, dados populacionais
- **Cache**: 7 dias (dados raramente mudam)

### Notícias
- **NewsAPI**: Feed de notícias por palavra-chave
- **GDELT**: Monitoramento global de eventos
- **Google Programmable Search**: Busca customizada
- **RSS**: Feeds de portais jornalísticos

### OpenAI
- **Uso**: Classificação de notícias, extração de promessas
- **Modelo**: gpt-4o-mini (custo-benefício)
- **Cache**: Resultado por hash do conteúdo
- **Logging**: Prompt, modelo, versão e resposta sempre logados

## Padrões de Resiliência

1. **Retry**: 3 tentativas com backoff exponencial
2. **Circuit Breaker**: Abre após 5 falhas consecutivas
3. **Timeout**: 30 segundos por requisição
4. **Cache**: Redis com TTL por fonte
5. **Rate Limiting**: Respeitar limites de cada API
6. **Fallback**: Dados em cache quando API indisponível
