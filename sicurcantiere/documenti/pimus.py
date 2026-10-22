"""Generazione del PiMUS (art. 136 e Allegato XXII del D.Lgs. 81/2008).

Stessa impaginazione del PSC e del POS, nel colore del programma: copertina, capitoli numerati secondo
l'Allegato XXII, dati mancanti evidenziati.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from docx import Document

from sicurcantiere import anagrafiche, pimus
from sicurcantiere.documenti import stile
from sicurcantiere.documenti.comune import data_it, indirizzo_cantiere, salva
from sicurcantiere.documenti.composizione import CONSIGLIATO, OBBLIGATORIO, Manca
from sicurcantiere.repository import Repository

CANTIERE, IMPRESA, PONTEGGI = "Cantiere", "Impresa", "Ponteggi"


def genera_pimus(repo: Repository, ponteggio_id: int, destinazione: str | Path) -> Path:
    with stile.colori_documento(*stile.COLORI_PIMUS):
        return _genera(repo, ponteggio_id, destinazione)


def _misura(valore: float) -> str:
    return f"{valore:g} m".replace(".", ",") if valore else ""


def _genera(repo: Repository, ponteggio_id: int, destinazione: str | Path) -> Path:
    p = repo.leggi("ponteggi", ponteggio_id)
    if p is None:
        raise ValueError("Ponteggio inesistente")
    c = repo.cantiere()
    impresa = (repo.leggi("imprese", p["impresa_id"]) if p["impresa_id"] else None) or {}
    testi = {chiave: repo.testo(pimus.chiave_testo(ponteggio_id, chiave)) for chiave, _, _ in pimus.SEZIONI}
    titoli = {chiave: titolo for chiave, titolo, _ in pimus.SEZIONI}
    comune = f"{c['comune']} ({c['provincia']})" if c["provincia"] else c["comune"]
    data_documento = data_it(date.today())
    progetto_richiesto = p["altezza"] > pimus.ALTEZZA_SENZA_PROGETTO or not p["conforme_schemi"]

    doc = Document()
    stile.imposta_stili(doc)
    stile.imposta_pagina(doc, " · ".join(v for v in (c["nome"], comune) if v),
                         (f"PiMUS · {p['nome']}".strip(" ·"), data_documento))
    stile.copertina(
        doc,
        comune=comune,
        titolo="Piano di montaggio, uso e smontaggio del ponteggio",
        riferimento="D.Lgs. 9 aprile 2008, n. 81 · art. 136 e Allegato XXII",
        voci=[("Cantiere", indirizzo_cantiere(c) or Manca("indirizzo del cantiere", CANTIERE)),
              ("Ponteggio", p["nome"] or Manca("ubicazione del ponteggio", PONTEGGI)),
              ("Tipologia", p["tipo"])],
        data_luogo=f"{c['comune'] or ''}, {data_documento}".strip(", "),
        firme=[("Il datore di lavoro dell'impresa che esegue il montaggio", impresa.get("datore_lavoro", "")),
               ("Il preposto alle operazioni", p["preposto"])],
        impresa=[impresa.get("ragione_sociale") or c["nome"] or "Ponteggio", anagrafiche.sede(impresa)
                 if impresa else ""],
        logo=impresa.get("logo", ""),
    )

    avvisi = pimus.avvisi(p)
    if avvisi:
        stile.banda(doc, "Avvertenze")
        for avviso in avvisi:
            stile.nota(doc, avviso, avviso=True)

    stile.capitolo(doc, "Dati identificativi del luogo di lavoro", "Allegato XXII, punto 1", nuova_pagina=True)
    stile.scheda(doc, [
        ("Opera", c["nome"] or Manca("denominazione dell'opera", CANTIERE)),
        ("Indirizzo del cantiere", indirizzo_cantiere(c) or Manca("indirizzo del cantiere", CANTIERE)),
        ("Ubicazione del ponteggio", p["nome"] or Manca("ubicazione del ponteggio", PONTEGGI)),
    ])

    stile.capitolo(doc, "Datore di lavoro che esegue montaggio, trasformazione e smontaggio",
                   "Allegato XXII, punto 2")
    stile.scheda(doc, [
        ("Impresa", impresa.get("ragione_sociale") or Manca("impresa che monta il ponteggio", PONTEGGI)),
        ("Sede", anagrafiche.sede(impresa) if impresa else ""),
        ("Partita IVA", impresa.get("partita_iva", "")),
        ("Datore di lavoro", impresa.get("datore_lavoro") or Manca("datore di lavoro dell'impresa", IMPRESA)),
    ])

    stile.capitolo(doc, "Squadra di lavoratori e preposto", "Allegato XXII, punto 3, e art. 136, comma 6")
    stile.scheda(doc, [
        ("Preposto alle operazioni", p["preposto"] or Manca("preposto al montaggio", PONTEGGI)),
        ("Addetti al montaggio", p["squadra"] or Manca("addetti al montaggio", PONTEGGI)),
    ])
    doc.add_paragraph("Gli addetti al montaggio, alla trasformazione e allo smontaggio hanno frequentato il corso "
                      "di formazione previsto dall'Allegato XXI (art. 136, comma 6) e operano sotto la diretta "
                      "sorveglianza del preposto.")

    stile.capitolo(doc, "Identificazione del ponteggio", "Allegato XXII, punto 4")
    stile.scheda(doc, [
        ("Tipologia", p["tipo"] or Manca("tipologia del ponteggio", PONTEGGI)),
        ("Fabbricante", p["fabbricante"] or Manca("fabbricante", PONTEGGI)),
        ("Modello", p["modello"]),
        ("Autorizzazione ministeriale", p["autorizzazione"] or Manca("autorizzazione ministeriale (art. 131)",
                                                                     PONTEGGI)),
        ("Altezza massima", _misura(p["altezza"]) or Manca("altezza massima", PONTEGGI)),
        ("Sviluppo in pianta", _misura(p["lunghezza"])),
        ("Classe / sovraccarico ammesso", p["classe_carico"] or Manca("classe di carico", PONTEGGI, CONSIGLIATO)),
    ])

    stile.capitolo(doc, "Disegno esecutivo e progetto", "Allegato XXII, punto 5, e artt. 132-133")
    if progetto_richiesto:
        doc.add_paragraph("Per il ponteggio è richiesto il progetto (art. 133), comprendente calcolo di resistenza "
                          "e stabilità e disegno esecutivo, firmato da un ingegnere o architetto abilitato e "
                          "allegato al presente piano.")
        stile.scheda(doc, [("Progettista", p["progettista"] or Manca("progettista abilitato", PONTEGGI))])
    else:
        doc.add_paragraph("Il ponteggio è montato secondo gli schemi tipo del libretto del fabbricante; il disegno "
                          "esecutivo, firmato dal responsabile del cantiere, riporta sovraccarichi ammessi, appoggi "
                          "e ancoraggi ed è allegato al presente piano (art. 132).")
    stile.scheda(doc, [
        ("Ancoraggi", p["ancoraggi"] or Manca("tipo e maglia degli ancoraggi", PONTEGGI)),
        ("Piano di appoggio", p["piano_appoggio"] or Manca("piano di appoggio", PONTEGGI)),
    ])

    stile.capitolo(doc, "Indicazioni generali per montaggio, trasformazione e smontaggio", "Allegato XXII, punto 6")
    for chiave in ("stoccaggio", "appoggio", "tracciamento", "dpi", "sollevamento", "ancoraggi", "meteo",
                   "istruzioni"):
        stile.sezione(doc, titoli[chiave])
        stile.testo(doc, testi[chiave], titoli[chiave], PONTEGGI, OBBLIGATORIO)
    stile.scheda(doc, [("DPI specifici", p["dpi"]), ("Attrezzature di sollevamento", p["sollevamento"])],
                 titolo="Dotazioni")

    stile.capitolo(doc, "Sequenze di montaggio, trasformazione e smontaggio", "Allegato XXII, punto 7")
    for chiave in ("montaggio", "trasformazione", "smontaggio"):
        stile.sezione(doc, titoli[chiave])
        stile.testo(doc, testi[chiave], titoli[chiave], PONTEGGI, OBBLIGATORIO)

    stile.capitolo(doc, "Regole da applicare durante l'uso", "Allegato XXII, punto 8")
    stile.testo(doc, testi["uso"], titoli["uso"], PONTEGGI, OBBLIGATORIO)

    stile.capitolo(doc, "Verifiche prima del montaggio e durante l'uso", "Allegato XIX")
    verifiche = repo.elenco("verifiche_ponteggio", ponteggio_id=ponteggio_id)
    if verifiche:
        t = stile.tabella_colorata(doc, ["Momento", "Verifica", "Esito", "Note"],
                                   [[v["momento"], v["voce"], v["esito"] or "Da eseguire", v["note"]]
                                    for v in verifiche], 8, larghezze=[3.0, 8.6, 2.4, 3.4])
        for riga, v in zip(t.rows[1:], verifiche):
            stile.colora_livello(riga.cells[2], 0 if v["esito"] in ("Conforme", "Non applicabile")
                                 else 3 if v["esito"] == "Non conforme" else 1)
    else:
        stile.testo(doc, "", "elenco delle verifiche dell'Allegato XIX", PONTEGGI, OBBLIGATORIO)

    p_data = doc.add_paragraph(f"{c['comune'] or ''}, {data_documento}".strip(", "))
    stile._spaziatura(p_data, 14, 8)
    stile.firme(doc, [("Il datore di lavoro dell'impresa che esegue il montaggio", impresa.get("datore_lavoro", "")),
                      ("Il preposto alle operazioni", p["preposto"])])
    stile.nota(doc, "Il PiMUS è redatto da persona competente e messo a disposizione del preposto e dei lavoratori "
                    "addetti; una copia, con il disegno esecutivo e il libretto del fabbricante, è tenuta in "
                    "cantiere a disposizione dell'organo di vigilanza (art. 136, comma 1).")
    return salva(doc, destinazione)
