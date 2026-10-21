"""Notifica preliminare (art. 99 e Allegato XII del D.Lgs. 81/2008).

Tutti i campi sono ricavati dai dati del progetto.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from sicurcantiere import anagrafiche, analisi
from sicurcantiere.documenti.comune import (
    data_it,
    euro,
    firma,
    indirizzo_cantiere,
    nuovo_documento,
    salva,
    tabella,
    tabella_voci,
)
from sicurcantiere.repository import Repository


def _soggetto(soggetti: list[dict], ruolo: str) -> str:
    trovati = [s for s in soggetti if s["ruolo"] == ruolo and s["nome"].strip()]
    return "; ".join(
        ", ".join(v for v in (s["nome"], s["codice_fiscale"], s["indirizzo"]) if v) for s in trovati
    )


def genera_notifica(repo: Repository, destinazione: str | Path) -> Path:
    c = repo.cantiere()
    soggetti = anagrafiche.soggetti(repo)
    imprese = repo.elenco("imprese")
    fasi = repo.elenco("fasi")
    periodo = analisi.periodo_lavori(fasi)
    durata = analisi.giorni_lavorativi(*periodo) if periodo else 0

    doc = nuovo_documento()
    doc.add_heading("NOTIFICA PRELIMINARE", 0)
    doc.add_paragraph("art. 99 e Allegato XII del D.Lgs. 9 aprile 2008, n. 81")
    doc.add_paragraph("All'Azienda Sanitaria Locale, all'Ispettorato territoriale del lavoro "
                      "e, per le opere pubbliche, al Prefetto competenti per territorio.")

    tabella_voci(doc, [
        ("1. Data della comunicazione", data_it(date.today())),
        ("2. Indirizzo del cantiere", indirizzo_cantiere(c)),
        ("3. Committente", _soggetto(soggetti, "Committente")),
        ("4. Natura dell'opera", c["natura_opera"] or c["nome"]),
        ("5. Responsabile dei lavori", _soggetto(soggetti, "Responsabile dei lavori")),
        ("6. Coordinatore per la progettazione", _soggetto(soggetti, "Coordinatore per la progettazione (CSP)")),
        ("7. Coordinatore per l'esecuzione", _soggetto(soggetti, "Coordinatore per l'esecuzione (CSE)")),
        ("8. Data presunta d'inizio dei lavori", data_it(periodo[0]) if periodo else ""),
        ("9. Durata presunta dei lavori", f"{durata} giorni lavorativi" if durata else ""),
        ("10. Numero massimo presunto dei lavoratori in cantiere", str(analisi.picco_lavoratori(fasi))),
        ("11. Numero previsto di imprese e di lavoratori autonomi", str(len(imprese))),
        ("13. Ammontare complessivo presunto dei lavori", euro(c["importo_lavori"])),
    ])

    doc.add_heading("12. Imprese già selezionate", 2)
    tabella(doc, ["Ragione sociale", "Tipo", "P. IVA / C.F.", "Sede"], [
        [i["ragione_sociale"], i["tipo"], i["partita_iva"] or i["codice_fiscale"], i["indirizzo"]]
        for i in imprese
    ])

    firma(doc, "Il Committente o il Responsabile dei lavori")
    return salva(doc, destinazione)
