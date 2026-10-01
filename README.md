# Refrain — Site estático (produção)

Pasta publicada do marketing site da **Refrain** (agência de GEO/AEO). Fonte do rebrand: `/workspace/agencia-ai/site/`.

- Tagline: **Seja o refrão que a IA repete.** / *Be the refrain AI repeats.*
- Domínio canônico: **https://www.refrain.com.br** (refrain.com.br registrado em 01/10/2026 no registro.br; apex → `www`)
- Contato: **contato@refrain.com.br** — *placeholder até a caixa de e-mail existir* (WhatsApp: a definir)
- Idioma: **pt-BR** · Guia de marca: `/workspace/agencia-ai/marca-refrain.md`
- Paleta: Tinta `#0B1220` · Azul Refrão `#2F6BFF` · Verde Citado `#00A896` · Papel `#F7F5F1` · Impreciso `#E85D04`

## Deploy atual — GitHub Pages

- Repositório: `github.com/leanderdulac/agencia-ai` (branch `main`, raiz) — cada push publica via *pages-build-deployment*.
- URL provisória: https://leanderdulac.github.io/agencia-ai/
- Sem build step (HTML + Tailwind CDN). `.nojekyll` presente.

### Domínio próprio (quando o DNS estiver no registro.br)

1. registro.br → refrain.com.br → DNS → "Editar zona" (servidores do registro.br):
   - `www`  CNAME  `leanderdulac.github.io.`
   - apex (`refrain.com.br`)  A  `185.199.108.153` · `185.199.109.153` · `185.199.110.153` · `185.199.111.153`
   - (opcional IPv6) AAAA  `2606:50c0:8000::153` · `2606:50c0:8001::153` · `2606:50c0:8002::153` · `2606:50c0:8003::153`
2. Depois que o DNS propagar: GitHub → repo → Settings → Pages → Custom domain = `www.refrain.com.br` → Save → marcar **Enforce HTTPS** (isso cria o arquivo `CNAME`).
3. **Não** criar o arquivo `CNAME` antes do DNS: o github.io passaria a redirecionar para um domínio que ainda não resolve.

## Conteúdo

| Arquivo | Descrição |
|---------|-----------|
| `index.html` | Landing (pacotes + FAQ + JSON-LD Organization/WebSite) |
| `servicos.html` · `metodologia.html` · `case-climatewise.html` | Páginas de conteúdo |
| `contato.html` | Formulário → API local (se houver) → FormSubmit (`config.js`) |
| `qualificar.html` | Diagnóstico rápido (client-side) → contato |
| `obrigado.html` · `onboarding.html` · `portal.html` · `ops.html` | Jornada CX — **exigem a API local** (`/api/*`); no Pages ficam sem dados (noindex) |
| `privacidade.html` · `termos.html` | Legal (LGPD) |
| `config.js` | `window.REFRAIN` (e-mail, WhatsApp, provider do form) |
| `assets/refrain-wordmark*.svg` · `favicon.svg` | Marca |
| `llms.txt` · `robots.txt` · `sitemap.xml` | GEO/SEO |

## Formulário em produção

`contato.html` tenta `POST /api/leads` (só existe no stack local) e cai no **FormSubmit** para `contato@refrain.com.br`.
Enquanto a caixa não existir e o FormSubmit não for ativado (o 1º envio dispara um e-mail de ativação para essa caixa), **os leads não chegam** — o usuário vê uma mensagem de erro com o e-mail. Ver `PRODUCTION-FORM.md`.

## Local

```bash
cd /workspace/agencia-ai-pages && python3 -m http.server 8080 --bind 127.0.0.1
```

`start-local.sh` (API CX em :8787) espera `local-api/server.py`, que **não está nesta pasta** — o stack CX local não sobe sem ele.
