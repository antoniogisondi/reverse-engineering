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


def controlla_pos(repo: Repository) -> list[Segnalazione]:
    """Controlli per il POS: dati dell'impresa, lavoratori, rischi e valutazioni."""
    from datetime import date

    from sicurcantiere.documenti.pos import SEZIONI_POS, chiave_testo
    from sicurcantiere.valutazioni import METODI
    from sicurcantiere.valutazioni.base import ROSSO, VIOLA

    s: list[Segnalazione] = []
    c = repo.cantiere()
    if not c["nome"].strip():
        s.append(Segnalazione(ERRORE, "Cantiere", "Manca la denominazione dell'opera."))
    if not (c["indirizzo"].strip() and c["comune"].strip()):
        s.append(Segnalazione(ERRORE, "Cantiere", "Manca l'indirizzo completo del cantiere."))

    imprese = [i for i in repo.elenco("imprese") if i["tipo"] != "Lavoratore autonomo"]
    if not imprese:
        s.append(Segnalazione(ERRORE, "Impresa", "Inserire l'impresa che redige il POS."))
    oggi = date.today().isoformat()
    for i in imprese:
        nome = i["ragione_sociale"] or f"Impresa n. {i['id']}"
        for campo, etichetta in (("datore_lavoro", "il datore di lavoro"), ("rspp", "l'RSPP"),
                                 ("medico_competente", "il medico competente"), ("rls", "l'RLS o RLST"),
                                 ("addetti_emergenze", "gli addetti alle emergenze")):
            if not i[campo].strip():
                s.append(Segnalazione(ERRORE, "Impresa", f"{nome}: indicare {etichetta}."))
        lavoratori = repo.elenco("lavoratori", impresa_id=i["id"])
        if not lavoratori:
            s.append(Segnalazione(ERRORE, "Lavoratori", f"{nome}: nessun lavoratore indicato."))
        for l in lavoratori:
            chi = l["nome"] or f"Lavoratore n. {l['id']}"
            if not l["formazione"].strip():
                s.append(Segnalazione(AVVISO, "Lavoratori", f"{chi}: formazione non indicata."))
            if not l["idoneita_scadenza"]:
                s.append(Segnalazione(AVVISO, "Lavoratori", f"{chi}: scadenza dell'idoneità sanitaria non indicata."))
            elif l["idoneita_scadenza"] < oggi:
                s.append(Segnalazione(ERRORE, "Lavoratori", f"{chi}: idoneità sanitaria scaduta."))
        fasi = repo.elenco("fasi", impresa_id=i["id"])
        if not fasi:
            s.append(Segnalazione(ERRORE, "Lavorazioni", f"{nome}: nessuna lavorazione assegnata."))
        for f in fasi:
            rischi = repo.elenco("rischi", fase_id=f["id"])
            etichetta = f"{f['codice']} {f['descrizione']}".strip() or f"Fase n. {f['id']}"
            if not rischi:
                s.append(Segnalazione(AVVISO, "Lavorazioni", f"{etichetta}: nessun rischio valutato."))
            for r in rischi:
                if not r["misure"].strip():
                    s.append(Segnalazione(AVVISO, "Rischi", f"{etichetta}: rischio \"{r['descrizione']}\" "
                                                          "senza misure di prevenzione."))
        from sicurcantiere.documenti.valutazione import valutazioni_impresa

        con_rumore = any(v["metodo"] == "rumore" for v in valutazioni_impresa(repo, i["id"]))
        for chiave, titolo in SEZIONI_POS:
            if chiave == "rumore" and con_rumore:
                continue  # l'esito viene dalla valutazione del rumore
            if chiave in ("attivita", "rumore") and not repo.testo(chiave_testo(i["id"], chiave)).strip():
                s.append(Segnalazione(AVVISO, "Testi del POS", f"{nome}: valutazione del rumore assente e "
                                      f"sezione «{titolo}» da compilare." if chiave == "rumore" else
                                      f"{nome}: sezione «{titolo}» da compilare."))

    from sicurcantiere import sostanze as classificazione

    for so in repo.elenco("sostanze"):
        nome = so["nome"] or f"Sostanza n. {so['id']}"
        codici = classificazione.codici_h(so["codici_h"])
        if not codici:
            s.append(Segnalazione(AVVISO, "Sostanze", f"{nome}: indicazioni di pericolo (frasi H) non inserite."))
        if not so["data_sds"]:
            s.append(Segnalazione(AVVISO, "Sostanze", f"{nome}: data della scheda di sicurezza non indicata."))
        if so["impresa_id"] is None and so["fase_id"] is None:
            s.append(Segnalazione(AVVISO, "Sostanze", f"{nome}: non collegata a un'impresa né a una lavorazione, "
                                                       "non comparirà nel POS."))
        for categoria in classificazione.categorie(codici):
            if categoria.grave:
                s.append(Segnalazione(AVVISO, "Sostanze", f"{nome}: {categoria.nome.lower()}, "
                                                           "valutare la sostituzione e le misure specifiche."))

    for v in repo.elenco("valutazioni"):
        metodo = METODI.get(v["metodo"])
        if metodo is None:
            continue
        esito = metodo.esegui(repo.dati_valutazione(v["id"]))
        if esito.colore in (ROSSO, VIOLA):
            s.append(Segnalazione(AVVISO, "Valutazioni",
                                  f"«{v['titolo'] or metodo.nome}»: {esito.classe.lower()}, "
                                  "attuare le misure indicate e la sorveglianza sanitaria."))
        if v["fase_id"] is None and v["impresa_id"] is None:
            s.append(Segnalazione(AVVISO, "Valutazioni",
                                  f"«{v['titolo'] or metodo.nome}»: non collegata a una fase né a un'impresa, "
                                  "non comparirà nel POS."))
    return s
