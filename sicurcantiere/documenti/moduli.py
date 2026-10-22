"""Modulistica dell'impresa collegata al POS."""

from __future__ import annotations

from pathlib import Path

from sicurcantiere import anagrafiche
from sicurcantiere.documenti import stile
from sicurcantiere.documenti.comune import indirizzo_cantiere, salva
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
    comune = f"{c['comune']} ({c['provincia']})" if c["provincia"] else c["comune"]
    doc = stile.documento_semplice(" · ".join(v for v in (c["nome"], comune) if v),
                                   ("Verbale di consegna dei DPI", impresa["ragione_sociale"]))
    for n, l in enumerate(lavoratori):
        stile.intestazione_modulo(doc, "D.Lgs. 9 aprile 2008, n. 81 · art. 18, comma 1, lettera d), e artt. 77-78",
                                  "Verbale di consegna dei DPI", anagrafiche.nominativo(l) or "", nuova_pagina=n > 0)
        stile.scheda(doc, [
            ("Impresa", impresa["ragione_sociale"]),
            ("Cantiere", " · ".join(v for v in (c["nome"], indirizzo_cantiere(c)) if v)),
            ("Lavoratore", anagrafiche.nominativo(l) or " "),
            ("Mansione", l["mansione"] or " "),
        ])
        propri = anagrafiche.dpi_lavoratore(l)
        righe = [[voce, " ", " ", " "] for voce in (propri or dpi)] + [[" ", " ", " ", " "] for _ in range(3)]
        stile.tabella_colorata(doc, ["Dispositivo", "Marca / modello", "Quantità", "Data di consegna"], righe, 9,
                               larghezze=[7.4, 4.6, 2.0, 3.4])
        doc.add_paragraph(
            "Il lavoratore dichiara di aver ricevuto i dispositivi sopra elencati, di essere stato informato e formato "
            "sul loro uso corretto e, per i DPI di terza categoria, addestrato; si impegna a utilizzarli secondo le "
            "istruzioni, ad averne cura e a segnalare immediatamente difetti o inconvenienti (artt. 20 e 78).")
        p = doc.add_paragraph("Data ____ / ____ / ________")
        stile._spaziatura(p, 12, 8)
        stile.firme(doc, [("Il datore di lavoro o un suo delegato", impresa["datore_lavoro"]),
                          ("Il lavoratore", anagrafiche.nominativo(l))])
    return salva(doc, destinazione)
