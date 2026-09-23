# Auto — relatório pronto / status (Khabs)

**Quando:** estágio `sprint30` ou `retain` · ReportBot gerou draft  
**Gate humano:** envio ao cliente do relatório formal (amostra) — Leandro ou Ops autorizado  
**Local:** draft em outbound; portal mostra `next_report_date` placeholder até D0

---

## Variáveis

- `{{contact_first}}` · `{{company}}` · `{{package}}`
- `{{period}}` — semana/mês
- `{{citation_share_delta}}` · `{{accuracy}}` · `{{coverage}}`
- `{{top_wins}}` · `{{p0_actions}}`
- `{{report_link}}` — path local ou Drive
- `{{token}}`

## Assunto

`Khabs — relatório {{period}} pronto ({{company}})`

## Corpo

```
Olá {{contact_first}},

O draft do relatório {{period}} de {{company}} ({{package}}) está pronto para revisão.

Destaques:
- Citation share: {{citation_share_delta}}
- Accuracy: {{accuracy}}
- Coverage: {{coverage}}

Wins: {{top_wins}}
P0 sugeridos: {{p0_actions}}

Arquivo: {{report_link}}
Portal: portal.html?token={{token}}

— ReportBot · Khabs
(rascunho local — envio externo após aprovação)
```
