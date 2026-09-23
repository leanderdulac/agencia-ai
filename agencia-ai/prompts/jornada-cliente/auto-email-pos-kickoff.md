# Auto-e-mail pós-kickoff (Khabs)

**Quando:** estágio `kickoff_auto` (após intake completo ou Ops advance)  
**SLA:** e-mail draft no mesmo dia do kickoff · AuditBot D1–D5  
**Gate humano:** nenhum para este draft; publish CMS permanece com cliente/Leandro se aplicável

---

## Variáveis

- `{{contact_first}}` · `{{company}}` · `{{package}}`
- `{{d0}}` — data oficial de início (America/Sao_Paulo)
- `{{audit_window}}` — ex. D1–D5
- `{{aprovador}}` · `{{sla_aprovacao}}` — 3 dias úteis
- `{{review_date}}` — D28–D30
- `{{pending_access}}` — lista CMS/GA4/GSC pendentes
- `{{token}}`

## Assunto

`Khabs — kickoff e próximos 30 dias ({{company}})`

## Corpo

```
Olá {{contact_first}},

Kickoff registrado para {{company}} (pacote {{package}}). D0: {{d0}}.

Nas próximas {{audit_window}} o AuditBot prepara a baseline de citabilidade.
Aprovador de conteúdo: {{aprovador}} (SLA {{sla_aprovacao}}).
Call/review planejada: {{review_date}}.

Pendências de acesso (se houver):
{{pending_access}}

Portal de status: portal.html?token={{token}}

— Ops Khabs (OnboardBot)
contato@getkhabs.com
```
