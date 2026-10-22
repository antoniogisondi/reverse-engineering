"""Generazione del Piano di Sicurezza e Coordinamento (art. 100 e Allegato XV, punto 2.1.2).

Stessa impaginazione del POS, nei colori del programma PSC. I capitoli seguono le lettere dei contenuti
minimi del punto 2.1.2: a) opera, b) soggetti, c-d) rischi e misure per area, organizzazione e
lavorazioni, e) interferenze, f) uso comune, g) cooperazione, h) emergenze, i) cronoprogramma,
l) costi della sicurezza.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Any

from docx import Document
from docx.shared import Pt

from sicurcantiere import anagrafiche, analisi
from sicurcantiere.documenti import stile
from sicurcantiere.documenti.comune import data_it, euro, indirizzo_cantiere, nome_fase, salva
from sicurcantiere.documenti.composizione import CONSIGLIATO, FACOLTATIVO, OBBLIGATORIO, Manca, segnaposto
from sicurcantiere.documenti.pos import NUMERI_EMERGENZA, dpi_con_icone, foto_cantiere, tabella_rischi
from sicurcantiere.relazione import SEZIONI
from sicurcantiere.repository import Repository

MAX_COLONNE_CRONO = 22
PRESCRIZIONE_GENERICA = (
    "Sfasamento spaziale delle lavorazioni o, se non possibile, sfasamento temporale; "
    "verifica del CSE prima dell'inizio."
)
# Sezioni dei programmi in cui si compilano i dati (per i collegamenti dei dati mancanti).
CANTIERE, SOGGETTI, IMPRESE, FASI, RISCHI, INTERFERENZE, COSTI, RELAZIONE = (
    "Dati generali", "Soggetti", "Imprese", "Fasi", "Rischi", "Interferenze", "Costi", "Relazione")


def _o(valore, dato: str, sezione: str, livello: str = OBBLIGATORIO):
    return valore if str(valore or "").strip() and valore != "-" else Manca(dato, sezione, livello)


def _livello(prodotto: int) -> int:
    """Indice del colore del livello P x D (come nelle tabelle dei rischi)."""
    return 3 if prodotto >= 9 else 2 if prodotto >= 6 else 1 if prodotto >= 3 else 0


def _colonne_cronoprogramma(inizio: date, fine: date) -> list[tuple[date, date, str]]:
    """Divide il periodo in settimane o, se troppo lungo, in periodi di più settimane."""
    inizio = inizio - timedelta(days=inizio.weekday())  # lunedì
    settimane = ((fine - inizio).days // 7) + 1
    passo = max(1, -(-settimane // MAX_COLONNE_CRONO))
    colonne = []
    giorno = inizio
    while giorno <= fine:
        termine = giorno + timedelta(days=7 * passo - 1)
        colonne.append((giorno, termine, giorno.strftime("%d/%m")))
        giorno = termine + timedelta(days=1)
    return colonne


def _cronoprogramma(doc, fasi: list[dict[str, Any]], imprese: dict[int, str],
                    interferenze: list[analisi.Interferenza]) -> None:
    """Diagramma a barre settimanale: barre nel colore del programma, in rosso le fasi che interferiscono."""
    periodo = analisi.periodo_lavori(fasi)
    if not periodo:
        stile.testo(doc, "", "date di inizio e fine delle fasi, per il cronoprogramma dei lavori", FASI,
                    OBBLIGATORIO)
        return
    colonne = _colonne_cronoprogramma(*periodo)
    interferenti = {f["id"] for i in interferenze for f in (i.fase_a, i.fase_b)}
    t = doc.add_table(rows=1, cols=len(colonne) + 2)
    stile._bordi_tabella(t, top=(stile.ACCENTO, 8), bottom=(stile.LINEA_FORTE, 6), insideH=(stile.LINEA, 4),
                         insideV=(stile.LINEA, 2))
    stile._margini_celle(t, 0.04, 0.05)
    stile._ripeti_intestazione(t.rows[0])
    for cella, testo_cella in zip(t.rows[0].cells, ["Fase", "Impresa"] + [c[2] for c in colonne]):
        stile.ombreggia_cella(cella, stile.TINTA)
        p = cella.paragraphs[0]
        stile._spaziatura(p)
        stile._run(p, testo_cella, 6 if testo_cella[:1].isdigit() else 7.5, stile.ACCENTO_SCURO, grassetto=True)
    for f in fasi:
        inizio, fine = analisi.data(f["data_inizio"]), analisi.data(f["data_fine"])
        riga = t.add_row()
        stile._non_spezzare(riga)
        celle = riga.cells
        for cella, testo_cella in zip(celle[:2], (nome_fase(f), imprese.get(f["impresa_id"], ""))):
            p = cella.paragraphs[0]
            stile._spaziatura(p)
            stile._run(p, testo_cella, 7)
        if not (inizio and fine):
            continue
        colore = stile.LIVELLI[3][1] if f["id"] in interferenti else stile.ACCENTO
        for cella, (da, a, _) in zip(celle[2:], colonne):
            if inizio <= a and fine >= da:
                stile.ombreggia_cella(cella, colore)
    resto = stile.LARGHEZZA_UTILE - 4.6 - 2.8
    stile.larghezze_colonne(t, [4.6, 2.8] + [resto / len(colonne)] * len(colonne))
    stile._spazio_dopo(doc)
    stile.nota(doc, "Ogni colonna è una settimana (o un gruppo di settimane per i lavori lunghi), indicata con la "
                    "data del lunedì. In rosso le fasi che si sovrappongono a quelle di altre imprese "
                    "(capitolo «Interferenze tra le lavorazioni»).")


def _programma(doc, fasi: list[dict[str, Any]], imprese: dict[int, str]) -> None:
    """Programma dei lavori in tabella: tutte le fasi di tutte le imprese, dall'inizio alla fine."""
    stile.banda(doc, "Programma dei lavori")
    ordinate = sorted(fasi, key=lambda f: (f["data_inizio"] is None, f["data_inizio"] or "", f["id"]))
    righe = []
    for f in ordinate:
        da, a = analisi.data(f["data_inizio"]), analisi.data(f["data_fine"])
        righe.append([nome_fase(f) + (f"\n{f['lavorazione']}" if f["lavorazione"] else ""),
                      imprese.get(f["impresa_id"], "") or "da definire",
                      data_it(da) if da else "—", data_it(a) if a else "—",
                      str(analisi.giorni_lavorativi(da, a)) if da and a and a >= da else "—",
                      str(f["lavoratori"]) if f.get("lavoratori") else "—"])
    stile.tabella_colorata(doc, ["Fase / lavorazione", "Impresa", "Inizio", "Fine", "gg lav.", "Lavoratori"],
                           righe, 8, larghezze=[6.6, 3.6, 2.1, 2.1, 1.4, 1.6])


def _diagramma_gantt(doc, fasi: list[dict[str, Any]], imprese: dict[int, str], livelli: dict[int, int],
                     interferenze: list[analisi.Interferenza]) -> None:
    """Diagramma di Gantt su pagine orizzontali; senza Qt (non dovrebbe capitare) resta la tabella."""
    import io

    from docx.shared import Cm

    from sicurcantiere.documenti import gantt

    if not analisi.periodo_lavori(fasi):
        _cronoprogramma(doc, fasi, imprese, interferenze)
        return
    try:
        pagine = gantt.immagini(fasi, imprese, livelli)
    except Exception:  # noqa: BLE001 - il documento si genera comunque, con la tabella settimanale
        pagine = []
    if not pagine:
        _cronoprogramma(doc, fasi, imprese, interferenze)
        return
    stile.pagine_orizzontali(doc)
    for n, immagine in enumerate(pagine):
        p = doc.add_paragraph()
        if n:
            p.paragraph_format.page_break_before = True
        stile._spaziatura(p, 0, 4)
        stile._bordo_paragrafo(p, ("bottom",), stile.ACCENTO, 12, 4)
        stile._run(p, "Diagramma di Gantt dei lavori" + (f" ({n + 1} di {len(pagine)})" if len(pagine) > 1 else ""),
                   13, stile.INCHIOSTRO, carattere=stile.CARATTERE_TITOLI)
        doc.add_picture(io.BytesIO(immagine), width=Cm(gantt.LARGHEZZA_CM))
    stile.nota(doc, "Barre colorate per impresa; in rosso i periodi in cui lavorazioni di imprese diverse si "
                    "sovrappongono (capitolo «Interferenze tra le lavorazioni»). In grigio i fine settimana. Sotto le "
                    "fasi, i lavoratori presenti e il rischio massimo di ogni giorno lavorativo.")
    stile.pagine_verticali(doc)


def _matrice_rischio(doc) -> None:
    """Matrice probabilità x danno con i colori dei livelli."""
    righe = [[f"P = {p}"] + [str(p * d) for d in range(1, 5)] for p in range(4, 0, -1)]
    t = stile.tabella_colorata(doc, ["Probabilità \\ Danno", "D = 1", "D = 2", "D = 3", "D = 4"], righe, 8.5,
                               larghezze=[4.2, 3.3, 3.3, 3.3, 3.3])
    for riga, p in zip(t.rows[1:], range(4, 0, -1)):
        for cella, d in zip(riga.cells[1:], range(1, 5)):
            stile.colora_livello(cella, _livello(p * d))
    stile.scheda(doc, [("1 - 2", "rischio basso: misure ordinarie e verifica periodica"),
                       ("3 - 4", "rischio medio: misure da programmare e verificare"),
                       ("6 - 8", "rischio alto: misure prima dell'inizio della fase, verifica del CSE"),
                       ("9 - 16", "rischio molto alto: la fase non inizia senza misure specifiche e verifica "
                                  "del CSE")], 3.0)


def _soggetto(doc, s: dict[str, Any]) -> None:
    stile.banda(doc, s["ruolo"])
    if s.get("nota"):
        stile.nota(doc, s["nota"])
    stile.scheda(doc, [
        ("Nominativo / ragione sociale", s["nome"]), ("Nella persona di", s["rappresentante"]),
        ("Qualifica", s["qualifica"]), ("Indirizzo", s["indirizzo"]),
        ("Telefono", s["telefono"]), ("Email", s["email"]), ("PEC", s["pec"]),
        ("Codice fiscale", s["codice_fiscale"]), ("Partita IVA", s["partita_iva"]),
    ])


def genera_psc(repo: Repository, destinazione: str | Path) -> Path:
    with stile.colori_documento(*stile.COLORI_PSC):
        return _genera(repo, destinazione)


def _genera(repo: Repository, destinazione: str | Path) -> Path:
    c = repo.cantiere()
    soggetti = anagrafiche.soggetti(repo)
    per_ruolo = {s["ruolo"]: s for s in soggetti if s["nome"].strip()}
    imprese = repo.elenco("imprese")
    fasi = repo.elenco("fasi")
    costi = repo.elenco("costi")
    rischi = repo.rischi()
    nomi_imprese = {i["id"]: i["ragione_sociale"] for i in imprese}
    livelli = analisi.livelli_fasi(rischi)
    elenco_interferenze = analisi.interferenze(fasi, livelli)
    prescrizioni = repo.prescrizioni()
    testi = {chiave: repo.testo(chiave) for chiave, _ in SEZIONI}
    titoli = dict(SEZIONI)
    periodo = analisi.periodo_lavori(fasi)
    revisioni = repo.elenco("revisioni", documento="PSC")
    ultima = revisioni[-1] if revisioni else None
    data_documento = data_it(ultima["data"]) if ultima and ultima["data"] else data_it(date.today())
    revisione = f"Rev. {ultima['numero']} del {data_documento}" if ultima else f"Emissione del {data_documento}"
    comune = f"{c['comune']} ({c['provincia']})" if c["provincia"] else c["comune"]
    committente = per_ruolo.get(anagrafiche.COMMITTENTE)
    csp = per_ruolo.get(anagrafiche.CSP)
    responsabile = per_ruolo.get(anagrafiche.RESPONSABILE_LAVORI)

    doc = Document()
    stile.imposta_stili(doc)
    stile.imposta_pagina(doc, " · ".join(v for v in (c["nome"], comune) if v),
                         (f"Piano di sicurezza e coordinamento · {c['nome']}".strip(" ·"), revisione))

    # --- copertina ---
    firme_copertina = [("Il coordinatore per la progettazione", csp["nome"] if csp else "")]
    if responsabile and responsabile["nome"] != (committente or {}).get("nome"):
        firme_copertina.append(("Il responsabile dei lavori", responsabile["nome"]))
    else:
        firme_copertina.append(("Il committente", committente["nome"] if committente else ""))
    stile.copertina(
        doc,
        comune=comune,
        titolo="Piano di sicurezza e coordinamento",
        riferimento="D.Lgs. 9 aprile 2008, n. 81 · art. 100 e Allegato XV punto 2",
        voci=[("Cantiere", _o(indirizzo_cantiere(c), "indirizzo del cantiere", CANTIERE)),
              ("Natura dell'opera", _o(c["natura_opera"], "natura dell'opera", CANTIERE, CONSIGLIATO)),
              ("Committente", _o(committente["nome"] if committente else "", "committente", SOGGETTI)),
              ("Importo dei lavori", euro(c["importo_lavori"]) if c["importo_lavori"] else "")],
        data_luogo=f"{c['comune'] or ''}, {data_documento}".strip(", "),
        firme=firme_copertina,
        impresa=[c["nome"] or "Opera", c["descrizione"].strip().split("\n")[0][:160] if c["descrizione"] else ""],
        revisione=revisione,
    )

    # --- indice e revisioni ---
    stile.indice(doc)
    stile.banda(doc, "Revisioni del documento")
    if revisioni:
        stile.tabella_colorata(doc, ["Rev.", "Data", "Descrizione"], [
            [str(r["numero"]), data_it(r["data"]), r["descrizione"]] for r in revisioni], larghezze=[1.2, 2.6, 13.6])
    else:
        doc.add_paragraph(f"Prima emissione del {data_documento}.")

    # ===== Parte 1 =====
    stile.parte(doc, "1", "L'opera e i soggetti",
                "Identificazione e descrizione dell'opera, soggetti con compiti di sicurezza, imprese e lavoratori "
                "autonomi (Allegato XV punto 2.1.2, lettere a e b).")

    stile.capitolo(doc, "Identificazione e descrizione dell'opera", "Allegato XV punto 2.1.2, lettera a)")
    stile.scheda(doc, [
        ("Opera", _o(c["nome"], "denominazione dell'opera", CANTIERE)),
        ("Natura dell'opera", _o(c["natura_opera"], "natura dell'opera", CANTIERE, CONSIGLIATO)),
        ("Indirizzo del cantiere", _o(indirizzo_cantiere(c), "indirizzo del cantiere", CANTIERE)),
        ("CAP", c["cap"]),
        ("Titolo abilitativo", _o(c["titolo_abilitativo"], "titolo abilitativo", CANTIERE, FACOLTATIVO)),
        ("Importo presunto dei lavori", euro(c["importo_lavori"]) if c["importo_lavori"] else
         Manca("importo presunto dei lavori", CANTIERE, CONSIGLIATO)),
        ("Inizio dei lavori (presunto)", data_it(periodo[0]) if periodo else ""),
        ("Fine dei lavori (presunta)", data_it(periodo[1]) if periodo else ""),
        ("Entità presunta del cantiere", f"{analisi.uomini_giorno(fasi)} uomini-giorno" if fasi else ""),
        ("Numero massimo presunto di lavoratori", str(analisi.picco_lavoratori(fasi)) if fasi else ""),
    ])
    stile.banda(doc, "Descrizione sintetica dell'opera")
    stile.testo(doc, c["descrizione"], "descrizione sintetica dell'opera, con le scelte progettuali, "
                                       "architettoniche, strutturali e tecnologiche", CANTIERE, OBBLIGATORIO)
    for n, foto in enumerate(foto_cantiere(repo), 1):
        stile.immagine(doc, foto, 11, f"Foto {n} - area del cantiere")

    stile.capitolo(doc, "Soggetti con compiti di sicurezza", "Allegato XV punto 2.1.2, lettera b), e artt. 89-93")
    for s in soggetti:
        if s["nome"].strip():
            _soggetto(doc, s)
    for ruolo, dato, livello in ((anagrafiche.COMMITTENTE, "committente", OBBLIGATORIO),
                                 (anagrafiche.CSP, "coordinatore per la progettazione (CSP)", OBBLIGATORIO),
                                 (anagrafiche.CSE, "coordinatore per l'esecuzione (CSE), se già designato",
                                  CONSIGLIATO)):
        if ruolo not in per_ruolo:
            p = doc.add_paragraph()
            stile._run(p, f"{ruolo}: ", grassetto=True)
            segnaposto(doc, p, Manca(dato, SOGGETTI, livello))

    stile.capitolo(doc, "Imprese esecutrici e lavoratori autonomi", "Allegato XV punto 2.1.2, lettera b)")
    if imprese:
        doc.add_paragraph("Imprese e lavoratori autonomi previsti, con i datori di lavoro. L'elenco si completa "
                          "prima dell'inizio dei lavori, quando le imprese sono note.")
        stile.tabella_colorata(doc, ["Ragione sociale", "Ruolo", "Datore di lavoro", "P. IVA", "Lavori affidati"], [
            [i["ragione_sociale"], i["tipo"],
             i["datore_lavoro"] or Manca("datore di lavoro di " + (i["ragione_sociale"] or "un'impresa"), IMPRESE,
                                         CONSIGLIATO),
             i["partita_iva"], i["tipologia_lavori"]] for i in imprese], larghezze=[4.2, 2.6, 3.6, 2.6, 4.4])
    else:
        stile.testo(doc, "", "imprese esecutrici e lavoratori autonomi, da indicare prima dell'inizio dei lavori",
                    IMPRESE, CONSIGLIATO)

    # ===== Parte 2 =====
    stile.parte(doc, "2", "Rischi, scelte e misure",
                "Valutazione dei rischi e scelte progettuali e organizzative per l'area di cantiere, "
                "l'organizzazione del cantiere e le lavorazioni (Allegato XV punto 2.1.2, lettere c e d, e "
                "punto 2.2).")

    stile.capitolo(doc, "Metodo di valutazione dei rischi", "Allegato XV punto 2.1.2, lettera c)")
    doc.add_paragraph("I rischi concreti sono individuati con riferimento all'area, all'organizzazione del cantiere, "
                      "alle lavorazioni e alle loro interferenze. Ogni rischio è valutato come prodotto R = P × D "
                      "della probabilità P (da 1, improbabile, a 4, altamente probabile) e del danno D (da 1, lieve, "
                      "a 4, gravissimo).")
    _matrice_rischio(doc)

    stile.capitolo(doc, "Area di cantiere", "Allegato XV punto 2.1.2, lettera d), punto 1, e punto 2.2.1")
    stile.testo(doc, testi["area"], "caratteristiche dell'area di cantiere, linee aeree e condutture sotterranee, "
                                    "rischi trasmessi dall'ambiente esterno e rischi che il cantiere comporta per "
                                    "l'area circostante", RELAZIONE, OBBLIGATORIO)

    stile.capitolo(doc, "Organizzazione del cantiere", "Allegato XV punto 2.1.2, lettera d), punto 2, e punto 2.2.2")
    stile.testo(doc, testi["organizzazione"], "recinzione, accessi e segnalazioni, servizi igienico-assistenziali, "
                                              "viabilità, impianti, zone di carico, scarico, deposito e stoccaggio",
                RELAZIONE, OBBLIGATORIO)

    stile.capitolo(doc, titoli["scelte"], "Allegato XV punto 2.1.2, lettera d)")
    stile.testo(doc, testi["scelte"], "scelte progettuali e organizzative, procedure e misure preventive e "
                                      "protettive generali", RELAZIONE, CONSIGLIATO)

    stile.capitolo(doc, "Lavorazioni: rischi e misure per fase", "Allegato XV punto 2.1.2, lettera d), punto 3, e "
                                                                "punto 2.2.3")
    if not fasi:
        stile.testo(doc, "", "fasi di lavoro con i loro rischi", FASI, OBBLIGATORIO)
    lavorazione_corrente = object()
    for f in fasi:
        if f["lavorazione"] != lavorazione_corrente:
            lavorazione_corrente = f["lavorazione"]
            gruppo = [g for g in fasi if g["lavorazione"] == lavorazione_corrente]
            stile.riquadro(doc, lavorazione_corrente or "Altre fasi di lavoro", "lavorazione")
            if lavorazione_corrente:
                p = doc.add_paragraph()
                stile._run(p, "La lavorazione è suddivisa nelle seguenti fasi: ", grassetto=True)
                p.add_run("; ".join(nome_fase(g) for g in gruppo) + ".")
        h = doc.add_heading(level=3)
        stile._run(h, nome_fase(f))
        attrezzature = repo.elenco("attrezzature", fase_id=f["id"])
        periodo_fase = (f"dal {data_it(f['data_inizio'])} al {data_it(f['data_fine'])}"
                        if f["data_inizio"] and f["data_fine"] else
                        Manca(f"date di inizio e fine della fase {nome_fase(f)}", FASI, OBBLIGATORIO))
        stile.scheda(doc, [
            ("Impresa", nomi_imprese.get(f["impresa_id"]) or
             Manca(f"impresa esecutrice della fase {nome_fase(f)}", FASI, CONSIGLIATO)),
            ("Periodo", periodo_fase),
            ("Zona del cantiere", f["zona"]),
            ("Lavoratori previsti", str(f["lavoratori"]) if f.get("lavoratori") else ""),
            ("Macchine, attrezzi e opere provvisionali", ", ".join(a["nome"] for a in attrezzature)),
            ("Procedure richieste ai POS", f["procedure_psc"]),
        ], 5.0)
        if f["dettaglio"]:
            stile.testo(doc, f["dettaglio"])
        rischi_fase = [r for r in rischi if r["fase_id"] == f["id"]]
        if rischi_fase:
            tabella_rischi(doc, rischi_fase)
            dpi_con_icone(doc, [r["dpi"] for r in rischi_fase], "DPI previsti:")
        else:
            stile.testo(doc, "", f"rischi della fase {nome_fase(f)} (nessun rischio valutato)", RISCHI, OBBLIGATORIO)

    # ===== Parte 3 =====
    stile.parte(doc, "3", "Coordinamento",
                "Interferenze tra le lavorazioni, uso comune di apprestamenti e servizi, cooperazione tra le imprese "
                "ed emergenze (Allegato XV punto 2.1.2, lettere e, f, g, h, e punto 2.3).")

    stile.capitolo(doc, "Interferenze tra le lavorazioni e prescrizioni operative",
                   "Allegato XV punto 2.1.2, lettera e), e punti 2.3.1-2.3.2")
    if elenco_interferenze:
        doc.add_paragraph("Dal cronoprogramma risultano le seguenti lavorazioni contemporanee di imprese diverse, "
                          "con la gravità (livello di rischio più alto tra le due fasi) e le prescrizioni per "
                          "eliminarle o ridurle.")
        t = stile.tabella_colorata(doc, ["Fase", "Fase interferente", "Periodo", "Gravità", "Prescrizioni operative"], [
            [nome_fase(i.fase_a), nome_fase(i.fase_b), f"{data_it(i.inizio)}\n{data_it(i.fine)}",
             f"{i.gravita}\n{analisi.classe_rischio(i.gravita)}" if i.gravita else "-",
             prescrizioni.get(i.chiave) or PRESCRIZIONE_GENERICA] for i in elenco_interferenze],
            8, larghezze=[3.6, 3.6, 2.0, 1.9, 6.3])
        for riga, i in zip(t.rows[1:], elenco_interferenze):
            if i.gravita:
                stile.colora_livello(riga.cells[3], _livello(i.gravita))
        for i in elenco_interferenze:
            if i.gravita >= 6 and not prescrizioni.get(i.chiave, "").strip():
                segnaposto(doc, doc.add_paragraph(), Manca(f"prescrizione specifica per l'interferenza grave tra {nome_fase(i.fase_a)} "
                                         f"e {nome_fase(i.fase_b)}", INTERFERENZE, CONSIGLIATO))
    else:
        doc.add_paragraph("Dal cronoprogramma non risultano lavorazioni contemporanee di imprese diverse. Le "
                          "eventuali variazioni del programma sono valutate dal coordinatore per l'esecuzione.")

    stile.capitolo(doc, titoli["uso_comune"], "Allegato XV punto 2.1.2, lettera f), e punto 2.3.4")
    stile.testo(doc, testi["uso_comune"], "misure di coordinamento per l'uso comune di apprestamenti, attrezzature, "
                                          "infrastrutture, mezzi e servizi di protezione collettiva", RELAZIONE,
                OBBLIGATORIO)

    stile.capitolo(doc, titoli["cooperazione"], "Allegato XV punto 2.1.2, lettera g), e punto 2.3.5")
    stile.testo(doc, testi["cooperazione"], "modalità di cooperazione, coordinamento e reciproca informazione tra i "
                                            "datori di lavoro e i lavoratori autonomi", RELAZIONE, OBBLIGATORIO)

    stile.capitolo(doc, "Primo soccorso, antincendio ed evacuazione", "Allegato XV punto 2.1.2, lettera h)")
    stile.testo(doc, testi["emergenze"], "organizzazione del primo soccorso, antincendio ed evacuazione dei "
                                         "lavoratori", RELAZIONE, OBBLIGATORIO)
    stile.banda(doc, "Numeri di emergenza")
    stile.scheda(doc, [(nome, numero) for nome, numero in NUMERI_EMERGENZA])
    stile.banda(doc, "Strutture del territorio")
    stile.testo(doc, testi["telefoni"], "telefoni e indirizzi delle strutture del territorio per il pronto "
                                        "soccorso e la prevenzione incendi", RELAZIONE, CONSIGLIATO)

    # ===== Parte 4 =====
    stile.parte(doc, "4", "Tempi e costi",
                "Durata delle lavorazioni e cronoprogramma, stima dei costi della sicurezza (Allegato XV punto "
                "2.1.2, lettere i e l, e punto 4).")

    stile.capitolo(doc, "Cronoprogramma dei lavori", "Allegato XV punto 2.1.2, lettera i)")
    if fasi:
        stile.scheda(doc, [
            ("Inizio e fine dei lavori", f"dal {data_it(periodo[0])} al {data_it(periodo[1])}" if periodo else ""),
            ("Durata presunta", f"{analisi.giorni_lavorativi(*periodo)} giorni lavorativi" if periodo else ""),
            ("Entità presunta del cantiere", f"{analisi.uomini_giorno(fasi)} uomini-giorno"),
            ("Numero massimo presunto di lavoratori", str(analisi.picco_lavoratori(fasi))),
        ])
        _programma(doc, fasi, nomi_imprese)
    _diagramma_gantt(doc, fasi, nomi_imprese, livelli, elenco_interferenze)

    stile.capitolo(doc, "Stima dei costi della sicurezza", "Allegato XV punto 2.1.2, lettera l), e punto 4")
    if costi:
        righe = [[c_["codice"], c_["descrizione"], c_["unita"], f"{c_['quantita']:g}".replace(".", ","),
                  euro(c_["prezzo_unitario"]), euro(c_["quantita"] * c_["prezzo_unitario"])] for c_ in costi]
        righe.append([" ", "Totale dei costi della sicurezza (non soggetti a ribasso)", " ", " ", " ",
                      euro(analisi.totale_costi(costi))])
        t = stile.tabella_colorata(doc, ["Codice", "Descrizione", "U.M.", "Quantità", "Prezzo unit.", "Importo"],
                                   righe, 8.5, larghezze=[1.8, 7.4, 1.4, 1.8, 2.4, 2.6])
        ultima_riga = t.rows[-1]
        for cella in ultima_riga.cells:
            stile.ombreggia_cella(cella, stile.TINTA)
            for run in cella.paragraphs[0].runs:
                run.bold = True
                run.font.size = Pt(9)
        stile.nota(doc, "I costi della sicurezza sono compresi nell'importo totale dei lavori e non sono soggetti a "
                        "ribasso nelle offerte delle imprese esecutrici (Allegato XV punto 4.1.4).")
    else:
        stile.testo(doc, "", "stima analitica dei costi della sicurezza (Allegato XV punto 4)", COSTI, OBBLIGATORIO)

    # --- allegati e firme ---
    stile.capitolo(doc, "Allegati e firme")
    elaborati = repo.elenco("elaborati")
    allegati = ["planimetria del cantiere con l'organizzazione delle aree (Allegato XV punto 2.1.4);"]
    allegati += [f"{e['titolo']}" + (f" ({e['autore']})" if e.get("autore") else "") + ";" for e in elaborati]
    allegati.append("fascicolo con le caratteristiche dell'opera (art. 91, comma 1, lettera b).")
    doc.add_paragraph("Fanno parte integrante del presente piano:")
    stile.elenco_lettere(doc, allegati)
    doc.add_paragraph("Il coordinatore per la progettazione dichiara di aver redatto il presente piano di sicurezza "
                      "e coordinamento ai sensi dell'art. 100 e dell'Allegato XV del D.Lgs. 81/2008. Il committente "
                      "o il responsabile dei lavori lo trasmette a tutte le imprese invitate a presentare offerte; "
                      "le imprese esecutrici ne prendono visione e lo mettono a disposizione dei rappresentanti dei "
                      "lavoratori per la sicurezza almeno dieci giorni prima dell'inizio dei lavori (art. 102).")
    p = doc.add_paragraph(f"{c['comune'] or ''}, {data_documento}".strip(", "))
    stile._spaziatura(p, 8, 8)
    firme = [("Il coordinatore per la progettazione", csp["nome"] if csp else ""),
             ("Il committente" if not responsabile else "Il responsabile dei lavori",
              (responsabile or committente or {}).get("nome", ""))]
    cse = per_ruolo.get(anagrafiche.CSE)
    if cse:
        firme.append(("Per presa visione, il coordinatore per l'esecuzione", cse["nome"]))
    for i in imprese:
        if i["ragione_sociale"].strip() and not anagrafiche.autonomo(i):
            firme.append((f"Per presa visione e accettazione, il datore di lavoro di {i['ragione_sociale']}",
                          i["datore_lavoro"]))
    stile.firme(doc, firme)

    return salva(doc, destinazione)
