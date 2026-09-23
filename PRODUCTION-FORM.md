# Formulário de contato — produção

O site estático em `/workspace/agencia-ai-pages/` envia leads via **FormSubmit AJAX** para o e-mail em `config.js` (`contato@getkhabs.com`), com fallback `mailto:`.

## Checklist no host (Cloudflare Pages / Netlify)

1. Confirme que `config.js` está publicado na raiz do site.
2. Ative FormSubmit: envie um teste pelo formulário e **confirme o e-mail** no link que FormSubmit manda para `contato@getkhabs.com` (primeira vez).
3. Alternativa: crie endpoint Formspree e troque a URL no script de `contato.html` / defina `formProvider`.
4. WhatsApp comercial: quando existir, preencha `window.KHABS.whatsapp` em `config.js` (formato internacional, ex. `5511999999999`) — a página de contato exibe o link automaticamente.
5. Não deixe credenciais de API no repositório público; FormSubmit usa só o e-mail de destino.

Não envie e-mails de teste em massa; um submit real basta para ativar.
