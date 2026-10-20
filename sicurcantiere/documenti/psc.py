"""Generazione del Piano di Sicurezza e Coordinamento in formato DOCX."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Any

from docx.shared import Pt

from sicurcantiere import anagrafiche, analisi
from sicurcantiere.documenti.comune import (
    data_it,
    euro,
    firma,
    frontespizio,
    indirizzo_cantiere,
    nome_fase,
    nuovo_documento,
    ombreggia,
    tabella,
    tabella_voci,
    testo_o_segnaposto,
)
from sicurcantiere.relazione import SEZIONI
from sicurcantiere.repository import Repository

COLORE_BARRA = "4F81BD"
COLORE_INTERFERENZA = "C0504D"
MAX_COLONNE_CRONO = 26
PRESCRIZIONE_GENERICA = (
    "Sfasamento spaziale delle lavorazioni o, se non possibile, sfasamento temporale; "
    "verifica del CSE prima dell'inizio."
)


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
    periodo = analisi.periodo_lavori(fasi)
    if not periodo:
        testo_o_segnaposto(doc, "")
        return
    colonne = _colonne_cronoprogramma(*periodo)
    interferenti = {f["id"] for i in interferenze for f in (i.fase_a, i.fase_b)}
    t = doc.add_table(rows=1, cols=len(colonne) + 2)
    t.style = "Table Grid"
    intestazione = t.rows[0].cells
    intestazione[0].text = "Fase"
    intestazione[1].text = "Impresa"
    for cella, (_, _, etichetta) in zip(intestazione[2:], colonne):
        cella.text = etichetta
    for cella in intestazione:
        for run in cella.paragraphs[0].runs:
            run.bold = True
            run.font.size = Pt(6)
    for f in fasi:
        inizio, fine = analisi.data(f["data_inizio"]), analisi.data(f["data_fine"])
        celle = t.add_row().cells
        celle[0].text = nome_fase(f)
        celle[1].text = imprese.get(f["impresa_id"], "")
        for cella in celle[:2]:
            for run in cella.paragraphs[0].runs:
                run.font.size = Pt(7)
        if not (inizio and fine):
            continue
        colore = COLORE_INTERFERENZA if f["id"] in interferenti else COLORE_BARRA
        for cella, (da, a, _) in zip(celle[2:], colonne):
            if inizio <= a and fine >= da:
                ombreggia(cella, colore)
    doc.add_paragraph(
        "In rosso le fasi con sovrapposizioni temporali tra imprese diverse (interferenze)."
    ).runs[0].italic = True


def genera_psc(repo: Repository, destinazione: str | Path) -> Path:
    cantiere = repo.cantiere()
    soggetti = anagrafiche.soggetti(repo)
    imprese = repo.elenco("imprese")
    fasi = repo.elenco("fasi")
    costi = repo.elenco("costi")
    rischi = repo.rischi()
    nomi_imprese = {i["id"]: i["ragione_sociale"] for i in imprese}
    livelli = analisi.livelli_fasi(rischi)
    elenco_interferenze = analisi.interferenze(fasi, livelli)
    prescrizioni = repo.prescrizioni()

    doc = nuovo_documento()
    frontespizio(doc, repo, "PIANO DI SICUREZZA E COORDINAMENTO",
                 "art. 100 e Allegato XV del D.Lgs. 9 aprile 2008, n. 81", "PSC")

    # a) Identificazione e descrizione dell'opera
    doc.add_heading("1. Identificazione e descrizione dell'opera", 1)
    periodo = analisi.periodo_lavori(fasi)
    tabella_voci(doc, [
        ("Opera", cantiere["nome"]),
        ("Natura dell'opera", cantiere["natura_opera"]),
        ("Indirizzo del cantiere", indirizzo_cantiere(cantiere)),
        ("Importo presunto dei lavori", euro(cantiere["importo_lavori"])),
        ("Inizio lavori presunto", data_it(periodo[0]) if periodo else "-"),
        ("Fine lavori presunta", data_it(periodo[1]) if periodo else "-"),
        ("Entità presunta del cantiere", f"{analisi.uomini_giorno(fasi)} uomini-giorno"),
        ("Numero massimo presunto di lavoratori", str(analisi.picco_lavoratori(fasi))),
    ])
    doc.add_heading("Descrizione sintetica dell'opera", 2)
    testo_o_segnaposto(doc, cantiere["descrizione"])

    # b) Soggetti
    doc.add_heading("2. Soggetti con compiti di sicurezza", 1)
    tabella(doc, ["Ruolo", "Nominativo", "Codice fiscale", "Recapiti"], [
        [s["ruolo"], s["nome"], s["codice_fiscale"],
         " - ".join(v for v in (s["indirizzo"], s["telefono"], s["email"]) if v)]
        for s in soggetti
    ])
    doc.add_heading("Imprese e lavoratori autonomi", 2)
    tabella(doc, ["Ragione sociale", "Tipo", "P. IVA", "Referente", "Telefono"], [
        [i["ragione_sociale"], i["tipo"], i["partita_iva"], i["referente"], i["telefono"]]
        for i in imprese
    ])

    # c) Area e organizzazione
    testi = {chiave: repo.testo(chiave) for chiave, _ in SEZIONI}
    numero = 3
    for chiave, titolo_sezione in SEZIONI[:3]:
        doc.add_heading(f"{numero}. {titolo_sezione}", 1)
        testo_o_segnaposto(doc, testi[chiave])
        numero += 1

    # c-d) Rischi per fase
    doc.add_heading(f"{numero}. Analisi e valutazione dei rischi per fase di lavoro", 1)
    numero += 1
    doc.add_paragraph(
        "Livello di rischio R = P x D, con probabilità P e danno D da 1 a 4. "
        "Classi: 1-2 basso, 3-4 medio, 6-8 alto, 9-16 molto alto."
    )
    for f in fasi:
        doc.add_heading(nome_fase(f), 2)
        p = doc.add_paragraph()
        p.add_run("Impresa: ").bold = True
        p.add_run(nomi_imprese.get(f["impresa_id"], "da definire"))
        p.add_run("   Periodo: ").bold = True
        p.add_run(f"{data_it(f['data_inizio'])} - {data_it(f['data_fine'])}")
        if f["zona"]:
            p.add_run("   Zona: ").bold = True
            p.add_run(f["zona"])
        attrezzature = repo.elenco("attrezzature", fase_id=f["id"])
        if attrezzature:
            p = doc.add_paragraph()
            p.add_run("Macchine, attrezzi e opere provvisionali: ").bold = True
            p.add_run(", ".join(a["nome"] for a in attrezzature))
        rischi_fase = [r for r in rischi if r["fase_id"] == f["id"]]
        if rischi_fase:
            righe = []
            for r in rischi_fase:
                livello = analisi.livello_rischio(r["probabilita"], r["danno"])
                descrizione = f"{r['descrizione']} ({r['fonte']})" if r["fonte"] else r["descrizione"]
                righe.append([
                    descrizione, f"{r['probabilita']}x{r['danno']}={livello}",
                    analisi.classe_rischio(livello), r["misure"], r["dpi"],
                ])
            tabella(doc, ["Rischio", "PxD", "Classe", "Misure di prevenzione e protezione", "DPI"], righe)
        else:
            testo_o_segnaposto(doc, "")

    # e) Interferenze
    doc.add_heading(f"{numero}. Interferenze tra le lavorazioni e prescrizioni operative", 1)
    numero += 1
    if elenco_interferenze:
        tabella(doc, ["Fase", "Fase interferente", "Periodo", "Gravità", "Prescrizioni"], [
            [
                nome_fase(i.fase_a), nome_fase(i.fase_b),
                f"{data_it(i.inizio)} - {data_it(i.fine)}",
                f"{i.gravita} {analisi.classe_rischio(i.gravita)}" if i.gravita else "-",
                prescrizioni.get(i.chiave) or PRESCRIZIONE_GENERICA,
            ]
            for i in elenco_interferenze
        ])
    else:
        doc.add_paragraph("Dal cronoprogramma non risultano lavorazioni contemporanee di imprese diverse.")

    # f-h) Coordinamento ed emergenze
    for chiave, titolo_sezione in SEZIONI[3:]:
        doc.add_heading(f"{numero}. {titolo_sezione}", 1)
        testo_o_segnaposto(doc, testi[chiave])
        numero += 1

    # i) Cronoprogramma
    doc.add_heading(f"{numero}. Cronoprogramma dei lavori", 1)
    numero += 1
    _cronoprogramma(doc, fasi, nomi_imprese, elenco_interferenze)

    # l) Costi
    doc.add_heading(f"{numero}. Stima dei costi della sicurezza", 1)
    righe_costi = [
        [c["codice"], c["descrizione"], c["unita"],
         f"{c['quantita']:g}".replace(".", ","), euro(c["prezzo_unitario"]),
         euro(c["quantita"] * c["prezzo_unitario"])]
        for c in costi
    ]
    righe_costi.append(["", "TOTALE COSTI DELLA SICUREZZA (non soggetti a ribasso)", "", "", "",
                        euro(analisi.totale_costi(costi))])
    t = tabella(doc, ["Codice", "Descrizione", "U.M.", "Quantità", "Prezzo unit.", "Importo"], righe_costi)
    for run in t.rows[-1].cells[1].paragraphs[0].runs + t.rows[-1].cells[5].paragraphs[0].runs:
        run.bold = True

    firma(doc, "Il Coordinatore per la sicurezza in fase di progettazione")

    destinazione = Path(destinazione)
    doc.save(destinazione)
    return destinazione
