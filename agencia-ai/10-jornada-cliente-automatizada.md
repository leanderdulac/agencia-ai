# Khabs — Jornada do cliente automatizada

**Versão:** 1.0 · 23 set 2026 (America/Sao_Paulo)  
**Princípio:** agentes + site automatizam **100%** da jornada.  
**Humano (Leandro) só para:** exceção de preço · aprovação de claims regulados · publish final no CMS do cliente se não houver grant de acesso · assinatura de contrato.

---

## 1. Diagnóstico CX ( lacunas que esta stack fecha )

| Lacuna anterior | Correção |
|-----------------|----------|
| Formulário de contato era beco sem saída (sem auto-qualificação / handoff) | `qualificar.html` → `contato.html` → `POST /api/leads` → CRM + estágio |
| Onboarding era markdown longo só para humanos | `onboarding.html` self-serve (Parte A) + auto-save |
| Cliente sem status self-serve | `portal.html?token=` |
| Ops esperava Leandro em cada passo | `ops.html` + `POST /api/advance` + regras auto |
| Sem lead API local | `local-api/server.py` em `:8787` |
| Mensagem de sucesso passiva | `obrigado.html` com timeline de bots + CTA intake |

---

## 2. Estágios (fonte de verdade)

```
visit → qualify → lead → diagnose_auto → proposal_draft → won
  → intake_selfserve → kickoff_auto → sprint30 → retain
```

| Estágio | Quem move | SLA | Auto vs gate |
|---------|-----------|-----|--------------|
| `visit` | Site | — | Auto |
| `qualify` | Wizard Diagnóstico | &lt; 2 min | Auto |
| `lead` | POST `/api/leads` | imediato | Auto + draft e-mail |
| `diagnose_auto` | API (auto após lead) | ≤ 1 dia útil p/ pacote | Auto |
| `proposal_draft` | ProposalBot / Ops advance | ≤ 1 dia útil | Auto; **gate** se preço fora da tabela |
| `won` | Contrato | conforme comercial | **Gate humano** (assinatura) |
| `intake_selfserve` | Cliente em `onboarding.html` | ≤ 5 dias úteis | Auto; Ops só escala |
| `kickoff_auto` | Intake completo ou Ops | ≤ 7 dias pós-assinatura | Auto + draft pós-kickoff |
| `sprint30` | OnboardBot | D0–D30 | Auto produção; gates de publish/claims |
| `retain` | Ops + MeasureBot | contínuo | Auto relatórios; gate envio formal |

---

## 3. Como rodar o stack local

```bash
cd /workspace/agencia-ai-pages
./start-local.sh
# → http://127.0.0.1:8787/  (site + API no mesmo processo)
```

URLs úteis:

- Diagnóstico: `/qualificar.html`
- Contato: `/contato.html`
- Obrigado: `/obrigado.html?id=&token=`
- Intake: `/onboarding.html?lead=&token=`
- Portal: `/portal.html?token=`
- Ops: `/ops.html` (banner **somente local**)
- Health: `/api/health`

**Preferência:** um processo em **8787** serve estáticos + API.  
Alternativa: estático em 8080 + apontar `config.js` `apiBase` para `http://127.0.0.1:8787` — não necessário se usar `start-local.sh`.

### API

| Método | Path | Efeito |
|--------|------|--------|
| POST | `/api/leads` | CSV `pipeline.csv` + `inbox/{id}.json` + outbound draft + advance `diagnose_auto` |
| POST | `/api/intake` | `accounts/{slug}/intake.json` + `accounts.csv` |
| GET | `/api/status?token=` | estágio + checklist + pendências |
| POST | `/api/advance` | move estágio · enfileira drafts |
| GET | `/api/leads` | inbox + outbound (Ops) |

CORS: apenas `localhost` / `127.0.0.1`.  
E-mail real: **nunca** — só `crm-lite/outbound/*.json`.

Contato canônico: **contato@getkhabs.com**.

---

## 4. Templates de automação

Pasta: `prompts/jornada-cliente/`

- `auto-resposta-lead.md`
- `auto-proposta-rascunho.md`
- `auto-email-pos-kickoff.md`
- `auto-lembrete-acessos.md`
- `auto-relatorio-pronto.md`

---

## 5. Preços oficiais (inalterados)

Starter R$ 4.900 + setup 4.900 · Growth 9.900 + 8.900 · Authority 19.900 + 14.900.

---

## 6. Fluxo feliz (demo)

1. Abrir `/qualificar.html` → responder wizard → CTA contato com query params.  
2. Enviar `/contato.html` → redirect `/obrigado.html?id=&token=`.  
3. Clicar intake → `/onboarding.html` → salvar / concluir.  
4. `/portal.html?token=` mostra progresso.  
5. `/ops.html` lista o lead · one-click advance · copiar draft.
