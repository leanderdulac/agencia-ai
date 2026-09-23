/**
 * Khabs — config pública do site estático.
 * Produção: FormSubmit/Formspree → contato@getkhabs.com
 * Local: apiBase vazio = same-origin com ./start-local.sh (:8787)
 */
window.KHABS = {
  brand: "Khabs",
  tagline: "Toda marca é uma estrela na resposta.",
  email: "contato@getkhabs.com",
  whatsapp: null,
  siteUrl: "https://getkhabs.com",
  formProvider: "local", // local | formsubmit | mailto
  apiBase: "" // same-origin on :8787; or "http://127.0.0.1:8787" if static on :8080
};
