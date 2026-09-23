# Auto-lembrete — acessos pendentes (Khabs)

**Quando:** intake salvo com `complete=true` mas CMS/GA4/GSC vazios · ou AlertBot >5–10 dias úteis  
**Cadência:** D+3, D+7, D+10 (escala Leandro no D+10)  
**Local:** `crm-lite/outbound/` apenas

---

## Variáveis

- `{{contact_first}}` · `{{company}}`
- `{{missing_list}}` — bullets dos sistemas
- `{{invite_hint}}` — “convidar e-mail do projeto, nunca senha em texto aberto”
- `{{token}}` · `{{day_n}}`

## Assunto

`Khabs — acessos pendentes D+{{day_n}} ({{company}})`

## Corpo

```
Olá {{contact_first}},

Para o sprint 30 dias de {{company}} seguir no ritmo, ainda precisamos de:

{{missing_list}}

Como enviar: {{invite_hint}}.

Atualize o status no intake/portal: portal.html?token={{token}}

Se algum sistema for bloqueado pelo jurídico, responda este fio com o plano B.

— OnboardBot · Khabs
```
