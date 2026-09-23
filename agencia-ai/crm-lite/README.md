# Khabs — CRM-lite

Planilhas CSV mínimas + **inbox JSON** via API local.  
Substitua por Notion/Airtable/HubSpot quando escalar; a estrutura de colunas permanece.

## Arquivos

| Arquivo / pasta | Uso |
|-----------------|-----|
| `pipeline.csv` | Leads e deals (funil comercial) + coluna `token` |
| `accounts.csv` | Contas / clientes (+ `token`, `slug`, `stage`, `lead_id`) |
| `work-items.csv` | Backlog de entrega GEO |
| `citations.csv` | Amostras do Caçador de Citações |
| `inbox/{id}.json` | Payload completo do lead (API) |
| `accounts/{slug}/intake.json` | Intake self-serve |
| `outbound/{id}.json` | Fila de rascunhos de e-mail (**não envia**) |

## API local

Subir: `cd /workspace/agencia-ai-pages && ./start-local.sh` → `http://127.0.0.1:8787`

- `POST /api/leads` — append `pipeline.csv` + `inbox/{id}.json`
- `POST /api/intake` — `accounts/{slug}/intake.json` + update `accounts.csv`
- `GET /api/status?token=` — estágio + checklist
- `POST /api/advance` — move estágio (Ops / regras)
- `GET /api/leads` — lista inbox + outbound (ops.html)

## Como usar (manual)

1. Abra os CSV no Google Sheets ou Excel (UTF-8).
2. Uma linha = um registro; não apague o header.
3. IDs: prefixos `L-` (lead), `A-` (account), `W-` (work), `C-` (citation), `OUT-` (outbound).
4. `updated_at` em ISO com offset `-03:00` (America/Sao_Paulo).
5. Estágios: `visit → qualify → lead → diagnose_auto → proposal_draft → won → intake_selfserve → kickoff_auto → sprint30 → retain`.
6. Pacotes: `starter` | `growth` | `authority` (preços em `02-oferta-e-precos.md`).

Contato comercial padrão: **contato@getkhabs.com**.
