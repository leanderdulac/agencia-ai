/**
 * Refrain — config pública do site estático.
 * Produção (GitHub Pages): não há API → o formulário cai no FormSubmit → e-mail abaixo.
 *   ATENÇÃO: contato@refrain.com.br é PLACEHOLDER até a caixa existir (MX em refrain.com.br)
 *   e o FormSubmit ser ativado (1º envio gera e-mail de ativação para essa caixa).
 * Local: ./start-local.sh (:8787) — a API local é tentada primeiro (same-origin).
 * WhatsApp: deixe null até o número comercial estar definido.
 */
window.REFRAIN = {
  brand: "Refrain",
  tagline: "Seja o refrão que a IA repete.",
  taglineEn: "Be the refrain AI repeats.",
  email: "contato@refrain.com.br", // placeholder — caixa ainda não configurada
  emailStatus: "placeholder",
  whatsapp: null,
  siteUrl: "https://www.refrain.com.br",
  formProvider: "formsubmit", // formsubmit | mailto  (API local é sempre tentada antes)
  apiBase: "" // same-origin on :8787; or "http://127.0.0.1:8787" if static on :8080
};
