"""Generazione del PiMUS (art. 136 e Allegato XXII del D.Lgs. 81/2008)."""

from __future__ import annotations

from pathlib import Path

from sicurcantiere import pimus
from sicurcantiere.documenti.comune import (
    firma,
    frontespizio,
    indirizzo_cantiere,
    nuovo_documento,
    salva,
    tabella,
    tabella_voci,
    testo_o_segnaposto,
)
from sicurcantiere.repository import Repository


def genera_pimus(repo: Repository, ponteggio_id: int, destinazione: str | Path) -> Path:
    p = repo.leggi("ponteggi", ponteggio_id)
    if p is None:
        raise ValueError("Ponteggio inesistente")
    c = repo.cantiere()
    impresa = repo.leggi("imprese", p["impresa_id"]) if p["impresa_id"] else None
    testi = {chiave: repo.testo(pimus.chiave_testo(ponteggio_id, chiave)) for chiave, _, _ in pimus.SEZIONI}
    titoli = {chiave: titolo for chiave, titolo, _ in pimus.SEZIONI}

    doc = nuovo_documento()
    frontespizio(doc, repo, "PIANO DI MONTAGGIO, USO E SMONTAGGIO DEL PONTEGGIO (PiMUS)",
                 "art. 136 e Allegato XXII del D.Lgs. 9 aprile 2008, n. 81", f"PIMUS:{ponteggio_id}",
                 [("Ponteggio", p["nome"]), ("Impresa", impresa["ragione_sociale"] if impresa else "")])

    avvisi = pimus.avvisi(p)
    if avvisi:
        doc.add_heading("Avvertenze", 1)
        for a in avvisi:
            doc.add_paragraph(a, style="List Bullet")

    doc.add_heading("1. Dati identificativi del luogo di lavoro", 1)
    tabella_voci(doc, [("Opera", c["nome"]), ("Indirizzo del cantiere", indirizzo_cantiere(c)),
                       ("Ubicazione del ponteggio", p["nome"])])

    doc.add_heading("2. Datore di lavoro che esegue montaggio, trasformazione e smontaggio", 1)
    tabella_voci(doc, [
        ("Impresa", impresa["ragione_sociale"] if impresa else ""),
        ("Sede", impresa["indirizzo"] if impresa else ""),
        ("Partita IVA", impresa["partita_iva"] if impresa else ""),
        ("Datore di lavoro", impresa["datore_lavoro"] if impresa else ""),
    ])

    doc.add_heading("3. Squadra di lavoratori e preposto", 1)
    tabella_voci(doc, [("Preposto alle operazioni", p["preposto"]), ("Addetti", p["squadra"])])
    doc.add_paragraph("Gli addetti hanno frequentato il corso di formazione previsto dall'Allegato XXI "
                      "(art. 136, comma 6).")

    doc.add_heading("4. Identificazione del ponteggio", 1)
    tabella_voci(doc, [
        ("Tipologia", p["tipo"]),
        ("Fabbricante", p["fabbricante"]),
        ("Modello", p["modello"]),
        ("Autorizzazione ministeriale", p["autorizzazione"]),
        ("Altezza massima", f"{p['altezza']:g} m".replace(".", ",") if p["altezza"] else ""),
        ("Sviluppo in pianta", f"{p['lunghezza']:g} m".replace(".", ",") if p["lunghezza"] else ""),
        ("Classe / sovraccarico ammesso", p["classe_carico"]),
    ])

    doc.add_heading("5. Disegno esecutivo e progetto", 1)
    if p["altezza"] > pimus.ALTEZZA_SENZA_PROGETTO or not p["conforme_schemi"]:
        doc.add_paragraph(
            "Per il ponteggio è richiesto il progetto (art. 133), allegato al presente piano, redatto da "
            f"{p['progettista'] or '[indicare il progettista abilitato]'}."
        )
    else:
        doc.add_paragraph(
            "Il ponteggio è montato secondo gli schemi tipo del libretto del fabbricante; il disegno "
            "esecutivo, firmato dal responsabile del cantiere, riporta sovraccarichi ammessi, "
            "appoggi e ancoraggi ed è allegato al presente piano."
        )
    tabella_voci(doc, [("Ancoraggi", p["ancoraggi"]), ("Piano di appoggio", p["piano_appoggio"])])

    doc.add_heading("6. Indicazioni generali per montaggio, trasformazione e smontaggio", 1)
    for chiave in ("stoccaggio", "appoggio", "tracciamento", "dpi", "sollevamento", "ancoraggi", "meteo",
                   "istruzioni"):
        doc.add_heading(titoli[chiave], 2)
        testo_o_segnaposto(doc, testi[chiave])
    if p["dpi"].strip() or p["sollevamento"].strip():
        tabella_voci(doc, [("DPI specifici", p["dpi"]), ("Attrezzature di sollevamento", p["sollevamento"])])

    doc.add_heading("7. Sequenze di montaggio, trasformazione e smontaggio", 1)
    for chiave in ("montaggio", "trasformazione", "smontaggio"):
        doc.add_heading(titoli[chiave], 2)
        testo_o_segnaposto(doc, testi[chiave])

    doc.add_heading("8. Regole da applicare durante l'uso", 1)
    testo_o_segnaposto(doc, testi["uso"])

    doc.add_heading("9. Verifiche prima del montaggio e durante l'uso", 1)
    verifiche = repo.elenco("verifiche_ponteggio", ponteggio_id=ponteggio_id)
    if verifiche:
        tabella(doc, ["Momento", "Verifica", "Esito", "Note"],
                [[v["momento"], v["voce"], v["esito"] or "Da eseguire", v["note"]] for v in verifiche],
                dimensione=8)
    else:
        testo_o_segnaposto(doc, "")

    firma(doc, "Il datore di lavoro dell'impresa che esegue il montaggio")
    doc.add_paragraph("Il preposto alle operazioni")
    doc.add_paragraph("_______________________________")
    return salva(doc, destinazione)
