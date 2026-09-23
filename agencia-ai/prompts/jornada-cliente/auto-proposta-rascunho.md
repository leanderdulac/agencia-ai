# Auto-proposta — rascunho (Khabs)

**Quando:** estágio `proposal_draft` (QualifyBot / ProposalBot)  
**Base:** `06-proposta-modelo.md` + preços oficiais `02-oferta-e-precos.md`  
**Local:** rascunho em `crm-lite/outbound/` — **não** altera preços oficiais  
**Gate humano:** exceção de preço (±15%) ou Authority custom → Leandro

---

## Variáveis

- `{{company}}` · `{{contact_name}}` · `{{email}}`
- `{{package}}` — starter | growth | authority
- `{{setup_brl}}` · `{{mrr_brl}}`
- `{{engines}}` · `{{prompt_count}}`
- `{{score_qualify}}` · `{{diagnosis_summary}}`
- `{{token}}` · `{{proposal_id}}`

## Preços oficiais (não inventar)

| Pacote | Setup | Mensal |
|--------|-------|--------|
| Starter | 4900 | 4900 |
| Growth | 8900 | 9900 |
| Authority | 14900 | 19900 |

## Assunto

`Khabs — rascunho de proposta GEO ({{company}} · {{package}})`

## Corpo (esqueleto)

```
Olá {{contact_name}},

Segue o rascunho de proposta Khabs para {{company}}, com base no diagnóstico automático.

Pacote recomendado: {{package}}
Setup: R$ {{setup_brl}}
Retainer: R$ {{mrr_brl}}/mês
Motores / prompts: {{engines}} · {{prompt_count}}

Resumo do diagnóstico:
{{diagnosis_summary}}

Entregáveis e KPIs 90 dias seguem o playbook oficial do pacote.
Próximo passo automático: revisão interna → envio formal (se preço de tabela).
Portal: portal.html?token={{token}}

— ProposalBot · Khabs
(rascunho — aguarda gate se houver exceção de preço)
```
