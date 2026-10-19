"""Modulistica dell'impresa collegata al POS."""

from __future__ import annotations

from pathlib import Path

from sicurcantiere.documenti.comune import indirizzo_cantiere, nuovo_documento, tabella
from sicurcantiere.documenti.pos import elenco_dpi
from sicurcantiere.repository import Repository


def dpi_impresa(repo: Repository, impresa_id: int) -> list[str]:
    rischi = [r for f in repo.elenco("fasi", impresa_id=impresa_id) for r in repo.elenco("rischi", fase_id=f["id"])]
    return elenco_dpi([r["dpi"] for r in rischi])


def genera_consegna_dpi(repo: Repository, impresa_id: int, destinazione: str | Path) -> Path:
    """Verbale di consegna dei DPI (art. 77 e 18 c. 1 lett. d): una pagina per lavoratore."""
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
        doc.add_paragraph("artt. 18 c. 1 lett. d) e 77 del D.Lgs. 81/2008")
        p = doc.add_paragraph()
        p.add_run("Impresa: ").bold = True
        p.add_run(impresa["ragione_sociale"])
        p = doc.add_paragraph()
        p.add_run("Cantiere: ").bold = True
        p.add_run(f"{c['nome']} - {indirizzo_cantiere(c)}".strip(" -"))
        p = doc.add_paragraph()
        p.add_run("Lavoratore: ").bold = True
        p.add_run(l["nome"] or "____________________________")
        p.add_run("   Mansione: ").bold = True
        p.add_run(l["mansione"] or "____________________")
        doc.add_paragraph()
        righe = [[voce, "", "", ""] for voce in dpi] + [["", "", "", ""] for _ in range(3)]
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
        doc.add_paragraph("Il Datore di lavoro (o suo delegato)            Il Lavoratore")
        doc.add_paragraph("_____________________________            _____________________________")
    destinazione = Path(destinazione)
    doc.save(destinazione)
    return destinazione
