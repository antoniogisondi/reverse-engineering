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


def _controlla_idoneita(i: dict, errore, avviso, sezione: str = "Imprese") -> None:
    """Patente a crediti (art. 27) e verifica dell'idoneità tecnico-professionale (Allegato XVII)."""
    nome = i["ragione_sociale"] or f"Impresa n. {i['id']}"
    regolare = anagrafiche.patente_regolare(i)
    if regolare is None:
        avviso(sezione, f"{nome}: indicare la situazione della patente a crediti (art. 27).")
    elif regolare is False:
        errore(sezione, f"{nome}: senza patente a crediti o con meno di {anagrafiche.CREDITI_MINIMI} crediti l'impresa "
                        "non può operare in cantiere (art. 27): verificare la situazione della patente.")
    esito = anagrafiche.esito_idoneita(i)
    if esito == "Non verificata":
        avviso(sezione, f"{nome}: eseguire la verifica dell'idoneità tecnico-professionale (Allegato XVII).")
    elif esito == "Documentazione incompleta":
        avviso(sezione, f"{nome}: completare la documentazione dell'Allegato XVII.")
    if i.get("durc_congruita") == "Non congruo":
        avviso(sezione, f"{nome}: DURC di congruità con esito «non congruo», verificare la regolarizzazione.")


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
        errore("Dati generali", "Indicare la denominazione dell'opera.")
    if not (c["indirizzo"].strip() and c["comune"].strip()):
        errore("Dati generali", "Indicare l'indirizzo completo del cantiere.")
    if not c["descrizione"].strip():
        avviso("Dati generali", "Inserire la descrizione sintetica dell'opera.")
    if c["importo_lavori"] <= 0:
        avviso("Dati generali", "Indicare l'importo presunto dei lavori.")

    ruoli = {x["ruolo"] for x in anagrafiche.soggetti(repo) if x["nome"].strip()}
    if "Committente" not in ruoli:
        errore("Soggetti", "Indicare il committente.")
    if analisi.obblighi(imprese, fasi).psc:
        for ruolo in ("Coordinatore per la progettazione (CSP)", "Coordinatore per l'esecuzione (CSE)"):
            if ruolo not in ruoli:
                errore("Soggetti", f"Indicare il {ruolo[0].lower()}{ruolo[1:]}, obbligatorio in presenza di più "
                                      "imprese esecutrici (art. 90, commi 3 e 4).")

    if not imprese:
        avviso("Imprese", "Inserire le imprese del cantiere.")
    for i in imprese:
        if not i["ragione_sociale"].strip():
            errore("Imprese", f"Impresa n. {i['id']}: indicare la ragione sociale.")
        _controlla_idoneita(i, errore, avviso)

    if not fasi:
        errore("Fasi", "Inserire le fasi di lavoro.")
    con_rischi = {r["fase_id"] for r in rischi}
    for f in fasi:
        nome = f"{f['codice']} {f['descrizione']}".strip() or f"Fase n. {f['id']}"
        if not (f["data_inizio"] and f["data_fine"]):
            errore("Fasi", f"{nome}: indicare le date di inizio e di fine.")
        if not f["impresa_id"]:
            avviso("Fasi", f"{nome}: assegnare l'impresa esecutrice.")
        if f["id"] not in con_rischi:
            avviso("Fasi", f"{nome}: valutare i rischi della fase.")
    codici = {f["id"]: f["codice"] or f"Fase n. {f['id']}" for f in fasi}
    for r in rischi:
        if not r["misure"].strip():
            avviso("Rischi", f"{codici.get(r['fase_id'], '')}: indicare le misure di prevenzione per il rischio "
                             f"«{r['descrizione']}».")

    prescrizioni = repo.prescrizioni()
    livelli = analisi.livelli_fasi(rischi)
    for i in analisi.interferenze(fasi, livelli):
        if i.gravita >= 6 and not prescrizioni.get(i.chiave, "").strip():
            avviso("Interferenze",
                   f"Interferenza grave tra {i.fase_a['codice']} e {i.fase_b['codice']}: indicare prescrizioni "
                   "specifiche.")

    if not repo.elenco("costi"):
        avviso("Costi", "Compilare la stima dei costi della sicurezza.")

    # contenuti minimi del PSC scritti nella relazione (Allegato XV punti 2.1.2, 2.2 e 2.3)
    from sicurcantiere import relazione

    for chiave, titolo in relazione.SEZIONI:
        if chiave in relazione.OBBLIGATORIE and not repo.testo(chiave).strip():
            avviso("Relazione", f"Compilare la sezione «{titolo}».")
    if not relazione.leggi_allegato_xi(repo.testo(relazione.CHIAVE_ALLEGATO_XI))["verificato"]:
        avviso("Rischi particolari", "Verificare i lavori comportanti rischi particolari (Allegato XI).")
    ordigni = relazione.leggi_ordigni(repo.testo(relazione.CHIAVE_ORDIGNI))
    con_scavi = relazione.fasi_con_scavi(fasi)
    if (con_scavi or ordigni["scavi"] == "Sì") and not ordigni["esito"]:
        errore("Rischi particolari", "Sono previsti scavi: eseguire la valutazione del rischio da ordigni bellici "
                                    "inesplosi (art. 91, comma 2-bis).")
    elif con_scavi and ordigni["scavi"] == "No":
        avviso("Rischi particolari", "Verificare la presenza di scavi: sono indicati come assenti, ma il "
                                     "cronoprogramma contiene fasi di scavo.")
    if not any(a["tipo"] == "Planimetria di cantiere" for a in repo.elenco("allegati_psc")):
        avviso("Tavole", "Allegare almeno una planimetria del cantiere (Allegato XV punto 2.1.4).")
    senza_categoria = [c for c in repo.elenco("costi") if not c["categoria"]]
    if senza_categoria:
        avviso("Costi", f"Assegnare la categoria (Allegato XV punto 4.1.1) alle voci di costo che ne "
                              f"sono prive ({len(senza_categoria)}).")
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
        s.append(Segnalazione(ERRORE, "Cantiere", "Indicare la denominazione dell'opera."))
    if not (c["indirizzo"].strip() and c["comune"].strip()):
        s.append(Segnalazione(ERRORE, "Cantiere", "Indicare l'indirizzo completo del cantiere."))

    if not any(x["ruolo"] == anagrafiche.COMMITTENTE and x["nome"].strip() for x in repo.elenco("soggetti")):
        s.append(Segnalazione(AVVISO, "Committente", "Indicare il committente dei lavori."))

    imprese = [i for i in repo.elenco("imprese") if not anagrafiche.autonomo(i)]
    # Le imprese senza lavorazioni né lavoratori sono solo di riferimento (affidataria, subappaltatrici,
    # imprese venute dal PSC): si controllano quelle che redigono il POS, se ce ne sono.
    operative = [i for i in imprese if repo.elenco("fasi", impresa_id=i["id"])
                 or repo.elenco("lavoratori", impresa_id=i["id"])]
    imprese = operative or imprese
    if not imprese:
        s.append(Segnalazione(ERRORE, "Impresa", "Inserire l'impresa che redige il POS."))
    oggi = date.today().isoformat()
    for i in imprese:
        nome = i["ragione_sociale"] or f"Impresa n. {i['id']}"
        if not i["datore_lavoro"].strip():
            s.append(Segnalazione(ERRORE, "Impresa", f"{nome}: indicare il datore di lavoro."))
        if not (i["indirizzo"].strip() and i["comune"].strip()):
            s.append(Segnalazione(AVVISO, "Impresa", f"{nome}: completare l'indirizzo della sede legale."))
        if not (i["partita_iva"].strip() or i["codice_fiscale"].strip()):
            s.append(Segnalazione(AVVISO, "Impresa", f"{nome}: indicare la partita IVA o il codice fiscale."))
        if not i["inail"].strip():
            s.append(Segnalazione(AVVISO, "Impresa", f"{nome}: indicare la posizione INAIL."))
        if i["durc_scadenza"] and i["durc_scadenza"] < oggi:
            s.append(Segnalazione(ERRORE, "Impresa", f"{nome}: DURC scaduto, acquisire il DURC in corso di validità."))
        regolare = anagrafiche.patente_regolare(i)
        if regolare is None:
            s.append(Segnalazione(AVVISO, "Impresa", f"{nome}: indicare la situazione della patente a crediti "
                                                     "(art. 27)."))
        elif regolare is False:
            s.append(Segnalazione(ERRORE, "Impresa", f"{nome}: senza patente a crediti o con meno di "
                                                     f"{anagrafiche.CREDITI_MINIMI} crediti l'impresa non può "
                                                     "operare in cantiere (art. 27): verificare la situazione "
                                                     "della patente."))
        elenco_figure = anagrafiche.figure(repo, i)
        ruoli = {anagrafiche.ruolo_riconosciuto(f["ruolo"]) for f in elenco_figure if f["nome"].strip()}
        ruoli |= {r for r, _ in anagrafiche.figure_non_presenti(i)}
        for f in elenco_figure:
            if f["ruolo"].strip() and not f["nome"].strip():
                s.append(Segnalazione(AVVISO, "Figure della sicurezza",
                                      f"{nome}: indicare il nominativo per «{f['ruolo']}» (senza nominativo "
                                      "la riga non viene stampata)."))
            if f.get("formazione_scadenza") and f["formazione_scadenza"] < oggi:
                s.append(Segnalazione(AVVISO, "Figure della sicurezza",
                                      f"{nome}: {f['nome'] or f['ruolo']}, formazione scaduta: programmare "
                                      "l'aggiornamento."))
        if i["rspp_datore"] and any(f["ruolo"] == anagrafiche.RSPP and f["nome"].strip()
                                    for f in repo.elenco("figure", impresa_id=i["id"])):
            s.append(Segnalazione(AVVISO, "Figure della sicurezza",
                                  f"{nome}: è selezionata la casella «Il datore di lavoro svolge direttamente i "
                                  "compiti di RSPP», ma nell'elenco è presente anche un RSPP, che non viene "
                                  "stampato. Deselezionare la casella o eliminare la riga."))
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
                                  "non può svolgere direttamente i compiti di primo soccorso e antincendio (art. 34, "
                                  "comma 1-bis): designare gli addetti."))
        if not lavoratori:
            s.append(Segnalazione(ERRORE, "Lavoratori", f"{nome}: indicare i lavoratori impiegati nel cantiere."))
        if anagrafiche.affidataria(i) and not i["incaricato_97"].strip():
            s.append(Segnalazione(AVVISO, "Impresa", f"{nome}: indicare il soggetto incaricato dei compiti "
                                                     "dell'impresa affidataria (art. 97)."))
        con_mansioni = set()
        for l in lavoratori:
            chi = anagrafiche.nominativo(l) or f"Lavoratore n. {l['id']}"
            mansioni = repo.mansioni(l["id"])
            con_mansioni |= {f for f, _ in mansioni}
            if not mansioni:
                s.append(Segnalazione(AVVISO, "Lavoratori", f"{chi}: assegnare le lavorazioni svolte (mansioni)."))
            if l["autonomo"]:
                continue
            if not anagrafiche.formazione_lavoratore(l):
                s.append(Segnalazione(AVVISO, "Lavoratori", f"{chi}: indicare la formazione ricevuta."))
            if not l["idoneita_scadenza"]:
                s.append(Segnalazione(AVVISO, "Lavoratori", f"{chi}: indicare la scadenza dell'idoneità sanitaria."))
            elif l["idoneita_scadenza"] < oggi:
                s.append(Segnalazione(ERRORE, "Lavoratori", f"{chi}: idoneità sanitaria scaduta, programmare la "
                                                             "visita medica."))
        fasi = repo.elenco("fasi", impresa_id=i["id"])
        if not fasi:
            s.append(Segnalazione(ERRORE, "Lavorazioni", f"{nome}: assegnare le lavorazioni da eseguire."))
        for f in fasi:
            for r in repo.rischi_esclusi(fase_id=f["id"]):
                if not r["motivazione"].strip():
                    s.append(Segnalazione(AVVISO, "Rischi", f"{f['codice']} {f['descrizione']}".strip()
                                          + f": motivare l'esclusione del rischio «{r['descrizione']}», "
                                          "indicato come non presente."))
            rischi = repo.rischi(fase_id=f["id"])
            etichetta = f"{f['codice']} {f['descrizione']}".strip() or f"Fase n. {f['id']}"
            if not rischi:
                s.append(Segnalazione(AVVISO, "Lavorazioni", f"{etichetta}: valutare i rischi della lavorazione."))
            if lavoratori and f["id"] not in con_mansioni:
                s.append(Segnalazione(AVVISO, "Lavorazioni", f"{etichetta}: assegnare i lavoratori."))
            for r in rischi:
                if not r["misure"].strip():
                    s.append(Segnalazione(AVVISO, "Rischi", f"{etichetta}: indicare le misure di prevenzione per "
                                                          f"il rischio «{r['descrizione']}»."))
        from sicurcantiere.documenti.valutazione import valutazioni_impresa

        con_rumore = any(v["metodo"] == "rumore" for v in valutazioni_impresa(repo, i["id"]))
        for chiave, titolo in SEZIONI_POS:
            if chiave == "rumore" and con_rumore:
                continue  # l'esito viene dalla valutazione del rumore
            if chiave in ("attivita", "rumore") and not repo.testo(chiave_testo(i["id"], chiave)).strip():
                s.append(Segnalazione(AVVISO, "Testi del POS", f"{nome}: eseguire la valutazione del rumore "
                                      f"o compilare la sezione «{titolo}»." if chiave == "rumore" else
                                      f"{nome}: compilare la sezione «{titolo}»."))

    from sicurcantiere import sostanze as classificazione

    for so in repo.elenco("sostanze"):
        nome = so["nome"] or f"Sostanza n. {so['id']}"
        codici = classificazione.codici_h(so["codici_h"])
        if not codici:
            s.append(Segnalazione(AVVISO, "Sostanze", f"{nome}: inserire le indicazioni di pericolo (frasi H)."))
        if not so["data_sds"]:
            s.append(Segnalazione(AVVISO, "Sostanze", f"{nome}: indicare la data della scheda di dati di sicurezza."))
        if so["impresa_id"] is None and not repo.fasi_sostanza(so["id"]):
            s.append(Segnalazione(AVVISO, "Sostanze", f"{nome}: collegare la sostanza a un'impresa o a una "
                                                       "lavorazione, altrimenti non compare nel POS."))
        for categoria in classificazione.categorie(codici):
            if categoria.grave:
                s.append(Segnalazione(AVVISO, "Sostanze", f"{nome}: {categoria.nome.lower()}, "
                                                           "valutare la sostituzione e le misure specifiche."))

    from sicurcantiere.valutazioni import automatiche

    for chiave, scoperte in automatiche.fasi_scoperte(repo).items():
        g = next(x for x in automatiche.GRUPPI if x.chiave == chiave)
        s.append(Segnalazione(ERRORE, "Valutazioni", f"{g.titolo}: estendere la valutazione alle "
                                                     f"lavorazioni che presentano il rischio ({len(scoperte)} "
                                                     "non coperte)."))
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
                                  f"«{v['titolo'] or metodo.nome}»: collegare la valutazione a una fase o a "
                                  "un'impresa, altrimenti non compare nel POS."))
    return s


def sincronizza_e_controlla_pos(repo: Repository) -> list[Segnalazione]:
    """Crea le valutazioni richieste dai rischi delle lavorazioni, poi esegue i controlli del POS."""
    from sicurcantiere.valutazioni.automatiche import sincronizza

    sincronizza(repo)
    return controlla_pos(repo)
