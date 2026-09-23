# Auto-resposta — lead inbound (Khabs)

**Canal:** e-mail (rascunho local → `crm-lite/outbound/`)  
**Quando:** `POST /api/leads` · estágio `lead` → `diagnose_auto`  
**Idioma:** pt-BR  
**De:** contato@getkhabs.com  
**Enviar de verdade:** só após revisão Ops / autoresponder aprovado (local = draft only)

---

## Variáveis

- `{{contact_first}}` — primeiro nome
- `{{company}}`
- `{{package_interest}}` — starter | growth | authority | diagnóstico
- `{{lead_id}}`
- `{{token}}`
- `{{portal_url}}` — ex. `http://127.0.0.1:8787/portal.html?token={{token}}`
- `{{onboarding_url}}` — `.../onboarding.html?lead={{lead_id}}&token={{token}}`

---

## Assunto

`Khabs — recebemos seu diagnóstico ({{company}})`

## Corpo

```
Olá {{contact_first}},

Recebemos seu pedido de diagnóstico GEO para {{company}}. Obrigado — daqui em diante a jornada é automatizada.

Próximos passos (SLA):
1. Agora — lead no CRM · estágio diagnose_auto · prep de auditoria enfileirada.
2. Em até 1 dia útil — recomendação de pacote{{#package_interest}} (interesse: {{package_interest}}){{/package_interest}} + rascunho de proposta.
3. Você pode adiantar o intake (Parte A) quando quiser: {{onboarding_url}}

Acompanhe o status: {{portal_url}}

Gates humanos só entram em: exceção de preço, claims regulados, publish no CMS (se sem acesso), assinatura de contrato.

Abraços,
Equipe Khabs
contato@getkhabs.com
Toda marca é uma estrela na resposta.
```
