"""Controlli di completezza del progetto prima della stampa dei documenti."""

from __future__ import annotations

from dataclasses import dataclass

from sicurcantiere import analisi
from sicurcantiere.repository import Repository

ERRORE = "Errore"
AVVISO = "Avviso"


@dataclass(frozen=True)
class Segnalazione:
    livello: str  # ERRORE o AVVISO
    sezione: str
    messaggio: str


def controlla(repo: Repository) -> list[Segnalazione]:
    s: list[Segnalazione] = []
    c = repo.cantiere()
    soggetti = repo.elenco("soggetti")
    imprese = repo.elenco("imprese")
    fasi = repo.elenco("fasi")
    rischi = repo.elenco("rischi")

    def errore(sezione: str, messaggio: str) -> None:
        s.append(Segnalazione(ERRORE, sezione, messaggio))

    def avviso(sezione: str, messaggio: str) -> None:
        s.append(Segnalazione(AVVISO, sezione, messaggio))

    if not c["nome"].strip():
        errore("Dati generali", "Manca la denominazione dell'opera.")
    if not (c["indirizzo"].strip() and c["comune"].strip()):
        errore("Dati generali", "Manca l'indirizzo completo del cantiere.")
    if not c["descrizione"].strip():
        avviso("Dati generali", "Manca la descrizione sintetica dell'opera.")
    if c["importo_lavori"] <= 0:
        avviso("Dati generali", "Importo presunto dei lavori non indicato.")

    ruoli = {x["ruolo"] for x in soggetti if x["nome"].strip()}
    if "Committente" not in ruoli:
        errore("Soggetti", "Manca il committente.")
    if analisi.obblighi(imprese, fasi).psc:
        for ruolo in ("Coordinatore per la progettazione (CSP)", "Coordinatore per l'esecuzione (CSE)"):
            if ruolo not in ruoli:
                errore("Soggetti", f"Con più imprese è obbligatorio indicare il {ruolo}.")

    if not imprese:
        avviso("Imprese", "Nessuna impresa inserita.")
    for i in imprese:
        if not i["ragione_sociale"].strip():
            errore("Imprese", f"Impresa n. {i['id']} senza ragione sociale.")

    if not fasi:
        errore("Fasi", "Nessuna fase di lavoro inserita.")
    con_rischi = {r["fase_id"] for r in rischi}
    for f in fasi:
        nome = f"{f['codice']} {f['descrizione']}".strip() or f"Fase n. {f['id']}"
        if not (f["data_inizio"] and f["data_fine"]):
            errore("Fasi", f"{nome}: date di inizio e fine mancanti.")
        if not f["impresa_id"]:
            avviso("Fasi", f"{nome}: impresa esecutrice non assegnata.")
        if f["id"] not in con_rischi:
            avviso("Fasi", f"{nome}: nessun rischio valutato.")
    codici = {f["id"]: f["codice"] or f"Fase n. {f['id']}" for f in fasi}
    for r in rischi:
        if not r["misure"].strip():
            avviso("Rischi", f"{codici.get(r['fase_id'], '')}: rischio \"{r['descrizione']}\" "
                             "senza misure di prevenzione.")

    prescrizioni = repo.prescrizioni()
    livelli = analisi.livelli_fasi(rischi)
    for i in analisi.interferenze(fasi, livelli):
        if i.gravita >= 6 and not prescrizioni.get(i.chiave, "").strip():
            avviso("Interferenze",
                   f"Interferenza grave tra {i.fase_a['codice']} e {i.fase_b['codice']} senza prescrizioni specifiche.")

    if not repo.elenco("costi"):
        avviso("Costi", "Stima dei costi della sicurezza vuota.")
    return s
