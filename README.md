# Khabs — Site estático (go-live)

Pasta canônica para publicar o marketing site da **Khabs**.

- Tagline: **Toda marca é uma estrela na resposta.** / *Every brand is a star in the answer.*
- Domínio canônico SEO: **https://getkhabs.com**
- Contato: **contato@getkhabs.com** (WhatsApp: a definir)
- Idioma: **pt-BR**
- Palette: Ink `#0B1220` · Surface `#F7F5F1` · Accent `#2F6BFF` / `#2557d6` · Cited `#00A896` · Inaccurate `#E85D04`

## Conteúdo desta pasta

| Arquivo | Descrição |
|---------|-----------|
| `index.html` | Landing (pacotes oficiais + FAQ + JSON-LD) |
| `servicos.html` | Serviços |
| `metodologia.html` | Metodologia GEO |
| `contato.html` | Diagnóstico + formulário (FormSubmit) |
| `privacidade.html` | Política de Privacidade (LGPD) |
| `termos.html` | Termos de Uso |
| `config.js` | `window.KHABS` (e-mail, WhatsApp, brand) |
| `llms.txt` | Contexto para LLMs |
| `robots.txt` | Crawlers de busca + IA |
| `sitemap.xml` | Sitemap |
| `favicon.svg` | Ícone |
| `PRODUCTION-FORM.md` | Ativação FormSubmit / Formspree |

## Deploy — Cloudflare Pages

1. Conecte o repositório **ou** faça upload direto desta pasta.
2. **Build command:** deixe vazio (site 100% estático).
3. **Build output directory:** `/` (raiz desta pasta) — ou o path do repo onde estes arquivos vivem.
4. Domínio custom: `getkhabs.com` (+ `www` → redirect).
5. Após o primeiro deploy, envie um lead de teste e **confirme o e-mail** no FormSubmit (`contato@getkhabs.com`).

```bash
# Preview local
cd /workspace/agencia-ai-pages && python3 -m http.server 8080
# Abrir http://localhost:8080
```

## Deploy — Netlify

1. New site → deploy desta pasta (drag-and-drop ou Git).
2. **Publish directory:** pasta com estes HTML (sem build).
3. Domain management → `getkhabs.com`.
4. Mesmo checklist FormSubmit em `PRODUCTION-FORM.md`.

`netlify.toml` opcional:

```toml
[build]
  publish = "."
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
  force = false
```

(Não force SPA redirect se quiser URLs `.html` limpas; os arquivos já são páginas reais.)

## Preços oficiais (não alterar sem playbook)

| Pacote | Setup | Mensal |
|--------|-------|--------|
| Starter | R$ 4.900 | R$ 4.900 |
| Growth | R$ 8.900 | R$ 9.900 |
| Authority | R$ 14.900 | R$ 19.900 |

## Stack

HTML + Tailwind CDN · Inter + JetBrains Mono · FormSubmit AJAX + mailto fallback.

Espelho HTML também em `/workspace/agencia-ai/site/*.html`. App Next.js em `/workspace/agencia-ai/site/src/` (paralelo; go-live prioritário é **esta** pasta estática).


## Stack local (CX automatizado)

```bash
cd /workspace/agencia-ai-pages
./start-local.sh
# http://127.0.0.1:8787/  — site + API no mesmo processo
```

Jornada: `qualificar.html` → `contato.html` → `obrigado.html` → `onboarding.html` → `portal.html` · Ops: `ops.html`  
Doc: `/workspace/agencia-ai/10-jornada-cliente-automatizada.md`
