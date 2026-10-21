// Piccole azioni delle pagine (niente script nelle pagine: lo vieta la Content-Security-Policy).
document.addEventListener("click", (e) => {
  const pulsante = e.target.closest("[data-copia]");
  if (pulsante) navigator.clipboard.writeText(document.getElementById(pulsante.dataset.copia).value);
});
document.addEventListener("submit", (e) => {
  const messaggio = e.target.dataset.conferma;
  if (messaggio && !confirm(messaggio)) e.preventDefault();
});
