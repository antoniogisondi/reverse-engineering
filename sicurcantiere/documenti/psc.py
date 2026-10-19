"""Generazione del Piano di Sicurezza e Coordinamento in formato DOCX."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Any

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

from sicurcantiere import analisi
from sicurcantiere.relazione import SEZIONI
from sicurcantiere.repository import Repository

COLORE_BARRA = "4F81BD"
COLORE_INTERFERENZA = "C0504D"
MAX_COLONNE_CRONO = 26


def euro(valore: float) -> str:
    testo = f"{valore:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"€ {testo}"


def data_it(valore: str | date | None) -> str:
    d = analisi.data(valore) if isinstance(valore, str) or valore is None else valore
    return d.strftime("%d/%m/%Y") if d else "-"


def _ombreggia(cella, colore: str) -> None:
    proprieta = cella._tc.get_or_add_tcPr()
    sfondo = OxmlElement("w:shd")
    sfondo.set(qn("w:val"), "clear")
    sfondo.set(qn("w:color"), "auto")
    sfondo.set(qn("w:fill"), colore)
    proprieta.append(sfondo)


def _tabella(doc, intestazioni: list[str], righe: list[list[str]]):
    t = doc.add_table(rows=1, cols=len(intestazioni))
    t.style = "Table Grid"
    for cella, testo in zip(t.rows[0].cells, intestazioni):
        cella.text = testo
        for run in cella.paragraphs[0].runs:
            run.bold = True
        _ombreggia(cella, "D9D9D9")
    for riga in righe:
        celle = t.add_row().cells
        for cella, testo in zip(celle, riga):
            cella.text = testo
    return t


def _testo_o_segnaposto(doc, testo: str) -> None:
    if testo.strip():
        for paragrafo in testo.strip().split("\n"):
            doc.add_paragraph(paragrafo)
    else:
        p = doc.add_paragraph()
        r = p.add_run("[Sezione da compilare]")
        r.italic = True


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


def _cronoprogramma(doc, fasi: list[dict[str, Any]], imprese: dict[int, str]) -> None:
    periodo = analisi.periodo_lavori(fasi)
    if not periodo:
        _testo_o_segnaposto(doc, "")
        return
    colonne = _colonne_cronoprogramma(*periodo)
    interferenti = {
        f["id"] for i in analisi.interferenze(fasi) for f in (i.fase_a, i.fase_b)
    }
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
        celle[0].text = f"{f['codice']} {f['descrizione']}".strip()
        celle[1].text = imprese.get(f["impresa_id"], "")
        for cella in celle[:2]:
            for run in cella.paragraphs[0].runs:
                run.font.size = Pt(7)
        if not (inizio and fine):
            continue
        colore = COLORE_INTERFERENZA if f["id"] in interferenti else COLORE_BARRA
        for cella, (da, a, _) in zip(celle[2:], colonne):
            if inizio <= a and fine >= da:
                _ombreggia(cella, colore)
    doc.add_paragraph(
        "In rosso le fasi con sovrapposizioni temporali tra imprese diverse (interferenze)."
    ).runs[0].italic = True


def genera_psc(repo: Repository, destinazione: str | Path) -> Path:
    cantiere = repo.cantiere()
    soggetti = repo.elenco("soggetti")
    imprese = repo.elenco("imprese")
    fasi = repo.elenco("fasi")
    costi = repo.elenco("costi")
    nomi_imprese = {i["id"]: i["ragione_sociale"] for i in imprese}

    doc = Document()
    for sezione in doc.sections:
        sezione.left_margin = sezione.right_margin = Cm(2)
    doc.styles["Normal"].font.name = "Calibri"
    doc.styles["Normal"].font.size = Pt(10)

    # Frontespizio
    titolo = doc.add_heading("PIANO DI SICUREZZA E COORDINAMENTO", 0)
    titolo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph("art. 100 e Allegato XV del D.Lgs. 9 aprile 2008, n. 81")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()
    for etichetta, valore in [
        ("Opera", cantiere["nome"]),
        ("Natura dell'opera", cantiere["natura_opera"]),
        ("Indirizzo del cantiere", ", ".join(
            v for v in (cantiere["indirizzo"], cantiere["comune"], cantiere["provincia"]) if v
        )),
        ("Data", data_it(date.today())),
    ]:
        p = doc.add_paragraph()
        p.add_run(f"{etichetta}: ").bold = True
        p.add_run(valore or "-")
    doc.add_page_break()

    # a) Identificazione e descrizione dell'opera
    doc.add_heading("1. Identificazione e descrizione dell'opera", 1)
    periodo = analisi.periodo_lavori(fasi)
    ug = analisi.uomini_giorno(fasi)
    _tabella(doc, ["Voce", "Valore"], [
        ["Opera", cantiere["nome"]],
        ["Natura dell'opera", cantiere["natura_opera"]],
        ["Indirizzo", cantiere["indirizzo"]],
        ["Comune", f"{cantiere['comune']} ({cantiere['provincia']})" if cantiere["provincia"] else cantiere["comune"]],
        ["Importo presunto dei lavori", euro(cantiere["importo_lavori"])],
        ["Inizio lavori presunto", data_it(periodo[0]) if periodo else "-"],
        ["Fine lavori presunta", data_it(periodo[1]) if periodo else "-"],
        ["Entità presunta del cantiere", f"{ug} uomini-giorno"],
    ])
    doc.add_heading("Descrizione sintetica dell'opera", 2)
    _testo_o_segnaposto(doc, cantiere["descrizione"])

    # b) Soggetti
    doc.add_heading("2. Soggetti con compiti di sicurezza", 1)
    _tabella(doc, ["Ruolo", "Nominativo", "Codice fiscale", "Recapiti"], [
        [s["ruolo"], s["nome"], s["codice_fiscale"],
         " - ".join(v for v in (s["indirizzo"], s["telefono"], s["email"]) if v)]
        for s in soggetti
    ])
    doc.add_heading("Imprese e lavoratori autonomi", 2)
    _tabella(doc, ["Ragione sociale", "Tipo", "P. IVA", "Referente", "Telefono"], [
        [i["ragione_sociale"], i["tipo"], i["partita_iva"], i["referente"], i["telefono"]]
        for i in imprese
    ])

    # c) Area e organizzazione
    testi = {chiave: repo.testo(chiave) for chiave, _ in SEZIONI}
    numero = 3
    for chiave, titolo_sezione in SEZIONI[:3]:
        doc.add_heading(f"{numero}. {titolo_sezione}", 1)
        _testo_o_segnaposto(doc, testi[chiave])
        numero += 1

    # c-d) Rischi per fase
    doc.add_heading(f"{numero}. Analisi e valutazione dei rischi per fase di lavoro", 1)
    numero += 1
    doc.add_paragraph(
        "Livello di rischio R = P x D, con probabilità P e danno D da 1 a 4. "
        "Classi: 1-2 basso, 3-4 medio, 6-8 alto, 9-16 molto alto."
    )
    for f in fasi:
        doc.add_heading(f"{f['codice']} {f['descrizione']}".strip(), 2)
        p = doc.add_paragraph()
        p.add_run("Impresa: ").bold = True
        p.add_run(nomi_imprese.get(f["impresa_id"], "da definire"))
        p.add_run("   Periodo: ").bold = True
        p.add_run(f"{data_it(f['data_inizio'])} - {data_it(f['data_fine'])}")
        rischi = repo.elenco("rischi", fase_id=f["id"])
        if rischi:
            righe = []
            for r in rischi:
                livello = analisi.livello_rischio(r["probabilita"], r["danno"])
                righe.append([
                    r["descrizione"], f"{r['probabilita']}x{r['danno']}={livello}",
                    analisi.classe_rischio(livello), r["misure"], r["dpi"],
                ])
            _tabella(doc, ["Rischio", "PxD", "Classe", "Misure di prevenzione e protezione", "DPI"], righe)
        else:
            _testo_o_segnaposto(doc, "")

    # e) Interferenze
    doc.add_heading(f"{numero}. Interferenze tra le lavorazioni e prescrizioni operative", 1)
    numero += 1
    elenco_interferenze = analisi.interferenze(fasi)
    if elenco_interferenze:
        _tabella(doc, ["Fase", "Fase interferente", "Periodo di sovrapposizione", "Prescrizione"], [
            [
                f"{i.fase_a['codice']} {i.fase_a['descrizione']}".strip(),
                f"{i.fase_b['codice']} {i.fase_b['descrizione']}".strip(),
                f"{data_it(i.inizio)} - {data_it(i.fine)}",
                "Sfasamento spaziale delle lavorazioni o, se non possibile, sfasamento temporale; "
                "verifica del CSE prima dell'inizio.",
            ]
            for i in elenco_interferenze
        ])
    else:
        doc.add_paragraph("Dal cronoprogramma non risultano lavorazioni contemporanee di imprese diverse.")

    # f-h) Coordinamento ed emergenze
    for chiave, titolo_sezione in SEZIONI[3:]:
        doc.add_heading(f"{numero}. {titolo_sezione}", 1)
        _testo_o_segnaposto(doc, testi[chiave])
        numero += 1

    # i) Cronoprogramma
    doc.add_heading(f"{numero}. Cronoprogramma dei lavori", 1)
    numero += 1
    _cronoprogramma(doc, fasi, nomi_imprese)

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
    t = _tabella(doc, ["Codice", "Descrizione", "U.M.", "Quantità", "Prezzo unit.", "Importo"], righe_costi)
    for run in t.rows[-1].cells[1].paragraphs[0].runs + t.rows[-1].cells[5].paragraphs[0].runs:
        run.bold = True

    # Firme
    doc.add_paragraph()
    doc.add_paragraph("Il Coordinatore per la sicurezza in fase di progettazione")
    doc.add_paragraph("_______________________________")

    destinazione = Path(destinazione)
    doc.save(destinazione)
    return destinazione
