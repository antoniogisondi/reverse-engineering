"""Controlli di completezza del progetto prima della stampa dei documenti."""

from __future__ import annotations

from dataclasses import dataclass

from sicurcantiere import anagrafiche, analisi
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
    imprese = repo.elenco("imprese")
    fasi = repo.elenco("fasi")
    rischi = repo.rischi()

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

    ruoli = {x["ruolo"] for x in anagrafiche.soggetti(repo) if x["nome"].strip()}
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

    if not any(x["ruolo"] == anagrafiche.COMMITTENTE and x["nome"].strip() for x in repo.elenco("soggetti")):
        s.append(Segnalazione(AVVISO, "Committente", "Manca il committente dei lavori."))

    imprese = [i for i in repo.elenco("imprese") if not anagrafiche.autonomo(i)]
    if not imprese:
        s.append(Segnalazione(ERRORE, "Impresa", "Inserire l'impresa che redige il POS."))
    oggi = date.today().isoformat()
    for i in imprese:
        nome = i["ragione_sociale"] or f"Impresa n. {i['id']}"
        if not i["datore_lavoro"].strip():
            s.append(Segnalazione(ERRORE, "Impresa", f"{nome}: indicare il datore di lavoro."))
        if not (i["indirizzo"].strip() and i["comune"].strip()):
            s.append(Segnalazione(AVVISO, "Impresa", f"{nome}: indirizzo della sede legale incompleto."))
        if not (i["partita_iva"].strip() or i["codice_fiscale"].strip()):
            s.append(Segnalazione(AVVISO, "Impresa", f"{nome}: partita IVA o codice fiscale non indicati."))
        if not i["inail"].strip():
            s.append(Segnalazione(AVVISO, "Impresa", f"{nome}: posizione INAIL non indicata."))
        if i["durc_scadenza"] and i["durc_scadenza"] < oggi:
            s.append(Segnalazione(ERRORE, "Impresa", f"{nome}: DURC scaduto."))
        elenco_figure = anagrafiche.figure(repo, i)
        ruoli = {anagrafiche.ruolo_riconosciuto(f["ruolo"]) for f in elenco_figure if f["nome"].strip()}
        ruoli |= {r for r, _ in anagrafiche.figure_non_presenti(i)}
        for f in elenco_figure:
            if f["ruolo"].strip() and not f["nome"].strip():
                s.append(Segnalazione(AVVISO, "Figure della sicurezza",
                                      f"{nome}: «{f['ruolo']}» senza nominativo (la riga non viene stampata)."))
            if f.get("formazione_scadenza") and f["formazione_scadenza"] < oggi:
                s.append(Segnalazione(AVVISO, "Figure della sicurezza",
                                      f"{nome}: {f['nome'] or f['ruolo']}, aggiornamento della formazione scaduto."))
        if i["rspp_datore"] and any(f["ruolo"] == anagrafiche.RSPP and f["nome"].strip()
                                    for f in repo.elenco("figure", impresa_id=i["id"])):
            s.append(Segnalazione(AVVISO, "Figure della sicurezza",
                                  f"{nome}: è spuntato «il datore di lavoro svolge i compiti di RSPP» ma c'è anche "
                                  "un RSPP nell'elenco, che non viene stampato. Togliere la spunta o la riga."))
        for richiesti, etichetta, grave in anagrafiche.FIGURE_OBBLIGATORIE:
            if not ruoli & set(richiesti):
                s.append(Segnalazione(ERRORE if grave else AVVISO, "Figure della sicurezza",
                                      f"{nome}: indicare {etichetta}."))
        lavoratori = repo.elenco("lavoratori", impresa_id=i["id"])
        dipendenti = sum(1 for l in lavoratori if not l["autonomo"])
        da_soli = [r for r in anagrafiche.ruoli_datore(i) if r in anagrafiche.NOTE_RUOLI_DATORE]
        if da_soli and dipendenti > anagrafiche.LIMITE_ART_34:
            s.append(Segnalazione(AVVISO, "Figure della sicurezza",
                                  f"{nome}: con più di {anagrafiche.LIMITE_ART_34} lavoratori il datore di lavoro "
                                  "non può svolgere da solo i compiti di primo soccorso e antincendio (art. 34 "
                                  "c. 1-bis): designare gli addetti."))
        if not lavoratori:
            s.append(Segnalazione(ERRORE, "Lavoratori", f"{nome}: nessun lavoratore indicato."))
        if anagrafiche.affidataria(i) and not i["incaricato_97"].strip():
            s.append(Segnalazione(AVVISO, "Impresa", f"{nome}: indicare il soggetto incaricato dei compiti "
                                                     "dell'impresa affidataria (art. 97)."))
        con_mansioni = set()
        for l in lavoratori:
            chi = anagrafiche.nominativo(l) or f"Lavoratore n. {l['id']}"
            mansioni = repo.mansioni(l["id"])
            con_mansioni |= {f for f, _ in mansioni}
            if not mansioni:
                s.append(Segnalazione(AVVISO, "Lavoratori", f"{chi}: nessuna lavorazione assegnata (mansioni)."))
            if l["autonomo"]:
                continue
            if not anagrafiche.formazione_lavoratore(l):
                s.append(Segnalazione(AVVISO, "Lavoratori", f"{chi}: formazione non indicata."))
            if not l["idoneita_scadenza"]:
                s.append(Segnalazione(AVVISO, "Lavoratori", f"{chi}: scadenza dell'idoneità sanitaria non indicata."))
            elif l["idoneita_scadenza"] < oggi:
                s.append(Segnalazione(ERRORE, "Lavoratori", f"{chi}: idoneità sanitaria scaduta."))
        fasi = repo.elenco("fasi", impresa_id=i["id"])
        if not fasi:
            s.append(Segnalazione(ERRORE, "Lavorazioni", f"{nome}: nessuna lavorazione assegnata."))
        for f in fasi:
            for r in repo.rischi_esclusi(fase_id=f["id"]):
                if not r["motivazione"].strip():
                    s.append(Segnalazione(AVVISO, "Rischi", f"{f['codice']} {f['descrizione']}".strip()
                                          + f": rischio \"{r['descrizione']}\" non presente senza motivazione."))
            rischi = repo.rischi(fase_id=f["id"])
            etichetta = f"{f['codice']} {f['descrizione']}".strip() or f"Fase n. {f['id']}"
            if not rischi:
                s.append(Segnalazione(AVVISO, "Lavorazioni", f"{etichetta}: nessun rischio valutato."))
            if lavoratori and f["id"] not in con_mansioni:
                s.append(Segnalazione(AVVISO, "Lavorazioni", f"{etichetta}: nessun lavoratore assegnato."))
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
        if so["impresa_id"] is None and not repo.fasi_sostanza(so["id"]):
            s.append(Segnalazione(AVVISO, "Sostanze", f"{nome}: non collegata a un'impresa né a una lavorazione, "
                                                       "non comparirà nel POS."))
        for categoria in classificazione.categorie(codici):
            if categoria.grave:
                s.append(Segnalazione(AVVISO, "Sostanze", f"{nome}: {categoria.nome.lower()}, "
                                                           "valutare la sostituzione e le misure specifiche."))

    from sicurcantiere.valutazioni import automatiche

    for chiave, scoperte in automatiche.fasi_scoperte(repo).items():
        g = next(x for x in automatiche.GRUPPI if x.chiave == chiave)
        s.append(Segnalazione(ERRORE, "Valutazioni", f"{g.titolo}: {len(scoperte)} lavorazioni presentano il "
                                                     "rischio ma non sono coperte da una valutazione."))
    for v in repo.elenco("valutazioni"):
        metodo = METODI.get(v["metodo"])
        if metodo is None:
            continue
        if automatiche.da_eseguire(repo, v["id"]):
            s.append(Segnalazione(ERRORE, "Valutazioni", f"«{v['titolo'] or metodo.nome}»: valutazione da "
                                                         "eseguire, inserire i parametri del metodo."))
            continue
        esito = metodo.esegui(repo.dati_valutazione(v["id"]))
        if esito.colore in (ROSSO, VIOLA):
            s.append(Segnalazione(AVVISO, "Valutazioni",
                                  f"«{v['titolo'] or metodo.nome}»: {esito.classe.lower()}, "
                                  "attuare le misure indicate e la sorveglianza sanitaria."))
        if v["impresa_id"] is None and not repo.fasi_valutazione(v["id"]):
            s.append(Segnalazione(AVVISO, "Valutazioni",
                                  f"«{v['titolo'] or metodo.nome}»: non collegata a una fase né a un'impresa, "
                                  "non comparirà nel POS."))
    return s


def sincronizza_e_controlla_pos(repo: Repository) -> list[Segnalazione]:
    """Crea le valutazioni richieste dai rischi delle lavorazioni, poi esegue i controlli del POS."""
    from sicurcantiere.valutazioni.automatiche import sincronizza

    sincronizza(repo)
    return controlla_pos(repo)
