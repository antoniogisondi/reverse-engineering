"""Fascicolo con le caratteristiche dell'opera (Allegato XVI del D.Lgs. 81/2008)."""

from __future__ import annotations

from pathlib import Path

from sicurcantiere import anagrafiche, analisi
from sicurcantiere.documenti.comune import (
    data_it,
    euro,
    firma,
    frontespizio,
    indirizzo_cantiere,
    nuovo_documento,
    tabella,
    tabella_voci,
    testo_o_segnaposto,
)
from sicurcantiere.repository import Repository


def genera_fascicolo(repo: Repository, destinazione: str | Path) -> Path:
    c = repo.cantiere()
    fasi = repo.elenco("fasi")
    interventi = repo.elenco("interventi")
    periodo = analisi.periodo_lavori(fasi)

    doc = nuovo_documento()
    frontespizio(doc, repo, "FASCICOLO DELL'OPERA",
                 "art. 91 c. 1 lett. b) e Allegato XVI del D.Lgs. 81/2008", "FASCICOLO")

    doc.add_heading("Capitolo I - Descrizione sintetica dell'opera e soggetti coinvolti", 1)
    doc.add_heading("Scheda I", 2)
    tabella_voci(doc, [
        ("Opera", c["nome"]),
        ("Natura dell'opera", c["natura_opera"]),
        ("Indirizzo", indirizzo_cantiere(c)),
        ("Importo dei lavori", euro(c["importo_lavori"])),
        ("Inizio lavori", data_it(periodo[0]) if periodo else "-"),
        ("Fine lavori", data_it(periodo[1]) if periodo else "-"),
    ])
    doc.add_paragraph()
    testo_o_segnaposto(doc, c["descrizione"])
    doc.add_heading("Soggetti", 3)
    tabella(doc, ["Ruolo", "Nominativo", "Recapiti"], [
        [s["ruolo"], s["nome"], " - ".join(v for v in (s["indirizzo"], s["telefono"], s["email"]) if v)]
        for s in anagrafiche.soggetti(repo)
    ])

    doc.add_heading("Capitolo II - Misure preventive e protettive in dotazione dell'opera e ausiliarie", 1)
    doc.add_heading("Scheda II-1: interventi di manutenzione e relative misure", 2)
    if interventi:
        for parte in dict.fromkeys(i["parte_opera"] for i in interventi):
            doc.add_heading(parte or "Opera", 3)
            tabella(doc, ["Intervento", "Periodicità", "Rischi individuati",
                          "Misure in dotazione dell'opera", "Misure ausiliarie"], [
                [i["intervento"], i["periodicita"], i["rischi"], i["misure_in_dotazione"], i["misure_ausiliarie"]]
                for i in interventi if i["parte_opera"] == parte
            ], dimensione=8)
    else:
        testo_o_segnaposto(doc, "")

    doc.add_heading("Scheda II-3: misure preventive e protettive in dotazione dell'opera", 2)
    dotazioni = sorted({i["misure_in_dotazione"].strip() for i in interventi if i["misure_in_dotazione"].strip()})
    if dotazioni:
        tabella(doc, ["Misura in dotazione", "Verifiche e controlli", "Periodicità"], [
            [m, "", ""] for m in dotazioni
        ])
    else:
        testo_o_segnaposto(doc, "")

    doc.add_heading("Capitolo III - Riferimenti alla documentazione di supporto", 1)
    elaborati = repo.elenco("elaborati")
    if elaborati:
        tabella(doc, ["Elaborato", "Autore", "Data", "Collocazione"], [
            [e["titolo"], e["autore"], data_it(e["data"]), e["collocazione"]] for e in elaborati
        ])
    else:
        testo_o_segnaposto(doc, "")

    firma(doc, "Il Coordinatore per la sicurezza")
    destinazione = Path(destinazione)
    doc.save(destinazione)
    return destinazione
