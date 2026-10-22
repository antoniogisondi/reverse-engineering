"""Modulistica dell'impresa collegata al POS."""

from __future__ import annotations

from pathlib import Path

from sicurcantiere import anagrafiche
from sicurcantiere.documenti.comune import indirizzo_cantiere, nuovo_documento, salva, tabella
from sicurcantiere.documenti.pos import elenco_dpi
from sicurcantiere.repository import Repository


def dpi_impresa(repo: Repository, impresa_id: int) -> list[str]:
    rischi = [r for f in repo.elenco("fasi", impresa_id=impresa_id) for r in repo.rischi(fase_id=f["id"])]
    return elenco_dpi([r["dpi"] for r in rischi])


def genera_consegna_dpi(repo: Repository, impresa_id: int, destinazione: str | Path) -> Path:
    """Verbale di consegna dei DPI (art. 77 e art. 18, comma 1, lettera d): una pagina per lavoratore."""
    impresa = repo.leggi("imprese", impresa_id)
    if impresa is None:
        raise ValueError("Impresa inesistente")
    c = repo.cantiere()
    lavoratori = repo.elenco("lavoratori", impresa_id=impresa_id) or [
        {"nome": "", "mansione": ""}  # modulo in bianco
    ]
    dpi = dpi_impresa(repo, impresa_id)
    doc = nuovo_documento()
    for n, l in enumerate(lavoratori):
        if n:
            doc.add_page_break()
        doc.add_heading("VERBALE DI CONSEGNA DEI DISPOSITIVI DI PROTEZIONE INDIVIDUALE", 1)
        doc.add_paragraph("Art. 18, comma 1, lettera d), e art. 77 del D.Lgs. 81/2008")
        p = doc.add_paragraph()
        p.add_run("Impresa: ").bold = True
        p.add_run(impresa["ragione_sociale"])
        p = doc.add_paragraph()
        p.add_run("Cantiere: ").bold = True
        p.add_run(f"{c['nome']} - {indirizzo_cantiere(c)}".strip(" -"))
        p = doc.add_paragraph()
        p.add_run("Lavoratore: ").bold = True
        p.add_run(anagrafiche.nominativo(l) or "____________________________")
        p.add_run("   Mansione: ").bold = True
        p.add_run(l["mansione"] or "____________________")
        doc.add_paragraph()
        propri = anagrafiche.dpi_lavoratore(l)
        righe = [[voce, "", "", ""] for voce in (propri or dpi)] + [["", "", "", ""] for _ in range(3)]
        tabella(doc, ["Dispositivo", "Marca / modello", "Quantità", "Data di consegna"], righe)
        doc.add_paragraph()
        doc.add_paragraph(
            "Il lavoratore dichiara di aver ricevuto i dispositivi sopra elencati, di essere stato "
            "informato e formato sul loro uso corretto e, per i DPI di terza categoria, addestrato; "
            "si impegna a utilizzarli secondo le istruzioni, ad averne cura e a segnalare "
            "immediatamente difetti o inconvenienti (art. 78)."
        )
        doc.add_paragraph()
        doc.add_paragraph("Data: ____/____/________")
        doc.add_paragraph("Il datore di lavoro (o suo delegato)            Il lavoratore")
        doc.add_paragraph("_____________________________            _____________________________")
    return salva(doc, destinazione)
