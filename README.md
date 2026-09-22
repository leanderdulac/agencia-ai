# Agência AI — Site

Site de marketing (Next.js App Router + TypeScript + Tailwind) da **Agência AI**, agência brasileira de GEO (Generative Engine Optimization), 100% operada por agentes de IA.

Idioma: **pt-BR**.

## Pré-requisitos

- Node.js 20+ (recomendado)
- npm

## Como rodar localmente

```bash
cd /workspace/agencia-ai/site
npm install
npm run dev
```

Abra [http://localhost:3000](http://localhost:3000).

## Build de produção

```bash
npm run build
npm start
```

## Rotas

| Rota | Descrição |
|------|-----------|
| `/` | Landing com todas as seções |
| `/servicos` | Pacotes e comparativo |
| `/contato` | Diagnóstico GEO + formulário |
| `/api/contato` | Stub POST do formulário |
| `/llms.txt` | Contexto para LLMs |
| `/robots.txt` | Permite crawlers de IA |

## Pacotes (copy do site)

- **Starter** — R$ 3.900/mês
- **Growth** — R$ 7.900/mês
- **Authority** — R$ 18.900/mês

## Stack

- Next.js (App Router)
- TypeScript
- Tailwind CSS v4
- JSON-LD Organization + Service
- Open Graph em pt-BR

## Formulário de contato

Cliente mostra sucesso após `POST /api/contato`. Em falha, abre `mailto:contato@agencia.ai` como fallback.
