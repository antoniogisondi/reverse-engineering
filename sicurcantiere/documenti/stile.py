"""Impaginazione dei documenti: stili, copertina, titoli dei capitoli, schede di dati, immagini.

Impostazione grafica di SicurCantiere: capitoli su banda grigia con il riferimento di legge
in blu, dati in elenchi etichetta-valore, lavorazioni e fasi in riquadri colorati, cartelli e
icone dei DPI, piè di pagina con opera, comune e numero di pagina.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

BLU = RGBColor(0x1F, 0x4E, 0x8C)
BLU_SCURO = RGBColor(0x1F, 0x3A, 0x5F)
ROSSO = RGBColor(0xB0, 0x1E, 0x23)
GRIGIO = RGBColor(0x59, 0x59, 0x59)
ARANCIO = "E8792B"
GRIGIO_BANDA, GRIGIO_CHIARO, AZZURRO, GIALLO = "D9D9D9", "F2F2F2", "DCE6F2", "FFD966"


# --- utilità XML ---

def _ombra(elemento_pr, colore: str) -> None:
    sfondo = OxmlElement("w:shd")
    sfondo.set(qn("w:val"), "clear")
    sfondo.set(qn("w:color"), "auto")
    sfondo.set(qn("w:fill"), colore)
    elemento_pr.append(sfondo)


def _bordo_paragrafo(paragrafo, lati: tuple[str, ...], colore: str, spessore: int = 8) -> None:
    pr = paragrafo._p.get_or_add_pPr()
    bordi = OxmlElement("w:pBdr")
    for lato in lati:
        b = OxmlElement(f"w:{lato}")
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), str(spessore))
        b.set(qn("w:space"), "4")
        b.set(qn("w:color"), colore)
        bordi.append(b)
    pr.append(bordi)


def ombreggia_paragrafo(paragrafo, colore: str) -> None:
    _ombra(paragrafo._p.get_or_add_pPr(), colore)


def ombreggia_cella(cella, colore: str) -> None:
    _ombra(cella._tc.get_or_add_tcPr(), colore)



def larghezze_colonne(t, larghezze_cm: list[float]) -> None:
    """Fissa la larghezza delle colonne (griglia e celle), rispettata anche da LibreOffice."""
    t.autofit = False
    griglia = t._tbl.tblGrid
    for col, cm in zip(griglia.findall(qn("w:gridCol")), larghezze_cm):
        col.set(qn("w:w"), str(int(Cm(cm).twips)))
    for riga in t.rows:
        for cella, cm in zip(riga.cells, larghezze_cm):
            cella.width = Cm(cm)

def senza_bordi(tabella) -> None:
    pr = tabella._tbl.tblPr
    bordi = OxmlElement("w:tblBorders")
    for lato in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b = OxmlElement(f"w:{lato}")
        b.set(qn("w:val"), "nil")
        bordi.append(b)
    pr.append(bordi)


def bordi_cella(cella, colore: str = "000000", spessore: int = 12, lati=("top", "left", "bottom", "right")) -> None:
    pr = cella._tc.get_or_add_tcPr()
    bordi = OxmlElement("w:tcBorders")
    for lato in lati:
        b = OxmlElement(f"w:{lato}")
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), str(spessore))
        b.set(qn("w:color"), colore)
        bordi.append(b)
    pr.append(bordi)


def campo(paragrafo, istruzione: str, testo: str = "") -> None:
    """Campo di Word (numero di pagina, indice...) aggiornato all'apertura del documento."""
    run = paragrafo.add_run()
    inizio = OxmlElement("w:fldChar")
    inizio.set(qn("w:fldCharType"), "begin")
    istr = OxmlElement("w:instrText")
    istr.set(qn("xml:space"), "preserve")
    istr.text = istruzione
    separa = OxmlElement("w:fldChar")
    separa.set(qn("w:fldCharType"), "separate")
    segnaposto = OxmlElement("w:t")
    segnaposto.text = testo
    fine = OxmlElement("w:fldChar")
    fine.set(qn("w:fldCharType"), "end")
    for e in (inizio, istr, separa, segnaposto, fine):
        run._r.append(e)


def aggiorna_campi_all_apertura(doc) -> None:
    impostazioni = doc.settings.element
    elemento = OxmlElement("w:updateFields")
    elemento.set(qn("w:val"), "true")
    impostazioni.append(elemento)


# --- stili del documento ---

def imposta_stili(doc) -> None:
    normale = doc.styles["Normal"]
    normale.font.name = "Calibri"
    normale.font.size = Pt(10)
    normale.paragraph_format.space_after = Pt(3)

    h1 = doc.styles["Heading 1"]
    h1.font.name, h1.font.size, h1.font.bold = "Calibri", Pt(15), True
    h1.font.color.rgb = RGBColor(0x26, 0x26, 0x26)
    h1.font.all_caps = True
    h1.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    h1.paragraph_format.space_before = Pt(0)
    h1.paragraph_format.space_after = Pt(2)
    h1.paragraph_format.page_break_before = True
    h1.paragraph_format.keep_with_next = True
    _ombra(h1.element.get_or_add_pPr(), GRIGIO_BANDA)

    h2 = doc.styles["Heading 2"]
    h2.font.name, h2.font.size, h2.font.bold = "Calibri", Pt(12.5), True
    h2.font.color.rgb = BLU_SCURO
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    h2.paragraph_format.keep_with_next = True

    h3 = doc.styles["Heading 3"]
    h3.font.name, h3.font.size, h3.font.bold = "Calibri", Pt(11), True
    h3.font.color.rgb = BLU
    h3.paragraph_format.space_before = Pt(10)
    h3.paragraph_format.space_after = Pt(3)
    h3.paragraph_format.keep_with_next = True


def imposta_pagina(doc, piede: str) -> None:
    """Margini A4 e piè di pagina con descrizione dell'opera e numero di pagina."""
    for sezione in doc.sections:
        sezione.page_height, sezione.page_width = Cm(29.7), Cm(21)
        sezione.left_margin = sezione.right_margin = Cm(1.8)
        sezione.top_margin, sezione.bottom_margin = Cm(1.6), Cm(1.8)
        sezione.different_first_page_header_footer = True  # copertina senza piè di pagina
        p = sezione.footer.paragraphs[0]
        p.text = ""
        _bordo_paragrafo(p, ("top",), "7F7F7F", 6)
        r = p.add_run(piede)
        r.italic, r.font.size, r.font.color.rgb = True, Pt(7.5), GRIGIO
        p2 = sezione.footer.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r = p2.add_run("Pag. ")
        r.italic, r.font.size, r.font.color.rgb = True, Pt(8), GRIGIO
        campo(p2, "PAGE", "1")


# --- elementi ---

def capitolo(doc, titolo: str, riferimento: str = "", nuova_pagina: bool = True) -> None:
    """Titolo di capitolo su banda grigia, con il riferimento normativo in blu sotto."""
    h = doc.add_heading(titolo, 1)
    if not nuova_pagina:
        h.paragraph_format.page_break_before = False
    if riferimento:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(10)
        r = p.add_run(f"({riferimento})")
        r.font.size, r.font.color.rgb = Pt(9), BLU
    else:
        h.paragraph_format.space_after = Pt(10)


def banda(doc, testo: str) -> None:
    """Sottotitolo su banda grigia chiara (es. «DATI IMPRESA»)."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    ombreggia_paragrafo(p, GRIGIO_CHIARO)
    _bordo_paragrafo(p, ("bottom",), "A6A6A6", 4)
    r = p.add_run(testo)
    r.font.all_caps = True
    r.bold, r.font.size = True, Pt(9)


def scheda(doc, voci: list[tuple[str, Any]], larghezza_etichetta: float = 5.5) -> None:
    """Elenco etichetta-valore senza griglia, valori in grassetto; le voci vuote non compaiono."""
    voci = [(e, str(v)) for e, v in voci if v not in (None, "", "-")]
    if not voci:
        return
    t = doc.add_table(rows=0, cols=2)
    senza_bordi(t)
    for etichetta, valore in voci:
        celle = t.add_row().cells
        p = celle[0].paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(f"{etichetta}:")
        r.font.size = Pt(9.5)
        p = celle[1].paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(valore)
        r.bold, r.font.size = True, Pt(9.5)
    larghezze_colonne(t, [larghezza_etichetta, 17 - larghezza_etichetta])


def riquadro(doc, testo: str, sottotitolo: str = "", colore: str = "1F4E8C", sfondo: str = AZZURRO,
             livello: int = 2) -> None:
    """Titolo in riquadro colorato (lavorazioni e fasi), incluso nell'indice."""
    h = doc.add_heading(level=livello)
    h.paragraph_format.space_before = Pt(12)
    ombreggia_paragrafo(h, sfondo)
    _bordo_paragrafo(h, ("top", "left", "bottom", "right"), colore, 8)
    h.add_run(testo)
    if sottotitolo:
        r = h.add_run(f"  {sottotitolo}")
        r.font.size, r.bold = Pt(9), False


def elenco_lettere(doc, voci: list[str], grassetto_iniziale: bool = False) -> None:
    """Elenco a), b), c)... come nei piani di sicurezza."""
    for i, voce in enumerate(voci):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.6)
        p.paragraph_format.first_line_indent = Cm(-0.6)
        p.paragraph_format.space_after = Pt(1)
        lettera = chr(ord("a") + i) if i < 26 else str(i + 1)
        p.add_run(f"{lettera})  ").bold = True
        p.add_run(voce)


def nota(doc, testo: str) -> None:
    p = doc.add_paragraph()
    r = p.add_run(testo)
    r.italic, r.font.size, r.font.color.rgb = True, Pt(8.5), GRIGIO


def immagine(doc, percorso: str | Path, larghezza_cm: float = 12, didascalia: str = "") -> bool:
    if not percorso or not Path(percorso).is_file():
        return False
    try:
        doc.add_picture(str(percorso), width=Cm(larghezza_cm))
    except Exception:  # noqa: BLE001 - immagine non leggibile: si salta
        return False
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if didascalia:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(didascalia)
        r.italic, r.font.size, r.font.color.rgb = True, Pt(8.5), GRIGIO
    return True


def griglia_immagini(doc, voci: list[tuple[Path, str]], colonne: int = 4, lato_cm: float = 2.6,
                     dimensione_testo: float = 7.5) -> None:
    """Immagini con didascalia disposte in griglia (cartelli, DPI)."""
    voci = [(p, t) for p, t in voci if Path(p).is_file()]
    if not voci:
        return
    t = doc.add_table(rows=0, cols=colonne)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = "Table Grid"
    for i, (percorso, testo) in enumerate(voci):
        if i % colonne == 0:
            celle = t.add_row().cells
        cella = celle[i % colonne]
        p = cella.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(percorso), width=Cm(lato_cm))
        d = cella.add_paragraph()
        d.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = d.add_run(testo.upper())
        r.bold, r.font.size = True, Pt(dimensione_testo)


def icone_in_riga(paragrafo, percorsi: list[Path], lato_cm: float = 0.9) -> None:
    for percorso in percorsi:
        if Path(percorso).is_file():
            paragrafo.add_run().add_picture(str(percorso), width=Cm(lato_cm))
            paragrafo.add_run(" ")


def cartello_testo(doc, testo: str, sfondo: str = "C8102E") -> None:
    """Cartello di solo testo (es. divieto di accesso) come cella colorata a tutta larghezza."""
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    cella = t.rows[0].cells[0]
    cella.width = Cm(12)
    ombreggia_cella(cella, sfondo)
    p = cella.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(10)
    r = p.add_run(testo.upper())
    r.bold, r.font.size, r.font.color.rgb = True, Pt(20), RGBColor(0xFF, 0xFF, 0xFF)


def tabella_colorata(doc, intestazioni: list[str], righe: list[list[str]], dimensione: float = 9,
                     colore_intestazione: str = "1F4E8C", larghezze: list[float] | None = None):
    """Tabella con intestazione colorata e righe alternate."""
    t = doc.add_table(rows=1, cols=len(intestazioni))
    t.style = "Table Grid"
    for cella, testo in zip(t.rows[0].cells, intestazioni):
        ombreggia_cella(cella, colore_intestazione)
        r = cella.paragraphs[0].add_run(testo)
        r.bold, r.font.size, r.font.color.rgb = True, Pt(dimensione), RGBColor(0xFF, 0xFF, 0xFF)
    for n, riga in enumerate(righe):
        celle = t.add_row().cells
        for cella, testo in zip(celle, riga):
            if n % 2:
                ombreggia_cella(cella, GRIGIO_CHIARO)
            r = cella.paragraphs[0].add_run(str(testo))
            r.font.size = Pt(dimensione)
    if not larghezze and intestazioni[0] in ("N.", "Rev."):
        resto = (17 - 1.2) / (len(intestazioni) - 1)
        larghezze = [1.2] + [resto] * (len(intestazioni) - 1)
    if larghezze:
        larghezze_colonne(t, larghezze)
    return t


def indice(doc) -> None:
    capitolo(doc, "Indice")
    p = doc.add_paragraph()
    campo(p, 'TOC \\o "1-2" \\h \\z \\u', "Aggiornare l'indice: tasto destro > Aggiorna campo.")
    aggiorna_campi_all_apertura(doc)


def interruzione_pagina(doc) -> None:
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def copertina(doc, *, comune: str, titolo: str, riferimento: str, voci: list[tuple[str, str]],
              data_luogo: str, firme: list[tuple[str, str]], impresa: list[str], logo: str = "") -> None:
    """Copertina incorniciata con banda colorata a sinistra, titolo rosso e dati dell'impresa in basso."""
    t = doc.add_table(rows=3, cols=2)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    larghezze_colonne(t, [2.6, 14.8])
    for riga in t.rows:
        ombreggia_cella(riga.cells[0], GIALLO)
    for riga in t.rows:
        for cella in riga.cells:
            bordi_cella(cella, "000000", 12)

    # Riga 1: comune.
    p = t.rows[0].cells[1].paragraphs[0]
    p.paragraph_format.space_before = Pt(14)
    r = p.add_run(comune or " ")
    r.bold, r.font.size, r.font.color.rgb = True, Pt(18), BLU
    t.rows[0].cells[1].add_paragraph()

    # Riga 2: titolo, dati principali, firme.
    cella = t.rows[1].cells[1]
    p = cella.paragraphs[0]
    p.paragraph_format.space_before = Pt(60)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(titolo)
    r.bold, r.font.size, r.font.color.rgb = True, Pt(30), ROSSO
    p = cella.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f"({riferimento})")
    r.font.size, r.font.color.rgb = Pt(10), BLU
    p.paragraph_format.space_after = Pt(60)
    interna = cella.add_table(rows=0, cols=2)
    senza_bordi(interna)
    for etichetta, valore in voci:
        celle = interna.add_row().cells
        q = celle[0].paragraphs[0]
        q.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        rr = q.add_run(f"{etichetta.upper()}:")
        rr.bold, rr.font.color.rgb, rr.font.size = True, ROSSO, Pt(10)
        rr = celle[1].paragraphs[0].add_run(valore or "-")
        rr.font.size = Pt(10)
    larghezze_colonne(interna, [3.6, 10.6])
    p = cella.add_paragraph()
    p.paragraph_format.space_before = Pt(24)
    p.add_run(data_luogo).font.size = Pt(9.5)
    for ruolo, nome in firme:
        p = cella.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run(ruolo).bold = True
        p = cella.add_paragraph("_________________________________")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if nome:
            p = cella.add_paragraph(f"({nome})")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.runs[0].font.size = Pt(8.5)
    cella.add_paragraph()

    # Riga 3: impresa con logo.
    cella = t.rows[2].cells[1]
    p = cella.paragraphs[0]
    p.paragraph_format.space_before = Pt(8)
    if logo and Path(logo).is_file():
        try:
            p.add_run().add_picture(logo, height=Cm(1.6))
            p = cella.add_paragraph()
        except Exception:  # noqa: BLE001 - logo non leggibile
            pass
    for i, riga in enumerate(r for r in impresa if r):
        q = p if i == 0 else cella.add_paragraph()
        q.paragraph_format.space_after = Pt(0)
        rr = q.add_run(riga)
        rr.font.color.rgb = BLU
        rr.font.size = Pt(11 if i == 0 else 9)
        rr.bold = i == 0
    cella.add_paragraph()


def nuova_sezione_verticale(doc) -> None:
    doc.add_section(WD_SECTION.NEW_PAGE)
