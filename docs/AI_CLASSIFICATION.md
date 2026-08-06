# Classificação por Inteligência Artificial — IFB

## Visão Geral

A IA é utilizada para:
1. Classificar impacto de notícias sobre políticos
2. Auxiliar na extração de promessas de campanha
3. Confirmar identidade de políticos em notícias (homônimos)
4. Identificar assunto principal

## IMPORTANTE

- A IA **nunca decide sozinha** se algo será publicado
- Toda análise com confiança abaixo de 80% requer revisão humana
- Notícias sensíveis (judicial, criminal) **sempre** requerem revisão
- O uso de IA é **sempre informado** ao usuário final

## Formato de Resposta

```json
{
  "politico_confirmado": true,
  "confianca_identidade": 0.97,
  "assunto_principal": true,
  "categoria": "judicial",
  "impacto": "negativo",
  "intensidade": -4,
  "confianca_impacto": 0.91,
  "resumo": "A denúncia foi aceita e o político tornou-se réu.",
  "justificativa": "Classificado como negativo por aceitação formal de denúncia.",
  "evidencias": ["A Justiça aceitou a denúncia..."],
  "precisa_revisao_humana": true
}
```

## Categorias

- `legislativo` — Atividade parlamentar
- `judicial` — Processos, investigações, condenações
- `eleitoral` — Eleições, candidatura, campanha
- `administrativo` — Gestão, nomeações
- `financeiro` — Gastos, patrimônio, doações
- `social` — Ações sociais, comunidade
- `politico` — Articulações, alianças, posicionamentos
- `pessoal` — Vida pessoal (quando relevante publicamente)

## Escala de Intensidade

| Valor | Significado |
|-------|-------------|
| -5 | Extremamente negativo (condenação criminal) |
| -4 | Muito negativo (denúncia aceita) |
| -3 | Negativo (investigação) |
| -2 | Moderadamente negativo |
| -1 | Levemente negativo |
| 0 | Neutro |
| +1 | Levemente positivo |
| +2 | Moderadamente positivo |
| +3 | Positivo (projeto aprovado) |
| +4 | Muito positivo |
| +5 | Extremamente positivo |

## Regras de Segurança

1. Nunca inventar fatos
2. Nunca concluir culpa
3. Nunca analisar apenas pelo título
4. Nunca usar linguagem ofensiva
5. Nunca criar score sem evidência
6. Nunca publicar análise com confiança < 60%
7. Sempre armazenar prompt, modelo, versão e resultado
8. Permitir reprocessamento
9. Manter histórico de mudanças

## Rastreabilidade

Cada análise armazena:
- `prompt_template_version` — Versão do prompt
- `model` — Modelo utilizado (ex: gpt-4o-mini)
- `model_version` — Versão do modelo
- `input_hash` — Hash do conteúdo de entrada
- `output_raw` — Resposta bruta da IA
- `output_parsed` — Resposta estruturada
- `tokens_used` — Tokens consumidos
- `cost_estimate` — Custo estimado
- `processing_time_ms` — Tempo de processamento
- `created_at` — Data/hora da análise

## Revisão Humana

Casos que OBRIGATORIAMENTE requerem revisão:
- Confiança de identidade < 85%
- Confiança de impacto < 80%
- Categoria `judicial` (qualquer confiança)
- Intensidade >= |4|
- Primeiro registro de um político novo
- Contradição com classificações anteriores
